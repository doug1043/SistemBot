import spacy

nlp = spacy.load('teste2')

#Promove testes com dados aprendidos 
test_text = 'grandes'
doc = nlp(test_text)
print("Entities in '%s'" % test_text)
for ent in doc.ents:
    print(ent.label_, ent.text)
