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
# 💰 Credit Package များနှင့် ဝယ်ယူနိုင်သည့် စျေးနှုန်းများ
# ============================================================
CREDIT_PACKAGES = {
    "credit50": {"name": "50 Credits", "price": "5000 Ks", "credits": 50},
    "credit100": {"name": "100 Credits", "price": "9000 Ks", "credits": 100},
    "credit200": {"name": "200 Credits", "price": "18000 Ks", "credits": 200},
}

RESELLER_SERVERS = {
    "res1d":  {"name": "🇹🇭 ၁ ရက် စမ်းသပ် (5 Credits)", "credits": 5, "days": 1},
    "res15d": {"name": "🇹🇭 ၁၅ ရက် VPN (25 Credits)", "credits": 25, "days": 15},
    "res30d": {"name": "🇹🇭 ၃၀ ရက် VPN (50 Credits)", "credits": 50, "days": 30},
    "res60d": {"name": "🇹🇭 ၆၀ ရက် VPN (100 Credits)", "credits": 100, "days": 60},
}

SERVERS = {
    "norm1d":  {"name": "🇹🇭 Thailand VPN - ၁ ရက် (စမ်းသပ်)", "price": "1000 Ks", "days": 1},
    "norm15d": {"name": "🇹🇭 Thailand VPN - ၁၅ ရက်", "price": "2500 Ks", "days": 15},
    "norm1m":  {"name": "🇹🇭 Thailand VPN - ၁ လ (၃၀ ရက်)", "price": "5000 Ks", "days": 30},
    "norm2m":  {"name": "🇹🇭 Thailand VPN - ၂ လ (၆၀ ရက်)", "price": "9000 Ks", "days": 60},
}

user_data = {}

# 🚨 ဒေတာ သိမ်းဆည်းရန် ဖိုင်များ
CREDIT_FILE = "reseller_credits.json"
JOINED_FILE = "joined_users.json"

user_credits = {}
user_names = {}
joined_users = set()

