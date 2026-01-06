import telebot
from telebot import types
from pymongo import MongoClient
from flask import Flask
import threading

# ================== SOZLAMALAR ==================

TOKEN = "8556430736:AAG9vvKx9dR7FILftmqB40WPAhjY9uMrZUU"
MONGO_URL = "mongodb+srv://duschanovabushahruhbek_db_user:Yr2rHBfM353STVYw@cluster0.le9wpj4.mongodb.net/?appName=Cluster0"

CHANNELS = [
    "@kino_test_kanallar"
]

VIDEO_CHANNEL = "kinokodi123"  # @siz yoziladi

# ================== BOT ==================

bot = telebot.TeleBot(TOKEN)

# ================== DATABASE ==================

client = MongoClient(MONGO_URL)
db = client["kinochi_bot"]
collection = db["videos"]

# ================== OBUNA TEKSHIRISH ==================

def check_user(user_id):
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

# ================== OBUNA SO‘RASH ==================

def ask_to_subscribe(chat_id):
    markup = types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        markup.add(
            types.InlineKeyboardButton(
                text=ch,
                url=f"https://t.me/{ch[1:]}"
            )
        )
    markup.add(types.InlineKeyboardButton("Tekshirish", callback_data="check"))
    bot.send_message(
        chat_id,
        "Botdan foydalanish uchun kanallarga obuna bo‘ling 👇",
        reply_markup=markup
    )

# ================== START ==================

@bot.message_handler(commands=["start"])
def start(message):
    if check_user(message.from_user.id):
        bot.send_message(message.chat.id, "Kod yuboring (1–100)")
    else:
        ask_to_subscribe(message.chat.id)

# ================== CALLBACK ==================

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_callback(call):
    if check_user(call.from_user.id):
        bot.send_message(call.message.chat.id, "Endi kod yuborishingiz mumkin")
    else:
        bot.send_message(call.message.chat.id, "Hali obuna bo‘lmagansiz")

# ================== KANALDAN VIDEO USHLASH ==================

# @bot.channel_post_handler(content_types=["video"])
# def save_video(message):
#     if message.chat.username == VIDEO_CHANNEL:
#         if message.caption and "Kod:" in message.caption:
#             try:
#                 code = int(message.caption.replace("Kod:", "").strip())
#                 collection.update_one(
#                     {"code": code},
#                     {"$set": {
#                         "code": code,
#                         "file_id": message.video.file_id,
#                         "caption": message.caption
#                     }},
#                     upsert=True
#                 )
#             except:
#                 pass

@bot.channel_post_handler(content_types=["video"])
def save_video(message):
    print("KANAL POST KELDI")  # <-- MUHIM
    print(message.chat.username)
    print(message.caption)

    if message.chat.username == "kinokodi123":
        if message.caption and "Kod:" in message.caption:
            code = int(message.caption.replace("Kod:", "").strip())
            collection.insert_one({
                "code": code,
                "file_id": message.video.file_id,
                "caption": message.caption
            })
            print("DB GA SAQLANDI:", code)


# ================== FOYDALANUVCHI KOD YUBORSA ==================

@bot.message_handler(func=lambda message: True)
def get_video(message):
    if not check_user(message.from_user.id):
        ask_to_subscribe(message.chat.id)
        return

    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Faqat raqam yuboring")
        return

    code = int(message.text)

    video = collection.find_one({"code": code})

    if video:
        bot.send_video(
            message.chat.id,
            video["file_id"],
            caption=video["caption"]
        )
    else:
        bot.send_message(message.chat.id, "Bu kod uchun video topilmadi")

# ================== FLASK ==================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot ishlayapti", 200

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=5000)
