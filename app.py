from flask import Flask,request,jsonify
import base64
import io
from google.cloud import vision
from PIL import Image
import os

app = Flask(__name__)

@app.route("/")
def index():
    return "hello"


# Google Cloud 認証キーのパス
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"

# Vision API クライアント
client = vision.ImageAnnotatorClient()

@app.route("/ocr", methods=["POST"])
def ocr_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "画像が見つかりません"}), 400

        image_file = request.files['image']
        content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        if response.error.message:
            return jsonify({"error": response.error.message}), 500

        # 認識された全テキスト
        full_text = response.full_text_annotation.text
        return jsonify({"text": full_text.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500