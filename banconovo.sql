
DROP DATABASE IF EXISTS BotSystem;
CREATE DATABASE BotSystem;

use BotSystem;

DROP TABLE IF EXISTS `usuarios`;

CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `senha` varchar(100) NOT NULL,
  PRIMARY KEY(id_usuario)
);

DROP TABLE IF EXISTS `frases`;

CREATE TABLE `frases` (
  `id_frase` int NOT NULL AUTO_INCREMENT,
  `texto` varchar(500) NOT NULL,
  `id_usuario` int NOT NULL REFERENCES usuarios(id_usuario),
  `data_cad` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(id_frase)
);

DROP TABLE IF EXISTS `tokens`;

CREATE TABLE `tokens` (
  `id_token` int NOT NULL AUTO_INCREMENT,
  `comeco` int NOT NULL,
  `fim` int NOT NULL,
  `id_frase` int NOT NULL REFERENCES frases(id_frase),
  `entidades` varchar(500) NOT NULL,
  PRIMARY KEY(id_token)
);

INSERT INTO usuarios(email,senha) VALUES ('doug104397@gmail.com', '1234'), ('saulo.oliveira@ifce.edu.br', '1234');

INSERT INTO frases(texto,id_usuario) VALUES ('Olá quero uma pizza sabor queijo', 1), ('Gostaria de ver o cardapio', 2);

INSERT INTO tokens(comeco,fim,id_frase,entidades) VALUES (10,12,1,'QUANTIDADE'), (14,18,1,'TIPO'), (26,31,1,'SABOR');


