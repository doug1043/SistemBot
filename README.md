# SistemBot

Projeto de desenvolvimento de um ChatBot para atendimento automatizado em pizzarias, utilizando ferramentas de processamento de Linguagem Natural, reconhecimento de padrões, e a API de BOTs do Telegram. 

O projeto implementa técnicas de reconhecimento de padrões para o processamento
e classificação das mensagens, visando assim auxiliar pizzarias nos atendimentos e questões
referentes a dúvidas dos clientes.

## Instalação

Use o gerenciador de pacotes [pip](https://pip.pypa.io/en/stable/) para instalar as ferramentas.

```bash
pip install tqdm
pip install python_telegram_bot
pip install numpy
pip install plac
pip install spacy
pip install scikit-learn
pip install telegram
```

Mais informações para instalação e documentação do processamento de linguagem disponível no site [spaCy](https://spacy.io/usage)

## Executando projeto
Primeiro acesso o arquivo de configuração para definir o nome e TOKEN do bot criado via plataforma de criação de BOTs [Telegram](https://core.telegram.org/bots/api).

```python
#config.py

import cProfile
import telegram

bot_token = "Seu Token"

bot_user_name = "nome do bot"

TOKEN = bot_token

bot = telegram.Bot(token=TOKEN)

nlp = {}

nlp["dic"] = '.../SistemBot/NLP' #localização da pasta NLP
```
#
Agora execute o arquivo mentor.py:

```
python3 mentor.py
```
## Em funcionamento:

  ![Cardapio](https://github.com/doug1043/SistemBot/blob/master/testes/cardapio.png?raw="true")   ![Confirmar](https://github.com/doug1043/SistemBot/blob/master/testes/confirma.png?raw="true")
#
  ![Finalizar](https://github.com/doug1043/SistemBot/blob/master/testes/finalizado.png?raw="true")   ![Pedindo](https://github.com/doug1043/SistemBot/blob/master/testes/pedidopizza.png?raw="true")


## Contribuindo
Solicitações pull são bem-vindas!

## Licença
[MIT](https://choosealicense.com/licenses/mit/)
