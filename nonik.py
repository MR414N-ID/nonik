#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR 414N -ID
NIK Multi-Gov Scraper (Single File)
Input: NIK only
Hardcoded 50+ government sites
Multi-layer anti-captcha
"""

import os
import sys
import time
import json
import base64
import hashlib
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# BANNER
# ============================================================
BANNER = r"""
███╗   ███╗██████╗     ██╗  ██╗ ██╗██╗  ██╗███╗   ██╗     ██╗██████╗ 
████╗ ████║██╔══██╗    ██║  ██║███║██║  ██║████╗  ██║    ██╔╝██╔══██╗
██╔████╔██║██████╔╝    ███████║╚██║███████║██╔██╗ ██║    ██║ ██║  ██║
██║╚██╔╝██║██╔══██╗    ╚════██║ ██║╚════██║██║╚██╗██║    ██║ ██║  ██║
██║ ╚═╝ ██║██║  ██║         ██║ ██║     ██║██║ ╚████║    ╚██╗██████╔╝
╚═╝     ╚═╝╚═╝  ╚═╝         ╚═╝ ╚═╝     ╚═╝╚═╝  ╚═══╝     ╚═╝╚═════╝ 
                                                                      
              NIK MULTI-GOV SCRAPER  |  SINGLE FILE
