

from flask import Flask, request, jsonify
import base64
import io
# from google.cloud import vision
from PIL import Image
import os
import mysql.connector
import datetime
import requests
from config import get_db_connection, db_config
import random
# from dotenv import load_dotenv
# from api.gemini_api import extract_food_items_from_text

# load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    # conn = get_db_connection()
    # if conn:
    #     cursor = conn.cursor(dictionary=True)
    #     query = """
    #         SELECT * FROM t_inventory
    #         """
    #     cursor.execute(query)
    #     data = cursor.fetchall()
    #     cursor.close()
    #     conn.close()
    # else:   
    #     # return "Database connection error", 500
    #     return jsonify({"error": "Database connection error"}), 500
    return "hello world"

# Google Cloud 認証キーのパス
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Vision API クライアント
# client = vision.ImageAnnotatorClient()

# @app.route("/ocr", methods=["POST"])
# def ocr_image():
#     # print("OCR機能は現在使用できません")
#     # return jsonify({"error": "OCR機能は現在使用できません"}), 503
#     try:
#         if 'image' not in request.files:
#             return jsonify({"error": "画像が見つかりません"}), 400

#         image_file = request.files['image']
#         # print("Received image file:", image_file.filename)
#         content = image_file.read()

#         image = vision.Image(content=content)
#         response = client.text_detection(image=image)

#         if response.error.message:
#             return jsonify({"error": response.error.message}), 500

#         # 認識された全テキスト
#         full_text = response.full_text_annotation.text
#         print("Full text detected:", full_text)
#         return jsonify({"text": full_text.strip()})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
    
    
# @app.route("/filter_text", methods=["POST"])
# def filter_text():
#     data = request.get_json()
#     ocr_text = data.get("text", "")

#     # print("📥 受信したOCR:", ocr_text)

#     if not ocr_text:
#         return jsonify({"error": "text field is required"}), 400

#     try:
#         cleaned = extract_food_items_from_text(ocr_text)
#         print("📤 抽出された食材:", cleaned)
#         return jsonify({"cleaned_text": cleaned})
#     except Exception as e:
#         print("❌ 処理中にエラー:", e)
#         return jsonify({"error": str(e)}), 500
    


@app.route("/test_ocr", methods=["post"])
def test_endpoint():
    return jsonify({"text": 
        """
    領収証
FEEL
生店
052-482-7676
登録番号
ご来店、誠にありがとうございます
2025年06月27日 (金) 17:55 レジ0001
青 No00000084 天野
*カップヌードルチリトマト ¥178
*北海道チーズのささみフラ ¥280
*燻製屋ポークウインナー ¥258
#!未来のレモンサワー オ ¥268
*いいたまごMサイズ 6コ入 ¥188
小計
¥1,172
(外8%
タイショウ
¥904)
外8%
#72
(外10%
タイショウ
¥268)
外10%
¥26
外税計
¥98
ご利用日
(税合計
合計
クイックペイ
お買上点数
5点
******** QUICPay 支払 *** ***
端末番号
65063-007-00001
2025/06/27 17:57:46
¥98)
¥1,270
¥1.270
ELE
"""})

@app.route("/test_filter", methods=["post"])
def test_filter():
    return jsonify({
        "cleaned_text": """
        燻製屋ポークウインナー
いいたまごMサイズ 6コ入
"""})


