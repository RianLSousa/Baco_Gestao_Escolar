import getpass

import mysql.connector
from werkzeug.security import generate_password_hash

conexao = mysql.connector.connect(
    host="localhost",
    user="secretaria_escolar",
    password="TrocarSenha_Secretaria!1",
    database="gestao_escolar",
)
cursor = conexao.cursor()

nome = input("Nome do primeiro usuário (será cadastrado como secretaria): ")
login = input("Login: ")
senha = getpass.getpass("Senha: ")

senha_hash = generate_password_hash(senha)

cursor.execute(
    "INSERT INTO usuario_sistema (nome, login, senha_hash, papel) VALUES (%s, %s, %s, %s)",
    (nome, login, senha_hash, "secretaria"),
)
conexao.commit()
print(f"Usuário '{nome}' criado com sucesso como secretaria!")

conexao.close()