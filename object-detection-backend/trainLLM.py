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
           ("telefoon", "mobile-phone"),
("telefoon", "mobile-phone"),
("telefoon", "mobile-phone"),
("mobiel", "mobile-phone"),
("telefoon", "mobile-phone"),
("mobiel", "mobile-phone"),
("smartphone", "mobile-phone"),
("gsm", "mobile-phone"),
("iPhone", "mobile-phone"),

("Mijn telefoon heeft onlangs een update gekregen.", "mobile-phone"),  
("De batterij van mijn telefoon is bijna leeg.", "mobile-phone"),  
("Ik gebruik mijn telefoon voor werk en privé.", "mobile-phone"),  
("Mijn mobiel is van het nieuwste model.", "mobile-phone"),  
("Ik kan mijn telefoon nergens vinden.", "mobile-phone"),  
("Mijn mobiel is altijd bij me.", "mobile-phone"),  
("Mijn smartphone herkent nu gezichten.", "mobile-phone"),  
("Mijn gsm moet opgeladen worden.", "mobile-phone"),  
("De nieuwe iPhone heeft een betere camera.", "mobile-phone"),  
("Mijn telefoon speelt muziek draadloos af.", "mobile-phone"),  
("Mijn mobiel heeft veel apps.", "mobile-phone"),  
("Ik kan de route niet vinden zonder mijn telefoon.", "mobile-phone"),  
("Mijn smartphone heeft een groter scherm.", "mobile-phone"),  
("De camera van mijn gsm is uitstekend.", "mobile-phone"),  
("De nieuwe iPhone is sneller.", "mobile-phone"),  
("Mijn telefoon geeft 's nachts geen meldingen.", "mobile-phone"),  
("Mijn mobiel heeft veel opslagruimte.", "mobile-phone"),  
("Mijn telefoon gebruikt de bankapp dagelijks.", "mobile-phone"),  
("Mijn smartphone heeft een langere batterijduur.", "mobile-phone"),  
("Ik heb mijn gsm verloren tijdens het winkelen.", "mobile-phone"),  
("Mijn telefoon is gloednieuw.", "mobile-phone"),  
("Ik heb mijn telefoon vergeten thuis.", "mobile-phone"),  
("Mijn telefoon werkt niet meer goed.", "mobile-phone"),  
("De batterij van mijn telefoon is bijna leeg.", "mobile-phone"),  
("Mijn telefoon maakt mooie foto's.", "mobile-phone"),  
("Ik heb mijn telefoon per ongeluk laten vallen.", "mobile-phone"),  
("De telefoon van mijn zus is kapot.", "mobile-phone"),  
("Ik moet mijn telefoon opladen.", "mobile-phone"),  
("De telefoon is niet te vinden.", "mobile-phone"),  
("Mijn telefoon heeft geen signaal.", "mobile-phone"),  
("De telefoon is dringend nodig.", "mobile-phone"),  
("Mijn telefoon is heel belangrijk voor mijn werk.", "mobile-phone"),  
("Ik belde hem met mijn telefoon.", "mobile-phone"),  
("Mijn telefoon heeft veel opslagruimte.", "mobile-phone"),  
("De telefoon werkt perfect na de reparatie.", "mobile-phone"),  
("Mijn telefoon heeft een update nodig.", "mobile-phone"),  
("Mijn telefoon kan niet meer opgeladen worden.", "mobile-phone"),  
("De telefoon heeft een nieuwe lader nodig.", "mobile-phone"),  
("Ik wil een nieuwe telefoon kopen.", "mobile-phone"),  
("De telefoon was te duur voor mij.", "mobile-phone"),

("horloge", "watch"),
("horloge", "watch"),
("horloge", "watch"),
("polshorloge", "watch"),
("horloge", "watch"),
("polshorloge", "watch"),
("apple watch", "watch"),
("digitaal horloge", "watch"),
("apple watch", "watch"),

