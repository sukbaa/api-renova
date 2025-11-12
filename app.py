from flask import Flask, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app)

def install_playwright():
    """Força instalação do Playwright se não estiver disponível"""
    try:
        from playwright.sync_api import sync_playwright
        # Tenta usar o Playwright
        with sync_playwright() as p:
            browsers = p.chromium.launch(headless=True)
            browsers.close()
        return True
    except Exception as e:
        print(f"Playwright não disponível: {e}")
        # Instala o Playwright
        try:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            print("Chromium instalado com sucesso!")
            return True
        except Exception as install_error:
            print(f"Falha ao instalar Chromium: {install_error}")
            return False

@app.route('/api/cloverpool', methods=['GET'])
def get_cloverpool_data():
    url = "https://explorer.cloverpool.com/btc/insights-difficulty"
    data = []

    try:
        # Verifica/instala Playwright
        if not install_playwright():
            return jsonify({"error": "Playwright não disponível"}), 500
            
        from playwright.sync_api import sync_playwright

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

        if not data:
            return jsonify({"error": "Nenhum dado encontrado."}), 404

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": f"Falha ao coletar dados: {e}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
