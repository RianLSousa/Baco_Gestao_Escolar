import os
import time
from datetime import date, datetime

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from mysql.connector import Error

from db.db import (
    DatabaseConnection,
    executar_insert_delete_update,
    executar_insert_retornando_id,
    executar_select,
)

load_dotenv()


# Criar a aplicacao Flask
app = Flask(__name__)
DB_NAME = "gestao_escolar"

app.secret_key = os.getenv("SECRET_KEY")

# seção de autenticação 

ROTAS_PUBLICAS = {"tela_login", "api_login", "static"}

@app.before_request
def exigir_login():
    if request.endpoint not in ROTAS_PUBLICAS and not session.get("db_user"):
        return redirect(url_for("tela_login"))


@app.route("/login", methods=["GET"])
def tela_login():
    erro = request.args.get("erro")
    return render_template("login.jinja2", erro=erro)


@app.route("/login", methods=["POST"])
def api_login():
    usuario = request.form.get("usuario") or ""
    senha = request.form.get("senha") or ""

    try:
        with DatabaseConnection(db=DB_NAME, user=usuario, password=senha):
            pass  # se não lançar erro, as credenciais são válidas
    except Error:
        return redirect(url_for("tela_login", erro="Usuário ou senha inválidos."))

    session["db_user"] = usuario
    session["db_password"] = senha
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("tela_login"))

##################
#     TELAS      #
##################

# Rota da tela inicial (Home Page)
@app.route('/', methods=['GET'])
def home():
    return render_template('index.jinja2')


# ==========================================
# TELAS - PROFESSOR
# ==========================================

@app.route("/consultar/professor", methods=['GET'])
def tela_consultar_professor():
    registros = executar_select(
        db=DB_NAME,
        consulta_sql="""
            SELECT 
                p.id_professor, 
                p.nome, 
                p.data_nascimento, 
                p.carga_horaria_trabalho,
                COALESCE(GROUP_CONCAT(DISTINCT d.nome SEPARATOR ', '), 'Nenhuma') AS disciplinas,
                COALESCE(GROUP_CONCAT(DISTINCT t.nome_turma SEPARATOR ', '), 'Nenhuma') AS turmas_leciona
            FROM professor p
            LEFT JOIN disciplina d ON p.id_professor = d.id_professor
            LEFT JOIN turma_disciplina td ON d.id_disciplina = td.id_disciplina
            LEFT JOIN turma t ON td.id_turma = t.id_turma
            GROUP BY p.id_professor, p.nome, p.data_nascimento, p.carga_horaria_trabalho
            ORDER BY p.id_professor
        """
    )
    cabecalho = [
        "ID", "Nome", "Data de Nascimento", "Carga Horária (h)", 
        "Disciplinas Ministradas", "Turmas que Leciona"
    ]
    return render_template(
        "consultar.jinja2",
        titulo="Consulta de Professores",
        api_atualizar="/atualizar/professor",
        api_apagar="/api/apagar/professor",
        cabecalho=cabecalho,
        dados=registros,
    )


@app.route("/cadastrar/professor", methods=['GET'])
def tela_cadastrar_professor():
    return render_template(
        "cadastrar/professor.jinja2",
        api="/api/cadastrar/professor",
    )


@app.route("/atualizar/professor", methods=['GET'])
def tela_atualizar_professor():
    id_prof = request.args.get('id') or request.args.get('id_professor') or ""
    registros = executar_select(
        db=DB_NAME,
        consulta_sql="""
            SELECT id_professor, nome, data_nascimento, carga_horaria_trabalho
            FROM professor
            WHERE id_professor = %s
        """,
        parametros=(id_prof,)
    )

    if not registros:
        return f"ERRO: Professor com ID '{id_prof}' não encontrado. <a href='/consultar/professor'>Voltar</a>"

    id_professor, nome, data_nascimento, carga_horaria_trabalho = registros[0]

    return render_template(
        "atualizar/professor.jinja2",
        api="/api/atualizar/professor",
        id_professor=id_professor,
        nome=nome,
        data_nascimento=str(data_nascimento),
        carga_horaria_trabalho=carga_horaria_trabalho,
    )