("Mijn horloge is kapot gegaan.", "watch"),  
("Ik draag altijd mijn horloge.", "watch"),  
("Dit horloge is heel duur.", "watch"),  
("Mijn polshorloge is van zilver.", "watch"),  
("Ik heb een nieuw horloge gekocht.", "watch"),  
("Mijn polshorloge is waterdicht.", "watch"),  
("De Apple Watch heeft veel functies.", "watch"),  
("Ik heb een digitaal horloge gekregen.", "watch"),  
("De Apple Watch is heel populair.", "watch"),  
("Mijn horloge is vertraagd.", "watch"),  
("Het horloge heeft een leren band.", "watch"),  
("Mijn polshorloge is heel comfortabel.", "watch"),  
("Mijn horloge geeft de tijd nauwkeurig weer.", "watch"),  
("De Apple Watch heeft een fitness-tracker.", "watch"),  
("Mijn horloge heeft een digitale klok.", "watch"),  
("Mijn polshorloge heeft een zwarte wijzerplaat.", "watch"),  
("De Apple Watch kan mijn hartslag meten.", "watch"),  
("Dit horloge heeft een metalen band.", "watch"),  
("Ik heb mijn horloge voor mijn verjaardag gekregen.", "watch"),  
("Het horloge is van uitstekende kwaliteit.", "watch"),  
("Mijn horloge heeft geen batterij meer.", "watch"),  
("Het polshorloge is geschikt voor sport.", "watch"),  
("De Apple Watch heeft een prachtig scherm.", "watch"),  
("Ik draag altijd mijn horloge als ik uit ga.", "watch"),  
("Mijn horloge heeft een alarmfunctie.", "watch"),  
("Het digitaal horloge is eenvoudig te gebruiken.", "watch"),  
("Mijn horloge is een erfstuk.", "watch"),  
("Dit polshorloge is mijn favoriete accessoire.", "watch"),  
("De Apple Watch heeft veel apps.", "watch"),  
("Ik kijk vaak op mijn horloge voor de tijd.", "watch"),  
("Het horloge is licht van gewicht.", "watch"),  
("Mijn horloge is krasbestendig.", "watch"),  
("Ik heb mijn horloge verloren tijdens het sporten.", "watch"),  
("Mijn polshorloge heeft een chronograaf.", "watch"),  
("De Apple Watch heeft een GPS-functie.", "watch"),  
("Mijn horloge geeft de datum aan.", "watch"),  
("Ik heb mijn horloge als cadeau gekregen.", "watch"),  
("Het digitaal horloge heeft een retro stijl.", "watch"),  
("Mijn polshorloge is een limited edition.", "watch"),  
("Dit horloge heeft een luxe uitstraling.", "watch"),  

("bril", "glasses"),
("bril", "glasses"),
("bril", "glasses"),
("zonnebril", "glasses"),
("zonnebril", "glasses"),
("bril", "glasses"),
("zonnebril", "glasses"),
("leestekst bril", "glasses"),
("opvouwbare bril", "glasses"),

("Mijn bril is gisteren gebroken.", "glasses"),  
("Ik draag altijd mijn bril tijdens het lezen.", "glasses"),  
("Deze bril is erg comfortabel.", "glasses"),  
("Mijn zonnebril is perfect voor de zomer.", "glasses"),  
("Ik heb een nieuwe zonnebril gekocht.", "glasses"),  
("Mijn bril heeft een anti-reflex coating.", "glasses"),  
("Deze zonnebril beschermt tegen UV-stralen.", "glasses"),  
("De leestekst bril is ideaal voor dichtbij lezen.", "glasses"),  
("Mijn opvouwbare bril past gemakkelijk in mijn tas.", "glasses"),  
("Mijn bril is heel licht.", "glasses"),  
("Ik heb altijd mijn zonnebril bij me.", "glasses"),  
("Mijn bril heeft een moderne uitstraling.", "glasses"),  
("De zonnebril beschermt mijn ogen tegen de zon.", "glasses"),  
("Deze bril is speciaal gemaakt voor mijn ogen.", "glasses"),  
("Mijn opvouwbare bril is heel praktisch.", "glasses"),  
("Ik gebruik mijn leestekst bril voor kleine lettertjes.", "glasses"),  
("Mijn bril heeft een titanium frame.", "glasses"),  
("De zonnebril is mijn favoriete accessoire.", "glasses"),  
("Ik moet mijn bril schoonmaken.", "glasses"),  
("Deze bril heeft een mooi design.", "glasses"),  
("Mijn zonnebril is in de auto blijven liggen.", "glasses"),  
("Mijn bril heeft een blauwe lichtfilter.", "glasses"),  
("De leestekst bril helpt me met lezen.", "glasses"),  
("Mijn zonnebril is perfect voor het strand.", "glasses"),  
("Ik ben mijn bril thuis vergeten.", "glasses"),  
("Mijn opvouwbare bril is heel compact.", "glasses"),  
("Ik heb een nieuwe leesbril nodig.", "glasses"),  
("Mijn zonnebril heeft een spiegelende lens.", "glasses"),  
("Deze bril is speciaal voor sport.", "glasses"),  
("Mijn zonnebril is van hoge kwaliteit.", "glasses"),  
("Ik heb een bril met een sterkere sterkte.", "glasses"),  
("Mijn bril helpt me beter te zien.", "glasses"),  
("De zonnebril is perfect voor op vakantie.", "glasses"),  
("Mijn opvouwbare bril past in mijn zak.", "glasses"),  
("Ik heb mijn bril bij de opticien laten aanpassen.", "glasses"),  
("De zonnebril heeft een stijlvolle uitstraling.", "glasses"),  
("Mijn bril is erg handig voor dagelijks gebruik.", "glasses"),  
("Deze bril is erg scherp.", "glasses"),  
("Mijn opvouwbare bril is een handig reisaccessoire.", "glasses"),  