@app.route('/add_food_items', methods=['POST'])
def add_food_items():
    items = request.get_json()
    if not isinstance(items, list):
        return jsonify({'error': 'Invalid data'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    now = datetime.date.today()

    for item in items:
        ingredients = item.get("name")
        expiration_date = item.get("expireDate", None)
        quantity = item.get("quantity", 1)

        cursor.execute(
            "INSERT INTO t_inventory (ingredients, expiration_date, quantity, add_date) VALUES (%s, %s, %s, %s)",
            (ingredients, expiration_date, quantity, now)
        )

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/get_food_items', methods=['GET'])
def get_food_items():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT ingredients, expiration_date, quantity FROM t_inventory")
    items = [
        {
            "ingredients": row[0],
            "expiration_date": row[1],
            "quantity": row[2]
        }
        for row in cursor.fetchall()
    ]
    cursor.close()
    conn.close()
    return jsonify(items)


@app.route("/get_recipe_categories", methods=["GET"])
def get_recipe_categories():
    try:
        print("✅ /get_recipe_categories にアクセスがありました") 
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT category_id, category_name FROM recipe_categories")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        print("❌ 例外発生:", e)
        return jsonify({"error": str(e)}), 500





def fetch_and_store_rakuten_categories_once():
    """楽天レシピカテゴリを取得・DB保存（大→中→小）"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # テーブル存在＆データチェック
        cursor.execute("SHOW TABLES LIKE 'recipe_categories'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM recipe_categories")
            count = cursor.fetchone()[0]
            if count > 0:
                print("📦 既にカテゴリデータは存在しています")
                cursor.close()
                conn.close()
                return

        # API取得
        app_id = "1081684173276999312"
        url = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryList/20170426?applicationId={app_id}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ APIエラー: {response.status_code}")
            return
        json_data = response.json()

        # DB構造：大・中・小カテゴリ
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipe_categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category1 VARCHAR(10),
                category2 VARCHAR(10),
                category3 VARCHAR(10),
                category_id VARCHAR(50),
                category_name VARCHAR(255)
            )
        """)
        cursor.execute("DELETE FROM recipe_categories")
        parent_dict = {}

        # 大カテゴリ
        for cat in json_data['result']['large']:
            cursor.execute("""
                INSERT INTO recipe_categories (category1, category2, category3, category_id, category_name)
                VALUES (%s, '', '', %s, %s)
            """, (cat['categoryId'], cat['categoryId'], cat['categoryName']))

        # 中カテゴリ
        for cat in json_data['result']['medium']:
            parent_id = cat['parentCategoryId']
            cursor.execute("""
                INSERT INTO recipe_categories (category1, category2, category3, category_id, category_name)
                VALUES (%s, %s, '', %s, %s)
            """, (parent_id, cat['categoryId'], f"{parent_id}-{cat['categoryId']}", cat['categoryName']))
            parent_dict[str(cat['categoryId'])] = parent_id

        # 小カテゴリ
        for cat in json_data['result']['small']:
            medium_id = cat['parentCategoryId']
            large_id = parent_dict.get(medium_id, "")
            if not large_id:
                print(f"⚠️ 中カテゴリ {medium_id} に対応する大カテゴリが見つかりません")
                continue
            cursor.execute("""
                INSERT INTO recipe_categories (category1, category2, category3, category_id, category_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (large_id, medium_id, cat['categoryId'], f"{large_id}-{medium_id}-{cat['categoryId']}", cat['categoryName']))

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ カテゴリ情報をDBに保存しました")

    except Exception as e:
        print(f"❌ カテゴリ取得中にエラー: {e}")

@app.route("/debug_recipe_api/<cat_id>")
def debug_recipe_api(cat_id):
    app_id = "1081684173276999312"
    url = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId={app_id}&categoryId={cat_id}"
    r = requests.get(url)
    return r.text

@app.route("/search_random_recipes", methods=["POST"])
def search_random_recipes():
    try:
        data = request.get_json()
        ingredient_names = data.get("ingredients", [])
        print(f"📥 検索対象の食材: {ingredient_names}")

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        selected_categories = []

        for ingredient in ingredient_names:
            cursor.execute("""
                SELECT category_id, category_name
                FROM recipe_categories
                WHERE category_name LIKE %s
            """, (f"%{ingredient}%",))
            matched = cursor.fetchall()
            print(f"🔍 「{ingredient}」にマッチしたカテゴリ数: {len(matched)}")

            if matched:
                chosen = random.choice(matched)
                selected_categories.append({
                    "ingredient": ingredient,
                    "category_id": chosen["category_id"],
                    "category_name": chosen["category_name"]
                })

        cursor.close()
        conn.close()

        # 楽天レシピAPIからレシピ取得（例として1つ目のみ取得）
        app_id = "1081684173276999312"
        results = []
        for cat in selected_categories:
            cat_id = cat["category_id"]
            url = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId={app_id}&categoryId={cat_id}"
            res = requests.get(url)
            if res.status_code == 200:
                json_data = res.json()
                recipes = json_data.get("result", [])
                if recipes:
                    results.append({
                        "ingredient": cat["ingredient"],
                        "category_name": cat["category_name"],
                        "category_id": cat["category_id"],
                        "recipe": random.choice(recipes)  # ランダムで1つ
                    })
                else:
                    print(f"⚠️ カテゴリ {cat_id} にレシピがありません")
            else:
                print(f"❌ APIエラー（カテゴリID: {cat_id}）: {res.status_code}")

        return jsonify(results)

    except Exception as e:
        print("❌ レシピ検索エラー:", e)
        return jsonify({"error": str(e)}), 500


# ✅ アプリ起動時に1度だけ実行
fetch_and_store_rakuten_categories_once()


@app.route('/delete_food_item', methods=['POST'])
def delete_food_item():
    data = request.get_json()
    ingredients = data.get("ingredients")
    expiration_date = data.get("expiration_date")
    quantity = data.get("quantity")

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM t_inventory WHERE ingredients=%s AND expiration_date=%s AND quantity=%s",
        (ingredients, expiration_date, quantity)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"result": "success"})

@app.route('/expiring_soon')
def expiring_soon():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    # 今日以降のデータを対象、近い順に並べる
    cursor.execute("""
SELECT ingredients, expiration_date
FROM t_inventory
WHERE expiration_date IS NOT NULL
  AND STR_TO_DATE(expiration_date, '%m/%d') >= STR_TO_DATE(DATE_FORMAT(CURDATE(), '%m/%d'), '%m/%d')
  AND STR_TO_DATE(expiration_date, '%m/%d') <= STR_TO_DATE(DATE_FORMAT(DATE_ADD(CURDATE(), INTERVAL 3 DAY), '%m/%d'), '%m/%d')
ORDER BY STR_TO_DATE(expiration_date, '%m/%d') ASC;

    """)
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(items)

    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