# ==========================================
# TELAS - ALUNO
# ==========================================

@app.route("/consultar/aluno", methods=['GET'])
def tela_consultar_aluno():
    registros = executar_select(
        db=DB_NAME,
        consulta_sql="""
            SELECT 
                a.id_aluno, 
                a.nome, 
                a.data_nascimento, 
                COALESCE(a.endereco, '-') AS endereco, 
                COALESCE(a.telefone, '-') AS telefone, 
                COALESCE(t.nome_turma, 'Sem Turma') AS turma,
                COALESCE(GROUP_CONCAT(DISTINCT CONCAT(tc.nome, ': ', ca.descricao) SEPARATOR '; '), 'Nenhuma') AS condicoes
            FROM aluno a
            LEFT JOIN turma t ON a.id_turma = t.id_turma
            LEFT JOIN condicao_aluno ca ON a.id_aluno = ca.id_aluno
            LEFT JOIN tipo_condicao tc ON ca.id_tipo_condicao = tc.id_tipo_condicao
            GROUP BY a.id_aluno, a.nome, a.data_nascimento, a.endereco, a.telefone, t.nome_turma
            ORDER BY a.id_aluno
        """
    )
    cabecalho = ["ID", "Nome", "Data de Nascimento", "Endereço", "Telefone", "Turma", "Condições / Alergias"]
    return render_template(
        "consultar.jinja2",
        titulo="Consulta de Alunos",
        api_atualizar="/atualizar/aluno",
        api_apagar="/api/apagar/aluno",
        cabecalho=cabecalho,
        dados=registros,
    )


@app.route("/cadastrar/aluno", methods=['GET'])
def tela_cadastrar_aluno():
    turmas = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_turma, nome_turma FROM turma ORDER BY nome_turma"
    )
    tipos_condicao = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_tipo_condicao, nome FROM tipo_condicao ORDER BY nome"
    )
    return render_template(
        "cadastrar/aluno.jinja2",
        api="/api/cadastrar/aluno",
        turmas=[("", "Sem Turma")] + list(turmas),
        tipos_condicao=tipos_condicao,
    )


@app.route("/atualizar/aluno", methods=['GET'])
def tela_atualizar_aluno():
    id_aluno_req = request.args.get('id') or request.args.get('id_aluno') or ""
    registros = executar_select(
        db=DB_NAME,
        consulta_sql="""
            SELECT id_aluno, nome, data_nascimento, endereco, telefone, id_turma
            FROM aluno
            WHERE id_aluno = %s
        """,
        parametros=(id_aluno_req,)
    )

    if not registros:
        return f"ERRO: Aluno com ID '{id_aluno_req}' não encontrado. <a href='/consultar/aluno'>Voltar</a>"

    id_aluno, nome, data_nascimento, endereco, telefone, id_turma = registros[0]

    # Busca TODAS as condições existentes do aluno (não só a primeira)
    condicoes = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_tipo_condicao, descricao FROM condicao_aluno WHERE id_aluno = %s",
        parametros=(id_aluno,)
    )

    tipos_condicao = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_tipo_condicao, nome FROM tipo_condicao ORDER BY nome"
    )

    turmas = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_turma, nome_turma FROM turma ORDER BY nome_turma"
    )

    return render_template(
        "atualizar/aluno.jinja2",
        api="/api/atualizar/aluno",
        id_aluno=id_aluno,
        nome=nome,
        data_nascimento=str(data_nascimento),
        endereco=endereco or "",
        telefone=telefone or "",
        id_turma=id_turma,
        condicoes=condicoes,
        tipos_condicao=tipos_condicao,
        turmas=[("", "Sem Turma")] + list(turmas),
    )


# ==========================================
# TELAS - TURMA
# ==========================================