("portemonnee", "wallet"),
("portemonnee", "wallet"),
("geld", "wallet"),
("pinpas", "wallet"),
("geld", "wallet"),
("pinpas", "wallet"),
("portemonnee", "wallet"),
("geld", "wallet"),
("pinpas", "wallet"),
("geldbuidel", "wallet"),
("pinautomaat portemonnee", "wallet"),
("geldbeugel", "wallet"),
("portefeuille", "wallet"),


("Mijn portemonnee is verloren gegaan.", "wallet"),  
("Ik stop mijn pinpas altijd in mijn portemonnee.", "wallet"),  
("Ik heb niet genoeg geld in mijn portemonnee.", "wallet"),  
("Mijn pinpas is geblokkeerd.", "wallet"),  
("Er zit veel geld in mijn portemonnee.", "wallet"),  
("Mijn pinpas werkt niet bij deze pinautomaat.", "wallet"),  
("Ik heb mijn portemonnee bij de kassa vergeten.", "wallet"),  
("Ik heb te veel geld uit mijn portemonnee gehaald.", "wallet"),  
("Mijn pinpas is beschadigd.", "wallet"),  
("Mijn geldbeugel is nieuw.", "wallet"),  
("Ik heb mijn portemonnee bij de pinautomaat achtergelaten.", "wallet"),  
("Mijn geldbeugel heeft een klein vakje voor muntgeld.", "wallet"),  
("Mijn portefeuille is vol met kaarten.", "wallet"),  
("Er zit geen geld meer in mijn portemonnee.", "wallet"),  
("Mijn pinpas past perfect in mijn portemonnee.", "wallet"),  
("Mijn portemonnee is van leer.", "wallet"),  
("Ik heb geen geld meer in mijn portemonnee.", "wallet"),  
("Mijn portemonnee is gestolen.", "wallet"),  
("Mijn geldbeugel is te groot voor mijn tas.", "wallet"),  
("Ik stop altijd mijn pinpas in mijn portemonnee.", "wallet"),  
("Mijn portefeuille heeft een rits.", "wallet"),  
("Mijn portemonnee is te dik geworden.", "wallet"),  
("Ik ben mijn geld in mijn portemonnee kwijt.", "wallet"),  
("De pinpas werkt niet in de winkel.", "wallet"),  
("Mijn portemonnee is van een goed merk.", "wallet"),  
("Ik heb mijn pinpas in mijn portemonnee gestopt.", "wallet"),  
("Mijn geldbeugel is in de auto blijven liggen.", "wallet"),  
("Mijn portemonnee is uit mijn tas gevallen.", "wallet"),  
("Ik heb te weinig geld in mijn portemonnee voor deze aankoop.", "wallet"),  
("Mijn portemonnee is van een dure stof.", "wallet"),  
("Ik heb mijn portemonnee gevonden in mijn tas.", "wallet"),  
("Mijn pinpas is vernieuwd.", "wallet"),  
("Mijn portemonnee is een beetje te groot.", "wallet"),  
("Mijn geldbeugel is gevuld met kleingeld.", "wallet"),  
("Mijn portefeuille heeft veel vakken.", "wallet"),  
("Ik heb mijn portemonnee niet bij me.", "wallet"),  
("De pinpas is niet geactiveerd.", "wallet"),  
("Mijn portemonnee is leeg.", "wallet"),  
("Mijn portemonnee zit vol met pasjes.", "wallet"),  
("Ik heb te veel geld in mijn portemonnee gestopt.", "wallet"),  
("Mijn geldbeugel heeft een leren afwerking.", "wallet"),  


