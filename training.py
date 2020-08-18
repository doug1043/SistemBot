import plac
import random
from pathlib import Path
import spacy
from tqdm import tqdm


TRAIN_DATA = [
("toscana",{"entities":[(0,7,"SABOR")]}),
("queijo",{"entities":[(0,6,"SABOR")]}),
("calabresa",{"entities":[(0,9,"SABOR")]}),
("pequenas",{"entities":[(0,8,"TAMANHO")]}),
("pequena",{"entities":[(0,7,"TAMANHO")]}),
("medias",{"entities":[(0,6,"TAMANHO")]}),
("media",{"entities":[(0,5,"TAMANHO")]}),
("grandes",{"entities":[(0,7,"TAMANHO")]}),
("grande",{"entities":[(0,6,"TAMANHO")]}),
("100",{"entities":[(0,3,"QUANTIDADE")]}),
("90",{"entities":[(0,2,"QUANTIDADE")]}),
("80",{"entities":[(0,2,"QUANTIDADE")]}),
("70",{"entities":[(0,2,"QUANTIDADE")]}),
("60",{"entities":[(0,2,"QUANTIDADE")]}),
("50",{"entities":[(0,2,"QUANTIDADE")]}),
("40",{"entities":[(0,2,"QUANTIDADE")]}),
("30",{"entities":[(0,2,"QUANTIDADE")]}),
("20",{"entities":[(0,2,"QUANTIDADE")]}),
("19",{"entities":[(0,2,"QUANTIDADE")]}),
("18",{"entities":[(0,2,"QUANTIDADE")]}),
("17",{"entities":[(0,2,"QUANTIDADE")]}),
("16",{"entities":[(0,2,"QUANTIDADE")]}),
("15",{"entities":[(0,2,"QUANTIDADE")]}),
("14",{"entities":[(0,2,"QUANTIDADE")]}),
("13",{"entities":[(0,2,"QUANTIDADE")]}),
("12",{"entities":[(0,2,"QUANTIDADE")]}),
("11",{"entities":[(0,2,"QUANTIDADE")]}),
("10",{"entities":[(0,2,"QUANTIDADE")]}),
("9",{"entities":[(0,1,"QUANTIDADE")]}),
("8",{"entities":[(0,1,"QUANTIDADE")]}),
("7",{"entities":[(0,1,"QUANTIDADE")]}),
("6",{"entities":[(0,1,"QUANTIDADE")]}),
("5",{"entities":[(0,1,"QUANTIDADE")]}),
("4",{"entities":[(0,1,"QUANTIDADE")]}),
("3",{"entities":[(0,1,"QUANTIDADE")]}),
("2",{"entities":[(0,1,"QUANTIDADE")]}),
("1",{"entities":[(0,1,"QUANTIDADE")]}),
("cem",{"entities":[(0,3,"QUANTIDADE")]}),
("noventa",{"entities":[(0,7,"QUANTIDADE")]}),
("oitenta",{"entities":[(0,7,"QUANTIDADE")]}),
("setenta",{"entities":[(0,7,"QUANTIDADE")]}),
("sessenta",{"entities":[(0,8,"QUANTIDADE")]}),
("cinquenta",{"entities":[(0,9,"QUANTIDADE")]}),
("quarenta",{"entities":[(0,8,"QUANTIDADE")]}),
("trinta",{"entities":[(0,6,"QUANTIDADE")]}),
("vinte",{"entities":[(0,5,"QUANTIDADE")]}),
("dezenove",{"entities":[(0,8,"QUANTIDADE")]}),
("dezoito",{"entities":[(0,7,"QUANTIDADE")]}),
("dezessete",{"entities":[(0,9,"QUANTIDADE")]}),
("dezesseis",{"entities":[(0,9,"QUANTIDADE")]}),
("quinze",{"entities":[(0,6,"QUANTIDADE")]}),
("quatorze",{"entities":[(0,8,"QUANTIDADE")]}),
("treze",{"entities":[(0,5,"QUANTIDADE")]}),
("doze",{"entities":[(0,4,"QUANTIDADE")]}),
("onze",{"entities":[(0,4,"QUANTIDADE")]}),
("dez",{"entities":[(0,3,"QUANTIDADE")]}),
("nove",{"entities":[(0,4,"QUANTIDADE")]}),
("oito",{"entities":[(0,4,"QUANTIDADE")]}),
("sete",{"entities":[(0,4,"QUANTIDADE")]}),
("seis",{"entities":[(0,4,"QUANTIDADE")]}),
("cinco",{"entities":[(0,5,"QUANTIDADE")]}),
("quatro",{"entities":[(0,6,"QUANTIDADE")]}),
("três",{"entities":[(0,4,"QUANTIDADE")]}),
("duas",{"entities":[(0,4,"QUANTIDADE")]}),
("uma",{"entities":[(0,3,"QUANTIDADE")]}),
("olá vou querer duas pizzas grandes de queijo",{"entities":[(15,19,"QUANTIDADE"),(20,26,"PIZZA"),(27,34,"TAMANHO"),(38,44,"SABOR")]}),
("olá vou querer uma pizza grande de queijo",{"entities":[(15,18,"QUANTIDADE"),(19,24,"PIZZA"),(25,31,"TAMANHO"),(35,41,"SABOR")]}),
("olá vou querer duas pizzas de queijo",{"entities":[(15,19,"QUANTIDADE"),(20,26,"PIZZA"),(30,36,"SABOR")]}),
("olá vou querer uma pizza de queijo",{"entities":[(15,18,"QUANTIDADE"),(19,24,"PIZZA"),(28,34,"SABOR")]}),
("olá quero duas pizzas grandes de queijo",{"entities":[(10,14,"QUANTIDADE"),(15,21,"PIZZA"),(22,29,"TAMANHO"),(33,39,"SABOR")]}),
("olá quero uma pizza grande de queijo",{"entities":[(10,13,"QUANTIDADE"),(14,19,"PIZZA"),(20,26,"TAMANHO"),(30,36,"SABOR")]}),
("olá quero duas pizzas de queijo",{"entities":[(10,14,"QUANTIDADE"),(15,21,"PIZZA"),(25,31,"SABOR")]}),
("olá quero uma pizza de queijo",{"entities":[(10,13,"QUANTIDADE"),(14,19,"PIZZA"),(23,29,"SABOR")]}),
("olá quero duas pizzas de queijo por favor",{"entities":[(10,14,"QUANTIDADE"),(15,21,"PIZZA"),(25,31,"SABOR")]}),
("olá quero uma pizza de queijo por favor",{"entities":[(10,13,"QUANTIDADE"),(14,19,"PIZZA"),(23,29,"SABOR")]}),
("duas pizzas grandes sabor queijo",{"entities":[(0,4,"QUANTIDADE"),(5,11,"PIZZA"),(12,19,"TAMANHO"),(26,32,"SABOR")]}),
("uma pizza grande sabor queijo",{"entities":[(0,3,"QUANTIDADE"),(4,9,"PIZZA"),(23,29,"SABOR"),(10,16,"TAMANHO")]}),
("duas pizzas sabor queijo",{"entities":[(0,4,"QUANTIDADE"),(5,11,"PIZZA"),(18,24,"SABOR")]}),
("uma pizza sabor queijo",{"entities":[(0,3,"QUANTIDADE"),(4,9,"PIZZA"),(16,22,"SABOR")]}),
("duas pizzas de queijo",{"entities":[(0,4,"QUANTIDADE"),(5,11,"PIZZA"),(15,21,"SABOR")]}),
("uma pizza de queijo",{"entities":[(0,3,"QUANTIDADE"),(4,9,"PIZZA"),(13,19,"SABOR")]}),
("quero duas pizzas grandes de queijo",{"entities":[(6,10,"QUANTIDADE"),(11,17,"PIZZA"),(18,25,"TAMANHO"),(29,35,"SABOR")]}),
("quero uma pizza grande de queijo",{"entities":[(6,9,"QUANTIDADE"),(10,15,"PIZZA"),(16,22,"TAMANHO"),(26,32,"SABOR")]}),
("eu quero duas pizzas grandes de queijo",{"entities":[(9,13,"QUANTIDADE"),(14,20,"PIZZA"),(21,28,"TAMANHO"),(32,38,"SABOR")]}),
("eu quero uma pizza grande de queijo",{"entities":[(9,12,"QUANTIDADE"),(13,18,"PIZZA"),(19,25,"TAMANHO"),(29,35,"SABOR")]}),
("boa noite, eu gostaria de duas pizzas grandes de queijo por favor",{"entities":[(26,30,"QUANTIDADE"),(31,37,"PIZZA"),(38,45,"TAMANHO"),(49,55,"SABOR")]}),
("boa noite, eu gostaria de uma pizza grande de queijo por favor",{"entities":[(26,29,"QUANTIDADE"),(30,35,"PIZZA"),(36,42,"TAMANHO"),(46,52,"SABOR")]}),
("boa noite eu quero duas pizzas grandes de queijo por favor",{"entities":[(19,23,"QUANTIDADE"),(24,30,"PIZZA"),(31,38,"TAMANHO"),(42,48,"SABOR")]}),
("boa noite eu quero uma pizza grande de queijo por favor",{"entities":[(19,22,"QUANTIDADE"),(23,28,"PIZZA"),(29,35,"TAMANHO"),(39,45,"SABOR")]}),
("boa noite eu quero duas pizzas de queijo por favor",{"entities":[(19,23,"QUANTIDADE"),(24,30,"PIZZA"),(34,40,"SABOR")]}),
("boa noite eu quero uma pizza de queijo por favor",{"entities":[(19,22,"QUANTIDADE"),(23,28,"PIZZA"),(32,38,"SABOR")]}),
("boa noite, gostaria de duas pizzas grandes de queijo por favor",{"entities":[(23,27,"QUANTIDADE"),(28,34,"PIZZA"),(35,42,"TAMANHO"),(46,52,"SABOR")]}),
("boa noite, gostaria de uma pizza grande de queijo por favor",{"entities":[(23,26,"QUANTIDADE"),(27,32,"PIZZA"),(33,39,"TAMANHO"),(43,49,"SABOR")]}),
("boa noite, gostaria de duas pizzas de queijo por favor",{"entities":[(23,27,"QUANTIDADE"),(28,34,"PIZZA"),(38,44,"SABOR")]}),
("boa noite, gostaria de uma pizza de queijo por favor",{"entities":[(23,26,"QUANTIDADE"),(27,32,"PIZZA"),(36,42,"SABOR")]}),
]

label_ = ['PIZZA', 'QUANTIDADE', 'TAMANHO', 'SABOR']

model = 'NLP'

saida = 'NLP'

n_iter = 20

def main():
    #Carrega o modelo
    if model is not None:
        nlp = spacy.load(model)
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('pt')

    #Seta o Pipeline
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)
    else:
        ner = nlp.get_pipe('ner')

    #Seta as entidades
    for LABEL in label_:
        ner.add_label(LABEL)

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        optimizer = nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in tqdm(TRAIN_DATA):
                nlp.update([text], [annotations], sgd=optimizer, drop=0.5,
                           losses=losses)
            print(losses)

    # #testa treino
    # test_text = 'ola quero uma pizza de queijo'
    # doc = nlp(test_text)
    # print("Entities in '%s'" % test_text)
    # for ent in doc.ents:
    #     print(ent.label_, ent.text)

    #salva o modelo
    nlp.to_disk(saida)
    print("Saved model to", saida)


main()