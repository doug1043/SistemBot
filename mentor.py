import pickle
import cProfile
import telegram
import csv
import spacy
import re
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import GaussianNB
from datetime import datetime
from config import nlp as nlpconfig, bot
from config import bot_token, bot_user_name, bot, TOKEN
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup


PIZZA, LANCHE, BEBIDA, FAZENDO_PEDIDO, ENVIANDO_ENDERECO, PEDIR_MAIS, BAIRRO, NUMERO, CONTATO, CONFIRMAR_ENDERECO = range(10)

END = ConversationHandler.END

nlp = spacy.load(nlpconfig["dic"])

usuarios = {
}

CHAT_TIMEOUT=300

perguntas = {
    "PIZZA":{"SABOR": 'Qual sabor você quer? Temos:\nQueijo\nCarne\nCalabresa',
             "TAMANHO": 'Ok, qual o tamanho? \nTemos:\nPequena\nMedia\nGrande',
             "QUANTIDADE": 'Agora informe a quantidade que deseja'},
    "LANCHE":{"QUANTIDADE": 'Agora informe a quantidade que deseja'},
    "BEBIDA":{"QUANTIDADE": 'Agora informe a quantidade que deseja'}
                  
    }

actions = {
    "TIPO": None,
    "PRODUTO": None,
    "PIZZA": {"SABOR": None, "TAMANHO": None, "QUANTIDADE": None},
    "LANCHE": {"QUANTIDADE": None},
    "BEBIDA": {"QUANTIDADE": None}
}

def mapping(tokens):
    word_to_id = dict()

    for i, token in enumerate(set(tokens)):
        word_to_id[token] = i

    return word_to_id

def generate_test_data(tokens, word_to_id):
    pattern = [0] * len(word_to_id)

    for token in tokens:
        if token in word_to_id.keys():
            pattern[ word_to_id[token] ] = 1

    return pattern

def generate_training_data(tokens, word_to_id, window_size):
    N = len(tokens)
    X, Y = [], []

    for i in range(N):
        nbr_inds = list(range(max(0, i - window_size), i)) + \
                   list(range(i + 1, min(N, i + window_size + 1)))
        for j in nbr_inds:
            X.append(word_to_id[tokens[i]])
            Y.append(word_to_id[tokens[j]])

    X = np.expand_dims(X, axis=0)
    Y = np.expand_dims(Y, axis=0)

    return X, Y

def extrair_tokens(comando):
    doc = nlp(comando.lower())
    extract = lambda token : token.lemma_ if token.pos_ == 'VERB' else token.orth_
    tokens = set([extract(token) for token in doc])

    return list(tokens)

def treino_dialog():
    lista1 = []
    lista2 = []

    try:
        with open('objs.pkl', 'rb') as f:
            X, word_to_id, le, L2 = pickle.load(f)

    except IOError:
        with open('dialogo.csv', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';')
            for coluna in spamreader:
                lista1 += [coluna[0]]
                lista2 += [coluna[1]]

        string1 = ', '.join(lista1)
        # extrair os tokens :)
        tokens = extrair_tokens(string1)
        word_to_id = mapping(tokens)
        X = [generate_test_data(extrair_tokens(comando), word_to_id) for comando in lista1]
        le = LabelEncoder()
        L2 = le.fit(lista2).transform(lista2)
        
        with open('objs.pkl', 'wb') as f:
            pickle.dump([X, word_to_id, le, L2], f)

    clf = GaussianNB()
    clf.fit(X, L2)

    def predicao_dialog(clf, le, Xt):
        saida = clf.predict(np.asarray(Xt).reshape(1, -1))
        proc = ''.join(le.inverse_transform(saida))
        print('proc: ',proc)
        return proc
    
    return lambda Xt: predicao_dialog(clf, le, Xt), word_to_id

predicao, word_to_id = treino_dialog()

def process_dialog(comando):
    global predicao
    global word_to_id

    tokens_frase = extrair_tokens(comando)

    Xt = generate_test_data(tokens_frase, word_to_id)

    return predicao(Xt)

def process_keys(msg):
    x = msg
    doc = nlp(x)
    k = [(entity.label_) for entity in doc.ents]
    print('tokens: ', k)
    return k

def process_cont(msg):
    x = msg
    doc = nlp(x)
    c = [(entity) for entity in doc.ents]
    print('conteudos: ', c)
    return c

def menu(update, context):
    update.message.reply_text(menu_principal_message(), reply_markup=menu_principal_keyboard())

