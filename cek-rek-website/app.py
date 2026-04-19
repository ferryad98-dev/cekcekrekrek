import os
import requests
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://v3.apivalidasi.my.id/api/v3/validate"

# ================== DAFTAR BANK & EWALLET ==================
BANK_LIST = {
    "BRI": "002", "BCA": "014", "Mandiri": "008", "BNI": "009",
    "BSI": "451", "BTN": "200", "CIMB Niaga": "022", "Danamon": "011",
    "Permata": "013", "Maybank": "016", "JAGO": "542", "SEABANK": "535",
    "JENIUS": "213", "PANIN": "019", "SINARMAS": "153"
}

EWALLET_LIST = {
    "DANA": "dana", "OVO": "ovo", "GoPay": "gopay",
    "ShopeePay": "shopeepay", "LinkAja": "linkaja"
}

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
        if r.status_code != 200:
            try:
                error = r.json()
                pesan = error.get("data", {}).get("pesan") or error.get("pesan") or "Gagal validasi"
                if "SERVICE_UNAVAILABLE" in pesan or "unavailable" in pesan.lower():
                    return {"status": False, "pesan": "Bank ini sedang tidak tersedia. Silakan coba bank lain."}
                return {"status": False, "pesan": pesan}
            except:
                return {"status": False, "pesan": "API Error"}
        return r.json()
    except Exception:
        return {"status": False, "pesan": "Error koneksi"}

# ================== HTML + TAILWIND ==================
HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CEK CEK REK - Validasi Rekening</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">
</head>
<body class="bg-gray-50 font-sans">
    <div class="max-w-2xl mx-auto mt-10 px-4">
        <h1 class="text-4xl font-bold text-center text-indigo-700 mb-2">CEK CEK REK</h1>
        <p class="text-center text-gray-600 mb-8">Validasi rekening bank & e-wallet secara instan</p>

        <div class="flex border-b mb-6">
            <button onclick="switchTab(0)" id="tab0" class="tab-button flex-1 py-4 font-semibold text-lg border-b-4 border-indigo-600 text-indigo-600">🏦 Bank</button>
            <button onclick="switchTab(1)" id="tab1" class="tab-button flex-1 py-4 font-semibold text-lg">💳 E-Wallet</button>
        </div>

        <!-- BANK FORM -->
        <div id="form-bank" class="tab-content">
            <select id="bank-select" class="w-full p-4 rounded-2xl border border-gray-300 focus:outline-none focus:border-indigo-500 text-lg mb-4">
                {% for nama, kode in bank_list.items() %}<option value="{{kode}}">{{nama}}</option>{% endfor %}
            </select>
            <input id="rek-bank" type="text" placeholder="Nomor Rekening" class="w-full p-4 rounded-2xl border border-gray-300 focus:outline-none focus:border-indigo-500 text-lg">
            <button onclick="cek('bank')" class="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-5 rounded-2xl text-xl transition">CEK REKENING</button>
        </div>

        <!-- EWALLET FORM -->
        <div id="form-ewallet" class="tab-content hidden">
            <select id="ewallet-select" class="w-full p-4 rounded-2xl border border-gray-300 focus:outline-none focus:border-indigo-500 text-lg mb-4">
                {% for nama, kode in ewallet_list.items() %}<option value="{{kode}}">{{nama}}</option>{% endfor %}
            </select>
            <input id="rek-ewallet" type="text" placeholder="Nomor HP / ID E-Wallet" class="w-full p-4 rounded-2xl border border-gray-300 focus:outline-none focus:border-indigo-500 text-lg">
            <button onclick="cek('ewallet')" class="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-5 rounded-2xl text-xl transition">CEK E-WALLET</button>
        </div>

        <!-- HASIL -->
        <div id="result" class="mt-8 hidden"></div>
    </div>

    <script>
        function switchTab(n) {
            document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('border-b-4', 'border-indigo-600', 'text-indigo-600'));
            document.getElementById('tab'+n).classList.add('border-b-4', 'border-indigo-600', 'text-indigo-600');
            
            document.getElementById('form-bank').classList.toggle('hidden', n !== 0);
            document.getElementById('form-ewallet').classList.toggle('hidden', n !== 1);
        }

        async function cek(jenis) {
            const resultDiv = document.getElementById('result');
            resultDiv.classList.remove('hidden');
            resultDiv.innerHTML = `<div class="text-center py-8"><i class="fas fa-spinner fa-spin text-4xl text-indigo-600"></i><p class="mt-4">Sedang memvalidasi...</p></div>`;

            let type_val = jenis;
            let code, account_number;

            if (jenis === 'bank') {
                code = document.getElementById('bank-select').value;
                account_number = document.getElementById('rek-bank').value.trim();
            } else {
                code = document.getElementById('ewallet-select').value;
                account_number = document.getElementById('rek-ewallet').value.trim();
            }

            if (!account_number) {
                resultDiv.innerHTML = `<div class="bg-red-100 text-red-700 p-6 rounded-2xl text-center">⚠️ Harap isi nomor rekening / ID</div>`;
                return;
            }

            const res = await fetch('/api/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type: type_val, code: code, account_number: account_number})
            });

            const data = await res.json();

            if (data.status === true) {
                const d = data.data;
                let html = `
                <div class="bg-green-50 border border-green-300 rounded-3xl p-6">
                    <div class="flex items-center gap-3 mb-4">
                        <i class="fas fa-check-circle text-4xl text-green-600"></i>
                        <h2 class="text-2xl font-bold text-green-700">Validasi Berhasil</h2>
                    </div>
                    <p><strong>${jenis.toUpperCase()}</strong> : ${d.bank_name || d.ewallet_name || code}</p>
                    <p><strong>Nama</strong> : ${d.account_name}</p>
                    <p><strong>Nomor</strong> : ${d.account_number}</p>
                </div>`;
                resultDiv.innerHTML = html;
            } else {
                resultDiv.innerHTML = `<div class="bg-red-100 text-red-700 p-6 rounded-3xl text-center font-medium">${data.pesan || 'Terjadi kesalahan'}</div>`;
            }
        }

        // Auto switch ke tab pertama
        window.onload = () => switchTab(0);
    </script>
</body>
</html>
"""

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
    app.run(host='0.0.0.0', port=5000, debug=True)
