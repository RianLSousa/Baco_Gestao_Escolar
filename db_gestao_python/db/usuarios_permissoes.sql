-- criando usuários
CREATE USER 'secretaria_escolar'@'localhost'     IDENTIFIED BY 'TrocarSenha_Secretaria!1';
CREATE USER 'coordenacao_pedagogica'@'localhost' IDENTIFIED BY 'TrocarSenha_Coord!2';

-- grants da secretaria 
-- leitura
GRANT SELECT ON gestao_escolar.* TO 'secretaria_escolar'@'localhost';

-- crud da secretaria
GRANT INSERT, UPDATE, DELETE ON gestao_escolar.professor        TO 'secretaria_escolar'@'localhost';
GRANT INSERT, UPDATE, DELETE ON gestao_escolar.turma            TO 'secretaria_escolar'@'localhost';
GRANT INSERT, UPDATE, DELETE ON gestao_escolar.disciplina       TO 'secretaria_escolar'@'localhost';
GRANT INSERT, UPDATE, DELETE ON gestao_escolar.aluno            TO 'secretaria_escolar'@'localhost';
GRANT INSERT, UPDATE, DELETE ON gestao_escolar.turma_disciplina TO 'secretaria_escolar'@'localhost';
GRANT INSERT, UPDATE, DELETE ON gestao_escolar.tipo_condicao    TO 'secretaria_escolar'@'localhost';
GRANT INSERT, UPDATE, DELETE ON gestao_escolar.condicao_aluno   TO 'secretaria_escolar'@'localhost';
GRANT INSERT, UPDATE, DELETE ON gestao_escolar.nota             TO 'secretaria_escolar'@'localhost';

-- secretaria não pode alterar media 

GRANT INSERT, UPDATE, DELETE ON gestao_escolar.media_aluno TO 'secretaria_escolar'@'localhost';
REVOKE INSERT, UPDATE, DELETE ON gestao_escolar.media_aluno FROM 'secretaria_escolar'@'localhost';

-- coordenacao_pedagogica (só consulta)

GRANT SELECT ON gestao_escolar.* TO 'coordenacao_pedagogica'@'localhost';

FLUSH PRIVILEGES;





