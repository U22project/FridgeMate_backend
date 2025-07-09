from flask import Flask,request,jsonify
import base64
import io
from google.cloud import vision
from PIL import Image
import os
from dotenv import load_dotenv
from api.gemini_api import extract_food_items_from_text

load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    return "hello"


# Google Cloud 認証キーのパス
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Vision API クライアント
client = vision.ImageAnnotatorClient()

@app.route("/ocr", methods=["POST"])
def ocr_image():
    # print("OCR機能は現在使用できません")
    # return jsonify({"error": "OCR機能は現在使用できません"}), 503
    try:
        if 'image' not in request.files:
            return jsonify({"error": "画像が見つかりません"}), 400

        image_file = request.files['image']
        # print("Received image file:", image_file.filename)
        content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        if response.error.message:
            return jsonify({"error": response.error.message}), 500

        # 認識された全テキスト
        full_text = response.full_text_annotation.text
        # print("Full text detected:", full_text)
        return jsonify({"text": full_text.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route("/filter_text", methods=["POST"])
def filter_text():
    data = request.get_json()
    ocr_text = data.get("text", "")

    # print("📥 受信したOCR:", ocr_text)

    if not ocr_text:
        return jsonify({"error": "text field is required"}), 400

    try:
        cleaned = extract_food_items_from_text(ocr_text)
        return jsonify({"cleaned_text": cleaned})
    except Exception as e:
        print("❌ 処理中にエラー:", e)
        return jsonify({"error": str(e)}), 500
    
    
    
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)