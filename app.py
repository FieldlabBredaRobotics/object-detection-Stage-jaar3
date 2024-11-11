from flask import Flask, Response, render_template, jsonify, request
import cv2
from ultralytics import YOLO
import threading
import queue
import time
import numpy as np
import os
import spacy
from nltk.corpus import wordnet as wn

from synonyms import synonyms

app = Flask(__name__)
camera = None
output_frame = None

lock = threading.Lock()
detection_running = False
frame_queue = queue.Queue(maxsize=10)
model = None
target_object = None


nlp = spacy.load("nl_core_news_sm")

# synoniemen via WordNet, gaat weg wanneer de LLM Ai af is, experiment nu 
def get_synonyms(word):
    synonyms = set()
    for syn in wn.synsets(word, lang='nld'):  
        for lemma in syn.lemmas('nld'):
            synonyms.add(lemma.name())
    return list(synonyms)

#Camera pakken 
def init_camera():
    global camera
    camera = cv2.VideoCapture(0) # << hier aanpassen als verkeerde webcame pakt!
    if not camera.isOpened():
        raise RuntimeError("Kon camera niet openen.")

# model pakken 
def init_model():
    global model
    model_path = os.path.join('models', 'best (7).pt')
    model = YOLO(model_path)
    print("Beschikbare object classes:")
    for idx, name in model.names.items():
        print(f"- {name}")



def generate_frames():
    global output_frame, detection_running, target_object  # output is voor laatste bewerkte frame, 2e is voor of actief moet zijn, 3e is of er terget ingevoerd is
    
    while True:
        if not detection_running: # als niet actief dan zwart beeld 
            black_frame = np.zeros((480, 640, 3), dtype=np.uint8)

            ret, buffer = cv2.imencode('.jpg', black_frame) # omzetten naar cv2 zodat kan versturen 
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            time.sleep(0.1)
            continue

        success, frame = camera.read() #lees frame van camera
        if not success:
            continue

        frame = cv2.resize(frame, (640, 480)) 

        if model is not None:
            results = model(frame) # voert detectie uit 
            annotated_frame = results[0].plot() #visueel weergegeven op frame


            if target_object:
                for detection in results[0].boxes.data:
                    class_id = int(detection[5])
                    class_name = results[0].names[class_id].lower()
                    confidence = float(detection[4])
                    
                    if class_name == target_object.lower():  # als gevonden dan groene box erom doen 
                        x1, y1, x2, y2 = map(int, detection[:4])
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                        label = f"Target: {class_name} ({confidence:.2f})"
                        cv2.putText(annotated_frame, label,
                                  (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                                  (0, 255, 0), 2)
        else:
            annotated_frame = frame

        with lock:
            output_frame = annotated_frame.copy()

        ret, buffer = cv2.imencode('.jpg', annotated_frame) # ret voor return 
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_objects')
def get_objects():
    if model is None:
        return jsonify({"status": "error", "message": "Model niet geladen"})
    return jsonify({
        "status": "success",
        "objects": list(model.names.values())
    })


@app.route('/start_detection')
def start_detection():
    global detection_running
    if not detection_running:
        detection_running = True
        return jsonify({"status": "success", "message": "Object detectie gestart"})
    return jsonify({"status": "error", "message": "Object detectie is al actief"})


@app.route('/stop_detection')
def stop_detection():
    global detection_running, target_object
    if detection_running:
        detection_running = False
        target_object = None
        return jsonify({"status": "success", "message": "Object detectie gestopt"})
    return jsonify({"status": "error", "message": "Object detectie is al gestopt"})


@app.route('/set_target/<object_name>')
def set_target(object_name):
    global target_object
    target_object = object_name
    return jsonify({"status": "success", "message": f"Doel object ingesteld op: {object_name}"})



@app.route('/process_natural_language', methods=['POST'])
def process_natural_language():
    data = request.json
    text = data.get('text', '').lower()  
       
    # checken in de lijst bij synonyms.py 
    for word, mapped_object in synonyms.items():
        if word in text:
            return jsonify({
                'status': 'success',
                'detected_object': mapped_object
            })

    doc = nlp(text) # met NLP model woorden omzetten naar tokens 
    detected_objects = []

    # opzoek naar relevante versie van het woord, bij spel fout ofzo dat het nog steeds gevonden wordt 
    for token in doc:
        detected_objects.append(token.lemma_) 

    # Controleer op synoniemen voor de gedetecteerde woorden
    for obj in detected_objects:
        obj_synonyms = get_synonyms(obj)

        # Combineer de gedetecteerde objecten met hun synoniemen
        if obj in synonyms or any(syn in synonyms for syn in obj_synonyms):
            matched_object = synonyms.get(obj, None)
            if matched_object:
                return jsonify({
                    'status': 'success',
                    'detected_object': matched_object
                })

    return jsonify({
        'status': 'error',
        'message': 'Geen overeenkomend object gevonden.'
    })

if __name__ == '__main__':
    init_camera()
    init_model()
    app.run(host='0.0.0.0', port=5000, debug=True)
