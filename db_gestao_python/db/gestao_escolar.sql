-- ============================================================
-- CRIAÇÃO DO BANCO DE DADOS
-- ============================================================
CREATE DATABASE IF NOT EXISTS gestao_escolar
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;

USE gestao_escolar;

-- ============================================================
-- CRIAÇÃO DAS TABELAS
-- ============================================================

-- Tabela professor 
CREATE TABLE IF NOT EXISTS professor (
    id_professor           INT          NOT NULL AUTO_INCREMENT,
    nome                   VARCHAR(100) NOT NULL,
    data_nascimento        DATE         NOT NULL,
    carga_horaria_trabalho DECIMAL(5,1) NOT NULL,
    CONSTRAINT pk_professor   PRIMARY KEY (id_professor),
    CONSTRAINT chk_carga_prof CHECK (carga_horaria_trabalho > 0)
);  

-- Tabela turma 
CREATE TABLE IF NOT EXISTS turma (
    id_turma   INT         NOT NULL AUTO_INCREMENT,
    nome_turma VARCHAR(50) NOT NULL,
    ano_letivo INT         NOT NULL,
    sala_aula  VARCHAR(25) DEFAULT NULL,
    CONSTRAINT pk_turma PRIMARY KEY (id_turma)
);  

-- Tabela disciplina 
CREATE TABLE IF NOT EXISTS disciplina (
    id_disciplina INT          NOT NULL AUTO_INCREMENT,
    nome          VARCHAR(100) NOT NULL,
    carga_horaria DECIMAL(5,2) NOT NULL,
    id_professor  INT          NOT NULL,
    CONSTRAINT pk_disciplina  PRIMARY KEY (id_disciplina),
    CONSTRAINT chk_carga_disc CHECK (carga_horaria > 0),
    CONSTRAINT fk_disc_prof   FOREIGN KEY (id_professor)
                              REFERENCES professor(id_professor)
                              ON DELETE RESTRICT
);  

-- Tabela aluno 
CREATE TABLE IF NOT EXISTS aluno (
    id_aluno        INT          NOT NULL AUTO_INCREMENT,
    nome            VARCHAR(100) NOT NULL,
    data_nascimento DATE         NOT NULL,
    endereco        VARCHAR(200) DEFAULT NULL,
    telefone        VARCHAR(20)  DEFAULT NULL,
    id_turma        INT          DEFAULT NULL,
    CONSTRAINT pk_aluno       PRIMARY KEY (id_aluno),
    CONSTRAINT fk_aluno_turma FOREIGN KEY (id_turma)
                              REFERENCES turma(id_turma)
                              ON DELETE SET NULL
);  

-- Tabela de junção turma_disciplina
CREATE TABLE IF NOT EXISTS turma_disciplina (
    id_turma      INT NOT NULL,
    id_disciplina INT NOT NULL,
    CONSTRAINT pk_td     PRIMARY KEY (id_turma, id_disciplina),
    CONSTRAINT fk_td_t   FOREIGN KEY (id_turma)
                         REFERENCES turma(id_turma)
                         ON DELETE RESTRICT,
    CONSTRAINT fk_td_d   FOREIGN KEY (id_disciplina)
                         REFERENCES disciplina(id_disciplina)
                         ON DELETE RESTRICT
);  


-- Tabela tipo_condicao
CREATE TABLE tipo_condicao (
    id_tipo_condicao INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    CONSTRAINT pk_tipo_condicao PRIMARY KEY (id_tipo_condicao),
    CONSTRAINT uq_tipo_condicao_nome UNIQUE (nome)
);


-- Tabela condicao_aluno
CREATE TABLE IF NOT EXISTS condicao_aluno (
    id_condicao INT NOT NULL AUTO_INCREMENT,
    id_aluno INT NOT NULL,
    id_tipo_condicao INT NOT NULL,
    descricao   VARCHAR(250) NOT NULL,
    CONSTRAINT pk_condicao   PRIMARY KEY (id_condicao),
    CONSTRAINT fk_cond_aluno FOREIGN KEY (id_aluno) REFERENCES aluno(id_aluno) ON DELETE RESTRICT,
    CONSTRAINT fk_cond_tipo FOREIGN KEY (id_tipo_condicao) REFERENCES tipo_condicao(id_tipo_condicao) ON DELETE RESTRICT,
    CONSTRAINT uq_condicao UNIQUE (id_aluno, id_tipo_condicao, descricao)
);  

