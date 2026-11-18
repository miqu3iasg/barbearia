---
title: ADR-002-fluxo-controller-repository
tags:
    - architecture
    - adr
date: 2026-11-18T00:06
id: ddff743b-03e0-4a24-afc7-f0303857482f
---

# ADR-002 Fluxo do controller para o repository

## Context

No [[ADR-001-estrutura-do-projeto]] a gente definiu as pastas do projeto e a responsabilidade de cada uma. Só que ficou faltando explicar uma coisa importante: **como uma ação sai do `controller`, passa pelo `model` e chega no `repository`**. Se cada controller resolver isso do seu jeito, o projeto vira uma bagunça rapidinho: um devolve erro de um jeito, outro de outro, um valida antes de salvar e outro depois, e ninguém sabe onde procurar quando algo quebra.

Hoje a gente tem quatro controllers (`cliente`, `barbeiro`, `servico` e `agendamento`), todos escritos pelo Salsa, e todos seguem o mesmo fluxo. Este ADR documenta esse fluxo pra ele continuar igual quando alguém for criar um controller novo.

## Decision

O `controller` é o único ponto de contato entre a `view` e o banco. A `view` nunca fala direto com o `repository`, e o `repository` nunca valida regra nenhuma, ele só lê e escreve. Como a gente não vai ter a camada de `service` (veja o ADR-001), o controller também faz esse papel de orquestrar o caso de uso.

O caminho de uma ação é sempre esse:

```
view  →  controller  →  model        (validação das regras da entidade)
                     →  repository   →  banco de dados (MySQL)
```

### O passo a passo de um cadastro

Pegando `cadastrar_cliente` como exemplo:

1. **A view chama o controller** com os dados crus, do jeito que vieram da tela (strings dos campos do tkinter).
2. **O controller limpa os dados**: tira espaços do nome, deixa só os dígitos do telefone (aceita `(75) 99999-0000`), converte o preço pra `Decimal` (aceita `35,50` e `35.50`).
3. **O controller monta a entidade do `model`** e chama os métodos de validação dela (`validar_nome`, `validar_telefone`, `validar_preco`...).
4. **O controller chama o `repository`** passando só valores simples (`cliente.nome`, `cliente.telefone`), não o objeto da entidade.
5. **O repository executa o SQL** e devolve o resultado.
6. **O controller devolve pra view** o ID criado, ou o registro atualizado.

Nos fluxos de `atualizar` e `excluir` tem um passo extra no começo: o controller chama `buscar_*` antes de qualquer coisa pra garantir que o registro existe. Assim o usuário recebe "não encontrado" e não um update que silenciosamente não faz nada.

### Convenção de erros

Erro de regra de negócio **sempre** vira `ValueError` com uma mensagem pronta pra mostrar pro usuário. A view só precisa de um `try/except ValueError` e exibir `str(erro)`.

Isso inclui os erros que vêm do banco. O `repository` deixa o `IntegrityError` do `mysql.connector` subir, e o controller é quem traduz:

| Situação                                             | Origem                  | Mensagem pro usuário                                 |
| ---------------------------------------------------- | ----------------------- | ---------------------------------------------------- |
| Telefone repetido                                    | UNIQUE em `cliente`     | "Já existe um cliente cadastrado com esse telefone." |
| Nome de serviço repetido                             | UNIQUE em `servico`     | "Já existe um serviço com esse nome."                |
| Excluir cliente, barbeiro ou serviço com agendamento | FOREIGN KEY             | "Não é possível excluir: ... possui agendamentos."   |
| Dois clientes pegam o mesmo horário ao mesmo tempo   | UNIQUE em `agendamento` | "Esse horário acabou de ser ocupado. Escolha outro." |

O `from None` no `raise` é de propósito: esconde o erro técnico do MySQL e deixa só a mensagem amigável.

### O que o controller espera do repository

O `repository` precisa seguir um contrato simples pra os controllers funcionarem do mesmo jeito:

- `buscar_*_por_id` devolve um `dict`, ou `None` se não achar. Quem decide que "não achar" é erro é o controller.
- `listar_*` devolve uma `list` de `dict`.
- `criar_*` devolve o ID do registro criado.
- `atualizar_*` pode devolver o `rowcount`, mas o controller **ignora** esse retorno. O MySQL devolve 0 quando os dados novos são iguais aos antigos, então 0 não significa erro. Por isso o controller busca o registro de novo no final e devolve ele atualizado.
- `excluir_*` devolve `True` ou `False` dizendo se apagou alguma coisa (usado em `cancelar_agendamento`).
- O repository não levanta `ValueError` e não conhece mensagem de usuário.

### O caso especial do agendamento

`agendamento_controller` é o único que conversa com mais de um repository: ele consulta `cliente`, `barbeiro` e `servico` pra confirmar que os três existem antes de agendar. Isso é aceitável porque quem une as entidades é o controller, os repositories continuam sem saber um do outro.

O conflito de horário tem **duas camadas de proteção** de propósito:

1. `existe_conflito_de_horario` checa antes de inserir e dá uma mensagem clara no caso comum.
2. O `IntegrityError` do banco cobre a corrida, quando duas pessoas passam pela checagem ao mesmo tempo. Só o banco consegue garantir isso de verdade.

Do mesmo jeito, a mudança de status (`AGENDADO` para `ATENDIDO`) e o cancelamento são regras decididas no controller, e o repository só executa o `UPDATE` ou o `DELETE`.

## Alternatives Considered

**Repository com as validações e as mensagens de erro.** Descartado porque o repository passaria a ter regra de negócio, e o ADR-001 deixa claro que cada módulo não assume a responsabilidade do outro. Também ficaria difícil reaproveitar o repository em outro contexto.

**Deixar o `IntegrityError` subir até a view.** Descartado porque a view teria que conhecer `mysql.connector` e entender o que cada constraint significa. Traduzir no controller mantém a view burra e as mensagens num lugar só.

**Criar uma camada de `service`.** Descartado pelo mesmo motivo do ADR-001: o projeto é pequeno e a camada extra não se paga. Se o projeto crescer, os controllers atuais já estão organizados de um jeito que facilita extrair essa lógica.

**Checar existência só pelo retorno do `atualizar_*` / `excluir_*`.** Descartado porque o MySQL devolve `rowcount` 0 quando nada mudou, o que seria confundido com "não encontrado".

## Consequences

### Positive

- Todos os controllers se comportam igual, então quem aprende um entende os outros
- A view só trata um tipo de erro (`ValueError`)
- O repository fica simples e fácil de testar, só SQL
- Mensagens de erro ficam centralizadas no controller

### Negative

- O controller acumula responsabilidade (orquestração, normalização e tradução de erro), o que pesa mais nos controllers maiores, como o de agendamento
- Algumas regras ainda moram no controller e não no `model`, o que foge um pouco do que o ADR-001 pede: o limite de 10 a 15 dígitos do telefone, a lista de status válidos do barbeiro, a grade de horários e o limite de 255 caracteres da observação. Vale mover pro `model` quando der
- O fluxo depende de todo mundo seguir a convenção do `ValueError` e do contrato do repository, e nada no código obriga isso

## References

- [[ADR-001-estrutura-do-projeto]]
- Controllers escritos pelo Salsa
- `controller/cliente_controller.py`: exemplo mais simples do fluxo completo
- `controller/agendamento_controller.py`: exemplo com vários repositories e conflito de horário
- `database/schema.sql`: constraints (UNIQUE, FOREIGN KEY, CHECK) que geram os `IntegrityError`