def menu_principal(update,context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=menu_principal_message(), reply_markup=menu_principal_keyboard())

def pizzas_salgadas(update,context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=pizzas_salgadas_message(), reply_markup=home_keyboard())

def pizzas_doces(update,context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=pizzas_doces_message(), reply_markup=home_keyboard())

def lanches(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=lanches_message(), reply_markup=home_keyboard())

def bebidas(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=bebidas_message(), reply_markup=home_keyboard())

def precos(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=precos_message(), reply_markup=home_keyboard())

############################ Keyboards Menu #########################################
def home_keyboard():
    keyboard = [[InlineKeyboardButton('Voltar', callback_data='main')]]
    return InlineKeyboardMarkup(keyboard)

def menu_principal_keyboard():
    keyboard = [[InlineKeyboardButton('\N{SLICE OF PIZZA} Pizzas Salgadas', callback_data='pizzas_salgadas'),
               InlineKeyboardButton('\N{SLICE OF PIZZA} Pizzas Doces', callback_data='pizzas_doces')],
              [InlineKeyboardButton('\N{HAMBURGER} Lanches', callback_data='lanches'),
               InlineKeyboardButton('\N{TROPICAL DRINK} Bebidas', callback_data='bebidas')],
             [InlineKeyboardButton('\N{MONEY BAG} Preços das Pizzas', callback_data='precos')]
  ]
    return InlineKeyboardMarkup(keyboard)

############################# Messages Menu #########################################
def menu_principal_message():
    return '-------------- Cardapio\nEscolha umas das opções abaixo para obter informações sobre os produtos disponíveis!\nEscolha um item e é só pedir'

def pizzas_salgadas_message():
    return 'Queijo__________\nCalabresa__________\nToscana__________'

def pizzas_doces_message():
    return 'Chocolate\nBrigadeiro'

def lanches_message():
    return '- X-Burger\n- X-Bacon\n- X-Tudo'

def bebidas_message():
    return '- Refrigerante Lata\n- Refrigerante 600ml\n- Refrigerante 2L\n- Cerveja Lata'

def precos_message():
    return '######### Pizzas ##########\n\n# Pequena_______________15,00R$ \n# Media__________________18,00R$ \n# Grande__________________20,00R$'
    
def verif_INFO(conteudo):
    conteudo = conteudo.split()
    if re.search("pagamentos?", str(conteudo)) or re.search("dinheiro", str(conteudo)) or re.search("cart[aãoõ](o|es)", str(conteudo)):
        return 'Aceitamos dinheiro, Cartão ou via Paypal'
    elif re.search("d[uú]vidas?", str(conteudo)) or re.search("funcionam?", str(conteudo)):
        return 'Entendi que você tem dúvidas, mande o comando /help \npara saber todos os comandos que consigo entender :)'
    elif re.search("desenvolv(eu|ido)", str(conteudo)) or re.search("pai", str(conteudo)):
        return 'Eu fui desenvolvido pelo Douglas :D'
    elif re.search("programado", str(conteudo)) or re.search("linguagem", str(conteudo)) or re.search("python", str(conteudo)):
        return 'Eu fui desenvolvido em Python'
    elif re.search("sabe", str(conteudo)) or re.search("fazer", str(conteudo)):
        return 'Por enquanto, não muita coisa. Mas pretendo evoluir com o tempo'
    elif re.search("java", str(conteudo)) or re.search("php", str(conteudo)) or re.search("sql", str(conteudo)):
        return 'Python'
    elif re.search("endereço", str(conteudo)) or re.search("localizaç[ãa]o", str(conteudo)):
        return 'Ficamos na rua Av. tal, Bairro tal numero tal'
    elif re.search("nome", str(conteudo)):
        return 'hmm... Eu ainda não tenho um nome :('
    elif re.search("rob[oô]", str(conteudo)) or re.search("bot", str(conteudo)):
        return 'Sou um robô desenvolvido para lhe atender de forma rapida e pratica. É só pedir :D'
    else: 
        return 'Desculpe, não entendi. Por favor Tente novamente com outras palavras'

def verif_SN(conteudo):
    conteudo = conteudo.split()
    for ac in conteudo:
        if re.search("cart[aã]o", str(ac)) or re.search("entregas?", str(ac)) or re.search("bebidas?", str(ac)) or re.search("pizzas?", str(ac)) or re.search("lanches?", str(ac)):
            return 'Sim'
    return 'Não'

