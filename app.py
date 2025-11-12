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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        
        print("Fazendo request para:", url)
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        print("Request bem-sucedido!")

        soup = BeautifulSoup(response.content, "html.parser")
        print("HTML parseado com sucesso")
        
        # Debug: salvar HTML para ver o que está vindo
        with open("debug.html", "w") as f:
            f.write(str(soup))
        print("HTML salvo em debug.html")

        # Encontrar todas as tabelas
        tables = soup.find_all('table')
        print(f"Encontradas {len(tables)} tabelas")
        
        for i, table in enumerate(tables):
            print(f"Tabela {i}: {len(table.find_all('tr'))} linhas")

        # Pegar a primeira tabela com dados
        if tables:
            table = tables[0]
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
            else:
                rows = table.find_all('tr')
                
            print(f"Processando {len(rows)} linhas")
            
            for row in rows:
                cols = [c.get_text(strip=True) for c in row.find_all('td')]
                if len(cols) >= 6:
                    data.append({
                        "block_time": cols[1],
                        "difficulty": cols[2],
                        "average_hashrate": cols[5]
                    })
                    print(f"Dados encontrados: {cols[1]}, {cols[2]}, {cols[5]}")
        else:
            print("Nenhuma tabela encontrada!")

        if not data:
            return jsonify({"error": "Nenhum dado encontrado na tabela"}), 404

        return jsonify(data)

    except Exception as e:
        print(f"ERRO: {str(e)}")
        return jsonify({"error": f"Falha ao coletar dados: {str(e)}"}), 500

@app.route('/')
def home():
    return jsonify({"message": "API Cloverpool está rodando!", "endpoint": "/api/cloverpool"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