("pen", "pen"),
("pen", "pen"),
("balpen", "pen"),
("vulpen", "pen"),
("stift", "pen"),
("pen", "pen"),
("balpen", "pen"),
("vulpen", "pen"),
("stift", "pen"),

("Mijn pen schrijft niet meer.", "pen"),  
("Ik gebruik altijd een pen voor mijn aantekeningen.", "pen"),  
("Deze balpen schrijft heel soepel.", "pen"),  
("Mijn vulpen is kapot.", "pen"),  
("Ik gebruik een stift voor markeren.", "pen"),  
("Deze pen heeft een mooie kleur.", "pen"),  
("De balpen is uitgedroogd.", "pen"),  
("Mijn vulpen schrijft beter dan mijn balpen.", "pen"),  
("De stift is perfect voor het tekenen.", "pen"),  
("Deze pen is van een duur merk.", "pen"),  
("Mijn pen is verdwenen.", "pen"),  
("De balpen ligt op mijn bureau.", "pen"),  
("Ik heb mijn vulpen gisteren verloren.", "pen"),  
("De stift heeft een brede punt.", "pen"),  
("Mijn pen heeft een blauwe inkt.", "pen"),  
("Ik schrijf altijd met een pen.", "pen"),  
("Deze balpen is niet geschikt voor schrijven op plastic.", "pen"),  
("Mijn vulpen heeft een gouden dop.", "pen"),  
("De stift heeft een watervaste inkt.", "pen"),  
("Deze pen is perfect voor het ondertekenen van documenten.", "pen"),  
("Ik heb mijn balpen per ongeluk laten vallen.", "pen"),  
("De vulpen is erg zwaar.", "pen"),  
("Mijn stift is bijna leeg.", "pen"),  
("Ik heb een nieuwe pen gekocht.", "pen"),  
("Deze balpen werkt niet goed op glad papier.", "pen"),  
("De vulpen glijdt soepel over het papier.", "pen"),  
("Mijn stift schrijft in felle kleuren.", "pen"),  
("Mijn pen is leeg.", "pen"),  
("De balpen schrijft in zwart.", "pen"),  
("Mijn vulpen heeft geen inkt meer.", "pen"),  
("De stift heeft een dikke punt.", "pen"),  
("Ik heb een pen nodig voor de vergadering.", "pen"),  
("Mijn balpen schrijft sneller dan de vulpen.", "pen"),  
("Deze vulpen is heel duur.", "pen"),  
("Ik gebruik de stift om te tekenen.", "pen"),  
("Mijn pen is verdwenen uit mijn tas.", "pen"),  
("Ik heb een balpen in mijn tas.", "pen"),  
("Deze vulpen is van de beste kwaliteit.", "pen"),  
("Mijn stift is uitgedroogd.", "pen"),  
("Ik heb een pen met een comfortabele grip.", "pen"),  

("auto", "car-key"),
("auto", "car-key"),
("auto", "car-key"),
("auto", "car-key"),
("auto", "car-key"),
("autosleutel", "car-key"),
("auto sleutel", "car-key"),
("sleutel van de auto", "car-key"),
("autosleutels", "car-key"),

