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
        self.model_path = 'tekstAI.pkl'

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
        training_data = []
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