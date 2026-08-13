import mysql.connector

from mysql.connector import Error
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.abstracts import MySQLConnectionAbstract

from typing import Any


class DatabaseConnection:
    def __init__(self, db: str, host: str = "localhost", user: str = "root", password: str = "") -> None:
        super().__init__()
        self._db: str = db
        self._host: str = host
        self._user: str = user
        self._password: str = password
        self._connection: PooledMySQLConnection | MySQLConnectionAbstract | None = None

    def __enter__(self) -> PooledMySQLConnection | MySQLConnectionAbstract:
        """
        Estabelece a conexão com o banco de dados e retorna a conexão.

        :param db: nome do banco de dados
        :param host: endereço do servidor de banco de dados (default: "localhost")
        :param user: nome de usuário do banco de dados (default: "root")
        :param password: senha do banco de dados (default: "")
        """
        try:
            self._connection = mysql.connector.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                database=self._db,
            )

            if self._connection.is_connected():
                print('Conexão com o banco de dados bem-sucedida!')
        except Error as e:
            print(f'Erro ao conectar ao banco de dados: {e}')
            raise
        return self._connection

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Fecha a conexão com o banco de dados ao sair do contexto.
        """
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
            print('Conexão com o banco de dados fechada.')


def executar_select(db: str, consulta_sql: str, parametros: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    """
    Conecta com o DB e executa uma consulta SQL do tipo SELECT FROM,
    passando uma lista de parametros para a consulta.

    Retorna uma lista de registros encontrados pela consulta SELECT.
    """
    try:
        with DatabaseConnection(db=db) as connection:
            cursor = connection.cursor()
            cursor.execute(consulta_sql, params=parametros)
            registros = cursor.fetchall()
            if not registros:
                return []
            return registros  # pyright: ignore[reportReturnType]
    except Error as e:
        print(f"Erro ao executar SELECT: {e}")
        raise


def executar_insert_delete_update(db: str, consulta_sql: str, parametros: tuple[Any, ...] = ()) -> int:
    """
    Conecta com o DB e executa uma consulta SQL do tipo INSERT INTO, DELETE ou UPDATE,
    passando uma lista de parametros para a consulta.

    :return: qtd linhas alteradas se operacao bem sucedida, do contrario retorna -1.
    """
    try:
        with DatabaseConnection(db=db) as connection:
            cursor = connection.cursor()
            cursor.execute(consulta_sql, params=parametros)
            connection.commit()
            qtd_linhas: int = cursor.rowcount or -1
            if cursor.with_rows:
                cursor.fetchall()
            return qtd_linhas
    except Error as e:
        print(f"Erro ao executar INSERT/UPDATE/DELETE: {e}")
        return -1


def executar_insert_retornando_id(db: str, consulta_sql: str, parametros: tuple[Any, ...] = ()) -> int:
    """
    Conecta com o DB, executa um INSERT INTO e retorna o ID autoincrementado gerado.
    """
    try:
        with DatabaseConnection(db=db) as connection:
            cursor = connection.cursor()
            cursor.execute(consulta_sql, params=parametros)
            connection.commit()
            last_id: int = cursor.lastrowid or -1
            if cursor.with_rows:
                cursor.fetchall()
            return last_id
    except Error as e:
        print(f"Erro ao executar INSERT com retorno de ID: {e}")
        return -1
