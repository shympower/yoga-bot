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
    "Ты — вежливый администратор студии йоги в Шымкенте. Ты говоришь на русском и казахском. "
    "Отвечай кратко, на том языке, на котором пишет пользователь. "
    "Отвечай на вопросы о расписании, ценах, пробных занятиях. "
    "Если клиент хочет записаться — спроси имя и удобное время, и скажи, что передашь @e2e4e6e8."
)

# GPT-ответ
def ask_gpt(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("GPT Error:", e)
        return "Извините, я немного задумался. Повторите, пожалуйста?"

# Обработка текста
@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_text = message.text
    reply = ask_gpt(user_text)
    bot.reply_to(message, reply)

# Обработка голосовых
@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
    try:
        audio_data = requests.get(file_url).content
        audio_file = BytesIO(audio_data)
        audio_file.name = "voice.oga"
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        message.text = transcript["text"]
        handle_text(message)
    except Exception as e:
        print("Whisper Error:", e)
        bot.reply_to(message, "Извините, не удалось распознать голос. Попробуйте ещё раз.")

print("AI бот запущен.")
bot.infinity_polling()
