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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================================
# ⚙️ သင့် Japan VPS အသစ်၏ အချက်အလက်များ
# ============================================================
BOT_TOKEN = "8609181446:AAFVndFscKHkqr6OgdmRXnvjWcQ6gRTfNq0"
ADMIN_ID = 5617375002
ADMIN_CONTACT = "@Kenobe21" 

# 🚨 သင့် Channel နဲ့ Bot လင့်ခ်
CHANNEL_LINK = "https://t.me/Skyblue021"
CHANNEL_USERNAME = "@Skyblue021"
BOT_LINK = "https://t.me/SkyBlueVpn0912_bot?start=" 

# 🚨 Japan VPS ၏ Panel အချက်အလက်များ (အသစ်ပြောင်းထားသည်)
PANEL_URL = "https://172.238.20.21:21117"  
WEB_BASE_PATH = "KvpUWFyN7fHaUAh"     
PANEL_USER = "SHGLCix5OL"
PANEL_PASS = "QMiK9qxMEr" 
INBOUND_ID = 1 

SERVER_IP = "172.238.20.21"
SERVER_PORT = "8080" 
PATH = "/skyblue"     
HOST = "portal-as.ruijienetworks.com" 

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
# 💰 Coin နှင့် ဈေးနှုန်းများ
# ============================================================
COIN_PER_JOIN = 2 

SERVERS = {
    "coin1d":  {"name": "🇯🇵 ၁ ရက် VPN (10 Coin)", "coin": 10, "days": 1, "gb": 5},
    "coin3d":  {"name": "🇯🇵 ၃ ရက် VPN (30 Coin)", "coin": 30, "days": 3, "gb": 10},
    "coin7d":  {"name": "🇯🇵 ၇ ရက် VPN (60 Coin)", "coin": 60, "days": 7, "gb": 20},
    "coin10d": {"name": "🇯🇵 ၁၀ ရက် VPN (100 Coin)", "coin": 100, "days": 10, "gb": 30},
}

user_data = {}

# 🚨 ဒေတာ သိမ်းဆည်းရန် ဖိုင်များ (Coin များ မပျောက်စေရန်)
DB_FILE = "users_coin.json"
HISTORY_FILE = "purchase_history.json"
users_db = {} 
purchase_history = [] 

def load_data():
    global users_db, purchase_history
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                users_db = json.load(f)
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                purchase_history = json.load(f)
    except Exception as e:
        print(f"Data Load Error: {e}")

def save_data():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users_db, f, ensure_ascii=False, indent=4)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(purchase_history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Data Save Error: {e}")

load_data()

# ============================================================
# 🛠️ Functions
# ============================================================
def check_join(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Join Check Error: {e}")
        return False

def auto_create_vless_account(username, days, gb):
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
            return True, vless_link
        else:
            if "Duplicate email" in response.text:
                return False, "Duplicate"
            return False, f"Error: {response.text}"
            
    except Exception as e:
        return False, str(e)

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
# 📱 Telegram Bot Handlers
# ============================================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    
    if user_id not in users_db:
        users_db[user_id] = {"coins": 0, "joined": False, "referred_by": None, "vpn": []}
    
    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id != user_id and users_db[user_id]["referred_by"] is None:
            users_db[user_id]["referred_by"] = referrer_id
            save_data()
            try:
                if referrer_id in users_db:
                    users_db[referrer_id]["coins"] += COIN_PER_JOIN
                    save_data()
                    bot.send_message(referrer_id, f"🎉 သင့်လင့်ခ်မှတစ်ဆင့် လူတစ်ယောက်ဝင်လာပါပြီ။\n💰 +{COIN_PER_JOIN} Coins ရရှိပါပြီ။")
            except:
                pass

    if users_db[user_id]["joined"]:
        show_main_menu(message.chat.id, user_id)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="📢 Channel Join ရန်", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton(text="✅ Join ပြီးပါပြီ", callback_data="check_join"))
        
        bot.send_message(
            message.chat.id, 
            "⚠️ **ကျွန်ုပ်တို့၏ ဝန်ဆောင်မှုကို အသုံးပြုရန် အောက်ပါ Channel ကို Join ပေးပါ။**\n\n"
            "Join ပြီးပါက '✅ Join ပြီးပါပြီ' ကို နှိပ်ပါ။", 
            reply_markup=markup, 
            parse_mode='Markdown'
        )

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def verify_join(call):
    user_id = str(call.from_user.id)
    if check_join(call.from_user.id):
        users_db[user_id]["joined"] = True
        save_data()
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "အဆင်ပြေပါပြီ။ ကြိုဆိုပါတယ်။")
        show_main_menu(call.message.chat.id, user_id)
    else:
        bot.answer_callback_query(call.id, "❌ Channel ကို Join မထားရသေးပါဘူး။", show_alert=True)

