#!/usr/bin/env python3
# nik_aggregator.py
# Single-file NIK aggregator for Termux.
#
# SETUP (jalankan sekali di Termux):
#   pkg update && pkg upgrade -y
#   pkg install python tesseract -y
#   pip install httpx beautifulsoup4 dnspython pytesseract cloudscraper curl_cffi
#
# CONFIG: edit bagian SECTION 1 (API keys, telegram, targets).

# ============================================================
# [SECTION 1] CONFIG
# ============================================================

CAPSOLVER_KEY   = ""          # https://capsolver.com — isi kalau punya
TWOCAPTCHA_KEY  = ""          # https://2captcha.com — isi kalau punya
TELEGRAM_TOKEN  = ""          # bot token dari @BotFather
TELEGRAM_CHAT   = ""          # chat id / @channel

OUTPUT_DB       = "nik_results.db"
OUTPUT_JSON     = "nik_results.json"
CONCURRENCY     = 10
HTTP_TIMEOUT    = 15
MAX_RETRIES     = 2

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; SM-A536E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
]

# 50 target placeholder — EDIT sesuai situs yang kamu mau.
# field: name, url, method, param, captcha, parser, rate
TARGETS = [
    {"name": "dukcapil_kemendagri",  "url": "https://dukcapil.kemendagri.go.id/",        "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemendagri",           "url": "https://kemendagri.go.id/",                 "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenkeu",             "url": "https://kemenkeu.go.id/",                   "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenkes",             "url": "https://kemkes.go.id/",                     "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemdikbud",            "url": "https://kemdikbud.go.id/",                  "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenag",              "url": "https://kemenag.go.id/",                    "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenkumham",          "url": "https://kemenkumham.go.id/",                "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenlu",              "url": "https://kemlu.go.id/",                      "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenhan",             "url": "https://kemhan.go.id/",                     "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenperin",           "url": "https://kemenperin.go.id/",                 "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenkop",             "url": "https://kemenkopukm.go.id/",                "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenparekraf",        "url": "https://kemenparekraf.go.id/",              "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenhub",             "url": "https://dephub.go.id/",                     "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenpupr",            "url": "https://pu.go.id/",                         "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenesdm",            "url": "https://esdm.go.id/",                       "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenlhk",             "url": "https://menlhk.go.id/",                     "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenpppa",            "url": "https://kemenpppa.go.id/",                  "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenko_polhukam",     "url": "https://polkam.go.id/",                     "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenko_marves",       "url": "https://maritim.go.id/",                    "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenko_ekon",         "url": "https://ekon.go.id/",                       "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "bappenas",             "url": "https://bappenas.go.id/",                   "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "bkn",                  "url": "https://bkn.go.id/",                        "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "bpjs_kesehatan",       "url": "https://bpjs-kesehatan.go.id/",             "method": "GET",  "param": "nik", "captcha": "recaptcha_v2","parser": "generic", "rate": 2.0},
    {"name": "bpjs_ketenagakerjaan", "url": "https://bpjsketenagakerjaan.go.id/",        "method": "GET",  "param": "nik", "captcha": "recaptcha_v2","parser": "generic", "rate": 2.0},
    {"name": "djp_online",           "url": "https://djponline.pajak.go.id/",            "method": "GET",  "param": "nik", "captcha": "recaptcha_v2","parser": "generic", "rate": 2.0},
    {"name": "pajak",                "url": "https://pajak.go.id/",                      "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "ahu_kemenkumham",      "url": "https://ahu.go.id/",                        "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "imigrasi",             "url": "https://imigrasi.go.id/",                   "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "ssc_kemenkeu",         "url": "https://ssc.kemenkeu.go.id/",               "method": "GET",  "param": "nik", "captcha": "hcaptcha",   "parser": "generic", "rate": 2.0},
    {"name": "lpse",                 "url": "https://lpse.lkpp.go.id/",                  "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "lkpp",                 "url": "https://lkpp.go.id/",                       "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "bssn",                 "url": "https://bssn.go.id/",                       "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kominfo",              "url": "https://kominfo.go.id/",                    "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "brin",                 "url": "https://brin.go.id/",                       "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "bappebti",             "url": "https://bappebti.go.id/",                   "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "bkpm",                 "url": "https://bkpm.go.id/",                       "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "bps",                  "url": "https://bps.go.id/",                        "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "bpn",                  "url": "https://atrbpn.go.id/",                     "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenkeu_djp_pajak",   "url": "https://www.pajak.go.id/",                  "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenperin_bea",       "url": "https://beacukai.go.id/",                   "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "ojk",                  "url": "https://ojk.go.id/",                        "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "bi",                   "url": "https://bi.go.id/",                         "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "lps",                  "url": "https://lps.go.id/",                        "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "idx",                  "url": "https://idx.co.id/",                        "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenkeu_bea",         "url": "https://customs.go.id/",                    "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenpora",            "url": "https://kemenpora.go.id/",                  "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenparekraf_bekraf", "url": "https://bekraf.go.id/",                     "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenpppa_dp3a",       "url": "https://dp3a.go.id/",                       "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kominfo_komdigi",      "url": "https://komdigi.go.id/",                    "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
    {"name": "kemenkeu_setjen",      "url": "https://setjen.kemenkeu.go.id/",            "method": "GET",  "param": "nik", "captcha": "none",       "parser": "generic", "rate": 1.0},
]

# ============================================================
# [SECTION 2] DEPENDENCY CHECK
# ============================================================

import sys, importlib

REQUIRED = [
    ("httpx",            "pip install httpx"),
    ("bs4",              "pip install beautifulsoup4"),
    ("dnspython",        "pip install dnspython"),
    ("pytesseract",      "pip install pytesseract  (butuh: pkg install tesseract)"),
    ("cloudscraper",     "pip install cloudscraper"),
    ("curl_cffi",        "pip install curl_cffi"),
    ("PIL",              "pip install pillow"),
]

def check_deps():
    missing = []
    for mod, hint in REQUIRED:
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append((mod, hint))
    if missing:
        print("\n[!] dependency kurang:\n")
        for m, h in missing:
            print(f"  - {m:<16} → {h}")
        print("\ninstall dulu, terus jalanin ulang.\n")
        sys.exit(1)

check_deps()

# ============================================================
# [SECTION 3] DATA MODELS
# ============================================================

import asyncio, sqlite3, json, time, random, io, re
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import urlparse

@dataclass
class TargetResult:
    target: str
    url: str
    status: str            # ok | fail | blocked | skipped
    nik: str
    data: dict = field(default_factory=dict)
    error: str = ""
    elapsed: float = 0.0
    timestamp: float = field(default_factory=time.time)

# ============================================================
# [SECTION 4] CAPTCHA SOLVERS
# ============================================================

class BaseSolver:
    name = "base"
    async def solve(self, page_html: str, sitekey: str = "", siteurl: str = "", img_bytes: bytes = b"") -> Optional[str]:
        raise NotImplementedError

class NoSolver(BaseSolver):
    name = "none"
    async def solve(self, *a, **k):
        return None

class CapsolverSolver(BaseSolver):
    name = "capsolver"
    def __init__(self, key: str, kind: str):
        self.key = key
        self.kind = kind  # recaptcha_v2 / hcaptcha / turnstile

    async def solve(self, page_html, sitekey="", siteurl="", img_bytes=b""):
        if not self.key or not sitekey:
            return None
        import httpx
        typ = {
            "recaptcha_v2": "ReCaptchaV2TaskProxyless",
            "recaptcha_v3": "ReCaptchaV3TaskProxyless",
            "hcaptcha":     "HCaptchaTaskProxyless",
            "turnstile":    "AntiTurnstileTaskProxyLess",
        }.get(self.kind, "ReCaptchaV2TaskProxyless")
        payload = {"clientKey": self.key, "task": {"type": typ, "websiteURL": siteurl, "websiteKey": sitekey}}
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post("https://api.capsolver.com/createTask", json=payload)
                tid = r.json().get("taskId")
                if not tid:
                    return None
                for _ in range(30):
                    await asyncio.sleep(3)
                    r = await c.post("https://api.capsolver.com/getTaskResult", json={"clientKey": self.key, "taskId": tid})
                    j = r.json()
                    if j.get("status") == "ready":
                        return j.get("solution", {}).get("gRecaptchaResponse") or j.get("solution", {}).get("token")
                    if j.get("status") == "failed":
                        return None
        except Exception:
            return None
        return None

class TwoCaptchaSolver(BaseSolver):
    name = "2captcha"
    def __init__(self, key: str, kind: str):
        self.key = key
        self.kind = kind

    async def solve(self, page_html, sitekey="", siteurl="", img_bytes=b""):
        if not self.key:
            return None
        import httpx
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                # image captcha
                if img_bytes:
                    import base64
                    r = await c.post("https://2captcha.com/in.php", data={
                        "key": self.key, "method": "base64",
                        "body": base64.b64encode(img_bytes).decode(), "json": 1
                    })
                    tid = r.json().get("request")
                    if not tid:
                        return None
                    for _ in range(30):
                        await asyncio.sleep(5)
                        r = await c.get(f"https://2captcha.com/res.php?key={self.key}&action=get&id={tid}&json=1")
                        j = r.json()
                        if j.get("status") == 1:
                            return j.get("request")
                    return None
                # token captcha
                meth = "userrecaptcha" if "recaptcha" in self.kind else "hcaptcha"
                r = await c.get(f"https://2captcha.com/in.php?key={self.key}&method={meth}&googlekey={sitekey}&pageurl={siteurl}&json=1")
                tid = r.json().get("request")
                if not tid:
                    return None
                for _ in range(30):
                    await asyncio.sleep(5)
                    r = await c.get(f"https://2captcha.com/res.php?key={self.key}&action=get&id={tid}&json=1")
                    j = r.json()
                    if j.get("status") == 1:
                        return j.get("request")
                return None
        except Exception:
            return None

class OcrSolver(BaseSolver):
    name = "ocr"
    async def solve(self, page_html, sitekey="", siteurl="", img_bytes=b""):
        if not img_bytes:
            return None
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(io.BytesIO(img_bytes)).convert("L")
            img = img.point(lambda x: 0 if x < 140 else 255)
            txt = pytesseract.image_to_string(img, config="--psm 7 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ").strip()
            return re.sub(r"\s+", "", txt) or None
        except Exception:
            return None

class MathSolver(BaseSolver):
    name = "math"
    async def solve(self, page_html, sitekey="", siteurl="", img_bytes=b""):
        m = re.search(r"(\d+)\s*([\+\-\*x])\s*(\d+)\s*=\s*\?", page_html)
        if not m:
            return None
        a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
        return str({"+" : a+b, "-": a-b, "*": a*b, "x": a*b}[op])

class CloudflareSolver(BaseSolver):
    name = "cloudflare"
    async def solve(self, page_html, sitekey="", siteurl="", img_bytes=b""):
        # handled at engine level via cloudscraper — solver stub
        return None

def build_solver(captcha_type: str) -> BaseSolver:
    ct = (captcha_type or "none").lower()
    if ct == "none":
        return NoSolver()
    if ct == "math":
        return MathSolver()
    if ct == "ocr_image":
        return OcrSolver()
    if ct == "cloudflare":
        return CloudflareSolver()
    # token-based, prefer capsolver then 2captcha
    if CAPSOLVER_KEY:
        return CapsolverSolver(CAPSOLVER_KEY, ct)
    if TWOCAPTCHA_KEY:
        return TwoCaptchaSolver(TWOCAPTCHA_KEY, ct)
    return NoSolver()

# ============================================================
# [SECTION 5] PROXY MANAGER (optional)
# ============================================================

class ProxyManager:
    def __init__(self, proxies: list[str] | None = None):
        self.proxies = proxies or []
        self.idx = 0

    def get(self) -> Optional[str]:
        if not self.proxies:
            return None
        p = self.proxies[self.idx % len(self.proxies)]
        self.idx += 1
        return p

    @staticmethod
    def load_from_file(path: str) -> list[str]:
        try:
            with open(path) as f:
                return [l.strip() for l in f if l.strip() and not l.startswith("#")]
        except Exception:
            return []

PROXY_MGR = ProxyManager(ProxyManager.load_from_file("proxies.txt"))

# ============================================================
# [SECTION 6] HTTP ENGINE
# ============================================================

import httpx

HEADERS_BASE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

def _rand_ua() -> str:
    return random.choice(USER_AGENTS)

async def fetch(client: httpx.AsyncClient, target: dict, nik: str) -> httpx.Response:
    h = dict(HEADERS_BASE)
    h["User-Agent"] = _rand_ua()

    url = target["url"]
    method = target.get("method", "GET").upper()
    param = target.get("param", "nik")

    if method == "GET":
        resp = await client.get(url, params={param: nik}, headers=h, timeout=HTTP_TIMEOUT, follow_redirects=True)
    else:
        resp = await client.post(url, data={param: nik}, headers=h, timeout=HTTP_TIMEOUT, follow_redirects=True)

    # Cloudflare check
    if resp.status_code in (403, 503) and "cf-" in (resp.text or "")[:2000].lower():
        resp = await _try_cloudscraper(url, method, param, nik, h)
    return resp

async def _try_cloudscraper(url, method, param, nik, headers):
    try:
        import cloudscraper
        sc = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "mobile": True})
        if method == "GET":
            r = sc.get(url, params={param: nik}, headers=headers, timeout=HTTP_TIMEOUT)
        else:
            r = sc.post(url, data={param: nik}, headers=headers, timeout=HTTP_TIMEOUT)
        return httpx.Response(r.status_code, content=r.content, headers=dict(r.headers), request=httpx.Request(method, url))
    except Exception:
        return httpx.Response(599, content=b"", request=httpx.Request(method, url))

# ============================================================
# [SECTION 7] PARSERS
# ============================================================

from bs4 import BeautifulSoup

def parse_generic(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.string or "").strip() if soup.title else ""
    body_text = re.sub(r"\s+", " ", soup.get_text(" ")).strip()[:4000]

    # heuristic extraction of NIK-like / name / address fields
    out = {"title": title, "text_sample": body_text}
    m = re.search(r"\b(\d{16})\b", html)
    if m:
        out["nik_found"] = m.group(1)
    for label in ("nama", "name", "alamat", "address", "tanggal lahir", "birth"):
        pat = re.compile(rf"{label}[^\w]{{0,6}}([A-Za-z0-9 ,\.\-/]{{2,80}})", re.I)
        mm = pat.search(body_text)
        if mm:
            out[label] = mm.group(1).strip()
    # status keyword
    txt_low = body_text.lower()
    if any(w in txt_low for w in ("tidak ditemukan", "not found", "tidak terdaftar")):
        out["status_hint"] = "not_found"
    elif any(w in txt_low for w in ("ditemukan", "found", "terdaftar")):
        out["status_hint"] = "found"
    else:
        out["status_hint"] = "unknown"
    return out

PARSERS = {
    "generic": parse_generic,
}

# ============================================================
# [SECTION 8] STORAGE
# ============================================================

def init_db(path: str = OUTPUT_DB):
    con = sqlite3.connect(path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL, target TEXT, url TEXT, status TEXT,
            nik TEXT, elapsed REAL, error TEXT, data TEXT
        )
    """)
    con.commit()
    return con

def save_result(con, r: TargetResult):
    con.execute(
        "INSERT INTO results (timestamp,target,url,status,nik,elapsed,error,data) VALUES (?,?,?,?,?,?,?,?)",
        (r.timestamp, r.target, r.url, r.status, r.nik, r.elapsed, r.error, json.dumps(r.data, ensure_ascii=False))
    )
    con.commit()

# ============================================================
# [SECTION 9] ORCHESTRATOR
# ============================================================

async def run_target(client: httpx.AsyncClient, sem: asyncio.Semaphore, target: dict, nik: str) -> TargetResult:
    async with sem:
        t0 = time.time()
        res = TargetResult(target=target["name"], url=target["url"], status="fail", nik=nik)
        try:
            solver = build_solver(target.get("captcha", "none"))

            # pre-solve math / ocr if the page needs it (needs a GET first)
            resp = await fetch(client, target, nik)
            if solver.name in ("math", "ocr", "capsolver", "2captcha"):
                token = await solver.solve(resp.text, siteurl=target["url"])
                if token:
                    res.data["captcha_token"] = token[:24] + "..."

            if resp.status_code >= 400:
                res.status = "blocked" if resp.status_code in (403, 429) else "fail"
                res.error = f"http {resp.status_code}"
                res.elapsed = time.time() - t0
                return res

            parser = PARSERS.get(target.get("parser", "generic"), parse_generic)
            res.data = parser(resp.text, str(resp.url))
            res.status = "ok"
        except Exception as e:
            res.error = f"{type(e).__name__}: {e}"
        res.elapsed = time.time() - t0
        # rate-limit per target
        await asyncio.sleep(target.get("rate", 1.0))
        return res

async def run_all(nik: str, on_result):
    sem = asyncio.Semaphore(CONCURRENCY)
    limits = httpx.Limits(max_keepalive_connections=CONCURRENCY * 2, max_connections=CONCURRENCY * 4)
    proxy = PROXY_MGR.get()
    async with httpx.AsyncClient(limits=limits, proxies=proxy, verify=False) as client:
        tasks = [asyncio.create_task(run_target(client, sem, t, nik)) for t in TARGETS]
        for coro in asyncio.as_completed(tasks):
            r = await coro
            on_result(r)

# ============================================================
# [SECTION 10] DELIVERY (telegram / print / file)
# ============================================================

async def deliver_telegram(con, nik: str, results: list[TargetResult]):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        return False
    ok_count = sum(1 for r in results if r.status == "ok")
    lines = [f"🔎 NIK: {nik}", f"✅ {ok_count}/{len(results)} ok", ""]
    for r in results:
        flag = {"ok": "✅", "blocked": "🚫", "skipped": "⏭️", "fail": "❌"}.get(r.status, "•")
        lines.append(f"{flag} {r.target} — {r.status} ({r.elapsed:.1f}s)")
        if r.status == "ok" and r.data.get("status_hint"):
            lines.append(f"   ↳ {r.data['status_hint']}")
        if r.status == "ok" and r.data.get("nama"):
            lines.append(f"   ↳ nama: {r.data['nama'][:40]}")
    text = "\n".join(lines)[:3800]
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            await c.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT, "text": text, "disable_web_page_preview": True}
            )
        return True
    except Exception:
        return False

def save_json(nik: str, results: list[TargetResult], path: str = OUTPUT_JSON):
    payload = {"nik": nik, "generated_at": time.time(), "results": [asdict(r) for r in results]}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return path

# ============================================================
# [SECTION 11] UI + MAIN
# ============================================================

def banner():
    print("=" * 48)
    print("  NIK AGGREGATOR  —  termux edition")
    print(f"  targets: {len(TARGETS)}")
    print("=" * 48)
    print()

def validate_nik(nik: str) -> bool:
    return bool(re.fullmatch(r"\d{16}", nik))

def main():
    banner()
    try:
        nik = input("masukkan NIK (16 digit): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nbatal.")
        return

    if not validate_nik(nik):
        print("[!] NIK harus 16 digit angka.")
        return

    con = init_db()
    results: list[TargetResult] = []
    done = 0

    def on_result(r: TargetResult):
        nonlocal done
        done += 1
        results.append(r)
        save_result(con, r)
        flag = {"ok": "✅", "blocked": "🚫", "skipped": "⏭️", "fail": "❌"}.get(r.status, "•")
        print(f"  [{done:>2}/{len(TARGETS)}] {flag} {r.target:<28} {r.status:<8} {r.elapsed:.1f}s")

    print(f"\n[~] scanning {len(TARGETS)} situs...\n")
    asyncio.run(run_all(nik, on_result))

    print("\n[~] menyusun hasil...")
    path = save_json(nik, results)
    print(f"[+] json: {path}")

    sent = asyncio.run(deliver_telegram(con, nik, results))
    print(f"[+] telegram: {'terkirim' if sent else 'tidak dikonfigurasi'}")

    ok = sum(1 for r in results if r.status == "ok")
    print(f"\n[done] {ok}/{len(results)} situs mengembalikan data.")
    print(f"       db: {OUTPUT_DB}")

    con.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\ninterrupted.")
