# FridgeMate Backend

U-22プログラミングコンテスト 2025 出展作品  
冷蔵庫管理アプリ **FridgeMate** のバックエンドAPIです。  
Flask + MySQL を使用し、食材管理・賞味期限管理・レシピ検索機能を提供します。

---

## 主な機能

- 食材の追加・取得・削除  
- 賞味期限が近い食材の取得  
- OCR解析のテストAPI（デモ用のダミーデータ返却）  
- 楽天レシピAPIと連携し、食材に基づいたレシピ提案  

---

## 開発環境

- Python 3.9.16
- Flask 3.1.1
- MySQL 8.0.31
- 依存ライブラリは `requirements.txt` を参照

---

## セットアップ方法

1. 仮想環境を作成・有効化
2. ライブラリのインポート
3. 20250823_dump.sqlを使用しmysql上でDBを作成
4. Cloud Vision API,Generative Language APIのAPIキーを取得する。
5. .envをapp.pyと同階層に作成し次の内容を記述する
    GOOGLE_APPLICATION_CREDENTIALS=/home/user/keys/your_application_credentials.json
    GEMINI_API_KEY=your_api_key
    DB_HOST=your_db_hostname
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
6. 仮想環境有効化
7. flaskの起動(以下コマンドで)
    flask run --host=0.0.0.0 --port=5000
8. 起動ポート確認
    以下リンクを確認する
    Running on http://192.168.00.00:0000/
    このリンクをフロントエンドのlocal.propertiesのSERVER_URLに記述
    ↑↑↑重要です。

