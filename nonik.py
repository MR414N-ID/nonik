#!/usr/bin/env python3
# nonik.py — termux single-file NIK aggregator
#
# SETUP:
#   pkg update && pkg upgrade -y
#   pkg install python tesseract -y
#   pip install httpx beautifulsoup4 pytesseract cloudscraper pillow
#
# EDIT SECTION 1: ganti url/param tiap target ke endpoint search NIK asli.

# ============================================================
# [SECTION 1] CONFIG
# ============================================================

CAPSOLVER_KEY   = ""
TWOCAPTCHA_KEY  = ""
TELEGRAM_TOKEN  = ""
TELEGRAM_CHAT   = ""

OUTPUT_JSON     = "nik_results.json"
CONCURRENCY     = 10
HTTP_TIMEOUT    = 15
SHOW_FULL_TEXT  = True
MAX_TEXT_CHARS  = 3000

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; SM-A536E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
]

# 50 target — GANTI url ke endpoint search NIK asli per situs.
# field: name, url, method, param, captcha, parser, rate
TARGETS = [
    {"name":"dukcapil_kemendagri",  "url":"https://dukcapil.kemendagri.go.id/",       "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemendagri",           "url":"https://kemendagri.go.id/",                "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenkeu",             "url":"https://kemenkeu.go.id/",                  "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemkes",               "url":"https://kemkes.go.id/",                    "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemdikbud",            "url":"https://kemdikbud.go.id/",                 "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenag",              "url":"https://kemenag.go.id/",                   "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenkumham",          "url":"https://kemenkumham.go.id/",               "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemlu",                "url":"https://kemlu.go.id/",                     "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemhan",               "url":"https://kemhan.go.id/",                    "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenperin",           "url":"https://kemenperin.go.id/",                "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenkop",             "url":"https://kemenkopukm.go.id/",               "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenparekraf",        "url":"https://kemenparekraf.go.id/",             "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenhub",             "url":"https://dephub.go.id/",                    "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenpupr",            "url":"https://pu.go.id/",                        "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenesdm",            "url":"https://esdm.go.id/",                      "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenlhk",             "url":"https://menlhk.go.id/",                    "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenpppa",            "url":"https://kemenpppa.go.id/",                 "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenko_polhukam",     "url":"https://polkam.go.id/",                    "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenko_marves",       "url":"https://maritim.go.id/",                   "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenko_ekon",         "url":"https://ekon.go.id/",                      "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"bappenas",             "url":"https://bappenas.go.id/",                  "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"bkn",                  "url":"https://bkn.go.id/",                       "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"bpjs_kesehatan",       "url":"https://bpjs-kesehatan.go.id/",            "method":"GET","param":"nik","captcha":"recaptcha_v2","parser":"generic","rate":2.0},
    {"name":"bpjs_ketenagakerjaan", "url":"https://bpjsketenagakerjaan.go.id/",       "method":"GET","param":"nik","captcha":"recaptcha_v2","parser":"generic","rate":2.0},
    {"name":"djp_online",           "url":"https://djponline.pajak.go.id/",           "method":"GET","param":"nik","captcha":"recaptcha_v2","parser":"generic","rate":2.0},
    {"name":"pajak",                "url":"https://pajak.go.id/",                     "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"ahu_kemenkumham",      "url":"https://ahu.go.id/",                       "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"imigrasi",             "url":"https://imigrasi.go.id/",                  "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"ssc_kemenkeu",         "url":"https://ssc.kemenkeu.go.id/",              "method":"GET","param":"nik","captcha":"hcaptcha","parser":"generic","rate":2.0},
    {"name":"lpse_lkpp",            "url":"https://lpse.lkpp.go.id/",                 "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"lkpp",                 "url":"https://lkpp.go.id/",                      "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"bssn",                 "url":"https://bssn.go.id/",                      "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kominfo",              "url":"https://kominfo.go.id/",                   "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"brin",                 "url":"https://brin.go.id/",                      "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"bappebti",             "url":"https://bappebti.go.id/",                  "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"bkpm",                 "url":"https://bkpm.go.id/",                      "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"bps",                  "url":"https://bps.go.id/",                       "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"atrbpn",               "url":"https://atrbpn.go.id/",                    "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"beacukai",             "url":"https://beacukai.go.id/",                  "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"ojk",                  "url":"https://ojk.go.id/",                       "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"bi",                   "url":"https://bi.go.id/",                        "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"lps",                  "url":"https://lps.go.id/",                       "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"idx",                  "url":"https://idx.co.id/",                       "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"customs",              "url":"https://customs.go.id/",                   "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenpora",            "url":"https://kemenpora.go.id/",                 "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"komdigi",              "url":"https://komdigi.go.id/",                   "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"setjen_kemenkeu",      "url":"https://setjen.kemenkeu.go.id/",           "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenkeu_djkn",        "url":"https://djkn.kemenkeu.go.id/",             "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenkeu_bppk",        "url":"https://bppk.kemenkeu.go.id/",             "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
    {"name":"kemenkeu_dja",         "url":"https://dja.kemenkeu.go.id/",              "method":"GET","param":"nik","captcha":"none","parser":"generic","rate":1.0},
]

# ============================================================
# [SECTION 2] DEPS
# ============================================================
import sys, importlib
REQUIRED=[
    ("httpx","pip install httpx"),
    ("bs4","pip install beautifulsoup4"),
    ("pytesseract","pip install pytesseract  (pkg install tesseract)"),
    ("cloudscraper","pip install cloudscraper"),
    ("PIL","pip install pillow"),
]
def _has(m):
    try: importlib.import_module(m); return True
    except ImportError: return False
def check_deps():
    miss=[(m,h) for m,h in REQUIRED if not _has(m)]
    if miss:
        print("\n[!] dependency kurang:\n")
        for m,h in miss: print(f"  - {m:<16} → {h}")
        print("\ninstall dulu, jalanin ulang.\n"); sys.exit(1)
check_deps()

# ============================================================
# [SECTION 3] MODELS
# ============================================================
import asyncio, sqlite3, json, time, random, io, re
from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class TargetResult:
    target:str; url:str; status:str; nik:str
    data:dict=field(default_factory=dict)
    error:str=""; elapsed:float=0.0
    timestamp:float=field(default_factory=time.time)

# ============================================================
# [SECTION 4] CAPTCHA
# ============================================================
class BaseSolver:
    name="base"
    async def solve(self,html,sitekey="",siteurl="",img=b""): raise NotImplementedError

class NoSolver(BaseSolver):
    name="none"
    async def solve(self,*a,**k): return None

class Capsolver(BaseSolver):
    def __init__(self,key,kind): self.key=key; self.kind=kind; self.name="capsolver"
    async def solve(self,html,sitekey="",siteurl="",img=b""):
        if not self.key or not sitekey: return None
        import httpx
        typ={"recaptcha_v2":"ReCaptchaV2TaskProxyless","recaptcha_v3":"ReCaptchaV3TaskProxyless",
             "hcaptcha":"HCaptchaTaskProxyless","turnstile":"AntiTurnstileTaskProxyLess"}.get(self.kind,"ReCaptchaV2TaskProxyless")
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r=await c.post("https://api.capsolver.com/createTask",json={"clientKey":self.key,"task":{"type":typ,"websiteURL":siteurl,"websiteKey":sitekey}})
                tid=r.json().get("taskId")
                if not tid: return None
                for _ in range(30):
                    await asyncio.sleep(3)
                    j=(await c.post("https://api.capsolver.com/getTaskResult",json={"clientKey":self.key,"taskId":tid})).json()
                    if j.get("status")=="ready": return j.get("solution",{}).get("gRecaptchaResponse") or j.get("solution",{}).get("token")
                    if j.get("status")=="failed": return None
        except Exception: return None
        return None

class TwoCaptcha(BaseSolver):
    def __init__(self,key,kind): self.key=key; self.kind=kind; self.name="2captcha"
    async def solve(self,html,sitekey="",siteurl="",img=b""):
        if not self.key: return None
        import httpx
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                if img:
                    import base64
                    r=await c.post("https://2captcha.com/in.php",data={"key":self.key,"method":"base64","body":base64.b64encode(img).decode(),"json":1})
                    tid=r.json().get("request")
                    if not tid: return None
                    for _ in range(30):
                        await asyncio.sleep(5)
                        j=(await c.get(f"https://2captcha.com/res.php?key={self.key}&action=get&id={tid}&json=1")).json()
                        if j.get("status")==1: return j.get("request")
                    return None
                meth="userrecaptcha" if "recaptcha" in self.kind else "hcaptcha"
                r=await c.get(f"https://2captcha.com/in.php?key={self.key}&method={meth}&googlekey={sitekey}&pageurl={siteurl}&json=1")
                tid=r.json().get("request")
                if not tid: return None
                for _ in range(30):
                    await asyncio.sleep(5)
                    j=(await c.get(f"https://2captcha.com/res.php?key={self.key}&action=get&id={tid}&json=1")).json()
                    if j.get("status")==1: return j.get("request")
                return None
        except Exception: return None

class Ocr(BaseSolver):
    name="ocr"
    async def solve(self,html,sitekey="",siteurl="",img=b""):
        if not img: return None
        try:
            import pytesseract; from PIL import Image
            im=Image.open(io.BytesIO(img)).convert("L").point(lambda x:0 if x<140 else 255)
            return re.sub(r"\s+","",pytesseract.image_to_string(im,config="--psm 7")) or None
        except Exception: return None

class Math(BaseSolver):
    name="math"
    async def solve(self,html,sitekey="",siteurl="",img=b""):
        m=re.search(r"(\d+)\s*([\+\-\*x])\s*(\d+)\s*=\s*\?",html)
        if not m: return None
        a,op,b=int(m.group(1)),m.group(2),int(m.group(3))
        return str({"+":a+b,"-":a-b,"*":a*b,"x":a*b}[op])

class Cloudflare(BaseSolver):
    name="cloudflare"
    async def solve(self,*a,**k): return None

def build_solver(t):
    t=(t or "none").lower()
    if t=="none": return NoSolver()
    if t=="math": return Math()
    if t=="ocr_image": return Ocr()
    if t=="cloudflare": return Cloudflare()
    if CAPSOLVER_KEY: return Capsolver(CAPSOLVER_KEY,t)
    if TWOCAPTCHA_KEY: return TwoCaptcha(TWOCAPTCHA_KEY,t)
    return NoSolver()

# ============================================================
# [SECTION 5] PROXY
# ============================================================
class ProxyMgr:
    def __init__(self,p=None): self.p=p or []; self.i=0
    def get(self):
        if not self.p: return None
        v=self.p[self.i%len(self.p)]; self.i+=1; return v
    @staticmethod
    def load(path):
        try: return [l.strip() for l in open(path) if l.strip() and not l.startswith("#")]
        except Exception: return []
PROXY=ProxyMgr(ProxyMgr.load("proxies.txt"))

# ============================================================
# [SECTION 6] HTTP — httpx versi baru (proxy singular)
# ============================================================
import httpx
HEADERS={"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
         "Accept-Language":"id-ID,id;q=0.9,en;q=0.8","Connection":"keep-alive"}

async def fetch(client,t,nik):
    h=dict(HEADERS); h["User-Agent"]=random.choice(USER_AGENTS)
    url,method,param=t["url"],t.get("method","GET").upper(),t.get("param","nik")
    if method=="GET":
        r=await client.get(url,params={param:nik},headers=h,timeout=HTTP_TIMEOUT,follow_redirects=True)
    else:
        r=await client.post(url,data={param:nik},headers=h,timeout=HTTP_TIMEOUT,follow_redirects=True)
    if r.status_code in (403,503) and "cf-" in (r.text or "")[:2000].lower():
        r=await _cf(url,method,param,nik,h)
    return r

async def _cf(url,method,param,nik,headers):
    try:
        import cloudscraper
        sc=cloudscraper.create_scraper(browser={"browser":"chrome","platform":"android","mobile":True})
        r=sc.get(url,params={param:nik},headers=headers,timeout=HTTP_TIMEOUT) if method=="GET" else sc.post(url,data={param:nik},headers=headers,timeout=HTTP_TIMEOUT)
        return httpx.Response(r.status_code,content=r.content,headers=dict(r.headers),request=httpx.Request(method,url))
    except Exception:
        return httpx.Response(599,content=b"",request=httpx.Request(method,url))

def _client_kwargs():
    kw={"limits":httpx.Limits(max_keepalive_connections=CONCURRENCY*2,max_connections=CONCURRENCY*4),
        "verify":False,"timeout":HTTP_TIMEOUT,"follow_redirects":True}
    p=PROXY.get()
    if p:
        # httpx baru pakai 'proxy', lama pakai 'proxies'
        try:
            v=httpx.__version__
            major,minor=[int(x) for x in v.split(".")[:2]]
            if (major,minor)>=(0,28): kw["proxy"]=p
            else: kw["proxies"]=p
        except Exception:
            kw["proxy"]=p
    return kw

# ============================================================
# [SECTION 7] PARSER
# ============================================================
from bs4 import BeautifulSoup

def parse_generic(html,url):
    soup=BeautifulSoup(html,"html.parser")
    out={"url":url,"title":"","headings":[],"paragraphs":[],"tables":[],
         "kv_pairs":[],"links":[],"nik_matches":[],"numbers":[],"status_hint":"unknown"}
    if soup.title and soup.title.string: out["title"]=soup.title.string.strip()

    for tag in soup.find_all(["h1","h2","h3","h4"]):
        txt=tag.get_text(" ",strip=True)
        if txt and len(txt)<200: out["headings"].append(txt)

    seen=set()
    for tag in soup.find_all(["p","li","td","span","div","label","strong","b"]):
        txt=tag.get_text(" ",strip=True)
        if 4<len(txt)<500 and txt not in seen and not any(txt in s for s in seen):
            seen.add(txt); out["paragraphs"].append(txt)

    for tbl in soup.find_all("table"):
        rows=[]
        for tr in tbl.find_all("tr"):
            cells=[c.get_text(" ",strip=True) for c in tr.find_all(["td","th"])]
            cells=[c for c in cells if c]
            if cells: rows.append(cells)
        if rows: out["tables"].append(rows)

    for tag in soup.find_all(["label","dt","th","strong","b"]):
        lab=tag.get_text(" ",strip=True).rstrip(":").strip()
        if not (2<len(lab)<60): continue
        sib=tag.find_next_sibling()
        if sib:
            val=sib.get_text(" ",strip=True)
            if 1<len(val)<200: out["kv_pairs"].append({"label":lab,"value":val})

    for a in soup.find_all("a",href=True):
        t=a.get_text(" ",strip=True)
        if t and 2<len(t)<80: out["links"].append({"text":t,"href":a["href"][:200]})

    for m in re.finditer(r"\b\d{16}\b",html):
        if m.group(0) not in out["nik_matches"]: out["nik_matches"].append(m.group(0))

    for kw in ("desil","decile","skor","score","peringkat","rank","kategori","category","status","kelas","golongan","bansos","bantuan"):
        for m in re.finditer(rf"{kw}[^\w]{{0,10}}([0-9]+|[A-Za-z]+)",html,re.I):
            entry=f"{kw}: {m.group(1)}"
            if entry not in out["numbers"]: out["numbers"].append(entry)

    body=re.sub(r"\s+"," ",soup.get_text(" ")).lower()
    if any(w in body for w in ("tidak ditemukan","not found","tidak terdaftar","data tidak ada")):
        out["status_hint"]="not_found"
    elif any(w in body for w in ("ditemukan","found","terdaftar","berhasil")):
        out["status_hint"]="found"

    if SHOW_FULL_TEXT:
        full=re.sub(r"\s+"," ",soup.get_text(" ")).strip()
        out["full_text"]=full[:MAX_TEXT_CHARS]
    return out

PARSERS={"generic":parse_generic}

# ============================================================
# [SECTION 8] STORAGE
# ============================================================
def init_db(path="nik_results.db"):
    c=sqlite3.connect(path)
    c.execute("""CREATE TABLE IF NOT EXISTS results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,timestamp REAL,target TEXT,url TEXT,
        status TEXT,nik TEXT,elapsed REAL,error TEXT,data TEXT)""")
    c.commit(); return c

def save(con,r):
    con.execute("INSERT INTO results(timestamp,target,url,status,nik,elapsed,error,data) VALUES(?,?,?,?,?,?,?,?)",
                (r.timestamp,r.target,r.url,r.status,r.nik,r.elapsed,r.error,json.dumps(r.data,ensure_ascii=False)))
    con.commit()

# ============================================================
# [SECTION 9] ORCHESTRATOR
# ============================================================
async def run_one(client,sem,t,nik):
    async with sem:
        t0=time.time(); res=TargetResult(target=t["name"],url=t["url"],status="fail",nik=nik)
        try:
            solver=build_solver(t.get("captcha","none"))
            resp=await fetch(client,t,nik)
            if solver.name in ("math","ocr","capsolver","2captcha"):
                tok=await solver.solve(resp.text,siteurl=t["url"])
                if tok: res.data["captcha_token"]=tok[:24]+"..."
            if resp.status_code>=400:
                res.status="blocked" if resp.status_code in (403,429) else "fail"
                res.error=f"http {resp.status_code}"; res.elapsed=time.time()-t0; return res
            parser=PARSERS.get(t.get("parser","generic"),parse_generic)
            res.data=parser(resp.text,str(resp.url)); res.status="ok"
        except Exception as e:
            res.error=f"{type(e).__name__}: {e}"
        res.elapsed=time.time()-t0
        await asyncio.sleep(t.get("rate",1.0))
        return res

async def run_all(nik,on_done):
    sem=asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient(**_client_kwargs()) as client:
        tasks=[asyncio.create_task(run_one(client,sem,t,nik)) for t in TARGETS]
        for c in asyncio.as_completed(tasks):
            on_done(await c)

# ============================================================
# [SECTION 10] DISPLAY
# ============================================================
def print_full_result(r:TargetResult,idx:int,total:int):
    flag={"ok":"✅","blocked":"🚫","fail":"❌","skipped":"⏭️"}.get(r.status,"•")
    print("\n"+"═"*60)
    print(f"{flag} [{idx}/{total}] {r.target} — {r.status} ({r.elapsed:.1f}s)")
    print(f"   {r.url}")
    if r.error: print(f"   error: {r.error}")
    if r.status!="ok" or not r.data: return
    d=r.data
    if d.get("title"): print(f"\n   📄 title: {d['title']}")
    if d.get("status_hint") and d["status_hint"]!="unknown": print(f"   📊 status: {d['status_hint']}")
    if d.get("nik_matches"): print(f"\n   🔢 NIK ditemukan: {', '.join(d['nik_matches'][:5])}")
    if d.get("numbers"):
        print("\n   📈 angka/kategori:")
        for n in d["numbers"][:15]: print(f"      • {n}")
    if d.get("kv_pairs"):
        print("\n   🏷️ label → value:")
        for kv in d["kv_pairs"][:20]: print(f"      • {kv['label']}: {kv['value'][:80]}")
    if d.get("tables"):
        print("\n   📋 tabel:")
        for ti,tbl in enumerate(d["tables"][:3]):
            print(f"      [tabel {ti+1}]")
            for row in tbl[:10]: print("        | "+" | ".join(c[:30] for c in row))
    if d.get("headings"):
        print("\n   🔖 headings:")
        for h in d["headings"][:10]: print(f"      • {h[:100]}")
    if d.get("paragraphs"):
        print("\n   📝 teks:")
        for p in d["paragraphs"][:15]: print(f"      • {p[:160]}")
    if d.get("full_text"):
        print("\n   📃 full text:")
        print("      "+d["full_text"][:1200])

def print_header(nik):
    print("="*60)
    print(f"  NIK AGGREGATOR — {len(TARGETS)} situs")
    print(f"  NIK: {nik}")
    print("="*60)

def print_summary(results):
    ok=sum(1 for r in results if r.status=="ok")
    print("\n"+"═"*60)
    print(f"  RINGKASAN: {ok}/{len(results)} ok")
    for r in results:
        flag={"ok":"✅","blocked":"🚫","fail":"❌"}.get(r.status,"•")
        hint=r.data.get("status_hint","") if r.status=="ok" else r.error
        print(f"   {flag} {r.target:<28} {r.status:<8} {hint}")
    print("═"*60)

# ============================================================
# [SECTION 11] DELIVERY + MAIN
# ============================================================
async def send_tg(nik,results):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT: return False
    lines=[f"🔎 NIK: {nik}",f"hasil: {sum(1 for r in results if r.status=='ok')}/{len(results)}",""]
    for r in results:
        flag={"ok":"✅","blocked":"🚫","fail":"❌"}.get(r.status,"•")
        lines.append(f"{flag} {r.target} — {r.status}")
        if r.status=="ok" and r.data.get("status_hint"): lines.append(f"   {r.data['status_hint']}")
        if r.status=="ok" and r.data.get("kv_pairs"):
            for kv in r.data["kv_pairs"][:3]: lines.append(f"   {kv['label']}: {kv['value'][:40]}")
    try:
        async with httpx.AsyncClient(timeout=20) as c:
            await c.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                         json={"chat_id":TELEGRAM_CHAT,"text":"\n".join(lines)[:3800]})
        return True
    except Exception: return False

def save_json(nik,results,path=OUTPUT_JSON):
    with open(path,"w",encoding="utf-8") as f:
        json.dump({"nik":nik,"generated_at":time.time(),
                   "results":[asdict(r) for r in results]},f,indent=2,ensure_ascii=False)
    return path

def main():
    if not TARGETS:
        print("[!] TARGETS kosong."); return
    print_header("—")
    try: nik=input("masukkan NIK (16 digit): ").strip()
    except (EOFError,KeyboardInterrupt): print("\nbatal."); return
    if not re.fullmatch(r"\d{16}",nik): print("[!] NIK harus 16 digit."); return

    print_header(nik)
    con=init_db(); results=[]; idx=0; total=len(TARGETS)

    def on_done(r):
        nonlocal idx
        idx+=1; results.append(r); save(con,r)
        print_full_result(r,idx,total)

    print(f"\n[~] scanning {total} situs...")
    asyncio.run(run_all(nik,on_done))

    print_summary(results)
    print(f"\n[+] json arsip: {save_json(nik,results)}")
    print(f"[+] telegram: {'terkirim' if asyncio.run(send_tg(nik,results)) else 'skip'}")
    con.close()

if __name__=="__main__":
    try: main()
    except KeyboardInterrupt: print("\n\ninterrupted.")
