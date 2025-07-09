import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_food_items_from_text(ocr_text: str) -> str:
    try:
        if not ocr_text.strip():
            return "（空の入力でした）"

        prompt = f"""
以下はレシートのOCR認識結果です。
料理に使う「食材名」だけを1行ずつ抽出してください。
金額・日付・レシート番号などの情報はすべて除外してください。
これ以外の情報は出力しないでください。

[OCR結果]
{ocr_text}
"""

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        print("❌ Gemini処理エラー:", e)
        raise e  # 上層に通知（Flaskが500返す）
