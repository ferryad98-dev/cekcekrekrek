import os
import requests
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://v3.apivalidasi.my.id/api/v3/validate"

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
    
    # HANYA DANA yang butuh server=2
    if type_val == "ewallet" and code == "dana":
        payload["server"] = "2"

    try:
        r = requests.get(BASE_URL, params=payload, timeout=30)
        print(f"📡 [{type_val.upper()} - {code}] Status: {r.status_code} | {r.text[:500]}")
        
        if r.status_code != 200:
            try:
                error = r.json()
                pesan = error.get("data", {}).get("pesan") or error.get("pesan") or "Gagal validasi"
                return {"status": False, "pesan": pesan}
            except:
                return {"status": False, "pesan": f"HTTP {r.status_code}"}
        
        return r.json()
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"status": False, "pesan": "Error koneksi ke server"}

# ================== HTML ==================
HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CEK CEK REK</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">
</head>
<body class="bg-gray-50 font-sans">
    <div class="max-w-2xl mx-auto mt-10 px-4">
        <h1 class="text-4xl font-bold text-center text-indigo-700 mb-1">CEK CEK REK</h1>
        <p class="text-center text-gray-600 mb-8">Validasi rekening bank & e-wallet secara instan</p>

        <div class="flex border-b mb-6">
            <button onclick="switchTab(0)" id="tab0" class="flex-1 py-4 font-semibold text-lg border-b-4 border-indigo-600 text-indigo-600">🏦 Bank</button>
            <button onclick="switchTab(1)" id="tab1" class="flex-1 py-4 font-semibold text-lg">💳 E-Wallet</button>
        </div>

        <div id="form-bank">
            <select id="bank-select" class="w-full p-4 rounded-2xl border border-gray-300 focus:outline-none focus:border-indigo-500 text-lg mb-4">
                {% for nama, kode in bank_list.items() %}<option value="{{kode}}">{{nama}}</option>{% endfor %}
            </select>
            <input id="rek-bank" type="text" placeholder="Nomor Rekening" class="w-full p-4 rounded-2xl border border-gray-300 focus:outline-none focus:border-indigo-500 text-lg">
            <button onclick="cek('bank')" class="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-5 rounded-2xl text-xl transition">CEK REKENING</button>
        </div>

        <div id="form-ewallet" class="hidden">
            <select id="ewallet-select" class="w-full p-4 rounded-2xl border border-gray-300 focus:outline-none focus:border-indigo-500 text-lg mb-4">
                {% for nama, kode in ewallet_list.items() %}<option value="{{kode}}">{{nama}}</option>{% endfor %}
            </select>
            <input id="rek-ewallet" type="text" placeholder="Nomor HP / ID E-Wallet" class="w-full p-4 rounded-2xl border border-gray-300 focus:outline-none focus:border-indigo-500 text-lg">
            <button onclick="cek('ewallet')" class="w-full mt-6 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-5 rounded-2xl text-xl transition">CEK E-WALLET</button>
        </div>

        <div id="result" class="mt-8 hidden"></div>
        <a href="/debug" class="block text-center text-xs text-gray-400 mt-8">🔧 Debug Page</a>
    </div>

    <script>
        function switchTab(n) {
            document.querySelectorAll('button').forEach(b => b.classList.remove('border-b-4', 'border-indigo-600', 'text-indigo-600'));
            document.getElementById('tab'+n).classList.add('border-b-4', 'border-indigo-600', 'text-indigo-600');
            document.getElementById('form-bank').classList.toggle('hidden', n !== 0);
            document.getElementById('form-ewallet').classList.toggle('hidden', n !== 1);
        }

        async function cek(jenis) {
            const resultDiv = document.getElementById('result');
            resultDiv.classList.remove('hidden');
            resultDiv.innerHTML = `<div class="text-center py-8"><i class="fas fa-spinner fa-spin text-4xl text-indigo-600"></i><p class="mt-4">Sedang memvalidasi...</p></div>`;

            let type_val = jenis;
            let code = jenis === 'bank' ? document.getElementById('bank-select').value : document.getElementById('ewallet-select').value;
            let account_number = (jenis === 'bank' ? document.getElementById('rek-bank') : document.getElementById('rek-ewallet')).value.trim();

            const res = await fetch('/api/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type: type_val, code: code, account_number: account_number})
            });
            const data = await res.json();

            if (data.status === true) {
                const d = data.data;
                resultDiv.innerHTML = `
                <div class="bg-green-50 border border-green-300 rounded-3xl p-6">
                    <div class="flex items-center gap-3 mb-4">
                        <i class="fas fa-check-circle text-4xl text-green-600"></i>
                        <h2 class="text-2xl font-bold text-green-700">✅ Validasi Berhasil</h2>
                    </div>
                    <p class="text-lg"><strong>Nama :</strong> ${d.account_name}</p>
                    <p class="text-lg"><strong>Nomor :</strong> ${d.account_number}</p>
                </div>`;
            } else {
                resultDiv.innerHTML = `<div class="bg-red-100 text-red-700 p-6 rounded-3xl text-center">${data.pesan}</div>`;
            }
        }
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
    result = validasi_api(data.get('type'), data.get('code'), clean_number(data.get('account_number', '')))
    return jsonify(result)

@app.route('/debug')
def debug():
    key = os.getenv("API_KEY") or "TIDAK DITEMUKAN"
    return f"""
    <h1>🔧 DEBUG PAGE</h1>
    <p><strong>API_KEY terbaca?</strong> {bool(API_KEY)}</p>
    <p><strong>Panjang:</strong> {len(key)}</p>
    <p><a href="/">← Kembali</a></p>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
