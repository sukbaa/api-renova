from flask import Flask, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import os

app = Flask(__name__)
CORS(app)

def collect_with_playwright():
    """Tenta com Playwright (funciona no Colab)"""
    try:
        from playwright.sync_api import sync_playwright
        
        url = "https://explorer.cloverpool.com/btc/insights-difficulty"
        data = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_selector("table tbody tr")

            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("table tbody tr")

        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) >= 6:
                data.append({
                    "block_time": cols[1],
                    "difficulty": cols[2],
                    "average_hashrate": cols[5]
                })

        return data
    except Exception as e:
        print(f"Playwright falhou: {e}")
        return None

def collect_with_requests():
    """Fallback com requests"""
    try:
        url = "https://explorer.cloverpool.com/btc/insights-difficulty"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.select("table tbody tr")
        data = []

        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) >= 6:
                data.append({
                    "block_time": cols[1],
                    "difficulty": cols[2],
                    "average_hashrate": cols[5]
                })

        return data
    except Exception as e:
        print(f"Requests falhou: {e}")
        return None

@app.route('/api/cloverpool', methods=['GET'])
def get_cloverpool_data():
    # Primeiro tenta com Playwright
    data = collect_with_playwright()
    
    # Se falhar, tenta com Requests
    if not data:
        data = collect_with_requests()
    
    if not data:
        return jsonify({"error": "Nenhum dado encontrado com nenhum método."}), 404

    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
