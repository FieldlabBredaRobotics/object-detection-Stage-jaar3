import sqlite3
from flask import Flask, Response, g, render_template, jsonify, request
import cv2
from flask_cors import CORS
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
CORS(app)

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

# Zorg ervoor dat het pad naar de database correct is
db_path = os.path.join(os.path.dirname(__file__), 'database', 'database.db')


allowed_object_classes = ['telefoon', 'portemonnee', 'pen', 'kam', 'horloge', 'sleutels', 'bril', 'auto sleutels']


def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

        
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
    camera = cv2.VideoCapture(0) # hier camera veranderene <<<<<<<<<<<<<<<<<<<---------------------------
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
    model_path = 'tekstAI.pkl'
    if not os.path.exists(model_path):
        raise RuntimeError("Text classification model not found.")
    
    vectorizer, classifier = joblib.load(model_path)
    text_classifier = {
        "vectorizer": vectorizer,
        "classifier": classifier
    }
    print("Text classifier model loaded.")

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
        return jsonify({"status": "error", "message": "Text classifier not initialized"})

    data = request.json
    if not data or 'text' not in data:
        return jsonify({"status": "error", "message": "No text provided"})

    input_text = data['text']
    processed_text = preprocess_text(input_text)
    
    # Make prediction
    text_vectorized = text_classifier['vectorizer'].transform([processed_text])
    predicted_probabilities = text_classifier['classifier'].predict_proba(text_vectorized)
    predicted_category_index = np.argmax(predicted_probabilities)
    predicted_category = text_classifier['classifier'].classes_[predicted_category_index]
    confidence = predicted_probabilities[0][predicted_category_index]

    # Get synonyms with error handling
    synonyms_list = get_synonyms(predicted_category)
       
    # Debug logging
    print(f"Input text: {input_text}")
    print(f"Processed text: {processed_text}") 
    print(f"Raw probabilities: {predicted_probabilities}")
    print(f"Selected category: {predicted_category}")
    print(f"Confidence: {confidence}")
    print(f"Synonyms: {synonyms_list}")

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

@app.route('/get_detection_status', methods=['GET'])
def get_detection_status():
    global detection_running
    return jsonify({"status": "success", "detection_running": detection_running}) 

@app.route('/set_target/<object_name>', methods=['POST'])
def set_target(object_name):
    global target_object
    target_object = object_name.lower()
    return jsonify({"status": "success", "message": f"Target object set to: {object_name}"})

@app.route('/get_object_detection_stats', methods=['GET'])
def get_object_detection_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all columns except id from count_detected
    cursor.execute('''
        SELECT carkeys, wallet, comb, glasses, keys, 
               mobile_phone, pen, watch 
        FROM count_detected 
        WHERE id = 1
    ''')
    row = cursor.fetchone()
    
    # Convert row data into column-count pairs
    if row:
        counts = []
        column_names = ['carkeys', 'wallet', 'comb', 'glasses', 'keys', 
                       'mobile_phone', 'pen', 'watch']
        for idx, count in enumerate(row):
            counts.append({
                'object_class': column_names[idx],
                'count': count
            })
    else:
        counts = []

    # Get matches from product_matches table
    cursor.execute('SELECT detected_product, correct_product FROM product_matches')
    matches = cursor.fetchall()

    # Calculate confidence percentages
    total_matches = {}
    correct_matches = {}
    for match in matches:
        detected = match[0]  # Using index since we're not using Row factory
        correct = match[1]
        if detected not in total_matches:
            total_matches[detected] = 0
            correct_matches[detected] = 0
        total_matches[detected] += 1
        if detected == correct:
            correct_matches[detected] += 1

    stats = []
    for count in counts:
        object_class = count['object_class']
        count_value = count['count']
        confidence = (correct_matches.get(object_class, 0) / total_matches.get(object_class, 1)) * 100 if total_matches.get(object_class, 0) > 0 else 0
        stats.append({
            'name': object_class,
            'count': count_value,
            'confidence': round(confidence, 2)
        })

    conn.close()
    return jsonify(stats)


