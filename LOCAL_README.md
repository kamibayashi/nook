# Nook ローカル版

このREADMEでは、Nookをローカル環境で実行する方法について説明します。

## 概要

Nookローカル版は、AWS（Lambda、S3、EventBridge）に依存せずに、ローカル環境でNookを実行できるようにしたバージョンです。以下の変更が行われています：

- AWS Lambda → ローカルのPythonスクリプト
- Amazon S3 → ローカルファイルシステム
- Amazon EventBridge → 手動実行またはcron
- Lambda URL → ローカルWebサーバー（FastAPI + Uvicorn）

## 前提条件

- Python 3.11以上
- 以下のAPIキー:
  - Google Gemini API キー
  - Reddit API キー（クライアントID、クライアントシークレット）

## セットアップ

1. **リポジトリをクローン**
   ```bash
   git clone https://github.com/kamibayashi/nook.git
   cd nook
   ```

2. **環境変数の設定**
   `.env` ファイルを作成し、以下の内容を設定
   ```
   GEMINI_API_KEY=your_gemini_api_key
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_CLIENT_SECRET=your_reddit_client_secret
   REDDIT_USER_AGENT=your_reddit_user_agent
   ```

3. **依存関係のインストール**
   ```bash
   uv venv --python 3.11.11
   source .venv/bin/activate

   # ローカル用依存関係をインストール
   # uv pip install -r requirements-local.txt
   ```

## 使用方法

### 情報収集と要約の実行

```bash
# すべてのモジュールを実行
python local_app.py collect

# 特定のモジュールのみ実行
python local_app.py collect --modules reddit_explorer github_trending
```

### Webサーバーの起動

```bash
# デフォルト設定（127.0.0.1:8000）でサーバーを起動
python local_app.py serve

# カスタム設定でサーバーを起動
python local_app.py serve --host 0.0.0.0 --port 5000
```

サーバー起動後、ブラウザで `http://127.0.0.1:8000` にアクセスすると、Nookのウェブインターフェースが表示されます。

## データの保存場所

収集したデータは `data/` ディレクトリに保存されます。ディレクトリ構造はAWS S3のキー構造と同じです：

```
data/
├── reddit_explorer/
│   ├── 2023-12-31.md
│   └── ...
├── github_trending/
│   ├── 2023-12-31.md
│   └── ...
├── hacker_news/
│   └── ...
├── paper_summarizer/
│   └── ...
└── tech_feed/
    └── ...
```

## 定期実行の設定

crontabを使用して定期実行を設定することができます：

```bash
# crontabを編集
crontab -e

# 毎日午前9時に実行する例
0 9 * * * cd /path/to/nook && /path/to/python /path/to/nook/local_app.py collect
```

## カスタマイズ

AWS版と同様に、各情報源の設定ファイルを編集することでカスタマイズできます：

- Reddit: `nook/lambda/reddit_explorer/subreddits.toml`
- GitHub Trending: `nook/lambda/github_trending/languages.toml`
- 技術ブログ: `nook/lambda/tech_feed/feed.toml`

## トラブルシューティング

- **モジュールが見つからないエラー**: `PYTHONPATH` に現在のディレクトリを追加してください。
  ```bash
  export PYTHONPATH=$PYTHONPATH:.
  ```

- **APIキーエラー**: `.env` ファイルが正しく設定されているか確認してください。

- **データが表示されない**: 先に `collect` コマンドを実行して、データを収集してください。

- **依存関係エラー**: 特定のモジュールの実行時に依存関係エラーが発生した場合は、そのモジュールの `requirements.txt` を個別にインストールしてください。
  ```bash
  pip install -r nook/lambda/<module_name>/requirements.txt
  ```