# Sistema de Gestão Escolar (Flask + MySQL)

Aplicação Web desenvolvida com Flask e MySQL para gestão escolar (administração de Professores, Alunos, Turmas, Disciplinas e Desempenho).

---

## 1. Instalar dependências

No terminal execute o seguinte comando:

```batch
python -m pip install -r requirements.txt
```

## 2. Banco de Dados

1. Acesse o PhpMyAdmin ( `http://localhost/phpmyadmin` ) ou o MySQL Workbench / CLI.
2. Importe e execute o script **[db/gestao_escolar.sql](file:///c:/Users/Robertty%20e%20Rian/OneDrive/Documentos/IFBA/RIAN/BDD/db_streaming_python/db/gestao_escolar.sql)**.

## 3. Executar App Flask

No terminal execute o seguinte comando:

```batch
python app.py
```

## 4. Acessar o App

Acesse no navegador: **`http://localhost:5000`**

---

## Estrutura do Projeto

- **app.py**: Aplicativo Python/Flask com rotas de telas (GET) e rotas de API (POST)
- **db/**:
  - **gestao_escolar.sql**: Script DDL/DML, Triggers, Views e Procedures do banco `gestao_escolar`
  - **db.py**: Gerenciador de conexão com MySQL (`DatabaseConnection`, `executar_select`, `executar_insert_delete_update`)
- **static/**: Folhas de estilo (Bootstrap 5, CSS customizado) e ícones
- **templates/**: Templates Jinja2
  - **_base.jinja2**: Layout base com Navbar de navegação
  - **_macros.jinja2**: Macros reutilizáveis para inputs, selects, tabelas e dropdowns
  - **index.jinja2**: Página inicial do sistema
  - **consultar.jinja2**: Template dinâmico para tabelas de consulta e ações de alteração/exclusão
  - **cadastrar/**: Formulários de cadastro (`professor.jinja2`, `aluno.jinja2`, `turma.jinja2`, `disciplina.jinja2`)
  - **atualizar/**: Formulários de edição (`professor.jinja2`, `aluno.jinja2`, `turma.jinja2`, `disciplina.jinja2`)