@app.route("/consultar/turma", methods=['GET'])
def tela_consultar_turma():
    registros = executar_select(
        db=DB_NAME,
        consulta_sql="""
            SELECT 
                t.id_turma, 
                t.nome_turma, 
                t.ano_letivo, 
                COALESCE(t.sala_aula, '-'),
                COALESCE(GROUP_CONCAT(d.nome SEPARATOR ', '), 'Nenhuma') AS disciplinas_vinculadas
            FROM turma t
            LEFT JOIN turma_disciplina td ON t.id_turma = td.id_turma
            LEFT JOIN disciplina d ON td.id_disciplina = d.id_disciplina
            GROUP BY t.id_turma, t.nome_turma, t.ano_letivo, t.sala_aula
            ORDER BY t.id_turma
        """
    )
    cabecalho = ["ID", "Nome da Turma", "Ano Letivo", "Sala de Aula", "Disciplinas Vinculadas"]
    return render_template(
        "consultar.jinja2",
        titulo="Consulta de Turmas",
        api_atualizar="/atualizar/turma",
        api_apagar="/api/apagar/turma",
        cabecalho=cabecalho,
        dados=registros,
    )


@app.route("/cadastrar/turma", methods=['GET'])
def tela_cadastrar_turma():
    todas_disciplinas = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_disciplina, nome FROM disciplina ORDER BY nome"
    )
    return render_template(
        "cadastrar/turma.jinja2",
        api="/api/cadastrar/turma",
        todas_disciplinas=todas_disciplinas,
    )


@app.route("/atualizar/turma", methods=['GET'])
def tela_atualizar_turma():
    id_turma_req = request.args.get('id') or request.args.get('id_turma') or ""
    registros = executar_select(
        db=DB_NAME,
        consulta_sql="""
            SELECT id_turma, nome_turma, ano_letivo, sala_aula
            FROM turma
            WHERE id_turma = %s
        """,
        parametros=(id_turma_req,)
    )

    if not registros:
        return f"ERRO: Turma com ID '{id_turma_req}' não encontrada. <a href='/consultar/turma'>Voltar</a>"

    id_turma, nome_turma, ano_letivo, sala_aula = registros[0]

    todas_disciplinas = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_disciplina, nome FROM disciplina ORDER BY nome"
    )

    disc_vinculadas = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_disciplina FROM turma_disciplina WHERE id_turma = %s",
        parametros=(id_turma,)
    )
    disciplinas_selecionadas = [str(d[0]) for d in disc_vinculadas]

    return render_template(
        "atualizar/turma.jinja2",
        api="/api/atualizar/turma",
        id_turma=id_turma,
        nome_turma=nome_turma,
        ano_letivo=ano_letivo,
        sala_aula=sala_aula or "",
        todas_disciplinas=todas_disciplinas,
        disciplinas_selecionadas=disciplinas_selecionadas,
    )


# ==========================================
# TELAS - DISCIPLINA
# ==========================================

@app.route("/consultar/disciplina", methods=['GET'])
def tela_consultar_disciplina():
    registros = executar_select(
        db=DB_NAME,
        consulta_sql="""
            SELECT d.id_disciplina, d.nome, d.carga_horaria, p.nome
            FROM disciplina d
            JOIN professor p ON d.id_professor = p.id_professor
            ORDER BY d.id_disciplina
        """
    )
    cabecalho = ["ID", "Disciplina", "Carga Horária (h)", "Professor Responsável"]
    return render_template(
        "consultar.jinja2",
        titulo="Consulta de Disciplinas",
        api_atualizar="/atualizar/disciplina",
        api_apagar="/api/apagar/disciplina",
        cabecalho=cabecalho,
        dados=registros,
    )


@app.route("/cadastrar/disciplina", methods=['GET'])
def tela_cadastrar_disciplina():
    professores = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_professor, nome FROM professor ORDER BY nome"
    )
    return render_template(
        "cadastrar/disciplina.jinja2",
        api="/api/cadastrar/disciplina",
        professores=professores,
    )