("Ik heb de auto sleutel niet gevonden.", "car-key"),  
("Mijn auto sleutel zit in mijn tas.", "car-key"),  
("De auto sleutel werkt niet goed.", "car-key"),  
("Heb je de sleutel van de auto gezien?", "car-key"),  
("De auto sleutel is op de tafel blijven liggen.", "car-key"),  
("Mijn autosleutel is beschadigd.", "car-key"),  
("Ik heb de auto sleutel in de kast gelegd.", "car-key"),  
("De auto sleutel is moeilijk te vinden.", "car-key"),  
("Mijn auto sleutel is gisteren kwijtgeraakt.", "car-key"),  
("Ik heb mijn autosleutels in mijn zak.", "car-key"),  
("De sleutel van de auto is nog niet terug.", "car-key"),  
("Ik zoek de sleutel van mijn auto.", "car-key"),  
("Heb je de autosleutels gezien?", "car-key"),  
("Mijn auto sleutel is verloren gegaan.", "car-key"),  
("Ik gebruik altijd de autosleutel om de auto te openen.", "car-key"),  
("De auto sleutel past niet meer in het slot.", "car-key"),  
("Ik heb de sleutel van de auto bij de deur laten liggen.", "car-key"),  
("Mijn auto sleutel is niet teruggevonden.", "car-key"),  
("De sleutel van de auto is kapot.", "car-key"),  
("De autosleutels liggen op het bureau.", "car-key"),  
("Ik heb de sleutel van mijn auto in mijn handtas.", "car-key"),  
("De auto sleutel zit vast in het slot.", "car-key"),  
("Mijn autosleutels zijn gestolen.", "car-key"),  
("Heb je de autosleutels al teruggegeven?", "car-key"),  
("Mijn auto sleutel is per ongeluk in de regen gevallen.", "car-key"),  
("De sleutel van de auto is op de grond gevallen.", "car-key"),  
("Ik heb mijn auto sleutel dubbel gecontroleerd.", "car-key"),  
("Mijn autosleutel is niet meer bruikbaar.", "car-key"),  
("De auto sleutel is per ongeluk gebroken.", "car-key"),  
("Ik heb mijn autosleutel veilig opgeborgen.", "car-key"),  
("De sleutel van mijn auto is in mijn zak.", "car-key"),  
("Ik moet de auto sleutel in de tas stoppen.", "car-key"),  
("Mijn autosleutel werkt niet meer goed.", "car-key"),  
("De auto sleutel is altijd makkelijk te vinden.", "car-key"),  
("Ik heb de autosleutel in de auto laten zitten.", "car-key"),  
("De sleutel van de auto valt niet goed in het slot.", "car-key"),  
("Mijn auto sleutel is gevallen.", "car-key"),  
("De sleutel van de auto is moeilijk te draaien.", "car-key"),  

("kam", "comb"),
("haarkam", "comb"),
("borstel", "comb"),
("haarborstel", "comb"),
("kam", "comb"),
("haarkam", "comb"),
("borstel", "comb"),
("haarborstel", "comb"),
("kam", "comb"),
("haarkam", "comb"),
("haarborstel", "comb"),


("Mijn kam is in de badkamer.", "comb"),  
("Ik gebruik een haarkam voor mijn haar.", "comb"),  
("De borstel ligt op de tafel.", "comb"),  
("Ik heb mijn haarborstel niet kunnen vinden.", "comb"),  
("Deze kam is erg oud.", "comb"),  
("Mijn haarkam is van plastic.", "comb"),  
("De borstel is te groot voor mijn tas.", "comb"),  
("Mijn haarborstel heeft zachte borstelharen.", "comb"),  
("Ik gebruik de kam elke ochtend.", "comb"),  
("De haarkam is nieuw en stevig.", "comb"),  
("De haarborstel is perfect voor lang haar.", "comb"),  
("Mijn kam heeft scherpe tanden.", "comb"),  
("De haarkam is ideaal voor nat haar.", "comb"),  
("De borstel is geschikt voor alle haartypes.", "comb"),  
("Mijn haarborstel is van hoge kwaliteit.", "comb"),  
("Ik heb mijn kam per ongeluk laten vallen.", "comb"),  
("De haarkam zit vast in mijn tas.", "comb"),  
("De haarborstel is te groot voor mijn tas.", "comb"),  
("Deze kam gebruik ik voor mijn kinderen.", "comb"),  
("De haarkam is makkelijk schoon te maken.", "comb"),  
("Mijn haarborstel heeft een houten handvat.", "comb"),  
("De kam past perfect in mijn make-uptas.", "comb"),  
("Ik zoek mijn haarkam.", "comb"),  
("De borstel is geschikt voor natte haren.", "comb"),  
("De haarborstel is gebroken.", "comb"),  
("De kam is nog steeds in goede staat.", "comb"),  
("Mijn haarkam is met de hand gemaakt.", "comb"),  
("Ik gebruik een haarborstel voor mijn gekrulde haar.", "comb"),  
("Mijn kam is vergeten op de badkamerplank.", "comb"),  
("De haarkam is ideaal voor fijn haar.", "comb"),  
("De haarborstel heeft zachte, flexibele borstelharen.", "comb"),  
("Mijn kam is overal mee naartoe genomen.", "comb"),  
("De haarkam heeft een uniek design.", "comb"),  
("De haarborstel is zacht voor de hoofdhuid.", "comb"),  
("Mijn kam is verdwenen in de wasmand.", "comb"),  
("De haarkam heeft lange, flexibele tanden.", "comb"),  
("De haarborstel is perfect voor dagelijks gebruik.", "comb"),  