def processar_token_faltante(context, tokens, conteudos):
    global actions

    for item in tokens:
        context.user_data[context.user_data['PRODUTO']][item] = str(conteudos[tokens.index(item)]) 
    for faltante in actions[context.user_data['PRODUTO']]:
        if context.user_data[context.user_data['PRODUTO']][faltante] == None:
            return faltante

    return None

def processar_produto(keymsg):
    for produto in keymsg:
        if produto == 'PIZZA' or produto == 'LANCHE' or produto == 'BEBIDA':
            return produto

    return None

def saudacao(update, context):
    update.message.reply_text('Olá, eu sou um robô e estou aqui para lhe atender. É só pedir :)')

def pedido_direto(update, context):
    context.user_data['direto'] = None
    frase = update.message.text.lower()
    frase = re.sub('[^a-z-áàâãéèêíïóôõöúç0-9 ]', '', frase)

    if frase == 'pedido' or frase == 'start' or frase == 'help':
        return None
    pedido(update, context)

    if context.user_data['TIPO'] == None:
        tipo = process_dialog(frase)

    context.user_data['TIPO'] = tipo

    if tipo == 'PEDIDO':
        return fazendo_pedido(update, context)
    elif tipo == 'CARDAPIO':
        menu(update, context) 
        return END
    elif tipo == 'SN':
        sn = verif_SN(frase)
        update.message.reply_text(sn)
    elif tipo == 'INFO':
        info = verif_INFO(frase)
        update.message.reply_text(info)
    elif tipo == 'SD':
        saudacao(update, context)
        return END
    else:
        return END

def start(update, context):
    now = datetime.now()
    dia = ('Olá, Bom Dia !')
    tarde = ('Olá, Boa Tarde !')
    noite = ('Olá, Boa Noite !')
    hora = now.hour

    if hora >= 6 and hora < 12:
        saudacao = dia
    elif hora >= 12 and hora < 18:
        saudacao = tarde
    elif hora >= 18 and hora < 24 or hora >= 0 and hora < 6:
        saudacao = noite
    
    update.message.reply_text(saudacao)

    return pedido(update, context)

def help_handler(update, context):
    update.message.reply_text('Eu sou um robô desenvolvido para lhe atender de maneira rápida e facil.\n'
    'Ainda estou em fase de desenvolvimento, então eu aprendi poucas coisas ainda.\n'
    'Você pode fazer o pedido completo ou por partes, vou citar alguns exemplos:\n'
    '"Quero pizza", ou "Quero uma pizza pequena", ou "quero uma pizza pequena de queijo"\n'
    '-----------Comandos Rapidos\n'
    '\N{WHITE RIGHT POINTING BACKHAND INDEX} /menu exibe um cardapio interativo com os produtos disponíveis\n'
    '\N{WHITE RIGHT POINTING BACKHAND INDEX} /pedido fazer um pedido')

    return END

def pedido(update, context):
    if 'direto' not in context.user_data:
        update.message.reply_text(
            'Eu sou um robô treinado para lhe ajudar a fazer seu pedido'
            '\nVocê pode começar fazendo o pedido como por exemplo:\n"Quero uma pizza" ou "quero uma coca"')

    context.user_data['TIPO'] = None
    context.user_data['PRODUTO'] = None
    context.user_data['PIZZA'] = {"SABOR": None, "TAMANHO": None, "QUANTIDADE": None}
    context.user_data['LANCHE'] = {"QUANTIDADE": None}
    context.user_data['BEBIDA'] = {"QUANTIDADE": None}
    context.user_data['endereco'] = {"rua": None, "bairro": None, "numero": None}
    context.user_data['contato'] = None
 
    return FAZENDO_PEDIDO

def pedir_mais(update, context):
    frase = update.message.text
    if frase == 'SIM':
        #guarda pedido anterior, e chama fazendo pedido
        context.user_data[context.user_data['PRODUTO']] = {"SABOR": None, "TAMANHO": None, "QUANTIDADE": None}
        update.message.reply_text('O que mais deseja?', 
        reply_markup=ReplyKeyboardRemove())
        return FAZENDO_PEDIDO
    elif frase == 'NÃO':
        update.message.reply_text('Ok, agora preciso de seu endereço. Vamos começar pelo nome da rua', 
        reply_markup=ReplyKeyboardRemove())
        return ENVIANDO_ENDERECO
    else:
        update.message.reply_text('Desculpe, não entendi :(\n\nEnvie /start para refazer o pedido', 
        reply_markup=ReplyKeyboardRemove())
        return END

