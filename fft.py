import flask 
from flask import request, jsonify, render_template, redirect, url_for
import testebd

app = flask.Flask(__name__) 
app.config["DEBUG"] = True 

# mod feita daqui
@app.route('/', methods=['GET']) 
def home():
    usuario = testebd.infoLinhas('usuarios',1)
    return render_template('home.html', user = usuario[0][1])

@app.route('/subir-robo', methods=['GET'])
def subir_robo():
    
    return render_template('index.html')

@app.route('/listar-robo', methods=['GET'])
def listar_robo():
    return render_template('index.html')

@app.route('/retreinar-robo', methods=['GET'])
def retreirar_robo():
    return render_template('index.html')

@app.route('/cadastrar-dicionario', methods=['GET'])
def cadastrar_dicionario():
    return render_template('index.html')
# Até aqui

@app.route('/cadfrases', methods=['GET']) 
def cadfrases(): 
    frases = testebd.infoDados('frases')
    return render_template('page.html',tokens = ['TIPO','COMIDA','QUANTIDADE','SABOR','TAMANHO','INFO','SAUDAÇÃO'], item = frases)

@app.route('/pessoa', methods=['GET'])
def buscar(): 
    usuario = testebd.infoDados('usuarios')
    print(usuario)
    return render_template('index.html',usuarios = usuario)

@app.route('/pessoa/editar', methods=['GET', 'POST'])
def editar_pessoa():
    if request.method == "POST":
        id_s = int(request.form.get('id_usuario'))
        email = str('%s' %(request.form.get('email')))
        senha = str('%s' %(request.form.get('senha')))
        testebd.atualizarDados('usuarios', email, senha, id_s)
    elif request.method == "GET":
        id_s = int(request.args['id_selec'])
        usuario = testebd.infoLinhas('usuarios', id_s)
        return render_template('editar_cad.html', usuario = usuario[0])
    else:
        print('erro')

    return redirect(url_for('buscar'))

@app.route('/pessoa/apagar', methods=['GET'])
def apagar_pessoa():
    id_s = int(request.args['id_selec'])
    testebd.apagarDados('usuarios', id_s)
    return redirect(url_for('buscar'))

@app.route('/pessoa/criar', methods=['GET'])
def criar_pessoa():
    return render_template('cadastro.html')

@app.route('/pessoa/gerenciar_frases', methods=['GET'])
def ger_frases():
    return render_template('gerenciarp.html')

@app.route('/pessoa/gerenciarp',  methods=['GET','POST'])
def adicionarp():
    if request.method == "POST":
        frase = str('%s' %(request.form.get('frase')))
        token = request.form.get('token').split(",")
        testebd.inserirDados('frases', frase, 1)
        testebd.inserirDados('tokens',token[0],token[1],token[2],str("'%s'" %(token[3])))
    else:
        print('erro')
    
    return redirect(url_for('buscar'))

@app.route('/pessoa/cadastro', methods=['GET','POST'])
def cadastrar_usuario():
    if request.method == "POST":
        email = str('%s' %(request.form.get('email')))
        senha = str('%s' %(request.form.get('senha')))
        testebd.inserirDados('usuarios', email, senha)
    else:
        print('erro')
    
    return redirect(url_for('buscar'))

    
app.run()

#criar 4 funções :
# /pessoa/criar
# /pessoa/editar
# /pssoa/apagar
# /pessoa
# /frases
# /tokens

# fazer funções dentro do flask  4 telas com flasks uma tela nome email e seha ok -> 

# faze uma tela de cadastro de usuario, /pessoas que quando acessar listar todos os usuarios pelo email e id criar um formulario de novo usuario quando apertar no boatao e segue ára /pessoa/criar botao apagar para cada usuario pelo id
# criar outra rota /pessoa/criar para gravar os dados no banco de dados
 
#pessoa/apagar que recbebe o id que sera apagado
 