@app.route('/get_product_detection_accuracy', methods=['GET'])
def get_product_detection_accuracy():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT detected_product, 
               SUM(CASE WHEN detected_product = correct_product THEN 1 ELSE 0 END) AS correct_count,
               COUNT(*) AS total_count
        FROM product_matches
        GROUP BY detected_product
    """)
    stats = cursor.fetchall()
    conn.close()
    accuracy_stats = {}
    for row in stats:
        detected_product = row['detected_product']
        correct_count = row['correct_count']
        total_count = row['total_count']
        accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
        accuracy_stats[detected_product] = accuracy
    return jsonify(accuracy_stats)

@app.route('/get_text_detection_accuracy', methods=['GET'])
def get_text_detection_accuracy():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT detected_product, 
               SUM(CASE WHEN detected_product = correct_product THEN 1 ELSE 0 END) AS correct_count,
               COUNT(*) AS total_count
        FROM text_matches
        GROUP BY detected_product
    """)
    stats = cursor.fetchall()
    conn.close()
    accuracy_stats = {}
    for row in stats:
        detected_product = row['detected_product']
        correct_count = row['correct_count']
        total_count = row['total_count']
        accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
        accuracy_stats[detected_product] = accuracy
    return jsonify(accuracy_stats)

@app.route('/save_product_match', methods=['POST'])
def save_product_match():
    data = request.get_json()
    detected_product = data['detectedProduct'].lower()
    correct_product = data['correctProduct'].lower()

    if detected_product == "niks" and correct_product == "niks":
        return jsonify({"status": "error", "message": "Both detected and correct product are 'niks'. Not saving to database."})

    conn = get_db_connection()
    conn.execute('INSERT INTO product_matches (detected_product, correct_product) VALUES (?, ?)',
                 (detected_product, correct_product))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Product match saved"})

@app.route('/save_text_match', methods=['POST'])
def save_text_match():
    data = request.get_json()
    detected_product = data['detectedProduct'].lower()
    correct_product = data['correctProduct'].lower()
    
    if detected_product == "niks" and correct_product == "niks":
        return jsonify({"status": "error", "message": "Both detected and correct product are 'niks'. Not saving to database."})

    conn = get_db_connection()
    conn.execute('INSERT INTO text_matches (detected_product, correct_product) VALUES (?, ?)',
                 (detected_product, correct_product))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Text match saved"})
    
@app.route('/get_product_stats', methods=['GET'])
def get_product_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT detected_product, correct_product FROM product_matches")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a list of dictionaries
    stats = []
    for row in rows:
        stats.append({
            "detected_product": row["detected_product"],
            "correct_product": row["correct_product"]
        })

    return jsonify(stats)


@app.route('/capture_and_detect', methods=['POST'])
def capture_and_detect():
    global camera, yolo_model

    if camera is None or not camera.isOpened():
        return jsonify({"status": "error", "message": "Camera not initialized"}), 500

    success, frame = camera.read()
    if not success:
        return jsonify({"status": "error", "message": "Failed to capture image"}), 500

    frame = cv2.resize(frame, (640, 480))

    if yolo_model is None:
        return jsonify({"status": "error", "message": "YOLO model not loaded"}), 500

    results = yolo_model(frame)
    detected_objects = {}

    for detection in results[0].boxes.data:
        class_id = int(detection[5])
        class_name = results[0].names[class_id].lower().replace('-', '_')
        if class_name in detected_objects:
            detected_objects[class_name] += 1
        else:
            detected_objects[class_name] = 1

    # Update the database with the detected objects
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for object_class, count in detected_objects.items():
            cursor.execute(f"UPDATE count_detected SET {object_class} = COALESCE({object_class}, 0) + ? WHERE id = 1", (count,))
        conn.commit()

    return jsonify({"status": "success", "detected_objects": detected_objects})


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

                    if class_name == target_object:
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