def fazendo_pedido(update, context):
    frase = update.message.text.lower()
    frase = re.sub('[^a-z-áàâãéèêíïóôõöúç0-9 ]', '', frase)

    if context.user_data['TIPO'] == None:
        context.user_data['TIPO'] = process_dialog(frase)

    contmsg = process_cont(frase) 
    keymsg = process_keys(frase)
    produto = processar_produto(keymsg)

    if produto == None:
        update.message.reply_text('Tivemos um problema ao processar seu pedido, por favor tente novamente com outras palavras.')
        return END

    context.user_data['PRODUTO'] = produto
    token_faltante = processar_token_faltante(context, keymsg, contmsg)
    print('produto: ',produto)
    if token_faltante == None:
        reply_keyboard = [['SIM','NÃO']]
        update.message.reply_text('Deseja mais alguma coisa?', 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        print(context.user_data)
        return PEDIR_MAIS
    else:
        update.message.reply_text(perguntas[context.user_data['PRODUTO']][token_faltante])

        if produto == 'PIZZA':
            return PIZZA

        elif produto == 'LANCHE':
            return LANCHE

        elif produto == 'BEBIDA':
            return BEBIDA
        else:
            return END

def pizza(update, context):
    print('entrou em pizza')
    frase = update.message.text
    contmsg = process_cont(frase) 
    keymsg = process_keys(frase)
    token_faltante = processar_token_faltante(context, keymsg, contmsg)

    if token_faltante == None:
        reply_keyboard = [['SIM','NÃO']]
        update.message.reply_text('Deseja mais alguma coisa?', 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        return PEDIR_MAIS
    else:
        update.message.reply_text(perguntas[context.user_data['PRODUTO']][token_faltante])

    return PIZZA
    
def lanche(update, context):
    print('entrou em lanche')
    frase = update.message.text
    contmsg = process_cont(frase) 
    keymsg = process_keys(frase)
    token_faltante = processar_token_faltante(context, keymsg, contmsg)

    if token_faltante == None:
        reply_keyboard = [['SIM','NÃO']]
        update.message.reply_text('Deseja mais alguma coisa?', 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        print(context.user_data)
        return PEDIR_MAIS
    else:
        update.message.reply_text(perguntas[context.user_data['PRODUTO']][token_faltante])
    

    return LANCHE

def confirmar_endereco(update, context):
    msg_corrige_rua = 'Corrigindo dados...\nInforme o nome da rua'
    msg_corrige_bairro = 'Corrigindo dados...\nInforme o nome do bairro'
    msg_corrige_numero = 'Corrigindo dados...\nInforme o numero de sua residencia'
    msg_corrige_contato = 'Corrigindo dados...\nInforme o contato'

    msg_rua = 'Agora informe o nome do bairro'
    msg_bairro = 'Informe o numero de sua residencia'
    msg_numero = 'Informe um contato para que a gente possa entrar em contato caso precisarmos de mais alguma informação'
    
    if update.message.text == 'SIM':
        if context.user_data['estado'] == 'rua':
            update.message.reply_text(msg_rua, 
            reply_markup=ReplyKeyboardRemove())
            return BAIRRO
        elif context.user_data['estado'] == 'bairro':
            update.message.reply_text(msg_bairro, 
            reply_markup=ReplyKeyboardRemove())
            return NUMERO
        elif context.user_data['estado'] == 'numero':
            update.message.reply_text(msg_numero, 
            reply_markup=ReplyKeyboardRemove())
            return CONTATO
        else:
            update.message.reply_text('Seu pedido está a caminho!\n\nAgradecemos seu contato\nenvie /start caso queira fazer um novo pedido.', 
            reply_markup=ReplyKeyboardRemove())
            return END

    if update.message.text == 'NÃO':
        if context.user_data['estado'] == 'rua':
            update.message.reply_text(msg_corrige_rua, 
            reply_markup=ReplyKeyboardRemove())
            return ENVIANDO_ENDERECO
        elif context.user_data['estado'] == 'bairro':
            update.message.reply_text(msg_corrige_bairro, 
            reply_markup=ReplyKeyboardRemove())
            return BAIRRO
        elif context.user_data['estado'] == 'numero':
            update.message.reply_text(msg_corrige_numero, 
            reply_markup=ReplyKeyboardRemove())
            return NUMERO
        else:
            update.message.reply_text(msg_corrige_contato, 
            reply_markup=ReplyKeyboardRemove())
            return CONTATO
    else:
        update.message.reply_text('Desculpe, não entendi :(\n\nEnvie /start para refazer o pedido', 
        reply_markup=ReplyKeyboardRemove())
        return END

def enviando_endereco(update, context):
    context.user_data['estado'] = 'rua'
    reply_keyboard = [['SIM','NÃO']]
    context.user_data['endereco']['rua'] = update.message.text
    update.message.reply_text('Rua: {}\n\nEstá correto?'.format(context.user_data['endereco']['rua']), 
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

    return CONFIRMAR_ENDERECO

def bairro(update, context):
    context.user_data['estado'] = 'bairro'
    reply_keyboard = [['SIM','NÃO']]
    context.user_data['endereco']['bairro'] = update.message.text
    update.message.reply_text('Bairro: {}\n\nEstá correto?'.format(context.user_data['endereco']['bairro']), 
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

    return CONFIRMAR_ENDERECO

def numero(update, context):
    context.user_data['estado'] = 'numero'
    reply_keyboard = [['SIM','NÃO']]
    context.user_data['endereco']['numero'] = update.message.text
    update.message.reply_text('Numero: {}\n\nEstá correto?'.format(context.user_data['endereco']['numero']), 
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

    return CONFIRMAR_ENDERECO

def contato(update, context):
    context.user_data['estado'] = 'contato'
    reply_keyboard = [['SIM','NÃO']]
    context.user_data['endereco']['contato'] = update.message.text
    print('Dados finais: ',context.user_data)
    update.message.reply_text('Contato: {}\n\nEstá correto?'.format(context.user_data['endereco']['contato']), 
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))

    return CONFIRMAR_ENDERECO

def error(update, context):
    print('Update "%s" caused error "%s"', update, context.error)

def timeout(update, context):
    update.message.reply_text('Tempo esgotado, para iniciar um novo pedido envie o comando /start', 
    reply_markup=ReplyKeyboardRemove())

    return END

def analisar_msg(update, context):
    comando = update.message.text.lower()
    comando = re.sub('[^a-z-áàâãéèêíïóôõöúç0-9 ]', '', comando)
    tipo = process_dialog(comando)

    if 'PEDIDO' in tipo:
        update.message.reply_text('Digite /pedido para fazer um pedido')
    elif 'CARDAPIO' in tipo:
        update.message.reply_text('Cardapio')
    elif 'INFO' in tipo:
        update.message.reply_text('Digite o comando /help para saber sobre diversas informações')
    else:
        update.message.reply_text('Desculpe, não entendi.\nDigite o comando /pedido para fazer um pedido\nhelp para informações')

def cancel(update, context):
    update.message.reply_text('Ok, conversa cancelada.\nPara fazer um novo pedido envie /start', 
    reply_markup=ReplyKeyboardRemove())

    return END

def main():
    updater = Updater(TOKEN, use_context=True)

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO  
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start), 
            CommandHandler('help', help_handler), 
            CommandHandler('pedido', pedido), 
            CommandHandler('menu', menu),
            CallbackQueryHandler(menu_principal, pattern='main'),
            CallbackQueryHandler(pizzas_salgadas, pattern='pizzas_salgadas'),
            CallbackQueryHandler(pizzas_doces, pattern='pizzas_doces'),
            CallbackQueryHandler(lanches, pattern='lanches'),
            CallbackQueryHandler(bebidas, pattern='bebidas'),
            CallbackQueryHandler(precos, pattern='precos'),
            MessageHandler(Filters.text, pedido_direto)],

        states={
            FAZENDO_PEDIDO: [MessageHandler(Filters.text, fazendo_pedido)],
            PIZZA: [MessageHandler(Filters.text, pizza)],
            LANCHE: [MessageHandler(Filters.text, lanche)],
            PEDIR_MAIS: [MessageHandler(Filters.text, pedir_mais)],
            ENVIANDO_ENDERECO: [MessageHandler(Filters.text, enviando_endereco)],
            BAIRRO: [MessageHandler(Filters.text, bairro)],
            NUMERO: [MessageHandler(Filters.text, numero)],
            CONTATO: [MessageHandler(Filters.text, contato)],
            CONFIRMAR_ENDERECO: [MessageHandler(Filters.text, confirmar_endereco)],

            ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, timeout)]
        },

        fallbacks=[CommandHandler('cancel', cancel)],
        conversation_timeout=CHAT_TIMEOUT,
        # allow_reentry= True
    )

    dp = updater.dispatcher

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



if __name__ == '__main__':
    main()