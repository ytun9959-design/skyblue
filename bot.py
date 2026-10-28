import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

import telebot
from telebot import types
import requests
import uuid
import datetime
import json
import urllib3
import os
import time
import threading

# SSL Warning ပိတ်ခြင်း
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================================
# ⚙️ ဆက်တင်များ
# ============================================================
BOT_TOKEN = "8765335393:AAFbRmIL8QM_tFS_yVzPlCnxl9XwElUAcOc"
ADMIN_ID = 5617375002

CHANNEL_LINK = "https://t.me/Skyblue021"
CHANNEL_USERNAME = "@Skyblue021" 

PAYMENT_INFO = (
    "💳 **ငွေလွှဲရန် အကောင့်များ**\n\n"
    "**Wave Pay** ✅\n"
    "အမည်: Sai Htet Aung\n"
    "ဖုန်း: 09898122462\n\n"
    "**KBZ Pay** ✅\n"
    "အမည်: Daw Thar HTAY\n"
    "ဖုန်း: 09426694626"
)

PANEL_URL = "https://119.10.142.16:37789"  
WEB_BASE_PATH = "X5JAs7BeSKXU038"          
PANEL_USER = "admin"
PANEL_PASS = "admin123"
INBOUND_ID = 1 

SERVER_IP = "119.10.142.16"
SERVER_PORT = "80"
PATH = "/"
HOST = "portal-as.ruijienetworks.com"

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
# 💰 ဈေးနှုန်းသတ်မှတ်ချက်များ
# ============================================================
CREDIT_PACKAGES = {
    "credit50": {"name": "50 Credits", "price": "5000 Ks", "credits": 50},
    "credit100": {"name": "100 Credits", "price": "9000 Ks", "credits": 100},
    "credit200": {"name": "200 Credits", "price": "18000 Ks", "credits": 200},
}

RESELLER_SERVERS = {
    "res1d":  {"name": "🇹🇭 ၁ ရက် စမ်းသပ် (5 Credits - 5GB)", "credits": 5, "days": 1, "gb": 5},
    "res15d": {"name": "🇹🇭 ၁၅ ရက် VPN (25 Credits - 30GB)", "credits": 25, "days": 15, "gb": 30},
    "res30d": {"name": "🇹🇭 ၃၀ ရက် VPN (50 Credits - 60GB)", "credits": 50, "days": 30, "gb": 60},
}

SERVERS = {
    "norm1d":  {"name": "🇹🇭 Thailand VPN - ၁ ရက် (5GB)", "price": "1000 Ks", "days": 1, "gb": 5},
    "norm15d": {"name": "🇹🇭 Thailand VPN - ၁၅ ရက် (30GB)", "price": "2500 Ks", "days": 15, "gb": 30},
    "norm1m":  {"name": "🇹🇭 Thailand VPN - ၁ လ (60GB)", "price": "5000 Ks", "days": 30, "gb": 60},
    "norm2m":  {"name": "🇹🇭 Thailand VPN - ၂ လ (120GB)", "price": "9000 Ks", "days": 60, "gb": 120},
}

user_data = {}

# 🚨 ဒေတာ သိမ်းဆည်းရန် ဖိုင်များ
CREDIT_FILE = "reseller_credits.json"
JOINED_FILE = "joined_users.json"
VPN_DATA_FILE = "vpn_accounts.json"

user_credits = {}
user_names = {}
joined_users = set()
vpn_accounts = {} 

