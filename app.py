import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
import telegram
from telebot.config import bot_token, bot_user_name,URL, bot, TOKEN
from telebot.mentor import get_response
import testebd
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/douglas/Sistema BOT/uploads'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

@app.route('/', methods=['GET']) 
def home():
    usuario = testebd.infoLinhas('usuarios',1)
    return render_template('home.html', user = usuario[0][1])

@app.route('/listar-robo', methods=['GET'])
def listar_robo():
    return render_template('index.html')

@app.route('/retreinar-robo', methods=['GET'])
def retreirar_robo():
    return render_template('index.html')

@app.route('/cadastrar-dicionario', methods=['GET'])
def cadastrar_dicionario():
    return render_template('index.html')

@app.route('/{}'.format(TOKEN), methods=['POST'])
def process():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    texto = update.message.text.encode('utf-8').decode()
    print("got text message :", texto)

    response = get_response(texto, chat_id, msg_id, update)

    return 'ok'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return 'webhook confgurado com sucesso!'
    else:
        return 'ERROR webhook não configurado!'
    
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload')
def upload_form():
	return render_template('upload.html')

@app.route('/uploader', methods=['POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return redirect('/')
		else:
			return redirect(request.url)

if __name__ == '__main__':
    app.run(threaded=True)