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
    payload = {"type": type_val, "code": code, "accountNumber": account_number, "api_key": API_KEY}
    if type_val == "ewallet":
        payload["server"] = "2"
    try:
        r = requests.get(BASE_URL, params=payload, timeout=30)
        if r.status_code != 200:
            error = r.json()
            pesan = error.get("data", {}).get("pesan") or error.get("pesan") or "Gagal validasi"
            return {"status": False, "pesan": pesan}
        return r.json()
    except:
        return {"status": False, "pesan": "Error koneksi ke server"}

# ================== HTML PREMIUM (DROPDOWN + INPUT SUDAH GELAP) ==================
HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CEK CEK REK</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
        
        /* FIX DROPDOWN DARK MODE */
        select {
            background-color: #ffffff !important;
            color: #111827 !important;
        }
        .dark select {
            background-color: #1f2937 !important;
            color: #f3f4f6 !important;
            border-color: #374151 !important;
        }
        select option {
            background-color: #ffffff !important;
            color: #111827 !important;
            padding: 14px 16px !important;
        }
        .dark select option {
            background-color: #1f2937 !important;
            color: #f3f4f6 !important;
        }
    </style>
</head>
<body class="bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100 min-h-screen transition-colors">
    <div class="max-w-2xl mx-auto mt-8 px-4">
        <div class="text-center mb-8">
            <h1 class="text-5xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">CEK CEK REK</h1>
            <p class="text-gray-500 dark:text-gray-400 mt-1">Validasi rekening & e-wallet secara instan</p>
        </div>

        <div class="flex border-b border-gray-200 dark:border-gray-700 mb-6">
            <button onclick="switchTab(0)" id="tab0" class="flex-1 py-4 font-semibold text-lg flex items-center justify-center gap-2 border-b-4 border-indigo-600 text-indigo-600 dark:text-indigo-400">🏦 Bank</button>
            <button onclick="switchTab(1)" id="tab1" class="flex-1 py-4 font-semibold text-lg flex items-center justify-center gap-2">💳 E-Wallet</button>
        </div>

        <!-- BANK -->
        <div id="form-bank">
            <select id="bank-select" class="w-full p-5 text-lg rounded-3xl border border-gray-200 dark:border-gray-700 focus:border-indigo-500 focus:outline-none mb-6">
                {% for nama, kode in bank_list.items() %}<option value="{{kode}}">{{nama}}</option>{% endfor %}
            </select>
            <input id="rek-bank" type="text" placeholder="Nomor Rekening" 
                   class="w-full p-5 rounded-3xl border border-gray-200 dark:border-gray-700 focus:border-indigo-500 text-lg mb-6 
                          bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
            <button onclick="cek('bank')" class="w-full bg-indigo-600 hover:bg-indigo-700 py-6 rounded-3xl text-white font-semibold text-xl flex items-center justify-center gap-3 transition">
                <i class="fas fa-search"></i> CEK REKENING
            </button>
        </div>

        <!-- EWALLET -->
        <div id="form-ewallet" class="hidden">
            <select id="ewallet-select" class="w-full p-5 text-lg rounded-3xl border border-gray-200 dark:border-gray-700 focus:border-indigo-500 focus:outline-none mb-6">
                {% for nama, kode in ewallet_list.items() %}<option value="{{kode}}">{{nama}}</option>{% endfor %}
            </select>
            <input id="rek-ewallet" type="text" placeholder="Nomor HP / ID E-Wallet" 
                   class="w-full p-5 rounded-3xl border border-gray-200 dark:border-gray-700 focus:border-indigo-500 text-lg mb-6 
                          bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
            <button onclick="cek('ewallet')" class="w-full bg-indigo-600 hover:bg-indigo-700 py-6 rounded-3xl text-white font-semibold text-xl flex items-center justify-center gap-3 transition">
                <i class="fas fa-search"></i> CEK E-WALLET
            </button>
        </div>

        <div id="result" class="mt-8 hidden"></div>

        <div class="mt-12">
            <h3 class="font-semibold text-lg mb-4 flex items-center gap-2"><i class="fas fa-history"></i> Riwayat Cek Terakhir</h3>
            <div id="history" class="space-y-3"></div>
        </div>
    </div>

    <script>
        function switchTab(n) {
            document.getElementById('tab0').classList.toggle('border-b-4', n===0);
            document.getElementById('tab0').classList.toggle('border-indigo-600', n===0);
            document.getElementById('tab0').classList.toggle('text-indigo-600', n===0);
            document.getElementById('tab1').classList.toggle('border-b-4', n===1);
            document.getElementById('tab1').classList.toggle('border-indigo-600', n===1);
            document.getElementById('tab1').classList.toggle('text-indigo-600', n===1);
            document.getElementById('form-bank').classList.toggle('hidden', n!==0);
            document.getElementById('form-ewallet').classList.toggle('hidden', n!==1);
        }

        function saveToHistory(jenis, entity, nama, nomor) {
            let history = JSON.parse(localStorage.getItem('cekrek_history') || '[]');
            history.unshift({ jenis, entity, nama, nomor, time: new Date().toLocaleTimeString('id-ID',{hour:'2-digit',minute:'2-digit'}) });
            if (history.length > 5) history.pop();
            localStorage.setItem('cekrek_history', JSON.stringify(history));
            renderHistory();
        }

        function renderHistory() {
            const div = document.getElementById('history');
            let history = JSON.parse(localStorage.getItem('cekrek_history') || '[]');
            if (history.length === 0) {
                div.innerHTML = `<p class="text-gray-400 text-center py-4">Belum ada riwayat</p>`;
                return;
            }
            div.innerHTML = history.map(h => `
                <div class="bg-white dark:bg-gray-900 rounded-2xl p-4 flex items-center justify-between border border-gray-100 dark:border-gray-700">
                    <div>
                        <span class="text-sm text-gray-500">${h.jenis.toUpperCase()} • ${h.entity}</span><br>
                        <span class="font-medium">${h.nama}</span><br>
                        <span class="text-sm text-gray-500">${h.nomor}</span>
                    </div>
                    <div class="text-xs text-gray-400">${h.time}</div>
                </div>
            `).join('');
        }

        async function cek(jenis) {
            const resultDiv = document.getElementById('result');
            resultDiv.classList.remove('hidden');
            resultDiv.innerHTML = `<div class="text-center py-12"><i class="fas fa-spinner fa-spin text-5xl text-indigo-600"></i><p class="mt-6 text-lg">Sedang memvalidasi...</p></div>`;

            let code = jenis === 'bank' ? document.getElementById('bank-select').value : document.getElementById('ewallet-select').value;
            let account_number = (jenis === 'bank' ? document.getElementById('rek-bank') : document.getElementById('rek-ewallet')).value.trim();
            let entityName = jenis === 'bank' ? document.getElementById('bank-select').options[document.getElementById('bank-select').selectedIndex].text : 
                                           document.getElementById('ewallet-select').options[document.getElementById('ewallet-select').selectedIndex].text;

            const res = await fetch('/api/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type: jenis, code: code, account_number: account_number})
            });
            const data = await res.json();

            if (data.status === true) {
                const d = data.data;
                const label = jenis === 'bank' ? 'Bank' : 'E-Wallet';
                resultDiv.innerHTML = `
                <div class="bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-3xl p-8">
                    <div class="flex items-center gap-4 mb-6">
                        <i class="fas fa-check-circle text-5xl text-green-600"></i>
                        <div>
                            <h2 class="text-3xl font-bold text-green-700 dark:text-green-400">Validasi Berhasil</h2>
                            <p class="text-green-600 dark:text-green-300">${label} • ${entityName}</p>
                        </div>
                    </div>
                    <div class="space-y-4 text-lg">
                        <div class="flex justify-between"><span class="text-gray-500 dark:text-gray-400">Nama</span><span class="font-semibold">${d.account_name}</span></div>
                        <div class="flex justify-between"><span class="text-gray-500 dark:text-gray-400">Nomor</span><span class="font-semibold">${d.account_number}</span></div>
                    </div>
                    <button onclick="copyToClipboard('${d.account_name}')" 
                            class="mt-8 w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 py-4 rounded-2xl font-medium flex items-center justify-center gap-2">
                        📋 Copy Nama
                    </button>
                </div>`;
                saveToHistory(jenis, entityName, d.account_name, d.account_number);
            } else {
                resultDiv.innerHTML = `<div class="bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300 p-8 rounded-3xl text-center text-lg">${data.pesan}</div>`;
            }
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                const btns = document.querySelectorAll('button');
                for (let b of btns) if (b.textContent.includes('Copy')) {
                    const original = b.innerHTML;
                    b.innerHTML = '✅ Tersalin!';
                    setTimeout(() => b.innerHTML = original, 2000);
                }
            });
        }

        window.onload = () => {
            switchTab(0);
            renderHistory();
        };
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
