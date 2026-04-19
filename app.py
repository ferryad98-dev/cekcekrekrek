import os
import requests
import time
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://v3.apivalidasi.my.id/api/v3/validate"

BANK_LIST = {
    "BRI": "002", "BCA": "014", "Mandiri": "008", "BNI": "009",
    "BTN": "200", "CIMB Niaga": "022", "Danamon": "011",
    "Permata": "013", "Maybank": "016", "JAGO": "542",
    "JENIUS": "213", "PANIN": "019", "SINARMAS": "153",
    "BSI (ERROR)": "451", "SEABANK (ERROR)": "535"
}

EWALLET_LIST = {
    "DANA": "dana", "OVO": "ovo", "GoPay": "gopay",
    "ShopeePay": "shopeepay", "LinkAja (ERROR)": "linkaja"
}

def clean_number(raw):
    nomor = raw.strip()
    nomor = nomor.replace("-", "").replace(" ", "").replace(".", "").replace(",", "")
    nomor = nomor.replace("_", "").replace("/", "").replace("\\", "")
    return nomor

# ================== AUTO RETRY (Fix error pertama) ==================
def validasi_api(type_val, code, account_number):
    payload = {
        "type": type_val,
        "code": code,
        "accountNumber": account_number,
        "api_key": API_KEY
    }
    if type_val == "ewallet":
        payload["server"] = "2"

    for attempt in range(2):   # coba maksimal 2 kali
        try:
            r = requests.get(BASE_URL, params=payload, timeout=25)
            
            if r.status_code == 200:
                return r.json()
            
            error = r.json()
            pesan = error.get("data", {}).get("pesan") or error.get("pesan") or "Gagal validasi"
            
            if "SERVICE_UNAVAILABLE" in pesan.upper() or "unavailable" in pesan.lower():
                if attempt == 0:
                    time.sleep(0.8)   # tunggu sebentar lalu coba lagi
                    continue
                return {"status": False, "pesan": "Bank/E-Wallet sedang sibuk. Coba lagi sebentar."}
            
            return {"status": False, "pesan": pesan}
            
        except:
            if attempt == 0:
                time.sleep(0.8)
                continue
            return {"status": False, "pesan": "Error koneksi ke server validasi"}
    
    return {"status": False, "pesan": "COBA 2X BARU BISA (Validasi Gagal atau Layanan tidak tersedia)"}

# ================== HTML (Kamu sudah bagus, tetap pakai yang ini) ==================
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
        select, input {
            background-color: #ffffff !important;
            color: #111827 !important;
        }
        .dark select, .dark input {
            background-color: #1f2937 !important;
            color: #f3f4f6 !important;
            border-color: #374151 !important;
        }
        select option {
            background-color: #1f2937;
            color: #f3f4f6;
        }
    </style>