@app.route("/atualizar/disciplina", methods=['GET'])
def tela_atualizar_disciplina():
    id_disc_req = request.args.get('id') or request.args.get('id_disciplina') or ""
    registros = executar_select(
        db=DB_NAME,
        consulta_sql="""
            SELECT id_disciplina, nome, carga_horaria, id_professor
            FROM disciplina
            WHERE id_disciplina = %s
        """,
        parametros=(id_disc_req,)
    )

    if not registros:
        return f"ERRO: Disciplina com ID '{id_disc_req}' não encontrada. <a href='/consultar/disciplina'>Voltar</a>"

    id_disciplina, nome, carga_horaria, id_professor = registros[0]
    professores = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_professor, nome FROM professor ORDER BY nome"
    )

    return render_template(
        "atualizar/disciplina.jinja2",
        api="/api/atualizar/disciplina",
        id_disciplina=id_disciplina,
        nome=nome,
        carga_horaria=carga_horaria,
        id_professor=id_professor,
        professores=professores,
    )


# ==========================================
# TELAS - NOTAS (LANÇAMENTO E CONSULTA)
# ==========================================

@app.route("/consultar/nota", methods=['GET'])
def tela_consultar_nota():
    registros = executar_select(
        db=DB_NAME,
        consulta_sql="""
            SELECT n.id_nota, a.nome, t.nome_turma, d.nome, n.unidade, n.nota
            FROM nota n
            JOIN aluno a ON n.id_aluno = a.id_aluno
            JOIN turma t ON n.id_turma = t.id_turma
            JOIN disciplina d ON n.id_disciplina = d.id_disciplina
            ORDER BY t.nome_turma, a.nome, d.nome, n.unidade
        """
    )
    cabecalho = ["ID", "Aluno", "Turma", "Disciplina", "Unidade", "Nota Lançada"]
    return render_template(
        "consultar.jinja2",
        titulo="Consulta de Notas Lançadas",
        api_atualizar="/atualizar/nota",
        api_apagar="/api/apagar/nota",
        cabecalho=cabecalho,
        dados=registros,
    )


@app.route("/cadastrar/nota", methods=['GET'])
def tela_cadastrar_nota():
    alunos = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_aluno, nome FROM aluno ORDER BY nome"
    )
    turmas = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_turma, nome_turma FROM turma ORDER BY nome_turma"
    )
    disciplinas = executar_select(
        db=DB_NAME,
        consulta_sql="SELECT id_disciplina, nome FROM disciplina ORDER BY nome"
    )
    return render_template(
        "cadastrar/nota.jinja2",
        api="/api/cadastrar/nota",
        alunos=alunos,
        turmas=turmas,
        disciplinas=disciplinas,
    )


@app.route("/atualizar/nota", methods=['GET'])
def tela_atualizar_nota():
    id_nota_req = request.args.get('id') or request.args.get('id_nota') or ""
    registros = executar_select(
        db=DB_NAME,
        consulta_sql="""
            SELECT id_nota, id_aluno, id_turma, id_disciplina, unidade, nota
            FROM nota
            WHERE id_nota = %s
        """,
        parametros=(id_nota_req,)
    )

    if not registros:
        return f"ERRO: Nota com ID '{id_nota_req}' não encontrada. <a href='/consultar/nota'>Voltar</a>"

    id_nota, id_aluno, id_turma, id_disciplina, unidade, nota = registros[0]

    alunos = executar_select(db=DB_NAME, consulta_sql="SELECT id_aluno, nome FROM aluno ORDER BY nome")
    turmas = executar_select(db=DB_NAME, consulta_sql="SELECT id_turma, nome_turma FROM turma ORDER BY nome_turma")
    disciplinas = executar_select(db=DB_NAME, consulta_sql="SELECT id_disciplina, nome FROM disciplina ORDER BY nome")

    return render_template(
        "atualizar/nota.jinja2",
        api="/api/atualizar/nota",
        id_nota=id_nota,
        id_aluno=id_aluno,
        id_turma=id_turma,
        id_disciplina=id_disciplina,
        unidade=str(unidade),
        nota=nota,
        alunos=alunos,
        turmas=turmas,
        disciplinas=disciplinas,
    )


# ==========================================
# TELAS - DESEMPENHO GERAL (VIEW)
# ==========================================

