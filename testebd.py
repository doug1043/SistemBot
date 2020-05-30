from pymysql.converters import escape_sequence
import pymysql
import json
import numpy as np
 
# Abrimos uma conexão com o banco de dados:
conexao = pymysql.connect(db='BotSystem', user='root', passwd='doug1023')
 
# Cria um cursor:
cursor = conexao.cursor()

# def consultarUsuarios():
#     cursor.execute("SELECT * FROM usuarios")
#     # Recupera o resultado:
#     resultado = cursor.fetchall()
#     print(json.dumps(resultado))
#     for linha in resultado:
#         print(json.dumps(linha))

def f(tabela):
    cursor.execute("SHOW COLUMNS FROM %s" %(tabela))
    campos = [res[0] for res in cursor.fetchall() if not res[0].startswith('id_%s' %(tabela[:-1])) and res[4] is None]
    return campos

def infoLinhas(tabela, *colunas): #informa uma linha da tabela, pelo ID
    cursor.execute("SELECT * FROM %s WHERE id_%s = %d" %(tabela, tabela[:-1], colunas[0]))
    resultado = cursor.fetchall()
    return resultado

def inserirDados(tabela, *colunas): #Insere dados a qualquer tabela
    campos = f(tabela)
    cursor.execute("INSERT INTO %s (%s) VALUES %s" %(tabela, ', '.join(campos), colunas))

def apagarDados(tabela, *colunas): #Apaga uma linha de qualquer tabela
    cursor.execute("DELETE FROM %s WHERE id_%s = %d" %(tabela, tabela[:-1], colunas[0]))

def atualizarDados(tabela, *colunas): #atualiza uma linha de qualquer tabela pelo id
    attrs = f(tabela)
    setar = ["{} = '{}'".format(attr, col) for attr, col in zip(attrs, colunas)]# ["%s = '%s'" %(''.join(attrs[i]),colunas[i]) for i in range(len(attrs))]
    cursor.execute("UPDATE %s SET %s WHERE id_%s = %d " %(tabela, ', '.join(setar), tabela[:-1], colunas[-1]))

def infoDados(tabela, *colunas): #informa todos os dados de qualquer tabela
    cursor.execute("SELECT * FROM %s" %(tabela))
    res = cursor.fetchall()
    return res

#função que passe o nome da tabela e uma lista de valores e gere um dicionario em que cada campo vai ter o seu valor da lista

# --------------TESTES-------------------------

# inserirDados('tokens',10,12,1,'QUANTIDADE')

# infoLinhas('usuarios',1)

# apagarDados('usuarios',25)

# atualizarDados('tokens',15,12,1,'QUANTIDADE',1)

# infoDados('tokens')


# ------------CONSULTAR TODOS OS DADOS------------
# cursor.execute("SELECT * FROM tokens")
# res = cursor.fetchall()
# for lin in res:
#     print(lin)

# Salva todas as alterações feitas
# conexao.commit()

# Finaliza a conexão
# conexao.close()
