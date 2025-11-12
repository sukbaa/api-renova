from flask import Flask, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/cloverpool', methods=['GET'])
def get_cloverpool_data():
    url = "https://explorer.cloverpool.com/btc/insights-difficulty"
    data = []

    try:
        # Configura Chrome headless
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        # Usa Chrome do sistema (já instalado no Render)
        driver = webdriver.Chrome(options=chrome_options)
        
        driver.get(url)
        
        # Espera a tabela carregar
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        
        html = driver.page_source
        driver.quit()

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