def show_main_menu(chat_id, user_id):
    coins = users_db[user_id]["coins"]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🛒 Coin ဖြင့် VPN ဝယ်ရန်", callback_data="buy_vpn"))
    markup.add(types.InlineKeyboardButton(text="🔗 သူငယ်ချင်းဖိတ်ခေါ်ရန် (Link ယူရန်)", callback_data="get_ref_link"))
    
    welcome_text = (
        "🌟 **Sky Blue Coin & VPN Bot မှ ကြိုဆိုပါတယ်** 🌟\n\n"
        f"💰 **သင့်လက်ကျန် Coin:** {coins} 🪙\n\n"
        "📌 **အသုံးပြုနည်း**\n"
        f"၁။ သူငယ်ချင်းများကို ဖိတ်ခေါ်ပြီး Coin ရယူပါ။ (၁ ယောက် = {COIN_PER_JOIN} Coin)\n"
        "၂။ ရရှိထားသော Coin များဖြင့် VPN လင့်ခ်များ ဝယ်ယူပါ။\n\n"
        f"👨‍💻 **အကူအညီလိုပါက ဆက်သွယ်ရန်:** {ADMIN_CONTACT}\n\n"
        "👇 ရွေးချယ်ပါ -"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "get_ref_link")
def get_ref_link(call):
    user_id = str(call.from_user.id)
    ref_link = f"{BOT_LINK}{user_id}"
    
    text = (
        "🔗 **သင့်ရဲ့ ဖိတ်ခေါ်လင့်ခ်**\n\n"
        f"`{ref_link}`\n\n"
        f"*(ဒီလင့်ခ်ကို ကူးယူပြီး သူငယ်ချင်းများကို ပို့ပေးပါ။ သူတို့ဝင်လာတိုင်း သင့်အကောင့်ထဲကို Coin {COIN_PER_JOIN} ခု အလိုအလျောက် ရောက်သွားပါမယ်။)*"
    )
    bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "buy_vpn")
def buy_vpn_menu(call):
    user_id = str(call.from_user.id)
    coins = users_db[user_id]["coins"]
    
    markup = types.InlineKeyboardMarkup()
    for key, info in SERVERS.items():
        if coins >= info["coin"]:
            markup.add(types.InlineKeyboardButton(text=info["name"], callback_data=f"buycoin_{key}"))
        else:
            markup.add(types.InlineKeyboardButton(text=f"🔒 {info['name']} (Coin မလုံလောက်ပါ)", callback_data="not_enough"))
            
    markup.add(types.InlineKeyboardButton(text="🔙 နောက်သို့", callback_data="back_main"))
    
    bot.edit_message_text(
        f"🛒 **VPN ဝယ်ယူရန်**\n\n💰 သင့် Coin: {coins} 🪙\n\nအောက်ပါ သက်တမ်းများထဲမှ ရွေးချယ်ပါ -",
        call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data == "not_enough")
def not_enough(call):
    bot.answer_callback_query(call.id, "❌ သင့် Coin မလုံလောက်သေးပါ။ သူငယ်ချင်းများကို ဖိတ်ခေါ်ပြီး Coin ရယူပါ။", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('buycoin_'))
