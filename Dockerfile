# ① Pythonの公式軽量イメージを使用
FROM python:3.11-slim

# ② 作業ディレクトリを作成・移動
WORKDIR /app

# ③ 依存関係ファイルをコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ④ ソースコードをすべてコピー
COPY . .

# ⑤ Botを起動するコマンド
CMD ["python", "main.py"]