("sleutels", "keys"),
("sleutel", "keys"),
("sleutels", "keys"),
("sleutels", "keys"),
("sleutels", "keys"),
("sleutels", "keys"),
("sleutel", "keys"),
("sleutelbos", "keys"),
("huissleutels", "keys"),


("Mijn sleutels liggen op de tafel.", "keys"),  
("Ik heb mijn sleutel vergeten.", "keys"),  
("De sleutels zijn verloren gegaan.", "keys"),  
("Heb je mijn sleutels gezien?", "keys"),  
("De sleutels zitten in mijn tas.", "keys"),  
("De sleutels rinkelden in mijn zak.", "keys"),  
("Waar is mijn sleutel?", "keys"),  
("Mijn sleutelbos is erg zwaar.", "keys"),  
("Ik ben mijn huissleutels kwijt.", "keys"),  
("De sleutels zitten in de deur.", "keys"),  
("Mijn sleutels zijn niet te vinden.", "keys"),  
("Ik heb de sleutel van de auto gevonden.", "keys"),  
("De sleutels passen niet in het slot.", "keys"),  
("Mijn sleutelbos heeft te veel sleutels.", "keys"),  
("De huissleutels zitten op de kast.", "keys"),  
("Mijn sleutels liggen op de gang.", "keys"),  
("Heb je de sleutels voor de auto?", "keys"),  
("Mijn sleutelbos is aan mijn tas bevestigd.", "keys"),  
("De huissleutels zitten in mijn jaszak.", "keys"),  
("Ik heb de sleutel van de fietsenstalling.", "keys"),  
("De sleutels zijn gevallen op de grond.", "keys"),  
("Ik heb de sleutels van het kantoor nodig.", "keys"),  
("Mijn sleutels hangen aan de haak.", "keys"),  
("De sleutels passen perfect in mijn zak.", "keys"),  
("De sleutelbos is in mijn tas gestopt.", "keys"),  
("Mijn sleutels zijn niet meer daar.", "keys"),  
("De huissleutels liggen op de salontafel.", "keys"),  
("De sleutels zijn snel te vinden.", "keys"),  
("De sleutel van de brievenbus is verdwenen.", "keys"),  
("Mijn sleutels zijn niet meer bruikbaar.", "keys"),  
("De sleutels kunnen niet in het slot draaien.", "keys"),  
("De sleutelbos is een beetje roestig.", "keys"),  
("Ik zoek de sleutels van de garage.", "keys"),  
("Mijn sleutels zijn veilig opgeborgen.", "keys"),  
("De sleutels zitten in mijn broekzak.", "keys"),  
("Ik heb mijn sleutels dubbel gecontroleerd.", "keys"),  
("De huissleutels zijn al in mijn handen.", "keys"),  
("Mijn sleutelbos is kwijtgeraakt.", "keys"),  
("De sleutels hangen aan de deurknop.", "keys"),


("iPhone", "mobile-phone"),
("horloge", "watch"),
("horloge", "watch"),
("horloge", "watch"),
("polshorloge", "watch"),
("horloge", "watch"),
("polshorloge", "watch"),
("apple watch", "watch"),
("digitaal horloge", "watch"),
("apple watch", "watch"),

