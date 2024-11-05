import re
from collections import defaultdict

class SimpleChatbot:
    def __init__(self):
        # Voorgedefinieerde antwoorden op basis van sleutelwoorden
        self.responses = {
            r'hallo|hi|hey': [
                'Hallo! Hoe kan ik je helpen?',
                'Hoi! Waar kan ik je mee helpen?'
            ],
            r'weer|temperatuur': [
                'Ik kan helaas geen real-time weerinformatie geven.',
                'Voor het weer kun je beter een weer-app gebruiken.'
            ],
            r'hoe gaat het|hoe is het': [
                'Met mij gaat het goed! Hoe kan ik je helpen?',
                'Prima, dank je! Waar kan ik je mee helpen?'
            ],
            r'bedankt|dankjewel': [
                'Graag gedaan!',
                'Geen probleem, ik help je graag!'
            ]
        }
        
        # Opslag voor context en gebruikersvoorkeuren
        self.context = defaultdict(str)
        
    def process_input(self, user_input):
        """Verwerk gebruikersinput en geef een passend antwoord terug"""
        # Converteer input naar kleine letters voor betere matching
        user_input = user_input.lower()
        
        # Zoek naar matches in de voorgedefinieerde antwoorden
        for pattern, answers in self.responses.items():
            if re.search(pattern, user_input):
                # Kies een willekeurig antwoord uit de mogelijke antwoorden
                return random.choice(answers)
        
        # Als er geen match is gevonden
        return "Sorry, ik begrijp niet helemaal wat je bedoelt. Kun je het anders formuleren?"
    
    def learn_from_interaction(self, user_input, context):
        """Voeg nieuwe context toe aan het geheugen"""
        # Hier kun je logica toevoegen om te leren van interacties
        self.context[user_input] = context
    
    def get_context(self, user_input):
        """Haal relevante context op voor de huidige interactie"""
        return self.context.get(user_input, "")

# Voorbeeld gebruik
if __name__ == "__main__":
    import random
    
    chatbot = SimpleChatbot()
    
    print("Chatbot: Hallo! Ik ben een eenvoudige chatbot. Type 'stop' om te stoppen.")
    
    while True:
        user_input = input("Jij: ")
        
        if user_input.lower() == 'stop':
            print("Chatbot: Tot ziens!")
            break
            
        response = chatbot.process_input(user_input)
        print(f"Chatbot: {response}")