</head>
<body class="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-black text-gray-900 dark:text-gray-100 min-h-screen">
    <div class="max-w-2xl mx-auto pt-10 px-4">
        <div class="text-center mb-10">
            <h1 class="text-6xl font-bold tracking-tighter bg-gradient-to-r from-indigo-600 via-purple-600 to-violet-600 bg-clip-text text-transparent">CEK CEK REK</h1>
            <p class="mt-3 text-lg text-gray-500 dark:text-gray-400">Validasi rekening & e-wallet secara instan • Aman & Cepat</p>
        </div>

        <div class="flex bg-white/80 dark:bg-gray-900/80 backdrop-blur-md rounded-3xl p-1 shadow-inner mb-8">
            <button onclick="switchTab(0)" id="tab0" class="flex-1 py-4 font-semibold text-lg rounded-3xl flex items-center justify-center gap-3 transition-all">🏦 Bank</button>
            <button onclick="switchTab(1)" id="tab1" class="flex-1 py-4 font-semibold text-lg rounded-3xl flex items-center justify-center gap-3 transition-all">💳 E-Wallet</button>
        </div>

        <div id="form-bank">
            <div class="bg-white dark:bg-gray-900 rounded-3xl p-8 shadow-xl">
                <select id="bank-select" class="w-full p-5 text-lg rounded-2xl border border-gray-200 dark:border-gray-700 focus:border-indigo-500 focus:outline-none mb-6"></select>
                <input id="rek-bank" type="text" placeholder="Nomor Rekening" class="w-full p-5 rounded-2xl border border-gray-200 dark:border-gray-700 focus:border-indigo-500 text-lg mb-8">
                <button onclick="cek('bank')" class="w-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 py-6 rounded-2xl text-white font-semibold text-xl flex items-center justify-center gap-3 transition-all">🔎 CEK REKENING</button>
            </div>
        </div>

        <div id="form-ewallet" class="hidden">
            <div class="bg-white dark:bg-gray-900 rounded-3xl p-8 shadow-xl">
                <select id="ewallet-select" class="w-full p-5 text-lg rounded-2xl border border-gray-200 dark:border-gray-700 focus:border-indigo-500 focus:outline-none mb-6"></select>
                <input id="rek-ewallet" type="text" placeholder="Nomor HP / ID E-Wallet" class="w-full p-5 rounded-2xl border border-gray-200 dark:border-gray-700 focus:border-indigo-500 text-lg mb-8">
                <button onclick="cek('ewallet')" class="w-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 py-6 rounded-2xl text-white font-semibold text-xl flex items-center justify-center gap-3 transition-all">🔎 CEK E-WALLET</button>
            </div>
        </div>

        <div id="result" class="mt-10 hidden"></div>

        <div class="mt-16">
            <h3 class="font-semibold text-xl mb-5 flex items-center gap-2"><i class="fas fa-history"></i> Riwayat Cek Terakhir</h3>
            <div id="history" class="space-y-4"></div>
        </div>
    </div>

    <script>
        const bankSelect = document.getElementById('bank-select');
        const ewalletSelect = document.getElementById('ewallet-select');

        // Isi dropdown
        {% for nama, kode in bank_list.items() %}
            bankSelect.innerHTML += `<option value="{{kode}}">{{nama}}</option>`;
        {% endfor %}
        {% for nama, kode in ewallet_list.items() %}
            ewalletSelect.innerHTML += `<option value="{{kode}}">{{nama}}</option>`;
        {% endfor %}

        function switchTab(n) {
            document.getElementById('tab0').classList.toggle('bg-white', n===0);
            document.getElementById('tab0').classList.toggle('shadow-sm', n===0);
            document.getElementById('tab1').classList.toggle('bg-white', n===1);
            document.getElementById('tab1').classList.toggle('shadow-sm', n===1);
            document.getElementById('form-bank').classList.toggle('hidden', n!==0);
            document.getElementById('form-ewallet').classList.toggle('hidden', n!==1);
        }

        function saveToHistory(jenis, entity, nama, nomor) {
            let history = JSON.parse(localStorage.getItem('cekrek_history') || '[]');
            history.unshift({ jenis, entity, nama, nomor, time: new Date().toLocaleTimeString('id-ID',{hour:'2-digit', minute:'2-digit'}) });
            if (history.length > 5) history.pop();
            localStorage.setItem('cekrek_history', JSON.stringify(history));
            renderHistory();
        }

        function renderHistory() {
            const div = document.getElementById('history');
            const history = JSON.parse(localStorage.getItem('cekrek_history') || '[]');
            if (history.length === 0) {
                div.innerHTML = `<p class="text-center text-gray-400 py-8">Belum ada riwayat cek</p>`;
                return;
            }
            div.innerHTML = history.map(h => `
                <div class="bg-white dark:bg-gray-900 rounded-2xl p-5 flex justify-between items-center border border-gray-100 dark:border-gray-700">
                    <div>
                        <span class="text-xs uppercase">${h.jenis} • ${h.entity}</span>
                        <p class="font-semibold mt-1">${h.nama}</p>
                        <p class="text-sm text-gray-500">${h.nomor}</p>
                    </div>
                    <span class="text-xs text-gray-400">${h.time}</span>
                </div>
            `).join('');
        }

        async function cek(jenis) {
            const resultDiv = document.getElementById('result');
            resultDiv.classList.remove('hidden');
            resultDiv.innerHTML = `<div class="text-center py-16"><i class="fas fa-spinner fa-spin text-6xl text-indigo-500"></i><p class="mt-6 text-lg">Sedang memvalidasi...</p></div>`;

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
                <div class="bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-3xl p-10">
                    <div class="flex items-center gap-5">
                        <i class="fas fa-check-circle text-6xl text-green-500"></i>
                        <div class="flex-1">
                            <h2 class="text-4xl font-bold text-green-700 dark:text-green-400">Validasi Berhasil</h2>
                            <p class="text-green-600 dark:text-green-300">${label} • ${entityName}</p>
                            <div class="mt-8 space-y-6 text-lg">
                                <div class="flex justify-between"><span class="text-gray-500">Nama</span><span class="font-semibold">${d.account_name}</span></div>
                                <div class="flex justify-between"><span class="text-gray-500">Nomor</span><span class="font-semibold">${d.account_number}</span></div>
                            </div>
                            <button onclick="copyToClipboard('${d.account_name}')" class="mt-10 w-full py-5 rounded-2xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-medium flex items-center justify-center gap-3 hover:scale-105 transition">📋 Copy Nama</button>
                        </div>
                    </div>
                </div>`;
                saveToHistory(jenis, entityName, d.account_name, d.account_number);
            } else {
                resultDiv.innerHTML = `<div class="bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300 p-10 rounded-3xl text-center text-lg">${data.pesan}</div>`;
            }
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                const btns = document.querySelectorAll('button');
                for (let b of btns) if (b.textContent.includes('Copy')) {
                    const original = b.innerHTML;
                    b.innerHTML = '✅ Tersalin!';
                    setTimeout(() => { b.innerHTML = original; }, 2000);
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
