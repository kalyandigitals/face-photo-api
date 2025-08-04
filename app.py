from flask import Flask, request, jsonify
import face_recognition
import os

app = Flask(__name__)
PHOTO_DIR = "photos"

@app.route("/match", methods=["POST"])
def match_faces():
    if 'selfie' not in request.files or 'event' not in request.form:
        return jsonify({"error": "Missing selfie or event ID"}), 400

    event = request.form['event']
    selfie = request.files['selfie']
    event_dir = os.path.join(PHOTO_DIR, event)
    if not os.path.exists(event_dir):
        return jsonify({"error": f"No such event '{event}'"}), 404

    try:
        selfie_img = face_recognition.load_image_file(selfie)
        selfie_enc = face_recognition.face_encodings(selfie_img)[0]
    except:
        return jsonify({"error": "Invalid selfie or no face found"}), 422

    matches = []
    for file in os.listdir(event_dir):
        file_path = os.path.join(event_dir, file)
        try:
            image = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(image)
            for face_encoding in encodings:
                result = face_recognition.compare_faces([selfie_enc], face_encoding, tolerance=0.5)
                if result[0]:
                    matches.append(f"https://yourdomain.com/uploads/events/{event}/{file}")
                    break
        except:
            continue
    return jsonify(matches)

@app.route("/upload", methods=["POST"])
def upload_event_photo():
    if 'photo' not in request.files or 'event' not in request.form:
        return jsonify({"error": "Missing photo or event ID"}), 400

    image = request.files['photo']
    event = request.form['event']
    save_dir = os.path.join(PHOTO_DIR, event)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, image.filename)
    image.save(save_path)
    return jsonify({"status": "success", "saved_to": save_path})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)