import csv
import spacy
import re
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import GaussianNB
from datetime import datetime
from telebot.config import nlp as nlpconfig, bot
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

nlp = spacy.load(nlpconfig["dic"])

usuarios = {
}

actions = { #Acho que aqui da para importar de algum arquivo
        "TIPO": None,
        "QUANTIDADE": None,
        "TAMANHO": None,
        "SABOR": None
        }

def tokenize(text):
    # obtains tokens with a least 1 alphabet
    pattern = re.compile(r'[A-Za-z]+[\w^\']*|[\w^\']*[A-Za-z]+[\w^\']*')
    return pattern.findall(text.lower())

def mapping(tokens):
    word_to_id = dict()
    id_to_word = dict()

    for i, token in enumerate(set(tokens)):
        word_to_id[token] = i
        id_to_word[i] = token

    return word_to_id, id_to_word

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
            
    X = np.array(X)
    X = np.expand_dims(X, axis=0)
    Y = np.array(Y)
    Y = np.expand_dims(Y, axis=0)

    return X, Y

def extrair_tokens(comando):
    doc = nlp(comando.lower())
    extract = lambda token : token.lemma_ if token.pos_ == 'VERB' else token.orth_
    tokens = set([extract(token) for token in doc])

    return list(tokens)

def process_dialog(comando):
    lista1 = []
    lista2 = []

    with open('dialogo.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        for coluna in spamreader:
            lista1 += [coluna[0]]
            lista2 += [coluna[1]]


    string2 = ', '.join(lista2)
    string1 = ', '.join(lista1)
    # extrair os tokens :)
    tokens = extrair_tokens(string1)

    word_to_id, id_to_word = mapping(tokens)

    tokens_frase = extrair_tokens(comando)

    Xt = generate_test_data(tokens_frase, word_to_id)

    le = LabelEncoder()
    L2 = le.fit(lista2).transform(lista2)


    clf = GaussianNB()

    X = [generate_test_data(extrair_tokens(comando), word_to_id) for comando in lista1]


    clf.fit(X, L2)

    tokens_frase = extrair_tokens(comando)

    Xt = generate_test_data(tokens_frase, word_to_id)
    saida = clf.predict(np.asarray(Xt).reshape(1, -1))
    proc = ''.join(le.inverse_transform(saida))

    return proc 

def process_keys(msg):
    x = msg
    doc = nlp(x)
    k = [(entity.label_) for entity in doc.ents]
    return k

def process_cont(msg):
    x = msg
    doc = nlp(x)
    c = [(entity) for entity in doc.ents]
    return c

def process_action(action, tokens, conteudos, chat_id, msg_id, update):
    global usuarios
    if chat_id not in usuarios:
        usuarios[chat_id] = { #Acho que aqui da para importar de algum arquivo
        "TIPO": None,
        "QUANTIDADE": None,
        "TAMANHO": None,
        "SABOR": None
        }
    perguntas = {
        "TIPO": 'Por favor informe qual produto deseja:\nTemos:\nPizzas\nBebidas\nLanches\nSucos',
        "QUANTIDADE": 'Agora informe a quantidade que deseja',
        "TAMANHO": 'Ok, qual o tamanho? \nTemos:\nPequena\nMedia\nGrande',
        "SABOR": 'Qual sabor você quer? Temos:\nQueijo\nCarne\nCalabresa'
    }

    for item in tokens:
        usuarios[chat_id][item] = str(conteudos[tokens.index(item)])

    for a in actions:
      if usuarios[chat_id][a] == None:
          solicitar_perg(perguntas[a], chat_id, msg_id, update)
          break

    print(usuarios)
    print(tokens)
    return 'tent'

def solicitar_perg(response, chat_id, msg_id, update):
    bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
    

def get_response(msg, chat_id, msg_id, update):
    if msg != "":
        comando = msg.lower()
        chaveS = process_dialog(comando)
        cm = chaveS
        contmsg = process_cont(comando)
        keymsg = process_keys(comando)
        cm1 = ' '.join([str(elem) for elem in contmsg])
        cm2 = ' '.join([str(elem) for elem in keymsg])
        # teste = 'conteudo: {}, tokens: {}, comando: {}'.format(cm1, cm2, cm)
        teste = process_action('PEDIDO',keymsg,contmsg, chat_id, msg_id, update)
        output = teste

    return output