-- Tabela media_aluno
CREATE TABLE IF NOT EXISTS media_aluno (
    id_aluno      INT         NOT NULL,
    id_disciplina INT         NOT NULL,
    id_turma      INT         NOT NULL,
    media         DECIMAL(4,2) DEFAULT NULL,
    situacao      VARCHAR(10)  DEFAULT NULL,
    CONSTRAINT pk_media    PRIMARY KEY (id_aluno, id_disciplina, id_turma),
    CONSTRAINT fk_ma_aluno FOREIGN KEY (id_aluno)
                           REFERENCES aluno(id_aluno)
                           ON DELETE RESTRICT,
    CONSTRAINT fk_ma_td    FOREIGN KEY (id_turma, id_disciplina)
                           REFERENCES turma_disciplina(id_turma, id_disciplina)
                           ON DELETE RESTRICT
);  

-- Tabela de notas 
CREATE TABLE IF NOT EXISTS nota (
    id_nota       INT          NOT NULL AUTO_INCREMENT,
    id_aluno      INT          NOT NULL,
    id_turma      INT          NOT NULL,
    id_disciplina INT          NOT NULL,
    unidade       INT          NOT NULL,
    nota          DECIMAL(4,2) NOT NULL,
    CONSTRAINT pk_nota     PRIMARY KEY (id_nota),
    CONSTRAINT chk_nota    CHECK (nota >= 0 AND nota <= 10),
    CONSTRAINT chk_unidade CHECK (unidade >= 1),
    CONSTRAINT fk_nota_aluno FOREIGN KEY (id_aluno)
                             REFERENCES aluno(id_aluno)
                             ON DELETE RESTRICT,
    CONSTRAINT fk_nota_td    FOREIGN KEY (id_turma, id_disciplina)
                             REFERENCES turma_disciplina(id_turma, id_disciplina)
                             ON DELETE RESTRICT
);  

-- CRIAÇÃO DE TABELA PARA USUÁRIOS

CREATE TABLE usuario_sistema (
    id_usuario INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    login VARCHAR(50) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    papel ENUM('secretaria', 'coordenacao') NOT NULL,
    PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usuario_login UNIQUE (login)
);



-- ============================================================
-- INSERÇÃO DE DADOS INICIAIS (DML)
-- ============================================================

INSERT INTO professor (nome, data_nascimento, carga_horaria_trabalho) VALUES
('Vinícius Andrade', '1980-04-10', 36.0),
('Fernanda Cardoso', '1975-09-23', 32.0),
('Lola Mendes',     '1990-01-15', 20.0);

INSERT INTO turma (nome_turma, ano_letivo, sala_aula) VALUES
('9º Ano A', 2026, 'Sala 12'),
('9º Ano B', 2026, 'Sala 14'),
('1º EM A',  2026, 'Sala 01');

INSERT INTO disciplina (nome, carga_horaria, id_professor) VALUES
('Matemática', 100.00, 1),
('Português',   80.00, 2),
('História',    60.00, 3),
('Ciências',    60.00, 3);

INSERT INTO aluno (nome, data_nascimento, endereco, telefone, id_turma) VALUES
('Ana Beatriz Silva', '2010-03-15', 'Rua das Flores, 10', '(71)99111-1111', 1),
('Bruno Souza Lima',  '2010-07-22', 'Av. Central, 45',    '(71)99222-2222', 1),
('Carla Mendes Reis', '2011-01-08', 'Rua do Prado, 88',   '(71)99333-3333', 2),
('Diego Ferreira',    '2010-11-30', 'Rua Nova, 23',       '(71)99444-4444', 2),
('Elisa Cardoso',     '2011-05-19', 'Av. Brasil, 100',    '(71)99555-5555', 1);

--  inserindo dados nas tabelas de condição e em junção de condição
INSERT INTO tipo_condicao (nome) VALUES
('Deficiência'),
('Alergia'),
('Condição médica');

INSERT INTO condicao_aluno (id_aluno, id_tipo_condicao, descricao)
SELECT 1, id_tipo_condicao, 'Dislexia leve'        FROM tipo_condicao WHERE nome = 'Deficiência'
UNION ALL
SELECT 1, id_tipo_condicao, 'Alergia a amendoim'    FROM tipo_condicao WHERE nome = 'Alergia'
UNION ALL
SELECT 3, id_tipo_condicao, 'Diabetes tipo 1'       FROM tipo_condicao WHERE nome = 'Condição médica';



-- Vínculos turma × disciplina
INSERT INTO turma_disciplina (id_turma, id_disciplina) VALUES
(1, 1),  -- 9º Ano A: Matemática
(1, 2),  -- 9º Ano A: Português
(2, 1),  -- 9º Ano B: Matemática
(2, 3),  -- 9º Ano B: História
(3, 2),  -- 1º EM A:  Português
(3, 3);  -- 1º EM A:  História

