import os
import telebot
import openai
import requests
from io import BytesIO

# Настройки
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(BOT_TOKEN)

# Системный промпт
SYSTEM_PROMPT = (
    "Ты — вежливый и доброжелательный администратор студии йоги в Шымкенте. "
    "Ты говоришь на русском и казахском. Если пользователь пишет на казахском — отвечай на казахском, "
    "если на русском — на русском. Общайся коротко, по одному сообщению, не выдавай блок текста. "
    "Рассказывай о расписании, ценах, пробных занятиях и предлагай записаться. "
    "Если пользователь хочет записаться, спроси имя и удобное время, и передай заявку @e2e4e6e8."
)

# Временные ответы
RESPONSES = {
    "расписание": "Наше расписание: Пн–Пт 08:00 Хатха, 12:00 Пилатес, 19:00 Аштанга. Сб–Вс: 10:00 мягкий класс.",
    "цены": "Разовое занятие — 2500 ₸. Абонемент (8 занятий) — 16000 ₸. Первое занятие — бесплатно!",
    "записаться": "Супер! Напишите ваше имя и удобное время. Я передам администратору @e2e4e6e8.",
    "привет": "Здравствуйте! Я голосовой бот студии йоги. Чем могу помочь?",
}

# Обработка текста
@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_text = message.text.lower()
    reply = None
    for key, val in RESPONSES.items():
        if key in user_text:
            reply = val
            break
    if not reply:
        reply = "Можете спросить про расписание, цены или как записаться :)"
    bot.reply_to(message, reply)

# Обработка голосовых сообщений
@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
    audio_data = requests.get(file_url).content
    audio_file = BytesIO(audio_data)
    audio_file.name = "audio.ogg"
    try:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        message.text = transcript["text"]
        handle_text(message)
    except Exception:
        bot.reply_to(message, "Извините, не удалось распознать голос. Попробуйте ещё раз.")

print("Бот запущен.")
bot.infinity_polling()