def load_data():
    global user_credits, user_names, joined_users, vpn_accounts
    try:
        if os.path.exists(CREDIT_FILE):
            with open(CREDIT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                user_credits = data.get("credits", {})
                user_names = data.get("names", {})
                
        if os.path.exists(JOINED_FILE):
            with open(JOINED_FILE, "r", encoding="utf-8") as f:
                joined_users = set(json.load(f))
                
        if os.path.exists(VPN_DATA_FILE):
            with open(VPN_DATA_FILE, "r", encoding="utf-8") as f:
                vpn_accounts = json.load(f)
    except Exception as e:
        print(f"Data Load Error: {e}")

def save_data():
    try:
        with open(CREDIT_FILE, "w", encoding="utf-8") as f:
            json.dump({"credits": user_credits, "names": user_names}, f, ensure_ascii=False, indent=4)
        with open(JOINED_FILE, "w", encoding="utf-8") as f:
            json.dump(list(joined_users), f)
        with open(VPN_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(vpn_accounts, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Data Save Error: {e}")

load_data()

# ============================================================
# 🔢 နံပါတ် ထုတ်ပေးမည့် Function
# ============================================================
def get_next_vip_number():
    filename = "vip_count.txt"
    try:
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                f.write("7")
            return 7
        
        with open(filename, "r") as f:
            current_num = int(f.read().strip())
        
        next_num = current_num + 1
        with open(filename, "w") as f:
            f.write(str(next_num))
        
        return current_num
    except:
        return 99

# ============================================================
# 🛠️ Channel Join စစ်ဆေးသည့် Function
# ============================================================
def check_join(user_id):
    if str(user_id) in joined_users:
        return True
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            joined_users.add(str(user_id))
            save_data()
            return True
        return False
    except Exception as e:
        print(f"Join Check Error: {e}")
        return False
# ============================================================
# 🛠️ Panel Login ဝင်ပြီး အကောင့်ဖန်တီးမည့် Function
# ============================================================
def auto_create_vless_account(username, days, gb):
    try:
        session = requests.Session()
        session.verify = False
        
        login_url = f"{PANEL_URL}/{WEB_BASE_PATH}/login"
        login_data = {"username": PANEL_USER, "password": PANEL_PASS}
        
        login_res = session.post(login_url, json=login_data, timeout=15)
        
        if login_res.status_code != 200 or not login_res.json().get("success"):
            return False, "Login မအောင်မြင်ပါ။", None

        expire_time = int((datetime.datetime.now() + datetime.timedelta(days=days)).timestamp() * 1000)
        new_uuid = str(uuid.uuid4())
        
        total_gb_bytes = int(gb) * 1073741824 
        
        add_url = f"{PANEL_URL}/{WEB_BASE_PATH}/panel/api/inbounds/addClient"
        
        settings_data = {
            "clients": [{
                "id": new_uuid,
                "flow": "",
                "email": username,
                "limitIp": 1, 
                "totalGB": total_gb_bytes, 
                "expiryTime": expire_time,
                "enable": True,
                "tgId": "",
                "subId": username
            }]
        }
        
        payload = {
            "id": int(INBOUND_ID),
            "settings": json.dumps(settings_data, ensure_ascii=True)
        }
        
        headers = {"Content-Type": "application/json"}
        response = session.post(add_url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200 and response.json().get("success"):
            vless_link = f"vless://{new_uuid}@{SERVER_IP}:{SERVER_PORT}?type=ws&encryption=none&path={PATH}&host={HOST}&security=none#{username}"
            return True, vless_link, expire_time
        else:
            if "Duplicate email" in response.text:
                return False, "Duplicate", None
            return False, f"Error: {response.text}", None
            
    except Exception as e:
        return False, str(e), None

# ============================================================
# 📊 လက်ကျန် Data စစ်ဆေးသည့် Function (ဖိုင်နာမည် ရှာဖွေမှုပါဝင်သည်)
# ============================================================
def get_remaining_data(user_id, search_email=None):
    if not search_email and (str(user_id) not in vpn_accounts or not vpn_accounts[str(user_id)]):
        return "⚠️ သင့်တွင် VPN အကောင့် မရှိပါ။\n(သို့မဟုတ်) ဖိုင်နာမည်ဖြင့် ရှာလိုပါက `/find ဖိုင်နာမည်` ဟု ရိုက်ပါ။"
        
    try:
        session = requests.Session()
        session.verify = False
        
        login_url = f"{PANEL_URL}/{WEB_BASE_PATH}/login"
        login_data = {"username": PANEL_USER, "password": PANEL_PASS}
        login_res = session.post(login_url, json=login_data, timeout=15)
        
        if login_res.status_code != 200 or not login_res.json().get("success"):
            return "⚠️ Panel Login မအောင်မြင်ပါ။"

        list_url = f"{PANEL_URL}/{WEB_BASE_PATH}/panel/api/inbounds/list"
        res_list = session.get(list_url, timeout=15)
        
        clients = []
        for inbound in res_list.json().get("obj", []):
            if inbound["id"] == int(INBOUND_ID):
                settings = json.loads(inbound["settings"])
                clients = settings.get("clients", [])
                break
                
        text = "📊 **သင့် VPN အကောင့် အခြေအနေ**\n\n"
        found = False
        
        # 🚨 ကိုယ်တိုင် ရိုက်ထည့်ပြီး ရှာတဲ့အခါ
        if search_email:
            for c in clients:
                if search_email.lower() in c.get("email", "").lower():
                    found = True
                    email = c.get("email")
                    total_bytes = c.get("totalGB", 0)
                    up_bytes = c.get("up", 0)
                    down_bytes = c.get("down", 0)
                    
                    total_gb = total_bytes / 1073741824
                    used_gb = (up_bytes + down_bytes) / 1073741824
                    remaining_gb = total_gb - used_gb
                    if remaining_gb < 0: remaining_gb = 0
                    
                    expiry = c.get("expiryTime", 0)
                    if expiry == 0:
                        exp_date = "မကုန်ဆုံးပါ"
                    else:
                        exp_utc = datetime.datetime.fromtimestamp(expiry / 1000, tz=datetime.timezone.utc)
                        exp_mm = exp_utc + datetime.timedelta(hours=6, minutes=30)
                        exp_date = exp_mm.strftime('%Y-%m-%d %H:%M')
                    
                    text += (
                        f"📁 **ဖိုင်နာမည်:** `{email}`\n"
                        f"📅 **ကုန်ဆုံးမည့်ရက်:** {exp_date}\n"
                        f"📦 **သတ်မှတ် Data:** {total_gb:.2f} GB\n"
                        f"📉 **သုံးပြီး:** {used_gb:.2f} GB\n"
                        f"✅ **လက်ကျန်:** **{remaining_gb:.2f} GB**\n\n"
                    )
            if not found:
                return f"❌ `{search_email}` ဆိုတဲ့ ဖိုင်နာမည်ကို ရှာမတွေ့ပါ။ ပြန်စစ်ပြီး ရိုက်ထည့်ပါ။"
                
        # 🚨 ဝယ်ထားတဲ့ ဖိုင်နာမည်တွေကို ပြမယ်
        else:
            for acc in vpn_accounts[str(user_id)]:
                email = acc.get("email")
                
                client_data = None
                for c in clients:
                    if c.get("email") == email:
                        client_data = c
                        break
                        
                if not client_data:
                    text += f"❌ **ဖိုင်နာမည်:** `{email}` (ဖျက်ခံထားရသည် / မတွေ့ပါ)\n\n"
                    continue
                    
                total_bytes = client_data.get("totalGB", 0)
                up_bytes = client_data.get("up", 0)
                down_bytes = client_data.get("down", 0)
                
                total_gb = total_bytes / 1073741824
                used_gb = (up_bytes + down_bytes) / 1073741824
                remaining_gb = total_gb - used_gb
                
                if remaining_gb < 0: remaining_gb = 0
                
                expiry = client_data.get("expiryTime", 0)
                if expiry == 0:
                    exp_date = "မကုန်ဆုံးပါ"
                else:
                    exp_utc = datetime.datetime.fromtimestamp(expiry / 1000, tz=datetime.timezone.utc)
                    exp_mm = exp_utc + datetime.timedelta(hours=6, minutes=30)
                    exp_date = exp_mm.strftime('%Y-%m-%d %H:%M')
                
                text += (
                    f"📁 **ဖိုင်နာမည်:** `{email}`\n"
                    f"📅 **ကုန်ဆုံးမည့်ရက်:** {exp_date}\n"
                    f"📦 **သတ်မှတ် Data:** {total_gb:.2f} GB\n"
                    f"📉 **သုံးပြီး:** {used_gb:.2f} GB\n"
                    f"✅ **လက်ကျန်:** **{remaining_gb:.2f} GB**\n\n"
                )
            
            text += "💡 **မှတ်ချက်** - သင့်ဖိုင်နာမည်ကို ရှာလိုပါက အောက်ပါအတိုင်း ရိုက်ထည့်ပါ။\n`/find VIP7_5617375002`"
            
        return text
    except Exception as e:
        return f"⚠️ Error: {e}"

# 🚨 ဖိုင်နာမည် ရိုက်ထည့်ပြီး ရှာသည့် Command
@bot.message_handler(commands=['find'])
def find_file_command(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ ဖိုင်နာမည် ရိုက်ထည့်ပါ။ (ဥပမာ - `/find VIP7_5617375002`)")
            return
        
        search_name = parts[1].strip()
        bot.reply_to(message, "⏳ ဖိုင်နာမည် ရှာဖွေနေသည်...")
        
        user_id = message.from_user.id
        text = get_remaining_data(user_id, search_email=search_name)
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

# ============================================================
# 🗑️ အကောင့်ဖျက်မည့် Function
# ============================================================
def delete_vless_account(username):
    try:
        session = requests.Session()
        session.verify = False
        
        login_url = f"{PANEL_URL}/{WEB_BASE_PATH}/login"
        login_data = {"username": PANEL_USER, "password": PANEL_PASS}
        login_res = session.post(login_url, json=login_data, timeout=15)
        
        if login_res.status_code != 200 or not login_res.json().get("success"):
            return False, "Login မအောင်မြင်ပါ။"

        list_url = f"{PANEL_URL}/{WEB_BASE_PATH}/panel/api/inbounds/list"
        res_list = session.get(list_url, timeout=15)
        
        clients = []
        for inbound in res_list.json().get("obj", []):
            if inbound["id"] == int(INBOUND_ID):
                settings = json.loads(inbound["settings"])
                clients = settings.get("clients", [])
                break
        
        target_uuid = None
        for client in clients:
            if client.get("email") == username:
                target_uuid = client.get("id")
                break
        
        if not target_uuid:
            return False, f"'{username}' ဆိုတဲ့ အကောင့်ကို ရှာမတွေ့ပါ။"

        del_url = f"{PANEL_URL}/{WEB_BASE_PATH}/panel/api/inbounds/{INBOUND_ID}/delClient/{target_uuid}"
        res_del = session.post(del_url, timeout=15)
        
        if res_del.status_code == 200 and res_del.json().get("success"):
            return True, f"'{username}' အကောင့်ကို အောင်မြင်စွာ ဖျက်လိုက်ပါပြီ။"
        else:
            return False, f"ဖျက်လို့မရပါ: {res_del.text}"
            
    except Exception as e:
        return False, str(e)

# ============================================================
# 📊 လက်ကျန် Data စစ်ဆေးသည့် Function (အချိန်ဇုန် အတိအကျ)
# ============================================================
def get_remaining_data(user_id, search_email=None):
    if not search_email and (str(user_id) not in vpn_accounts or not vpn_accounts[str(user_id)]):
        return "⚠️ သင့်တွင် VPN အကောင့် မရှိပါ။\n(သို့မဟုတ်) ဖိုင်နာမည်ဖြင့် ရှာလိုပါက အောက်ပါအတိုင်း ရိုက်ထည့်ပါ။"
        
    try:
        session = requests.Session()
        session.verify = False
        
        login_url = f"{PANEL_URL}/{WEB_BASE_PATH}/login"
        login_data = {"username": PANEL_USER, "password": PANEL_PASS}
        login_res = session.post(login_url, json=login_data, timeout=15)
        
        if login_res.status_code != 200 or not login_res.json().get("success"):
            return "⚠️ Panel Login မအောင်မြင်ပါ။"

        list_url = f"{PANEL_URL}/{WEB_BASE_PATH}/panel/api/inbounds/list"
        res_list = session.get(list_url, timeout=15)
        
        clients = []
        for inbound in res_list.json().get("obj", []):
            if inbound["id"] == int(INBOUND_ID):
                settings = json.loads(inbound["settings"])
                clients = settings.get("clients", [])
                break
                
        text = "📊 **သင့် VPN အကောင့် အခြေအနေ**\n\n"
        found = False
        
        # 🚨 ကိုယ်တိုင် ရိုက်ထည့်ပြီး ရှာတဲ့အခါ
        if search_email:
            for c in clients:
                if search_email.lower() in c.get("email", "").lower():
                    found = True
                    email = c.get("email")
                    total_bytes = c.get("totalGB", 0)
                    up_bytes = c.get("up", 0)
                    down_bytes = c.get("down", 0)
                    
                    total_gb = total_bytes / 1073741824
                    used_gb = (up_bytes + down_bytes) / 1073741824
                    remaining_gb = total_gb - used_gb
                    if remaining_gb < 0: remaining_gb = 0
                    
                    expiry = c.get("expiryTime", 0)
                    if expiry == 0:
                        exp_date = "မကုန်ဆုံးပါ"
                    else:
                        exp_utc = datetime.datetime.fromtimestamp(expiry / 1000, tz=datetime.timezone.utc)
                        exp_mm = exp_utc + datetime.timedelta(hours=6, minutes=30)
                        exp_date = exp_mm.strftime('%Y-%m-%d %H:%M')
                    
                    text += (
                        f"📁 **ဖိုင်နာမည်:** `{email}`\n"
                        f"📅 **ကုန်ဆုံးမည့်ရက်:** {exp_date}\n"
                        f"📦 **သတ်မှတ် Data:** {total_gb:.2f} GB\n"
                        f"📉 **သုံးပြီး:** {used_gb:.2f} GB\n"
                        f"✅ **လက်ကျန်:** **{remaining_gb:.2f} GB**\n\n"
                    )
            if not found:
                return f"❌ `{search_email}` ဆိုတဲ့ ဖိုင်နာမည်ကို ရှာမတွေ့ပါ။ ပြန်စစ်ပြီး ရိုက်ထည့်ပါ။"
                
        # 🚨 ဝယ်ထားတဲ့ ဖိုင်နာမည်တွေကို ပြမယ်
        else:
            for acc in vpn_accounts[str(user_id)]:
                email = acc.get("email")
                
                client_data = None
                for c in clients:
                    if c.get("email") == email:
                        client_data = c
                        break
                        
                if not client_data:
                    text += f"❌ **ဖိုင်နာမည်:** `{email}` (ဖျက်ခံထားရသည် / မတွေ့ပါ)\n\n"
                    continue
                    
                total_bytes = client_data.get("totalGB", 0)
                up_bytes = client_data.get("up", 0)
                down_bytes = client_data.get("down", 0)
                
                total_gb = total_bytes / 1073741824
                used_gb = (up_bytes + down_bytes) / 1073741824
                remaining_gb = total_gb - used_gb
                
                if remaining_gb < 0: remaining_gb = 0
                
                expiry = client_data.get("expiryTime", 0)
                if expiry == 0:
                    exp_date = "မကုန်ဆုံးပါ"
                else:
                    exp_utc = datetime.datetime.fromtimestamp(expiry / 1000, tz=datetime.timezone.utc)
                    exp_mm = exp_utc + datetime.timedelta(hours=6, minutes=30)
                    exp_date = exp_mm.strftime('%Y-%m-%d %H:%M')
                
                text += (
                    f"📁 **ဖိုင်နာမည်:** `{email}`\n"
                    f"📅 **ကုန်ဆုံးမည့်ရက်:** {exp_date}\n"
                    f"📦 **သတ်မှတ် Data:** {total_gb:.2f} GB\n"
                    f"📉 **သုံးပြီး:** {used_gb:.2f} GB\n"
                    f"✅ **လက်ကျန်:** **{remaining_gb:.2f} GB**\n\n"
                )
            
            text += "💡 **မှတ်ချက်** - သင့်ဖိုင်နာမည်ကို ရှာလိုပါက အောက်ပါအတိုင်း ရိုက်ထည့်ပါ။\n`/find VIP7_5617375002`"
            
        return text
    except Exception as e:
        return f"⚠️ Error: {e}"

# 🚨 ဖိုင်နာမည် ရိုက်ထည့်ပြီး ရှာသည့် Command
@bot.message_handler(commands=['find'])
def find_file_command(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ ဖိုင်နာမည် ရိုက်ထည့်ပါ။ (ဥပမာ - `/find VIP7_5617375002`)")
            return
        
        search_name = parts[1].strip()
        bot.reply_to(message, "⏳ ဖိုင်နာမည် ရှာဖွေနေသည်...")
        
        user_id = message.from_user.id
        text = get_remaining_data(user_id, search_email=search_name)
        bot.send_message(message.chat.id, text, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

# ============================================================
# 🎯 Menu နှင့် Callback Handler များ
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data == "check_data")
def check_data_menu(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id, "⏳ Data စစ်ဆေးနေသည်...")
    text = get_remaining_data(user_id)
    bot.send_message(call.message.chat.id, text, parse_mode='Markdown')
