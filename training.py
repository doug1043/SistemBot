import random
import spacy

TRAIN_DATA = [
    # ('Ola gostaria de uma pizza de queijo', {'entities': [(16, 19, 'QUANTIDADE'), (20, 25, 'TIPO'), (29, 35, 'SABOR')]}), 
    # ('olá quero uma pizza de frango', {'entities': [(10, 13, 'QUANTIDADE'), (14, 19, 'TIPO'), (23, 29, 'SABOR')]}), 
    # ('boa noite quero duas pizzas de queijo por favor', {'entities': [(16, 20, 'QUANTIDADE'), (21, 27, 'TIPO'), (31, 37, 'SABOR')]}), 
    # ('olá boa noite quero três pizzas de calabresa', {'entities': [(20, 24, 'QUANTIDADE'), (25, 31, 'TIPO'), (35, 44, 'SABOR')]}), 
    # ('são duas pizzas', {'entities': [(4, 8, 'QUANTIDADE'), (9, 15, 'TIPO')]}), 
    # ('são três pizzas', {'entities': [(4, 8, 'QUANTIDADE'), (9, 15, 'TIPO')]}), 
    # ('uma', {'entities': [(0, 3, 'QUANTIDADE')]}), 
    # ('duas', {'entities': [(0, 4, 'QUANTIDADE')]}), 
    # ('três', {'entities': [(0, 4, 'QUANTIDADE')]}), 
    # ('quatro', {'entities': [(0, 6, 'QUANTIDADE')]}), 
    # ('cinco', {'entities': [(0, 5, 'QUANTIDADE')]}), 
    # ('seis', {'entities': [(0, 4, 'QUANTIDADE')]}), 
    # ('sete', {'entities': [(0, 4, 'QUANTIDADE')]}), 
    # ('oito', {'entities': [(0, 4, 'QUANTIDADE')]}), 
    # ('nove', {'entities': [(0, 4, 'QUANTIDADE')]}), 
    # ('dez', {'entities': [(0, 3, 'QUANTIDADE')]}), 
    # ('1', {'entities': [(0, 1, 'QUANTIDADE')]}), 
    # ('2', {'entities': [(0, 1, 'QUANTIDADE')]}), 
    # ('3', {'entities': [(0, 1, 'QUANTIDADE')]}), 
    # ('4', {'entities': [(0, 1, 'QUANTIDADE')]}), 
    # ('5', {'entities': [(0, 1, 'QUANTIDADE')]}), 
    # ('6', {'entities': [(0, 1, 'QUANTIDADE')]}), 
    # ('7', {'entities': [(0, 1, 'QUANTIDADE')]}), 
    # ('8', {'entities': [(0, 1, 'QUANTIDADE')]}), 
    # ('9', {'entities': [(0, 1, 'QUANTIDADE')]}), 
    # ('0', {'entities': [(0, 1, 'QUANTIDADE')]})]
    # ('Boa noite gostaria de uma pizza grande sabor toscana', {'entities': [(22, 25, 'QUANTIDADE'), (26, 31, 'TIPO'), (32, 38, 'TAMANHO'), (45, 52, 'SABOR')]})
    ('ola quero uma pizza sabor portuguesa', {'entities': [(10, 13, 'QUANTIDADE'), (14, 19, 'TIPO'), (26, 36, 'SABOR')]})
]

label_ = ['TIPO', 'QUANTIDADE', 'SABOR', 'TAMANHO']


model = '/home/douglas/Sistema BOT/NLP'

saida = '/home/douglas/Sistema BOT/NLP'

n_iter=30

def train():
    
    nlp = spacy.load(model)

    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)
    else:
        ner = nlp.get_pipe('ner')

    for LABEL in label_:
        ner.add_label(LABEL)

    optimizer = nlp.entity.create_optimizer()


    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']

    with nlp.disable_pipes(*other_pipes):  # only train NER
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                nlp.update([text], [annotations], sgd=optimizer, drop=0.35,
                           losses=losses)

    # save model to output directory
    nlp.to_disk('NLP')

train()