def load_data():
    global user_credits, user_names, joined_users
    try:
        if os.path.exists(CREDIT_FILE):
            with open(CREDIT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                user_credits = data.get("credits", {})
                user_names = data.get("names", {})
                
        if os.path.exists(JOINED_FILE):
            with open(JOINED_FILE, "r", encoding="utf-8") as f:
                joined_users = set(json.load(f))
    except Exception as e:
        print(f"Data Load Error: {e}")

def save_data():
    try:
        with open(CREDIT_FILE, "w", encoding="utf-8") as f:
            json.dump({"credits": user_credits, "names": user_names}, f, ensure_ascii=False, indent=4)
        with open(JOINED_FILE, "w", encoding="utf-8") as f:
            json.dump(list(joined_users), f)
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
    # 🚨 မှတ်တမ်းဖိုင်ထဲမှာ ရှိရင် တိုက်ရိုက် ဖြတ်မယ်
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
def auto_create_vless_account(username, days):
    try:
        session = requests.Session()
        session.verify = False
        
        login_url = f"{PANEL_URL}/{WEB_BASE_PATH}/login"
        login_data = {"username": PANEL_USER, "password": PANEL_PASS}
        
        login_res = session.post(login_url, json=login_data, timeout=15)
        
        if login_res.status_code != 200 or not login_res.json().get("success"):
            return False, "Login မအောင်မြင်ပါ။"

        expire_time = int((datetime.datetime.now() + datetime.timedelta(days=days)).timestamp() * 1000)
        new_uuid = str(uuid.uuid4())
        
        add_url = f"{PANEL_URL}/{WEB_BASE_PATH}/panel/api/inbounds/addClient"
        
        settings_data = {
            "clients": [{
                "id": new_uuid,
                "flow": "",
                "email": username,
                "limitIp": 1, 
                "totalGB": 0,
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
            return True, vless_link
        else:
            if "Duplicate email" in response.text:
                return False, "Duplicate"
            return False, f"Error: {response.text}"
            
    except Exception as e:
        return False, str(e)

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
        
        if res_list.status_code != 200:
            return False, "Inbound စာရင်း ဆွဲယူလို့မရပါ။"

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
# 📱 Telegram Bot Handlers
# ============================================================

def show_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🛒 သာမန်ဝယ်ယူရန် (Normal)", callback_data="menu_normal"))
    markup.add(types.InlineKeyboardButton(text="💼 Reseller ဝယ်ယူရန် (Credit)", callback_data="menu_reseller"))
    
    welcome_text = (
        "🌟 **Sky Blue Channel မှ ကြိုဆိုပါတယ်** 🌟\n\n"
        "📌 **စည်းကမ်းချက်များ**\n"
        "🔸 Server error ဖြစ်ပါက 100% တာဝန်ယူပါတယ်။\n"
        "🔸 ဆိုင်ဖက်က VPN ပိတ်ခဲ့ရင် လုံးဝတာဝန်မယူပါ။\n"
        "🔸 တစ်စုံတစ်ရာ ပြဿနာဖြစ်ပါက Owner ဆုံးဖြတ်ချက်အတိုင်း တာဝန်ယူပါသည်။\n\n"
        "🙏 ဝယ်ယူအားပေးမှုကို အထူးကျေးဇူးတင်ပါတယ်။\n\n"
        "👇 ဝယ်ယူရန် ရွေးချယ်ပါ -"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_names[str(user_id)] = message.from_user.full_name
    save_data()
    
    # 🚨 Channel ဝင်ထားခြင်း ရှိ/မရှိ စစ်ဆေးမည်
    if check_join(user_id):
        show_main_menu(message.chat.id)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="📢 Channel Join ရန်", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton(text="✅ Join ပြီးပါပြီ", callback_data="check_join_again"))
        
        bot.send_message(
            message.chat.id, 
            "⚠️ **ကျွန်ုပ်တို့၏ ဝန်ဆောင်မှုကို အသုံးပြုရန် အောက်ပါ Channel ကို Join ပေးပါ။**\n\n"
            "Join ပြီးပါက '✅ Join ပြီးပါပြီ' ကို နှိပ်ပါ။", 
            reply_markup=markup, 
            parse_mode='Markdown'
        )

# --- Admin Commands ---
@bot.message_handler(commands=['help'])
def help_command(message):
    if message.from_user.id != ADMIN_ID: return
    help_text = (
        "🤖 **Admin အတွက် အသုံးပြုနိုင်သော Command များ**\n\n"
        "🔹 **/help** - ဒီစာမျက်နှာကို ဖွင့်ရန်။\n\n"
        "🔹 **/list** - လက်ရှိ ဖန်တီးထားသော VPN အကောင့်စာရင်းနှင့် သက်တမ်းကုန်မည့်ရက်ကို ကြည့်ရန်။\n\n"
        "🔹 **/delete [အကောင့်နာမည်]** - VPN အကောင့်ကို ဖျက်ရန်။ (ဥပမာ - `/delete VIP7_8823368996`)\n\n"
        "🔹 **/credits** - Reseller အားလုံး၏ နာမည်နှင့် လက်ကျန် Credit စာရင်းကို ကြည့်ရန်။\n\n"
        "🔹 **/addcredit [ID] [ပမာဏ]** - လူတစ်ယောက်ကို Credit ဖြည့်ပေးရန်။ (ဥပမာ - `/addcredit 8823368996 50`)\n\n"
        "🔹 **/cutcredit [ID] [ပမာဏ]** - လူတစ်ယောက်ဆီမှ Credit နှုတ်ရန်။ (ဥပမာ - `/cutcredit 8823368996 50`)\n"
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['delete'])
def delete_command(message):
    if message.from_user.id != ADMIN_ID: return
    text_parts = message.text.split()
    if len(text_parts) > 1:
        username = text_parts[1].strip()
        bot.reply_to(message, f"⏳ '{username}' ကို ဖျက်နေသည်...")
        success, result = delete_vless_account(username)
        bot.reply_to(message, f"{'✅' if success else '⚠️'} {result}")
    else:
        msg = bot.reply_to(message, "🗑️ ဖျက်ချင်တဲ့ VPN အကောင့်နာမည်ကို ရိုက်ထည့်ပါ:")
        bot.register_next_step_handler(msg, lambda m: process_delete_account(m, delete_vless_account))

def process_delete_account(message, func):
    if message.text == '/cancel': return
    username = message.text.strip()
    success, result = func(username)
    bot.reply_to(message, f"{'✅' if success else '⚠️'} {result}")

@bot.message_handler(commands=['list'])
def list_vpn_command(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, "⏳ စာရင်း ဆွဲယူနေသည်...")
    try:
        session = requests.Session()
        session.verify = False
        login_url = f"{PANEL_URL}/{WEB_BASE_PATH}/login"
        login_data = {"username": PANEL_USER, "password": PANEL_PASS}
        login_res = session.post(login_url, json=login_data, timeout=15)
        if login_res.status_code != 200 or not login_res.json().get("success"):
            bot.reply_to(message, "Login မအောင်မြင်ပါ။")
            return
        list_url = f"{PANEL_URL}/{WEB_BASE_PATH}/panel/api/inbounds/list"
        res_list = session.get(list_url, timeout=15)
        clients = []
        for inbound in res_list.json().get("obj", []):
            if inbound["id"] == int(INBOUND_ID):
                settings = json.loads(inbound["settings"])
                clients = settings.get("clients", [])
                break
        if not clients:
            bot.reply_to(message, "လက်ရှိတွင် VPN အကောင့် မရှိပါ။")
            return
        msg = "📋 **VPN အကောင့် စာရင်း**\n\n"
        for i, c in enumerate(clients, 1):
            email = c.get("email", "Unknown")
            expiry = c.get("expiryTime", 0)
            if expiry == 0:
                expire_date = "မကုန်ဆုံးပါ"
            else:
                expire_date = datetime.datetime.fromtimestamp(expiry / 1000).strftime('%Y-%m-%d %H:%M')
            msg += f"{i}. `{email}` (ကုန်ဆုံး: {expire_date})\n"
        if len(msg) > 4000:
            for i in range(0, len(msg), 4000):
                bot.send_message(message.chat.id, msg[i:i+4000], parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, msg, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

@bot.message_handler(commands=['credits'])
def list_credits_command(message):
    if message.from_user.id != ADMIN_ID: return
    if not user_credits:
        bot.reply_to(message, "လက်ရှိတွင် Credit ရှိသူ မရှိပါ။")
        return
    text = "💼 **Reseller Credit စာရင်း**\n\n"
    for uid, amount in user_credits.items():
        name = user_names.get(uid, "Unknown")
        text += f"👤 {name}\n🆔 `{uid}`\n💰 Credit: **{amount}**\n\n"
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['addcredit'])
def add_credit_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        target_user = str(parts[1])
        amount = int(parts[2])
        user_credits[target_user] = user_credits.get(target_user, 0) + amount
        save_data()
        bot.reply_to(message, f"✅ User ({target_user}) ဆီသို့ Credit {amount} ဖြည့်ပြီးပါပြီ။\n(လက်ကျန်: {user_credits[target_user]})")
        bot.send_message(target_user, f"🎉 Admin မှ သင့်အကောင့်ထဲသို့ Credit {amount} ဖြည့်သွင်းပေးလိုက်ပါသည်။")
    except:
        bot.reply_to(message, "⚠️ ပုံစံမှားနေပါတယ်။ ဥပမာ - `/addcredit 8823368996 50` လို့ ရိုက်ပါ။")

@bot.message_handler(commands=['cutcredit'])
def cut_credit_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        target_user = str(parts[1])
        amount = int(parts[2])
        current = user_credits.get(target_user, 0)
        if current < amount:
            bot.reply_to(message, f"⚠️ သူ့ဆီမှာ Credit {current} ပဲ ရှိပါတယ်။ နှုတ်လို့မရပါဘူး။")
            return
        user_credits[target_user] = current - amount
        save_data()
        bot.reply_to(message, f"✅ User ({target_user}) ဆီမှ Credit {amount} နှုတ်ပြီးပါပြီ။\n(လက်ကျန်: {user_credits[target_user]})")
        bot.send_message(target_user, f"⚠️ Admin မှ သင့်အကောင့်ထဲမှ Credit {amount} ကို နှုတ်ယူလိုက်ပါသည်။")
    except:
        bot.reply_to(message, "⚠️ ပုံစံမှားနေပါတယ်။ ဥပမာ - `/cutcredit 8823368996 50` လို့ ရိုက်ပါ။")


# ============================================================
# 🎯 Menu နှင့် Callback Handler များ
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data == "check_join_again")
def verify_join(call):
    if check_join(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "အဆင်ပြေပါပြီ။")
        show_main_menu(call.message.chat.id)
    else:
        bot.answer_callback_query(call.id, "❌ Channel ကို Join မထားရသေးပါဘူး။", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "menu_normal")
def menu_normal(call):
    markup = types.InlineKeyboardMarkup()
    for key, info in SERVERS.items():
        btn = types.InlineKeyboardButton(text=f"{info['name']} - {info['price']}", callback_data=f"buy_{key}")
        markup.add(btn)
    markup.add(types.InlineKeyboardButton(text="🔙 နောက်သို့", callback_data="back_to_main"))
    bot.edit_message_text("🛒 **သာမန် VPN ဝယ်ယူရန်**\n\nအောက်ပါ သက်တမ်းများထဲမှ ရွေးချယ်ပါ -", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "menu_reseller")
def menu_reseller(call):
    user_id = str(call.from_user.id)
    credits = user_credits.get(user_id, 0)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🛍️ VPN ဝယ်ယူရန် (Credit ဖြင့်)", callback_data="buy_vpn_with_credit"))
    
    for key, info in CREDIT_PACKAGES.items():
        btn = types.InlineKeyboardButton(text=f"💳 {info['name']} ({info['price']})", callback_data=f"buycredit_{key}")
        markup.add(btn)
        
    markup.add(types.InlineKeyboardButton(text="🔙 နောက်သို့", callback_data="back_to_main"))
    
    text = (
        f"💼 **Reseller စနစ်**\n\n"
        f"💰 သင့်လက်ကျန် Credit: **{credits}**\n\n"
        f"📌 VPN ဝယ်ယူရန် (သို့မဟုတ်) Credit ဖြည့်သွင်းရန် အောက်ပါ ခလုတ်များကို နှိပ်ပါ။\n\n"
        f"👇 ရွေးချယ်ပါ -"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "buy_vpn_with_credit")
def buy_vpn_with_credit_menu(call):
    user_id = str(call.from_user.id)
    credits = user_credits.get(user_id, 0)
    
    markup = types.InlineKeyboardMarkup()
    for key, info in RESELLER_SERVERS.items():
        if credits >= info['credits']:
            btn = types.InlineKeyboardButton(text=f"{info['name']}", callback_data=f"vipbuy_{key}")
            markup.add(btn)
            
    markup.add(types.InlineKeyboardButton(text="🔙 နောက်သို့", callback_data="menu_reseller"))
    
    if not markup.keyboard:
        text = f"⚠️ သင့် Credit ({credits}) က ဝယ်ယူရန် မလုံလောက်ပါ။\nCredit အရင်ဖြည့်ပါ။"
    else:
        text = f"💼 သင့် Credit: **{credits}**\n\nဝယ်ယူလိုသော VPN သက်တမ်းကို ရွေးချယ်ပါ -"
        
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_main_menu(call.message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('buycredit_'))
def process_buy_credit(call):
    key = call.data.replace("buycredit_", "")
    info = CREDIT_PACKAGES.get(key)
    if not info: return
    user_data[call.from_user.id] = ("credit", key)
    text = (f"✅ သင်ရွေးချယ်လိုက်သည်: {info['name']}\n"
            f"💰 ဈေးနှုန်း: {info['price']}\n\n"
            f"📌 ငွေပေးချေရန်:\n\n{PAYMENT_INFO}\n\n"
            f"ငွေလွှဲပြီးပါက ပြေစာ (screenshot) ကို ဤနေရာတွင် ပို့ပါ။")
    bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def process_buy(call):
    key = call.data.replace("buy_", "")