@app.route("/consultar/desempenho", methods=['GET'])
def tela_consultar_desempenho():
    registros = executar_select(
        db=DB_NAME,
        consulta_sql="""
            SELECT id_aluno, aluno, turma, disciplina, total_avaliacoes, media, situacao
            FROM vw_desempenho_alunos
            ORDER BY turma, aluno
        """
    )
    cabecalho = ["ID Aluno", "Aluno", "Turma", "Disciplina", "Qtd Avaliações", "Média Final", "Situação"]
    return render_template(
        "consultar.jinja2",
        titulo="Relatório de Desempenho e Aprovação",
        api_atualizar=None,
        api_apagar=None,
        cabecalho=cabecalho,
        dados=registros,
    )


################
#     API      #
################

# ==========================================
# API - PROFESSOR
# ==========================================

@app.route('/api/cadastrar/professor', methods=['POST'])
def api_cadastrar_professor():
    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="""
            INSERT INTO professor (nome, data_nascimento, carga_horaria_trabalho)
            VALUES (%s, %s, %s)
        """,
        parametros=(
            request.form.get('nome') or "",
            request.form.get('data_nascimento') or "",
            request.form.get('carga_horaria_trabalho') or "0",
        )
    )
    if qtd < 0:
        return "ERRO ao cadastrar professor. Verifique os logs do console."
    return f"SUCESSO: Professor cadastrado com sucesso! <a href='/consultar/professor'>Ver Lista</a>"


@app.route('/api/atualizar/professor', methods=['POST'])
def api_atualizar_professor():
    id_prof = request.form.get('id_professor') or request.form.get('id') or ""
    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="""
            UPDATE professor
            SET nome = %s, data_nascimento = %s, carga_horaria_trabalho = %s
            WHERE id_professor = %s
        """,
        parametros=(
            request.form.get('nome') or "",
            request.form.get('data_nascimento') or "",
            request.form.get('carga_horaria_trabalho') or "0",
            id_prof,
        )
    )
    if qtd < 0:
        return "ERRO ao atualizar professor. Verifique os logs do console."
    return f"SUCESSO: Professor atualizado com sucesso! <a href='/consultar/professor'>Ver Lista</a>"


@app.route('/api/apagar/professor', methods=['POST'])
def api_apagar_professor():
    id_prof = request.form.get('id') or request.form.get('id_professor') or ""
    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="DELETE FROM professor WHERE id_professor = %s",
        parametros=(id_prof,)
    )
    if qtd < 0:
        return "ERRO ao apagar professor. Verifique se o professor possui disciplinas vinculadas."
    return f"SUCESSO: Professor apagado com sucesso! <a href='/consultar/professor'>Ver Lista</a>"


# ==========================================
# API - ALUNO
# ==========================================

@app.route('/api/cadastrar/aluno', methods=['POST'])
def api_cadastrar_aluno():
    id_turma_val = request.form.get('id_turma') or None
    if id_turma_val == "":
        id_turma_val = None

    id_gerado = executar_insert_retornando_id(
        db=DB_NAME,
        consulta_sql="""
            INSERT INTO aluno (nome, data_nascimento, endereco, telefone, id_turma)
            VALUES (%s, %s, %s, %s, %s)
        """,
        parametros=(
            request.form.get('nome') or "",
            request.form.get('data_nascimento') or "",
            request.form.get('endereco') or "",
            request.form.get('telefone') or "",
            id_turma_val,
        )
    )
    if id_gerado < 0:
        return "ERRO ao cadastrar aluno. Verifique os logs do console."

    # Cadastro de 0, 1 ou várias condições (mesmo padrão de getlist já usado nas
    # disciplinas da turma, mas aqui para tipo_condicao + descricao_condicao)
    tipos_condicao = request.form.getlist('tipo_condicao')
    descricoes_condicao = request.form.getlist('descricao_condicao')
    for tipo, descricao in zip(tipos_condicao, descricoes_condicao):
        if tipo and descricao.strip():
            qtd_cond = executar_insert_delete_update(
                db=DB_NAME,
                consulta_sql="""
                    INSERT INTO condicao_aluno (id_aluno, id_tipo_condicao, descricao)
                    VALUES (%s, %s, %s)
                """,
                parametros=(id_gerado, tipo, descricao.strip())
            )
            if qtd_cond < 0:
                return (
                    "SUCESSO PARCIAL: Aluno cadastrado, mas uma das condições não pôde ser "
                    "salva (pode ser uma condição duplicada para este aluno). "
                    f"<a href='/atualizar/aluno?id={id_gerado}'>Revisar Aluno</a>"
                )

    return f"SUCESSO: Aluno cadastrado com sucesso! <a href='/consultar/aluno'>Ver Lista</a>"


