from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.conversation import Statement

chatbot = ChatBot(
    "MyBot",
    database_uri='sqlite:///db.sqlite3',
    
    preprocessors=[
        'chatterbot.preprocessors.clean_whitespace',
        
    ]
)

trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("backend/src/my_corpus.yml")

def get_bot_response(user_input: str) -> str:
    print("Chatbot is ready to chat!")
    print("Type 'quit' to stop.")
    response = chatbot.get_response(user_input)
    return str(response)
