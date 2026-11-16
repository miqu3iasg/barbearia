import logging
import os
import time

import mysql.connector
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

mysql_host = os.getenv("MYSQL_HOST")
mysql_database = os.getenv("MYSQL_DATABASE")
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")

CONFIG = {
    "user": mysql_user,
    "password": mysql_password,
    "host": mysql_host,
    "database": mysql_database,
    "raise_on_warnings": True,
}


# Veja: https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
def connect(config: dict = None, attempts: int = 3, delay: float = 2):
    """Conecta ao MySQL, tentando novamente com backoff exponencial.

    Args:
        config: Dicionário de configuração do conector. Se None, usa CONFIG.
        attempts: Número total de tentativas de conexão.
        delay: Base do backoff exponencial, em segundos. A espera após a
            tentativa n é delay**n (com delay=2: 2s, 4s, 8s...).

    Returns:
        A conexão MySQL aberta.

    Raises:
        mysql.connector.Error: Se todas as tentativas falharem.
    """
    if config is None:
        config = CONFIG
    attempt = 1
    while attempt <= attempts:
        try:
            return mysql.connector.connect(**config)
        except (mysql.connector.Error, IOError) as err:
            if attempt == attempts:
                logger.error("Falha ao conectar, encerrando conexão: %s", err)
                raise
            logger.info(
                "Falha na conexão: %s. Tentando novamente (%d/%d)...",
                err,
                attempt,
                attempts,
            )
            time.sleep(delay**attempt)
            attempt += 1


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    cnx = connect(CONFIG)
    logger.info("Conectado ao MySQL versão %s", cnx.server_info)
    cnx.close()