@app.route('/api/atualizar/aluno', methods=['POST'])
def api_atualizar_aluno():
    id_aluno = request.form.get('id_aluno') or request.form.get('id') or ""
    id_turma_val = request.form.get('id_turma') or None
    if id_turma_val == "":
        id_turma_val = None

    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="""
            UPDATE aluno
            SET nome = %s, data_nascimento = %s, endereco = %s, telefone = %s, id_turma = %s
            WHERE id_aluno = %s
        """,
        parametros=(
            request.form.get('nome') or "",
            request.form.get('data_nascimento') or "",
            request.form.get('endereco') or "",
            request.form.get('telefone') or "",
            id_turma_val,
            id_aluno,
        )
    )
    if qtd < 0:
        return "ERRO ao atualizar aluno. Verifique os logs do console."

    # Substitui todas as condições do aluno pelas que vieram do formulário
    executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="DELETE FROM condicao_aluno WHERE id_aluno = %s",
        parametros=(id_aluno,)
    )

    tipos_condicao = request.form.getlist('tipo_condicao')
    descricoes_condicao = request.form.getlist('descricao_condicao')
    for tipo, descricao in zip(tipos_condicao, descricoes_condicao):
        if tipo and descricao.strip():
            qtd_cond = executar_insert_delete_update(
                db=DB_NAME,
                consulta_sql="""
                    INSERT INTO condicao_aluno (id_aluno, id_tipo_condicao, descricao)
                    VALUES (%s, %s, %s)
                """,
                parametros=(id_aluno, tipo, descricao.strip())
            )
            if qtd_cond < 0:
                return (
                    "SUCESSO PARCIAL: Aluno atualizado, mas uma das condições não pôde ser "
                    "salva (pode ser uma condição duplicada para este aluno). "
                    f"<a href='/atualizar/aluno?id={id_aluno}'>Revisar Aluno</a>"
                )

    return f"SUCESSO: Aluno atualizado com sucesso! <a href='/consultar/aluno'>Ver Lista</a>"


@app.route('/api/apagar/aluno', methods=['POST'])
def api_apagar_aluno():
    id_aluno = request.form.get('id') or request.form.get('id_aluno') or ""
    # Remove dependencias de condicoes medicas e notas caso existam
    executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="DELETE FROM condicao_aluno WHERE id_aluno = %s",
        parametros=(id_aluno,)
    )
    executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="DELETE FROM nota WHERE id_aluno = %s",
        parametros=(id_aluno,)
    )
    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="DELETE FROM aluno WHERE id_aluno = %s",
        parametros=(id_aluno,)
    )
    if qtd < 0:
        return "ERRO ao apagar aluno. Verifique os logs do console."
    return f"SUCESSO: Aluno apagado com sucesso! <a href='/consultar/aluno'>Ver Lista</a>"


# ==========================================
# API - TURMA
# ==========================================

@app.route('/api/cadastrar/turma', methods=['POST'])
def api_cadastrar_turma():
    id_gerado = executar_insert_retornando_id(
        db=DB_NAME,
        consulta_sql="""
            INSERT INTO turma (nome_turma, ano_letivo, sala_aula)
            VALUES (%s, %s, %s)
        """,
        parametros=(
            request.form.get('nome_turma') or "",
            request.form.get('ano_letivo') or "2026",
            request.form.get('sala_aula') or "",
        )
    )
    if id_gerado < 0:
        return "ERRO ao cadastrar turma. Verifique os logs do console."

    # Vinculo de disciplinas selecionadas
    disciplinas_selecionadas = request.form.getlist('disciplinas')
    for id_disc in disciplinas_selecionadas:
        executar_insert_delete_update(
            db=DB_NAME,
            consulta_sql="INSERT IGNORE INTO turma_disciplina (id_turma, id_disciplina) VALUES (%s, %s)",
            parametros=(id_gerado, id_disc)
        )

    return f"SUCESSO: Turma cadastrada com sucesso! <a href='/consultar/turma'>Ver Lista</a>"