-- Notas
INSERT INTO nota (id_aluno, id_turma, id_disciplina, unidade, nota) VALUES
(1, 1, 1, 1, 8.50),
(1, 1, 1, 2, 7.00),
(1, 1, 2, 1, 6.50),
(1, 1, 2, 2, 5.00),
(2, 1, 1, 1, 9.00),
(2, 1, 1, 2, 8.00),
(3, 2, 1, 1, 4.50),
(3, 2, 1, 2, 5.50),
(4, 2, 3, 1, 7.00),
(4, 2, 3, 2, 8.50);

-- ============================================================
-- CRIAÇÃO DE VIEWS
-- ============================================================

CREATE OR REPLACE VIEW vw_desempenho_alunos AS
SELECT
    a.id_aluno,
    a.nome                AS aluno,
    t.nome_turma          AS turma,
    d.nome                AS disciplina,
    COUNT(n.id_nota)      AS total_avaliacoes,
    ROUND(AVG(n.nota), 2) AS media,
    CASE
        WHEN AVG(n.nota) >= 6.0 THEN 'APROVADO'
        ELSE 'REPROVADO'
    END                   AS situacao
FROM aluno a
JOIN nota         n ON a.id_aluno      = n.id_aluno
JOIN turma        t ON n.id_turma      = t.id_turma
JOIN disciplina   d ON n.id_disciplina = d.id_disciplina
GROUP BY a.id_aluno, a.nome, t.nome_turma, d.nome;

-- ============================================================
-- PROCEDURES AUXILIARES & TRIGGERS
-- ============================================================

DELIMITER //

-- Procedure para centralizar a lógica de cálculo e atualização da média (DRY)
CREATE PROCEDURE sp_recalcular_media(
    IN p_id_aluno      INT,
    IN p_id_disciplina INT,
    IN p_id_turma      INT
)
BEGIN
    DECLARE v_count    INT;
    DECLARE v_media    DECIMAL(4,2);
    DECLARE v_situacao VARCHAR(10);

    SELECT COUNT(*), ROUND(AVG(nota), 2)
    INTO   v_count, v_media
    FROM   nota
    WHERE  id_aluno      = p_id_aluno
      AND  id_disciplina = p_id_disciplina
      AND  id_turma      = p_id_turma;

    IF v_count = 0 THEN
        DELETE FROM media_aluno
        WHERE id_aluno      = p_id_aluno
          AND id_disciplina = p_id_disciplina
          AND id_turma      = p_id_turma;
    ELSE
        IF v_media >= 6.0 THEN
            SET v_situacao = 'APROVADO';
        ELSE
            SET v_situacao = 'REPROVADO';
        END IF;

        INSERT INTO media_aluno (id_aluno, id_disciplina, id_turma, media, situacao)
        VALUES (p_id_aluno, p_id_disciplina, p_id_turma, v_media, v_situacao)
        ON DUPLICATE KEY UPDATE
            media    = v_media,
            situacao = v_situacao;
    END IF;
END//

-- Triggers enxutos delegando o cálculo para a procedure centralizada
CREATE TRIGGER trg_media_after_insert
AFTER INSERT ON nota
FOR EACH ROW
BEGIN
    CALL sp_recalcular_media(NEW.id_aluno, NEW.id_disciplina, NEW.id_turma);
END//

CREATE TRIGGER trg_media_after_update
AFTER UPDATE ON nota
FOR EACH ROW
BEGIN
    CALL sp_recalcular_media(NEW.id_aluno, NEW.id_disciplina, NEW.id_turma);
END//

CREATE TRIGGER trg_media_after_delete
AFTER DELETE ON nota
FOR EACH ROW
BEGIN
    CALL sp_recalcular_media(OLD.id_aluno, OLD.id_disciplina, OLD.id_turma);
END//

DELIMITER ;

-- ============================================================
-- PROCEDURES
-- ============================================================

DELIMITER //

CREATE PROCEDURE sp_boletim_aluno(
    IN p_id_aluno INT
)
BEGIN
    SELECT
        a.nome            AS aluno,
        t.nome_turma      AS turma,
        d.nome            AS disciplina,
        n.unidade,
        n.nota,
        m.media,
        m.situacao
    FROM nota n
    JOIN aluno        a  ON n.id_aluno      = a.id_aluno
    JOIN turma        t  ON n.id_turma      = t.id_turma
    JOIN disciplina   d  ON n.id_disciplina = d.id_disciplina
    LEFT JOIN media_aluno m
           ON m.id_aluno      = n.id_aluno
          AND m.id_disciplina = n.id_disciplina
          AND m.id_turma      = n.id_turma
    WHERE n.id_aluno = p_id_aluno
    ORDER BY d.nome, n.unidade;
END//

DELIMITER ;

COMMIT;