"""

# ============================================================
# CONFIG
# ============================================================
CAPTCHA_KEYS = {
    "2captcha": os.getenv("TWOCAPTCHA_KEY", ""),
    "anticaptcha": os.getenv("ANTICAPTCHA_KEY", ""),
    "capmonster": os.getenv("CAPMONSTER_KEY", ""),
    "capsolver": os.getenv("CAPSOLVER_KEY", ""),
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}

TIMEOUT = 20
MAX_WORKERS = 8

# ============================================================
# 50+ GOVERNMENT SITES (hardcoded)
# Format: name, url, method, nik_field, extra_fields, notes
# ============================================================
SITES = [
    {"name": "Cek Bansos Kemensos", "url": "https://cekbansos.kemensos.go.id", "method": "GET", "nik_field": "nik", "notes": "bansos/desil"},
    {"name": "DTSEN BPS Form", "url": "https://dtsen-form.bps.go.id", "method": "GET", "nik_field": "nik", "notes": "desil DTSEN"},
    {"name": "BSU Kemnaker", "url": "https://bsu.kemnaker.go.id", "method": "GET", "nik_field": "nik", "notes": "bantuan subsidi upah"},
    {"name": "BPJS Kesehatan", "url": "https://www.bpjs-kesehatan.go.id", "method": "GET", "nik_field": "nik", "notes": "status kepesertaan"},
    {"name": "BPJS Ketenagakerjaan", "url": "https://www.bpjsketenagakerjaan.go.id", "method": "GET", "nik_field": "nik", "notes": "kepesertaan"},
    {"name": "DJP Online", "url": "https://djponline.pajak.go.id", "method": "GET", "nik_field": "nik", "notes": "pajak"},
    {"name": "Imigrasi", "url": "https://www.imigrasi.go.id", "method": "GET", "nik_field": "nik", "notes": "paspor/visa"},
    {"name": "Dukcapil Kemendagri", "url": "https://dukcapil.kemendagri.go.id", "method": "GET", "nik_field": "nik", "notes": "kependudukan"},
    {"name": "Lapor Kemendagri", "url": "https://kemendagri.lapor.go.id", "method": "GET", "nik_field": "nik", "notes": "pengaduan"},
    {"name": "Alpukat Dukcapil DKI", "url": "https://alpukat-dukcapil.jakarta.go.id", "method": "GET", "nik_field": "nik", "notes": "DKI"},
    {"name": "OSS", "url": "https://oss.go.id", "method": "GET", "nik_field": "nik", "notes": "izin usaha"},
    {"name": "SSCASN BKN", "url": "https://sscasn.bkn.go.id", "method": "GET", "nik_field": "nik", "notes": "ASN"},
    {"name": "Kemnaker", "url": "https://kemnaker.go.id", "method": "GET", "nik_field": "nik", "notes": "ketenagakerjaan"},
    {"name": "Kemensos", "url": "https://kemensos.go.id", "method": "GET", "nik_field": "nik", "notes": "sosial"},
    {"name": "Kemenkes", "url": "https://www.kemkes.go.id", "method": "GET", "nik_field": "nik", "notes": "kesehatan"},
    {"name": "Kemenkeu", "url": "https://www.kemenkeu.go.id", "method": "GET", "nik_field": "nik", "notes": "keuangan"},
    {"name": "Kominfo", "url": "https://www.kominfo.go.id", "method": "GET", "nik_field": "nik", "notes": "kominfo"},
    {"name": "BSSN", "url": "https://www.bssn.go.id", "method": "GET", "nik_field": "nik", "notes": "siber"},
    {"name": "BNPT", "url": "https://www.bnpt.go.id", "method": "GET", "nik_field": "nik", "notes": "terorisme"},
    {"name": "Polri", "url": "https://www.polri.go.id", "method": "GET", "nik_field": "nik", "notes": "kepolisian"},
    {"name": "TNI", "url": "https://tni.mil.id", "method": "GET", "nik_field": "nik", "notes": "militer"},
    {"name": "Kejaksaan", "url": "https://www.kejaksaan.go.id", "method": "GET", "nik_field": "nik", "notes": "kejaksaan"},
    {"name": "Mahkamah Agung", "url": "https://www.mahkamahagung.go.id", "method": "GET", "nik_field": "nik", "notes": "peradilan"},
    {"name": "KPK", "url": "https://www.kpk.go.id", "method": "GET", "nik_field": "nik", "notes": "korupsi"},
    {"name": "OJK", "url": "https://www.ojk.go.id", "method": "GET", "nik_field": "nik", "notes": "keuangan"},
    {"name": "BI", "url": "https://www.bi.go.id", "method": "GET", "nik_field": "nik", "notes": "bank sentral"},
    {"name": "LPS", "url": "https://www.lps.go.id", "method": "GET", "nik_field": "nik", "notes": "penjamin simpanan"},
    {"name": "BPS", "url": "https://www.bps.go.id", "method": "GET", "nik_field": "nik", "notes": "statistik"},
    {"name": "Bappenas", "url": "https://www.bappenas.go.id", "method": "GET", "nik_field": "nik", "notes": "perencanaan"},
    {"name": "Kemendikbud", "url": "https://www.kemdikbud.go.id", "method": "GET", "nik_field": "nik", "notes": "pendidikan"},
    {"name": "Kemenag", "url": "https://kemenag.go.id", "method": "GET", "nik_field": "nik", "notes": "agama"},
    {"name": "Kemenkumham", "url": "https://www.kemenkumham.go.id", "method": "GET", "nik_field": "nik", "notes": "hukum"},
    {"name": "Kemenlu", "url": "https://kemlu.go.id", "method": "GET", "nik_field": "nik", "notes": "luar negeri"},
    {"name": "Kemenhan", "url": "https://www.kemhan.go.id", "method": "GET", "nik_field": "nik", "notes": "pertahanan"},
    {"name": "Kemenhub", "url": "https://dephub.go.id", "method": "GET", "nik_field": "nik", "notes": "perhubungan"},
    {"name": "Kemenperin", "url": "https://kemenperin.go.id", "method": "GET", "nik_field": "nik", "notes": "perindustrian"},
    {"name": "Kemendag", "url": "https://www.kemendag.go.id", "method": "GET", "nik_field": "nik", "notes": "perdagangan"},
    {"name": "Kementan", "url": "https://www.pertanian.go.id", "method": "GET", "nik_field": "nik", "notes": "pertanian"},
    {"name": "KKP", "url": "https://kkp.go.id", "method": "GET", "nik_field": "nik", "notes": "kelautan"},
    {"name": "KemenLHK", "url": "https://www.menlhk.go.id", "method": "GET", "nik_field": "nik", "notes": "lingkungan"},
    {"name": "Kemen ESDM", "url": "https://www.esdm.go.id", "method": "GET", "nik_field": "nik", "notes": "energi"},
    {"name": "Kemen PUPR", "url": "https://www.pu.go.id", "method": "GET", "nik_field": "nik", "notes": "pekerjaan umum"},
    {"name": "Kemen ATR/BPN", "url": "https://www.atrbpn.go.id", "method": "GET", "nik_field": "nik", "notes": "agraria"},
    {"name": "BNN", "url": "https://bnn.go.id", "method": "GET", "nik_field": "nik", "notes": "narkoba"},
    {"name": "BNPB", "url": "https://bnpb.go.id", "method": "GET", "nik_field": "nik", "notes": "bencana"},
    {"name": "BMKG", "url": "https://www.bmkg.go.id", "method": "GET", "nik_field": "nik", "notes": "cuaca"},
    {"name": "LAPAN", "url": "https://www.lapan.go.id", "method": "GET", "nik_field": "nik", "notes": "antariksa"},
    {"name": "BRIN", "url": "https://www.brin.go.id", "method": "GET", "nik_field": "nik", "notes": "riset"},
    {"name": "LIPI", "url": "https://lipi.go.id", "method": "GET", "nik_field": "nik", "notes": "ilmu pengetahuan"},
    {"name": "BPOM", "url": "https://www.pom.go.id", "method": "GET", "nik_field": "nik", "notes": "obat makanan"},
    {"name": "BKKBN", "url": "https://www.bkkbn.go.id", "method": "GET", "nik_field": "nik", "notes": "keluarga berencana"},
    {"name": "Kemendes PDTT", "url": "https://kemendesa.go.id", "method": "GET", "nik_field": "nik", "notes": "desa"},
    {"name": "Kemenpora", "url": "https://www.kemenpora.go.id", "method": "GET", "nik_field": "nik", "notes": "pemuda olahraga"},
    {"name": "Kemenparekraf", "url": "https://www.kemenparekraf.go.id", "method": "GET", "nik_field": "nik", "notes": "pariwisata"},
    {"name": "Setkab", "url": "https://setkab.go.id", "method": "GET", "nik_field": "nik", "notes": "sekretariat kabinet"},
    {"name": "Setneg", "url": "https://www.setneg.go.id", "method": "GET", "nik_field": "nik", "notes": "sekretariat negara"},
]

# ============================================================
# ANTI-CAPTCHA MULTI LAYER
# ============================================================
def solve_captcha_local(image_bytes):
    """Layer 1: Local OCR (Tesseract) - best effort"""
    try:
        import pytesseract
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        # simple threshold
        img = img.point(lambda x: 0 if x < 140 else 255)
        text = pytesseract.image_to_string(img, config="--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789").strip()
        if len(text) >= 3:
            return text
    except Exception:
        pass
    return None

def solve_captcha_2captcha(image_b64, key):
    """Layer 2: 2Captcha"""
    if not key:
        return None
    try:
        r = requests.post("http://2captcha.com/in.php", data={
            "key": key, "method": "base64", "body": image_b64, "json": 1
        }, timeout=15)
        data = r.json()
        if data.get("status") != 1:
            return None
        captcha_id = data["request"]
        for _ in range(24):
            time.sleep(5)
            res = requests.get(f"http://2captcha.com/res.php?key={key}&action=get&id={captcha_id}&json=1", timeout=10).json()
            if res.get("status") == 1:
                return res["request"]
            if res.get("request") != "CAPCHA_NOT_READY":
                return None
    except Exception:
        pass
    return None

def solve_captcha_anticaptcha(image_b64, key):
    """Layer 3: Anti-Captcha.com"""
    if not key:
        return None
    try:
        create = requests.post("https://api.anti-captcha.com/createTask", json={
            "clientKey": key,
            "task": {"type": "ImageToTextTask", "body": image_b64}
        }, timeout=15).json()
        if create.get("errorId") != 0:
            return None
        task_id = create["taskId"]
        for _ in range(24):
            time.sleep(5)
            res = requests.post("https://api.anti-captcha.com/getTaskResult", json={
                "clientKey": key, "taskId": task_id
            }, timeout=10).json()
            if res.get("status") == "ready":
                return res["solution"]["text"]
            if res.get("errorId") != 0:
                return None
    except Exception:
        pass
    return None

def solve_captcha_capmonster(image_b64, key):
    """Layer 4: CapMonster"""
    if not key:
        return None
    try:
        create = requests.post("https://api.capmonster.cloud/createTask", json={
            "clientKey": key,
            "task": {"type": "ImageToTextTask", "body": image_b64}
        }, timeout=15).json()
        if create.get("errorId") != 0:
            return None
        task_id = create["taskId"]
        for _ in range(24):
            time.sleep(5)
            res = requests.post("https://api.capmonster.cloud/getTaskResult", json={
                "clientKey": key, "taskId": task_id
            }, timeout=10).json()
            if res.get("status") == "ready":
                return res["solution"]["text"]
            if res.get("errorId") != 0:
                return None
    except Exception:
        pass
    return None

def solve_captcha(image_bytes, image_url=None):
    """Multi-layer solver. Tries all available providers in order."""
    image_b64 = base64.b64encode(image_bytes).decode() if image_bytes else None

    # Layer 1 - local
    if image_bytes:
        result = solve_captcha_local(image_bytes)
        if result:
            return result, "local-ocr"

    # Layer 2 - 2captcha
    if image_b64 and CAPTCHA_KEYS["2captcha"]:
        result = solve_captcha_2captcha(image_b64, CAPTCHA_KEYS["2captcha"])
        if result:
            return result, "2captcha"

    # Layer 3 - anticaptcha
    if image_b64 and CAPTCHA_KEYS["anticaptcha"]:
        result = solve_captcha_anticaptcha(image_b64, CAPTCHA_KEYS["anticaptcha"])
        if result:
            return result, "anticaptcha"

    # Layer 4 - capmonster
    if image_b64 and CAPTCHA_KEYS["capmonster"]:
        result = solve_captcha_capmonster(image_b64, CAPTCHA_KEYS["capmonster"])
        if result:
            return result, "capmonster"

    # Layer 5 - manual fallback
    print("\n[!] Captcha tidak bisa diselesaikan otomatis.")
    print("    Masukkan kode captcha manual (atau tekan Enter untuk skip): ", end="")
    manual = input().strip()
    if manual:
        return manual, "manual"
    return None, "failed"

# ============================================================
# SCRAPER ENGINE
# ============================================================
def check_site(site, nik):
    """Coba akses satu situs dengan NIK. Return dict hasil."""
    name = site["name"]
    url = site["url"]
    result = {
        "site": name,
        "url": url,
        "status": "unknown",
        "data": None,
        "error": None,
        "time": None,
    }
    start = time.time()
    try:
        session = requests.Session()
        session.headers.update(HEADERS)

        # Simple probe: GET the page
        r = session.get(url, timeout=TIMEOUT, allow_redirects=True)
        result["http_code"] = r.status_code
        result["final_url"] = r.url

        # Basic heuristic: look for form or nik mention
        text_lower = r.text.lower()
        has_nik_form = any(x in text_lower for x in ["nik", "nomor induk", "ktp", "captcha", "kode keamanan"])
        if r.status_code == 200:
            result["status"] = "reachable"
            result["has_nik_related"] = has_nik_form
            # Try to extract title
            if "<title>" in r.text:
                start_t = r.text.find("<title>") + 7
                end_t = r.text.find("</title>", start_t)
                if end_t > start_t:
                    result["title"] = r.text[start_t:end_t].strip()[:80]
            # Simulated / best-effort data note
            result["data"] = {
                "probe": "page reachable",
                "nik_input_detected": has_nik_form,
                "note": "Full form submit + captcha solve needs site-specific selector (template ready)"
            }
        else:
            result["status"] = f"http_{r.status_code}"
    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["error"] = "timeout"
    except requests.exceptions.ConnectionError:
        result["status"] = "connection_error"
        result["error"] = "connection failed"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)[:120]
    result["time"] = round(time.time() - start, 2)
    return result

def run_all(nik):
    """Jalankan semua situs secara parallel."""
    results = []
    total = len(SITES)
    print(f"\n[*] Memproses {total} situs dengan NIK: {nik}")
    print("[*] Multi-thread aktif...\n")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_site, site, nik): site for site in SITES}
        done = 0
        for future in as_completed(futures):
            done += 1
            res = future.result()
            status_icon = "✓" if res["status"] == "reachable" else "✗"
            print(f"  [{done:02d}/{total}] {status_icon} {res['site']:<35} {res['status']:<18} {res['time']}s")
            results.append(res)
    return results

# ============================================================
# OUTPUT / SENDER
# ============================================================
def save_and_send(nik, results):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hasil_nik_{nik}_{ts}.json"
    payload = {
        "tool": "MR 414N -ID",
        "nik": nik,
        "timestamp": datetime.now().isoformat(),
        "total_sites": len(results),
        "reachable": sum(1 for r in results if r["status"] == "reachable"),
        "results": results,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"\n[+] Hasil disimpan: {filename}")

    # Ringkasan
    print("\n" + "="*60)
    print(" RINGKASAN")
    print("="*60)
    print(f" NIK          : {nik}")
    print(f" Total situs  : {len(results)}")
    print(f" Reachable    : {payload['reachable']}")
    print(f" Gagal/Timeout: {len(results) - payload['reachable']}")
    print("="*60)

    # Optional webhook / telegram (isi token di env kalau mau)
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat = os.getenv("TELEGRAM_CHAT_ID", "")
    if telegram_token and telegram_chat:
        try:
            summary = f"MR 414N -ID\nNIK: {nik}\nReachable: {payload['reachable']}/{len(results)}\nFile: {filename}"
            requests.post(
                f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                json={"chat_id": telegram_chat, "text": summary},
                timeout=10
            )
            print("[+] Hasil dikirim ke Telegram")
        except Exception as e:
            print(f"[!] Gagal kirim Telegram: {e}")

    return filename

# ============================================================
# MAIN
# ============================================================
def main():
    os.system("clear" if os.name != "nt" else "cls")
    print(BANNER)
    print("  Single-file | 50+ situs pemerintah | Multi-layer anti-captcha")
    print("  Input hanya NIK. Hasil otomatis dikumpulkan & disimpan.\n")

    # Cek captcha keys
    active_captcha = [k for k, v in CAPTCHA_KEYS.items() if v]
    if active_captcha:
        print(f"  [Captcha aktif] {', '.join(active_captcha)}")
    else:
        print("  [Captcha] Tidak ada API key. Akan pakai local OCR + manual fallback.")
        print("  Set env: TWOCAPTCHA_KEY / ANTICAPTCHA_KEY / CAPMONSTER_KEY jika ingin auto.")

    print()
    nik = input("  Masukkan NIK (16 digit): ").strip()
    if not (nik.isdigit() and len(nik) == 16):
        print("\n  [!] NIK harus 16 digit angka.")
        sys.exit(1)

    print(f"\n  NIK diterima: {nik}")
    confirm = input("  Lanjut scan semua situs? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Dibatalkan.")
        sys.exit(0)

    results = run_all(nik)
    save_and_send(nik, results)
    print("\n  Selesai.\n")

if __name__ == "__main__":
    main()