@app.route('/api/atualizar/turma', methods=['POST'])
def api_atualizar_turma():
    id_turma = request.form.get('id_turma') or request.form.get('id') or ""
    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="""
            UPDATE turma
            SET nome_turma = %s, ano_letivo = %s, sala_aula = %s
            WHERE id_turma = %s
        """,
        parametros=(
            request.form.get('nome_turma') or "",
            request.form.get('ano_letivo') or "2026",
            request.form.get('sala_aula') or "",
            id_turma,
        )
    )
    if qtd < 0:
        return "ERRO ao atualizar turma. Verifique os logs do console."

    # Atualiza vinculo de disciplinas da turma
    executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="DELETE FROM turma_disciplina WHERE id_turma = %s",
        parametros=(id_turma,)
    )
    disciplinas_selecionadas = request.form.getlist('disciplinas')
    for id_disc in disciplinas_selecionadas:
        executar_insert_delete_update(
            db=DB_NAME,
            consulta_sql="INSERT IGNORE INTO turma_disciplina (id_turma, id_disciplina) VALUES (%s, %s)",
            parametros=(id_turma, id_disc)
        )

    return f"SUCESSO: Turma atualizada com sucesso! <a href='/consultar/turma'>Ver Lista</a>"


@app.route('/api/apagar/turma', methods=['POST'])
def api_apagar_turma():
    id_turma = request.form.get('id') or request.form.get('id_turma') or ""
    executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="DELETE FROM turma_disciplina WHERE id_turma = %s",
        parametros=(id_turma,)
    )
    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="DELETE FROM turma WHERE id_turma = %s",
        parametros=(id_turma,)
    )
    if qtd < 0:
        return "ERRO ao apagar turma. Verifique se existem alunos vinculados."
    return f"SUCESSO: Turma apagada com sucesso! <a href='/consultar/turma'>Ver Lista</a>"


# ==========================================
# API - DISCIPLINA
# ==========================================

@app.route('/api/cadastrar/disciplina', methods=['POST'])
def api_cadastrar_disciplina():
    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="""
            INSERT INTO disciplina (nome, carga_horaria, id_professor)
            VALUES (%s, %s, %s)
        """,
        parametros=(
            request.form.get('nome') or "",
            request.form.get('carga_horaria') or "0",
            request.form.get('id_professor') or "",
        )
    )
    if qtd < 0:
        return "ERRO ao cadastrar disciplina. Verifique os logs do console."
    return f"SUCESSO: Disciplina cadastrada com sucesso! <a href='/consultar/disciplina'>Ver Lista</a>"


@app.route('/api/atualizar/disciplina', methods=['POST'])
def api_atualizar_disciplina():
    id_disciplina = request.form.get('id_disciplina') or request.form.get('id') or ""
    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="""
            UPDATE disciplina
            SET nome = %s, carga_horaria = %s, id_professor = %s
            WHERE id_disciplina = %s
        """,
        parametros=(
            request.form.get('nome') or "",
            request.form.get('carga_horaria') or "0",
            request.form.get('id_professor') or "",
            id_disciplina,
        )
    )
    if qtd < 0:
        return "ERRO ao atualizar disciplina. Verifique os logs do console."
    return f"SUCESSO: Disciplina atualizada com sucesso! <a href='/consultar/disciplina'>Ver Lista</a>"


