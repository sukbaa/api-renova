from flask import Flask, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/cloverpool', methods=['GET'])
def get_cloverpool_data():
    url = "https://explorer.cloverpool.com/btc/insights-difficulty"
    data = []

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.select("table tbody tr")

        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) >= 6:
                data.append({
                    "block_time": cols[1],
                    "difficulty": cols[2],
                    "average_hashrate": cols[5]
                })

        if not data:
            return jsonify({"error": "Nenhum dado encontrado."}), 404

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": f"Falha ao coletar dados: {e}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