def process_buy_coin(call):
    key = call.data.replace("buycoin_", "")
    info = SERVERS.get(key)
    user_id = str(call.from_user.id)
    
    if not info: return
    
    coins = users_db[user_id]["coins"]
    if coins < info["coin"]:
        bot.answer_callback_query(call.id, "❌ Coin မလုံလောက်ပါ။", show_alert=True)
        return
    
    bot.answer_callback_query(call.id, "⏳ VPN အကောင့် ဖန်တီးနေသည်...")
    
    users_db[user_id]["coins"] -= info["coin"]
    save_data()
    
    username = f"COIN_{user_id}_{int(time.time())}"
    success, result = auto_create_vless_account(username, info["days"], info["gb"])

    if success:
        users_db[user_id]["vpn"].append({
            "email": username,
            "link": result,
            "days": info["days"],
            "gb": info["gb"]
        })
        
        purchase_history.append({
            "user_id": user_id,
            "username": username,
            "days": info["days"],
            "gb": info["gb"],
            "coin": info["coin"],
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        save_data()
        
        bot.send_message(
            call.message.chat.id, 
            f"🎉 သင့် VPN အကောင့် အဆင်သင့်ဖြစ်ပါပြီ!\n\n"
            f"📄 လင့်ခ်:\n`{result}`\n\n"
            f"💰 လက်ကျန် Coin: **{users_db[user_id]['coins']}** 🪙\n\n"
            f"*(နောက်ပိုင်းကျရင် Server အသစ်တွေ တိုးပေးပါမယ်နော်။)*", 
            parse_mode='Markdown'
        )
        try:
            bot.send_message(ADMIN_ID, f"🔔 Coin နဲ့ ဝယ်ယူမှု\n👤 ID: {user_id}\n🎫 အကောင့်: {username}\n💰 ကျန်ရှိ Coin: {users_db[user_id]['coins']}")
        except:
            pass
    else:
        users_db[user_id]["coins"] += info["coin"]
        save_data()
        bot.send_message(call.message.chat.id, f"⚠️ Error: အကောင့်ဖန်တီးမရပါ။ Coin ပြန်အမ်းပြီးပါပြီ။\n{result}")

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back_main(call):
    user_id = str(call.from_user.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_main_menu(call.message.chat.id, user_id)
# ============================================================
# 🚨 Admin Commands
# ============================================================
@bot.message_handler(commands=['help'])
def help_command(message):
    if message.from_user.id != ADMIN_ID: 
        bot.reply_to(message, "❌ ဒီ Command ကို Admin ပဲ အသုံးပြုခွင့်ရှိပါတယ်။")
        return
        
    help_text = (
        "🤖 **Admin အတွက် အသုံးပြုနိုင်သော Command များ**\n\n"
        "🔹 **/help** - ဒီစာမျက်နှာကို ဖွင့်ရန်။\n\n"
        "🔹 **/list** - VPS အတွင်းရှိ VPN အကောင့်စာရင်းနှင့် သက်တမ်းကုန်မည့်ရက်ကို ကြည့်ရန်။\n\n"
        "🔹 **/delete [အကောင့်နာမည်]** - VPN အကောင့်ကို ဖျက်ရန်။ (ဥပမာ - `/delete COIN_5617375002_1699999`)\n\n"
        "🔹 **/addcoin [User_ID] [Coin]** - လူတစ်ယောက်ကို Coin ဖြည့်ပေးရန်။ (ဥပမာ - `/addcoin 8823368996 50`)\n\n"
        "🔹 **/cutcoin [User_ID] [Coin]** - လူတစ်ယောက်ဆီမှ Coin နှုတ်ရန်။ (ဥပမာ - `/cutcoin 8823368996 50`)\n\n"
        "🔹 **/history** - ဝယ်ယူမှု မှတ်တမ်းများကို ကြည့်ရန်။"
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['list'])
def list_vpn_command(message):
    if message.from_user.id != ADMIN_ID: return
    bot.reply_to(message, "⏳ VPS အတွင်းမှ အကောင့်စာရင်းကို ဆွဲယူနေသည်...")
    try:
        session = requests.Session()
        session.verify = False
        login_url = f"{PANEL_URL}/{WEB_BASE_PATH}/login"
        login_data = {"username": PANEL_USER, "password": PANEL_PASS}
        login_res = session.post(login_url, json=login_data, timeout=15)
        
        if login_res.status_code != 200 or not login_res.json().get("success"):
            bot.reply_to(message, "❌ Panel Login မအောင်မြင်ပါ။")
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
            bot.reply_to(message, "📁 လက်ရှိတွင် VPS အတွင်း VPN အကောင့် (Client) မရှိပါ။")
            return
            
        msg = f"📋 **VPS အတွင်း VPN အကောင့် စာရင်း (စုစုပေါင်း - {len(clients)} ခု)**\n\n"
        for i, c in enumerate(clients, 1):
            email = c.get("email", "Unknown")
            expiry = c.get("expiryTime", 0)
            if expiry == 0:
                expire_date = "မကုန်ဆုံးပါ"
            else:
                exp_utc = datetime.datetime.fromtimestamp(expiry / 1000, tz=datetime.timezone.utc)
                exp_mm = exp_utc + datetime.timedelta(hours=6, minutes=30)
                expire_date = exp_mm.strftime('%Y-%m-%d %H:%M')
                
            total_gb = c.get("totalGB", 0) / 1073741824
            msg += f"{i}. `{email}` (ကုန်ဆုံး: {expire_date}) | Data: {total_gb:.1f} GB\n"
            
        if len(msg) > 4000:
            for i in range(0, len(msg), 4000):
                bot.send_message(message.chat.id, msg[i:i+4000], parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, msg, parse_mode='Markdown')
            
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

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
        msg = bot.reply_to(message, "🗑️ ဖျက်ချင်တဲ့ အကောင့်နာမည် (ဖိုင်နာမည်) ကို ရိုက်ထည့်ပါ:")
        bot.register_next_step_handler(msg, lambda m: process_delete_account(m, delete_vless_account))

def process_delete_account(message, func):
    if message.text == '/cancel': return
    username = message.text.strip()
    success, result = func(username)
    bot.reply_to(message, f"{'✅' if success else '⚠️'} {result}")

@bot.message_handler(commands=['addcoin'])
def add_coin_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        target_user = str(parts[1])
        amount = int(parts[2])
        
        if target_user in users_db:
            users_db[target_user]["coins"] += amount
            save_data()
            bot.reply_to(message, f"✅ User ({target_user}) ဆီသို့ Coin {amount} ဖြည့်ပေးလိုက်ပါပြီ။\n(လက်ကျန်: {users_db[target_user]['coins']})")
            try:
                bot.send_message(target_user, f"🎉 Admin မှ သင့်အကောင့်ထဲသို့ Coin {amount} လက်ဆောင်ပေးလိုက်ပါသည်။\n💰 လက်ကျန် Coin: {users_db[target_user]['coins']}")
            except:
                pass
        else:
            users_db[target_user] = {"coins": amount, "joined": False, "referred_by": None, "vpn": []}
            save_data()
            bot.reply_to(message, f"✅ User အသစ် ({target_user}) ကို ဖန်တီးပြီး Coin {amount} ဖြည့်ပေးလိုက်ပါပြီ။")
            try:
                bot.send_message(target_user, f"🎉 Admin မှ သင့်အကောင့်ထဲသို့ Coin {amount} လက်ဆောင်ပေးလိုက်ပါသည်။\n💰 လက်ကျန် Coin: {amount}")
            except:
                pass
                
    except:
        bot.reply_to(message, "⚠️ ပုံစံမှားနေပါတယ်။ ဥပမာ - `/addcoin 8823368996 50` လို့ ရိုက်ပါ။")

@bot.message_handler(commands=['cutcoin'])
def cut_coin_command(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        target_user = str(parts[1])
        amount = int(parts[2])
        
        if target_user in users_db:
            current = users_db[target_user]["coins"]
            if current >= amount:
                users_db[target_user]["coins"] -= amount
                save_data()
                bot.reply_to(message, f"✅ User ({target_user}) ဆီမှ Coin {amount} ကို ဖျက်လိုက်ပါပြီ။\n(လက်ကျန်: {users_db[target_user]['coins']})")
                try:
                    bot.send_message(target_user, f"⚠️ Admin မှ သင့် Coin {amount} ကို ဖျက်လိုက်ပါသည်။")
                except:
                    pass
            else:
                bot.reply_to(message, f"⚠️ သူ့ဆီမှာ Coin {current} ပဲ ရှိပါတယ်။")
        else:
            bot.reply_to(message, "❌ အဲ့ဒီ User ID ကို ရှာမတွေ့ပါ။")
    except:
        bot.reply_to(message, "⚠️ ပုံစံမှားနေပါတယ်။ ဥပမာ - `/cutcoin 8823368996 50` လို့ ရိုက်ပါ။")

@bot.message_handler(commands=['history'])
def history_command(message):
    if message.from_user.id != ADMIN_ID: return
    if not purchase_history:
        bot.reply_to(message, "📁 ဝယ်ယူမှု မှတ်တမ်း မရှိသေးပါ။")
        return
        
    msg = "📋 **ဝယ်ယူမှု မှတ်တမ်း (မကြာသေးမီက)**\n\n"
    for item in purchase_history[-20:]:
        msg += (
            f"👤 User: `{item['user_id']}`\n"
            f"🎫 အကောင့်: `{item['username']}`\n"
            f"📅 ရက်: {item['days']} ရက် | 📦 Data: {item['gb']} GB\n"
            f"💰 Coin: {item['coin']} | 🕒 {item['date']}\n"
            f"--- --- ---\n"
        )
        
    if len(msg) > 4000:
        for i in range(0, len(msg), 4000):
            bot.send_message(message.chat.id, msg[i:i+4000], parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, msg, parse_mode='Markdown')

# ============================================================
# 🚀 Bot စတင်ခြင်း
# ============================================================
if __name__ == '__main__':
    print("🤖 Sky Blue Coin Bot စတင်နေသည်...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Error တက်သွားပါသည်: {e}")
            print("5 စက္ကန့်အတွင်း ပြန်လည် စတင်ပါမည်...")
            time.sleep(5)