@app.route('/api/apagar/disciplina', methods=['POST'])
def api_apagar_disciplina():
    id_disciplina = request.form.get('id') or request.form.get('id_disciplina') or ""
    executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="DELETE FROM turma_disciplina WHERE id_disciplina = %s",
        parametros=(id_disciplina,)
    )
    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="DELETE FROM disciplina WHERE id_disciplina = %s",
        parametros=(id_disciplina,)
    )
    if qtd < 0:
        return "ERRO ao apagar disciplina. Verifique se existem notas vinculadas."
    return f"SUCESSO: Disciplina apagada com sucesso! <a href='/consultar/disciplina'>Ver Lista</a>"


# ==========================================
# API - NOTAS
# ==========================================

@app.route('/api/cadastrar/nota', methods=['POST'])
def api_cadastrar_nota():
    id_aluno = request.form.get('id_aluno') or ""
    id_turma = request.form.get('id_turma') or ""
    id_disciplina = request.form.get('id_disciplina') or ""
    unidade = request.form.get('unidade') or "1"
    nota = request.form.get('nota') or "0"

    # Garante que a associacao turma_disciplina existe antes de gravar a nota
    executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="INSERT IGNORE INTO turma_disciplina (id_turma, id_disciplina) VALUES (%s, %s)",
        parametros=(id_turma, id_disciplina)
    )

    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="""
            INSERT INTO nota (id_aluno, id_turma, id_disciplina, unidade, nota)
            VALUES (%s, %s, %s, %s, %s)
        """,
        parametros=(id_aluno, id_turma, id_disciplina, unidade, nota)
    )

    if qtd < 0:
        return "ERRO ao lançar nota. Verifique se o valor está entre 0.00 e 10.00."
    return f"SUCESSO: Nota lançada com sucesso! As médias foram recalculadas automaticamente pelos triggers. <a href='/consultar/nota'>Ver Notas</a> | <a href='/consultar/desempenho'>Ver Desempenho</a>"


@app.route('/api/atualizar/nota', methods=['POST'])
def api_atualizar_nota():
    id_nota = request.form.get('id_nota') or request.form.get('id') or ""
    id_aluno = request.form.get('id_aluno') or ""
    id_turma = request.form.get('id_turma') or ""
    id_disciplina = request.form.get('id_disciplina') or ""
    unidade = request.form.get('unidade') or "1"
    nota = request.form.get('nota') or "0"

    executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="INSERT IGNORE INTO turma_disciplina (id_turma, id_disciplina) VALUES (%s, %s)",
        parametros=(id_turma, id_disciplina)
    )

    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="""
            UPDATE nota
            SET id_aluno = %s, id_turma = %s, id_disciplina = %s, unidade = %s, nota = %s
            WHERE id_nota = %s
        """,
        parametros=(id_aluno, id_turma, id_disciplina, unidade, nota, id_nota)
    )

    if qtd < 0:
        return "ERRO ao atualizar nota. Verifique se o valor está entre 0.00 e 10.00."
    return f"SUCESSO: Nota atualizada com sucesso! <a href='/consultar/nota'>Ver Notas</a>"


@app.route('/api/apagar/nota', methods=['POST'])
def api_apagar_nota():
    id_nota = request.form.get('id') or request.form.get('id_nota') or ""
    qtd = executar_insert_delete_update(
        db=DB_NAME,
        consulta_sql="DELETE FROM nota WHERE id_nota = %s",
        parametros=(id_nota,)
    )
    if qtd < 0:
        return "ERRO ao apagar nota."
    return f"SUCESSO: Nota apagada com sucesso! <a href='/consultar/nota'>Ver Notas</a>"


# Inicia o servidor Flask (NAO ALTERE OU REMOVA O CODIGO ABAIXO)
if __name__ == '__main__':
    while True:
        try:
            print("Iniciando servidor Flask de Gestão Escolar...")
            print("Pressione Ctrl+C para encerrar o servidor.")
            app.run(debug=True)
            raise KeyboardInterrupt()  # Encerra servidor
        except KeyboardInterrupt:
            print("Servidor Flask encerrado pelo usuário.")
            break  # Sai do loop se o servidor for encerrado normalmente
        except Exception as e:
            print(f"Erro no servidor Flask: {e}")
            time.sleep(0.500)