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
    nomor = ''.join(filter(str.isdigit, nomor))
    return nomor

def validasi_api(type_val, code, account_number):
    payload = {"type": type_val, "code": code, "accountNumber": account_number, "api_key": API_KEY}
    if type_val == "ewallet":
        payload["server"] = "2"

    for attempt in range(2):
        try:
            r = requests.get(BASE_URL, params=payload, timeout=25)
            if r.status_code == 200:
                return r.json()
            error = r.json()
            pesan = error.get("data", {}).get("pesan") or error.get("pesan") or "Gagal validasi"
            if "SERVICE_UNAVAILABLE" in pesan.upper() and attempt == 0:
                time.sleep(0.8)
                continue
            return {"status": False, "pesan": pesan}
        except:
            if attempt == 0:
                time.sleep(0.8)
                continue
            return {"status": False, "pesan": "Error koneksi ke server"}
    
    return {"status": False, "pesan": "Validasi Gagal atau Layanan tidak tersedia"}

# ================== HTML DENGAN PESAN ERROR YANG DIPERBARUI ==================
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
    </style>
</head>
<body class="bg-gradient-to-br from-slate-50 to-indigo-50 dark:from-slate-950 dark:to-slate-900 min-h-screen text-gray-900 dark:text-gray-100">
    <div class="max-w-2xl mx-auto pt-12 px-6">
        <div class="text-center mb-12">
            <h1 class="text-6xl font-bold tracking-tighter bg-gradient-to-r from-indigo-600 via-purple-600 to-violet-600 bg-clip-text text-transparent">CEK CEK REK</h1>
            <p class="mt-4 text-xl text-slate-600 dark:text-slate-400">Validasi rekening & e-wallet cepat dan aman</p>
            <p class="mt-2 text-sm text-amber-600 dark:text-amber-400">
                Kalau cek pertama gagal, coba lagi, dan kalau masih gagal langsung ke GRUP FD saja ya 🙂
            </p>
        </div>

        <div class="flex bg-white dark:bg-slate-800 rounded-3xl p-2 shadow-xl mb-12">
            <button onclick="switchTab(0)" id="tab0" class="flex-1 py-5 text-lg font-semibold rounded-3xl transition-all flex items-center justify-center gap-3">🏦 Bank</button>
            <button onclick="switchTab(1)" id="tab1" class="flex-1 py-5 text-lg font-semibold rounded-3xl transition-all flex items-center justify-center gap-3">💳 E-Wallet</button>
        </div>

        <div id="form-bank" class="relative">
            <div class="bg-white dark:bg-slate-800 rounded-3xl p-10 shadow-2xl border border-white/70 dark:border-slate-700">
                <select id="bank-select" class="w-full p-6 text-lg rounded-2xl border border-slate-200 dark:border-slate-600 focus:border-indigo-500 mb-6"></select>
                <input id="rek-bank" type="text" placeholder="Nomor Rekening" maxlength="20"
                       class="w-full p-6 text-lg rounded-2xl border border-slate-200 dark:border-slate-600 focus:border-indigo-500" 
                       oninput="this.value = this.value.replace(/[^0-9]/g, '')"
                       onkeypress="if(event.key === 'Enter') cek('bank')">
                <button onclick="cek('bank')" 
                        class="mt-10 w-full py-7 rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold text-xl flex items-center justify-center gap-3 transition-all">🔎 CEK REKENING</button>
            </div>
            <div id="loading-bank" class="loading-overlay hidden">
                <div class="flex flex-col items-center">
                    <div class="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
                    <p class="mt-4 text-slate-600 dark:text-slate-400 font-medium">Sedang memvalidasi...</p>
                </div>
            </div>
        </div>

        <div id="form-ewallet" class="relative hidden">
            <div class="bg-white dark:bg-slate-800 rounded-3xl p-10 shadow-2xl border border-white/70 dark:border-slate-700">
                <select id="ewallet-select" class="w-full p-6 text-lg rounded-2xl border border-slate-200 dark:border-slate-600 focus:border-indigo-500 mb-6"></select>
                <input id="rek-ewallet" type="text" placeholder="Nomor HP / ID E-Wallet" maxlength="20"
                       class="w-full p-6 text-lg rounded-2xl border border-slate-200 dark:border-slate-600 focus:border-indigo-500" 
                       oninput="this.value = this.value.replace(/[^0-9]/g, '')"
                       onkeypress="if(event.key === 'Enter') cek('ewallet')">
                <button onclick="cek('ewallet')" 
                        class="mt-10 w-full py-7 rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold text-xl flex items-center justify-center gap-3 transition-all">🔎 CEK E-WALLET</button>
            </div>
            <div id="loading-ewallet" class="loading-overlay hidden">
                <div class="flex flex-col items-center">
                    <div class="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
                    <p class="mt-4 text-slate-600 dark:text-slate-400 font-medium">Sedang memvalidasi...</p>
                </div>
            </div>
        </div>

        <div id="result" class="mt-12 hidden"></div>

        <div class="mt-20">
            <h3 class="font-semibold text-xl mb-6 flex items-center gap-3"><i class="fas fa-history"></i> Riwayat Cek Terakhir</h3>
            <div id="history" class="space-y-4"></div>
        </div>
    </div>

    <script>
        // Isi dropdown
        {% for nama, kode in bank_list.items() %}
            document.getElementById('bank-select').innerHTML += `<option value="{{kode}}">{{nama}}</option>`;
        {% endfor %}
        {% for nama, kode in ewallet_list.items() %}
            document.getElementById('ewallet-select').innerHTML += `<option value="{{kode}}">{{nama}}</option>`;
        {% endfor %}

        function switchTab(n) {
            document.getElementById('tab0').classList.toggle('bg-white', n===0);
            document.getElementById('tab0').classList.toggle('shadow-md', n===0);
            document.getElementById('tab1').classList.toggle('bg-white', n===1);
            document.getElementById('tab1').classList.toggle('shadow-md', n===1);
            document.getElementById('form-bank').classList.toggle('hidden', n!==0);
            document.getElementById('form-ewallet').classList.toggle('hidden', n!==1);
        }

        function showLoading(jenis) {
            document.getElementById(`loading-${jenis}`).classList.remove('hidden');
        }

        function hideLoading(jenis) {
            document.getElementById(`loading-${jenis}`).classList.add('hidden');
        }

        async function cek(jenis) {
            showLoading(jenis);

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

            hideLoading(jenis);

            const resultDiv = document.getElementById('result');
            resultDiv.classList.remove('hidden');

            if (data.status === true) {
                const d = data.data;
                const label = jenis === 'bank' ? 'Bank' : 'E-Wallet';
                resultDiv.innerHTML = `
                <div class="bg-white dark:bg-slate-800 rounded-3xl p-10 shadow-2xl border border-white/70 dark:border-slate-700">
                    <div class="flex items-center gap-6 mb-8">
                        <div class="w-20 h-20 bg-emerald-100 dark:bg-emerald-900/50 rounded-3xl flex items-center justify-center">
                            <i class="fas fa-check-circle text-6xl text-emerald-500"></i>
                        </div>
                        <div>
                            <h2 class="text-4xl font-bold text-emerald-700 dark:text-emerald-400">Validasi Berhasil</h2>
                            <p class="text-emerald-600 dark:text-emerald-300">${label} • ${entityName}</p>
                        </div>
                    </div>
                    <div class="space-y-8 text-lg">
                        <div class="flex justify-between pb-4 border-b border-slate-200 dark:border-slate-700">
                            <span class="text-slate-500">Nama</span>
                            <span class="font-semibold">${d.account_name}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-slate-500">Nomor</span>
                            <span class="font-semibold">${d.account_number}</span>
                        </div>
                    </div>
                    <button onclick="copyToClipboard('${d.account_name}')" 
                            class="mt-12 w-full py-7 rounded-2xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold flex items-center justify-center gap-3 transition-all">
                        <i class="fas fa-copy"></i> Copy Nama
                    </button>
                </div>`;
                saveToHistory(jenis, entityName, d.account_name, d.account_number);
            } else {
                let pesan = data.pesan || "Terjadi kesalahan";
                if (pesan.includes("Validasi Gagal atau Layanan tidak tersedia") || pesan.includes("Gagal validasi")) {
                    pesan = `
                        Validasi Gagal atau Layanan tidak tersedia<br>
                        Coba cek lagi, kalau masih gagal, langsung ke GRUP FD aja ya 🙂<br><br>
                        <span class="text-rose-600 dark:text-rose-400 font-bold italic">*PASTIKAN JENIS REKENINGNYA SUDAH SESUAI*</span>
                    `;
                }
                resultDiv.innerHTML = `<div class="bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 p-14 rounded-3xl text-center text-xl">${pesan}</div>`;
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
                div.innerHTML = `<p class="text-center text-slate-400 py-12">Belum ada riwayat cek</p>`;
                return;
            }
            div.innerHTML = history.map(h => `
                <div class="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-white/50 dark:border-slate-700">
                    <div class="flex justify-between">
                        <div>
                            <span class="text-xs uppercase tracking-widest text-indigo-500">${h.jenis} • ${h.entity}</span>
                            <p class="font-medium mt-2">${h.nama}</p>
                            <p class="text-slate-500">${h.nomor}</p>
                        </div>
                        <span class="text-xs text-slate-400">${h.time}</span>
                    </div>
                </div>
            `).join('');
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