("bril", "glasses"),
("bril", "glasses"),
("bril", "glasses"),
("zonnebril", "glasses"),
("zonnebril", "glasses"),
("bril", "glasses"),
("zonnebril", "glasses"),
("leestekst bril", "glasses"),
("opvouwbare bril", "glasses"),

("portemonnee", "wallet"),
("portemonnee", "wallet"),
("geld", "wallet"),
("pinpas", "wallet"),
("geld", "wallet"),
("pinpas", "wallet"),
("portemonnee", "wallet"),
("geld", "wallet"),
("pinpas", "wallet"),
("geldbuidel", "wallet"),
("pinautomaat portemonnee", "wallet"),
("geldbeugel", "wallet"),
("portefeuille", "wallet"),

("pen", "pen"),
("pen", "pen"),
("balpen", "pen"),
("vulpen", "pen"),
("stift", "pen"),
("pen", "pen"),
("balpen", "pen"),
("vulpen", "pen"),
("stift", "pen"),

("auto", "car-key"),
("auto", "car-key"),
("auto", "car-key"),
("auto", "car-key"),
("auto", "car-key"),
("autosleutel", "car-key"),
("auto sleutel", "car-key"),
("sleutel van de auto", "car-key"),
("autosleutels", "car-key"),

("kam", "comb"),
("haarkam", "comb"),
("borstel", "comb"),
("haarborstel", "comb"),
("kam", "comb"),
("haarkam", "comb"),
("borstel", "comb"),
("haarborstel", "comb"),
("kam", "comb"),
("haarkam", "comb"),
("haarborstel", "comb"),

("sleutels", "keys"),
("sleutel", "keys"),
("sleutels", "keys"),
("sleutels", "keys"),
("sleutels", "keys"),
("sleutels", "keys"),
("sleutel", "keys"),
("sleutelbos", "keys"),
("huissleutels", "keys"),


("iPhone", "mobile-phone"),

("horloge", "watch"),
("horloge", "watch"),
("horloge", "watch"),
("polshorloge", "watch"),
("horloge", "watch"),
("polshorloge", "watch"),
("apple watch", "watch"),
("digitaal horloge", "watch"),
("apple watch", "watch"),

("bril", "glasses"),
("bril", "glasses"),
("bril", "glasses"),
("zonnebril", "glasses"),
("zonnebril", "glasses"),
("bril", "glasses"),
("zonnebril", "glasses"),
("leestekst bril", "glasses"),
("opvouwbare bril", "glasses"),

("portemonnee", "wallet"),
("portemonnee", "wallet"),
("geld", "wallet"),
("pinpas", "wallet"),
("geld", "wallet"),
("pinpas", "wallet"),
("portemonnee", "wallet"),
("geld", "wallet"),
("pinpas", "wallet"),
("geldbuidel", "wallet"),
("pinautomaat portemonnee", "wallet"),
("geldbeugel", "wallet"),
("portefeuille", "wallet"),

("pen", "pen"),
("pen", "pen"),
("balpen", "pen"),
("vulpen", "pen"),
("stift", "pen"),
("pen", "pen"),
("balpen", "pen"),
("vulpen", "pen"),
("stift", "pen"),

("auto", "car-key"),
("auto", "car-key"),
("auto", "car-key"),
("auto", "car-key"),
("auto", "car-key"),
("autosleutel", "car-key"),
("auto sleutel", "car-key"),
("sleutel van de auto", "car-key"),
("autosleutels", "car-key"),

("kam", "comb"),
("haarkam", "comb"),
("borstel", "comb"),
("haarborstel", "comb"),
("kam", "comb"),
("haarkam", "comb"),
("borstel", "comb"),
("haarborstel", "comb"),
("kam", "comb"),
("haarkam", "comb"),
("haarborstel", "comb"),

("sleutels", "keys"),
("sleutel", "keys"),
("sleutels", "keys"),
("sleutels", "keys"),
("sleutels", "keys"),
("sleutels", "keys"),
("sleutel", "keys"),
("sleutelbos", "keys"),
("huissleutels", "keys"),


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