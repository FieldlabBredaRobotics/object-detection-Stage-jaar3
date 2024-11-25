import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import nltk
import re
import joblib
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


class ProductClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.classifier = RandomForestClassifier()
        self.lemmatizer = WordNetLemmatizer()

        # Download benodigde NLTK data
        # nltk.download('punkt')
        # nltk.download('stopwords')
        # nltk.download('wordnet')

        # Definieer stopwoorden
        self.stop_words = set(stopwords.words('dutch'))

        # Product klassen
        self.classes = ['car-key', 'wallet', 'carkeys', 'comb', 'glasses', 
                       'keys', 'mobile-phone', 'pen', 'watch']
        
        # Pad naar het opgeslagen modelbestand
        self.model_path = 'tekstAI.pkl'  #pad aanpassen zo nodg
        

    def preprocess_text(self, text):
        # Tekst naar kleine letters
        text = text.lower()

        # Verwijder speciale karakters
        text = re.sub(r'[^\w\s]', '', text)

        # Tokenization
        tokens = word_tokenize(text)

        # Verwijder stopwoorden en lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words]

        return ' '.join(tokens)

    def prepare_training_data(self):
        # Voorbeeld training data
        training_data = [
            # Directe benamingen (synoniemen)
            ("telefoon", "mobile-phone"),
            ("mobiel", "mobile-phone"),
            ("smartphone", "mobile-phone"),
            ("gsm", "mobile-phone"),
            ("handy", "mobile-phone"),
            ("iPhone", "mobile-phone"),
            ("horloge", "watch"),
            ("polshorloge", "watch"),
            ("digitaal horloge", "watch"),
            ("bril", "glasses"),
            ("zonnebril", "glasses"),
            ("leestekst bril", "glasses"),
            ("opvouwbare bril", "glasses"),
            ("portemonnee", "wallet"),
            ("portemonee", "wallet"),
            ("geldbuidel", "wallet"),
            ("pinautomaat portemonnee", "wallet"),
            ("pen", "pen"),
            ("balpen", "pen"),
            ("vulpen", "pen"),
            ("stift", "pen"),
            ("autosleutel", "car-key"),
            ("auto sleutel", "car-key"),
            ("sleutel van de auto", "car-key"),
            ("autosleutels", "car-key"),
            ("kam", "comb"),
            ("haarkam", "comb"),
            ("borstel", "comb"),
            
            # Beschrijvingen van objecten
            ("iets om de tijd te zien", "watch"),
            ("apparaat om mee te bellen", "mobile-phone"),
            ("ding om mee te schrijven", "pen"),
            ("iets om je haar mee te kammen", "comb"),
            ("iets om beter te kunnen zien", "glasses"),
            ("ding om de auto mee te starten", "car-key"),
            ("waar ik mijn geld in bewaar", "wallet"),
            
            # Meer variaties in zinsstructuren
            ("de mobiel ligt op de tafel", "mobile-phone"),
            ("heb je mijn smartphone gezien?", "mobile-phone"),
            ("deze pen schrijft geweldig", "pen"),
            ("ik heb een nieuwe portemonnee gekocht", "wallet"),
            ("ik heb mijn bril vergeten", "glasses"),
            ("de autosleutels liggen op de salontafel", "car-key"),
            ("kun je het horloge voor me halen?", "watch"),
            ("de kam ligt op het nachtkastje", "comb"),
            
            # Complexe zinnen met meerdere objecten
            ("Ik zoek mijn mobiele telefoon en portemonnee", "mobile-phone"),
            ("Mijn horloge en bril zijn beide kapot", "watch"),
            ("Ik heb mijn pen en portemonnee verloren", "pen"),
            ("De autosleutels liggen op de tafel en mijn bril is daar ook", "car-key"),
            ("Ik kan mijn smartphone en bril niet vinden", "mobile-phone"),
            ("Kun je mijn kam en portemonnee aan mij geven?", "comb"),
            
            # Gecombineerde objecten
            ("Ik heb zowel mijn mobiel als mijn autosleutels verloren", "mobile-phone"),
            ("Mijn horloge is stuk, maar ik heb mijn bril wel gevonden", "watch"),
            ("Kun je mijn portemonnee en sleutels pakken?", "wallet"),
            ("De pen en het horloge liggen samen op de tafel", "pen"),
            
            # Met spelfouten
            ("telefon", "mobile-phone"),
            ("horloge", "watch"),
            ("portemonee", "wallet"),
            ("brill", "glasses"),
            ("sleutels van de auto", "car-key"),
            ("smartfon", "mobile-phone"),
            ("horloje", "watch"),
            ("pens", "pen"),
            ("sleutel van de auto", "car-key"),
            ("kom", "comb"),

            # Slang en informele taal
            ("heb je mijn mobieltje gezien?", "mobile-phone"),
            ("is mijn gsm ergens?", "mobile-phone"),
            ("waar is mijn watch?", "watch"),
            ("ik heb een bril nodig", "glasses"),
            ("mijn portemonee is weg", "wallet"),
            ("heeft iemand mijn autosleutels gezien?", "car-key"),
            ("ik heb een nieuwe balpen gekocht", "pen"),
            
            # Nieuwe objecten en hun beschrijvingen
            ("een oplader voor mijn telefoon", "mobile-phone"),
            ("een batterij voor mijn horloge", "watch"),
            ("een zonnebril om in de zomer te dragen", "glasses"),
            ("een leren portemonnee", "wallet"),
            ("een goedkope plastic pen", "pen"),
            ("een sleutel van mijn auto", "car-key"),
            ("een houten kam voor mijn haar", "comb"),
            
            # Meerdere zinnen in één beschrijving
            ("Mijn gsm ligt op de salontafel en mijn bril is in de keuken", "mobile-phone"),
            ("De pen en het horloge zijn samen in mijn tas", "pen"),
            ("De autosleutels en het kam liggen in mijn tas", "car-key"),
            ("Ik zoek zowel mijn zonnebril als mijn portemonnee", "glasses"),
            
            # Variaties in vraagstellingen
            ("Waar is mijn telefoon?", "mobile-phone"),
            ("Kun je mijn horloge vinden?", "watch"),
            ("Heb je mijn portemonnee gezien?", "wallet"),
            ("Waar liggen mijn sleutels?", "car-key"),
            ("Heb je de pen voor me?", "pen"),
            ("Waar is mijn kam?", "comb"),
            
            # Vertalingen en alternatieve woorden
            ("Waar is mijn cell phone?", "mobile-phone"),  
            ("I can't find my wallet", "wallet"),  
            ("My pen is gone", "pen"),  
            ("Do you have my keys?", "car-key"),  
            ("It's my wrist watch", "watch"), 
            ("I need my glasses", "glasses"),  
            ("I have lost my comb", "comb")  
        ]
        texts, labels = zip(*training_data)
        texts = [self.preprocess_text(text) for text in texts]
        return texts, labels

    def train(self):
        # Bereid data voor
        texts, labels = self.prepare_training_data()

        # Vectorize de tekst
        X = self.vectorizer.fit_transform(texts)

        # Train de classifier
        self.classifier.fit(X, labels)

        # Sla het model op
        joblib.dump((self.vectorizer, self.classifier), self.model_path)
        print("Model is getraind en opgeslagen.")

    def load_model(self):
        # Kijk of het model al bestaat
        if os.path.exists(self.model_path):
            self.vectorizer, self.classifier = joblib.load(self.model_path)
            print("Model is geladen.")
        else:
            print("Model bestaat niet, het moet eerst worden getraind.")

    def predict(self, text):
        # Verwerk de tekst
        text = self.preprocess_text(text)
        text_vectorized = self.vectorizer.transform([text])

        # Voorspel de klasse
        prediction = self.classifier.predict(text_vectorized)
        return prediction[0]


# Voorbeeld gebruik
classifier = ProductClassifier()
classifier.load_model()  # Laad het model als het bestaat

# Als het model nog niet is geladen, train het dan en sla het op
if not os.path.exists(classifier.model_path):
    classifier.train()

# Test de voorspellingen
test_text = "Ik heb mijn portemonnee verloren"
prediction = classifier.predict(test_text)
print(f"Voorspelling: {prediction}")

# Sla het model op
# joblib.dump(classifier, 'tekstAI.pkl')
##joblib.dump((classifier.vectorizer, classifier.classifier), 'tekstAI.pkl')

# # Laad het model weer in een andere sessie
# model = joblib.load('tekstAI.pkl')