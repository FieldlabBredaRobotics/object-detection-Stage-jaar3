from flask import Flask, Response, render_template, jsonify, request
import cv2
from ultralytics import YOLO
import threading
import queue
import time
import numpy as np
import os
import joblib
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet as wn
from nltk.stem import WordNetLemmatizer
import spacy
from trainLLM import ProductClassifier
import nltk
from synonyms import synonyms

app = Flask(__name__)

# Global variables
camera = None
output_frame = None
lock = threading.Lock()
detection_running = False
frame_queue = queue.Queue(maxsize=10)
yolo_model = None
target_object = None
text_classifier = None
nlp = spacy.load("nl_core_news_sm")

# # Initialize NLTK resources
# def init_nltk():
#     try:
#         nltk.download('punkt')
#         nltk.download('stopwords')
#         nltk.download('wordnet')
#         nltk.download('omw-1.4')
#     except Exception as e:
#         print(f"Warning: Could not download all NLTK resources: {e}")

# def get_synonyms(word):
#     try:
#         synonyms = set()
#         for syn in wn.synsets(word, lang='nld'):
#             for lemma in syn.lemmas('nld'):
#                 synonyms.add(lemma.name())
#         return list(synonyms)
#     except Exception as e:
#         print(f"Warning: Could not get synonyms: {e}")
#         return []  

# def get_synonyms(predicted_category):
#     if predicted_category in synonyms:
#         return [synonyms[predicted_category]]
#     else:
#         return []

# Import de synonyms dictionary uit je synonyms.py bestand
from synonyms import synonyms

def get_synonyms(user_input):
    # Maak een lege lijst voor synoniemen
    matched_classes = []
    
    # Zet de gebruikersinvoer om naar kleine letters om het case-insensitief te maken
    user_input = user_input.lower()
    
    # Doorloop alle synoniemen in de synonyms dictionary
    for key, value in synonyms.items():
        # Split de sleutel in woorden en controleer of een van deze woorden voorkomt in de gebruikersinvoer
        if any(word in user_input for word in key.split()):
            # Als een match wordt gevonden, voeg de klasse toe aan de matched_classes lijst
            matched_classes.append(value)
    
    # Als er synoniemen zijn gevonden, geef dan de bijbehorende klassen terug
    return matched_classes if matched_classes else []


def init_camera():
    global camera
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Could not open camera.")

def init_yolo_model():
    global yolo_model
    model_path = os.path.join('models', 'best (7).pt')
    if not os.path.exists(model_path):
        raise RuntimeError("YOLO model not found.")
    yolo_model = YOLO(model_path)
    print("Available object classes:")
    for idx, name in yolo_model.names.items():
        print(f"- {name}")

def init_text_classifier():
    global text_classifier
    model_path = os.path.join('models', 'tekstAI.pkl')
    if not os.path.exists(model_path):
        raise RuntimeError("Text classification model not found.")
    
    classifier_model = joblib.load(model_path)
    text_classifier = {
        "vectorizer": classifier_model.vectorizer,
        "classifier": classifier_model.classifier
    }

def preprocess_text(text):
    try:
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        tokens = word_tokenize(text)
        # Only use stopwords if available
        try:
            tokens = [token for token in tokens if token not in stopwords.words('dutch')]
        except:
            pass  # Skip stopwords removal if not available
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token) for token in tokens]
        return ' '.join(tokens)
    except Exception as e:
        print(f"Warning: Error in text preprocessing: {e}")
        return text  # Return original text if preprocessing fails

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/process_natural_language', methods=['POST'])
def process_natural_language():
    if not text_classifier:
        return jsonify({"status": "error", "message": "Text classifier model not loaded"}), 500

    data = request.json
    if not data or 'text' not in data:
        return jsonify({"status": "error", "message": "No text received"}), 400

    input_text = data['text']
    processed_text = preprocess_text(input_text)
    
    # Make prediction
    print("Voor prediction")
    text_vectorized = text_classifier['vectorizer'].transform([processed_text])
    predicted_category = text_classifier['classifier'].predict(text_vectorized)[0]
    print("input:",data, predicted_category)
    print ("eind prediction")
    print(f"Predicted category: {predicted_category}")
    print(f"Synonyms found: {synonyms.get(predicted_category.lower(), [])}")


    # Get synonyms with error handlin\
    synonyms_list = get_synonyms(predicted_category)
    print("Uit synonyms lijst: ", synonyms_list)

    return jsonify({
        "status": "success",
        "detected_object": predicted_category,
        "synonyms": synonyms_list
    })

@app.route('/get_objects')
def get_objects():
    if yolo_model is None:
        return jsonify({"status": "error", "message": "Model not loaded"})
    return jsonify({
        "status": "success",
        "objects": list(yolo_model.names.values())
    })

@app.route('/start_detection')
def start_detection():
    global detection_running
    if not detection_running:
        detection_running = True
        return jsonify({"status": "success", "message": "Object detection started"})
    return jsonify({"status": "error", "message": "Object detection already active"})

@app.route('/stop_detection')
def stop_detection():
    global detection_running, target_object
    if detection_running:
        detection_running = False
        target_object = None
        return jsonify({"status": "success", "message": "Object detection stopped"})
    return jsonify({"status": "error", "message": "Object detection already stopped"})

@app.route('/set_target/<object_name>')
def set_target(object_name):
    global target_object
    target_object = object_name
    return jsonify({"status": "success", "message": f"Target object set to: {object_name}"})

def generate_frames():
    global output_frame, detection_running, target_object

    while True:
        if not detection_running:
            black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            ret, buffer = cv2.imencode('.jpg', black_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
            continue

        success, frame = camera.read()
        if not success:
            continue

        frame = cv2.resize(frame, (640, 480))

        if yolo_model is not None:
            results = yolo_model(frame)
            annotated_frame = results[0].plot()

            if target_object:
                for detection in results[0].boxes.data:
                    class_id = int(detection[5])
                    class_name = results[0].names[class_id].lower()
                    confidence = float(detection[4])

                    if class_name == target_object.lower():
                        x1, y1, x2, y2 = map(int, detection[:4])
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                        label = f"Target: {class_name} ({confidence:.2f})"
                        cv2.putText(annotated_frame, label,
                                  (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                  (0, 255, 0), 2)
        else:
            annotated_frame = frame

        with lock:
            output_frame = annotated_frame.copy()

        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == '__main__':
    try:
       # init_nltk()  # Initialize NLTK resources
        init_camera()
        init_yolo_model()
        init_text_classifier()
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"Error during startup: {e}")