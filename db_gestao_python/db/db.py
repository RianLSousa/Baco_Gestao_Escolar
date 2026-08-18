import os

import mysql.connector
from dotenv import load_dotenv
from flask import session

from mysql.connector import Error
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.abstracts import MySQLConnectionAbstract

from typing import Any

load_dotenv()


class DatabaseConnection:
    def __init__(
        self,
        db: str,
        host: str | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        super().__init__()
        self._db: str = db
        self._host: str = host or os.getenv("DB_HOST", "localhost")

        # Se usuário/senha não vieram explícitos (uso normal dentro das rotas),
        # busca da sessão do Flask, que é preenchida no login.
        if user is None or password is None:
            user = session.get("db_user")
            password = session.get("db_password")

        if not user or password is None:
            raise PermissionError(
                "Nenhum usuário conectado ao banco de dados. É necessário fazer login."
            )

        self._user: str = user
        self._password: str = password
        self._connection: PooledMySQLConnection | MySQLConnectionAbstract | None = None

    def __enter__(self) -> PooledMySQLConnection | MySQLConnectionAbstract:
        try:
            self._connection = mysql.connector.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                database=self._db,
            )
            if self._connection.is_connected():
                print(f"Conexão com o banco de dados bem-sucedida! (usuário: {self._user})")
        except Error as e:
            print(f'Erro ao conectar ao banco de dados: {e}')
            raise
        return self._connection

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None
            print('Conexão com o banco de dados fechada.')


def executar_select(db: str, consulta_sql: str, parametros: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
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
    try:
        with DatabaseConnection(db=db) as connection:
            cursor = connection.cursor()
            cursor.execute(consulta_sql, params=parametros)
            connection.commit()
            qtd_linhas: int = cursor.rowcount if cursor.rowcount is not None else -1
            if cursor.with_rows:
                cursor.fetchall()
            return qtd_linhas
    except Error as e:
        print(f"Erro ao executar INSERT/UPDATE/DELETE: {e}")
        return -1


def executar_insert_retornando_id(db: str, consulta_sql: str, parametros: tuple[Any, ...] = ()) -> int:
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