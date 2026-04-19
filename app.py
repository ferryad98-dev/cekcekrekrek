import os
import requests
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://v3.apivalidasi.my.id/api/v3/validate"

BANK_LIST = { ... }      # sama seperti sebelumnya
EWALLET_LIST = { ... }   # sama seperti sebelumnya

def clean_number(raw):
    nomor = raw.strip()
    nomor = nomor.replace("-", "").replace(" ", "").replace(".", "").replace(",", "")
    nomor = nomor.replace("_", "").replace("/", "").replace("\\", "")
    return nomor

def validasi_api(type_val, code, account_number):
    payload = {
        "type": type_val,
        "code": code,
        "accountNumber": account_number,
        "api_key": API_KEY
    }
    try:
        r = requests.get(BASE_URL, params=payload, timeout=30)
        print(f"API Response: {r.status_code} | {r.text[:300]}")  # ← debug di Vercel log
        if r.status_code != 200:
            try:
                error = r.json()
                pesan = error.get("data", {}).get("pesan") or error.get("pesan") or "Gagal validasi"
                return {"status": False, "pesan": pesan}
            except:
                return {"status": False, "pesan": f"HTTP {r.status_code}"}
        return r.json()
    except Exception as e:
        print(f"Exception: {str(e)}")  # ← debug
        return {"status": False, "pesan": f"Error koneksi: {str(e)}"}

# ================== HTML (sama seperti sebelumnya, tapi error lebih jelas) ==================
HTML = """ ... (sama persis seperti kode sebelumnya) ... """

@app.route('/')
def home():
    return render_template_string(HTML, bank_list=BANK_LIST, ewallet_list=EWALLET_LIST)

@app.route('/api/validate', methods=['POST'])
def validate():
    data = request.get_json()
    type_val = data.get('type')
    code = data.get('code')
    account_number = clean_number(data.get('account_number', ''))
    
    result = validasi_api(type_val, code, account_number)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
