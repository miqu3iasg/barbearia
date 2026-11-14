---
title: ADR-001-estrutura-do-projeto
tags:
    - architecture
    - adr
date: 2026-11-13T21:17:12
id: 6807c9ec-378a-456c-83fd-67de19cc005c
---

# ADR-001 Estrutura do projeto

## Context

Fala rapaziada, isso aqui é um ADR (Architecture Decision Record). A gente usa isso pra documentar decisões, porque assim facilita vocês saberem o motivo de cada decisão, e todo mundo consegue acompanhar o raciocínio de todo mundo. Vou explicar um pouco da estrutura do projeto pra vocês.

## Decision

A estrutura do projeto usa uma arquitetura que a gente chama de MVC (Model View Controller), que wild já explicou na aula. Mas é um arquitetura bem simples que permite a gente moduluzarizar um projeto e manter consistência e organização,separando um pouco as responsabilidades de cada módulo e mantendo uma estrutura básica e fácil de manter para projetos pequenos. Cada pasta representa um módulo e nenhum módulo assume a responsabilidade do outro.

Por enquanto a estrutura tá basicamente assim:

```
├── controller
├── database
├── docs # Documentações no geral
│   └── adr
├── model
├── repository
├── resources # PDFs de ajuda
└── view
```

O `controller` é o que gerencia as requsições que chegam na aplicação, é ele que redireciona cada ação usando o que chama de _"rotas"_. Cada rota direciona para uma ação ou serviço específico dentro da aplicação. Numa aplicação um pouquinho maior, a gente teria mais uma camada de abstração entre o `controller` e o `repository` (já vou falar depois), que seria o `service`, onde ele seria o mediador entre os repositórios que se integram ao banco e a camada de controller, mas nesse caso a gente não vai fazer isso, toda a lógica de serviço será colocada dentro do própri controller, já que é um programa bem pequeno.

A pasta `database` é onde a gente vai colocar os arquivos de conexão com o banco de dados e o `schema.sql` que é só o código SQL que vai criar o nosso banco e as tabelas. Em `docs` é onde a gente vai documentar o que for necessário, eu sempre vou escrever aqui. O `model` é onde vamos colocar os arquivos de entidades da aplicação, e em cada arquivo de entidade a gente vai ter os atributos de cada um de modo que eles espelhem a tabela do banco (veja: database/schema.sql). Além disso, dentro de cada classe vamos colocar funções que validam algumas regras de negócio. Esses métodos devem ficar dentro das classes de domínio porque dessa forma a gente preserva a integridade das classes que refletem o banco. A camada de controller não deve conhecer as regras de negócio da aplicação porque ela é uma camada "mais acima" dentro do modelo MVC, a gente chama de layers, camadas (vou deixar uns links pra vocês estudarem legal).

O `repository` é onde a gente interagir de ato com o banco, não tem segredo, já vimos isso na aula. E a `view` é onde vamos colocar as telas do tkinter :(. Também vou deixar aqui uma pasta chamada `resources`, onde vou colocar PDFs que podem ajudar vocês a estudarem.

## Alternatives Considered

Nenhuma outra alternativa foi considerada porque o escopo do trabalho é justamente trabalhar com MVC. Se pudéssemos usar uma arquitetura livre, também teria escolhido MVC pela simplicidade. Não faria sentido usar uma arquitetura mais complexa com arquitetura hexagonal ou clean arch pra um projeto tão pequeno.

## Consequences

### Positive

- Maior organização
- Melhor manutabilidade
- Reforça a integridade da aplicação

### Negative

- Traz o desafio de aprender a integração entre módulos de maneira consistente

## References

- [Arqutitetura MVC](https://pt.wikipedia.org/wiki/MVC)
- [Arquitetura em camadas](https://www.ibm.com/br-pt/think/topics/three-tier-architecture)
- [O que é um ADR](https://www.archyl.com/pt/blog/architecture-decision-records-complete-guide)
- [Playlist completa destrinchando MVC em python](https://youtube.com/playlist?list=PLAgbpJQADBGKvsjOu4gHU5E9WUQs8XRgS&si=OaMPnMDhZwbvqevL)
