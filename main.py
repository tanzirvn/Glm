import os
import telebot
from flask import Flask
from openai import OpenAI
from threading import Thread

# 1. Load Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# 2. Initialize Clients
bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# 3. Flask Web Server (Required for Render)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

def run_flask():
    # Render provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 4. Telegram Bot Logic
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am an AI Chatbot powered by GLM-5. Send me a message!")

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        # Send typing action to show the bot is thinking
        bot.send_chat_action(message.chat.id, 'typing')

        # Call Hugging Face API via OpenAI SDK
        chat_completion = client.chat.completions.create(
            model="zai-org/GLM-5:novita",
            messages=[
                {"role": "user", "content": message.text}
            ],
            max_tokens=500
        )

        # Get response text
        response_text = chat_completion.choices[0].message.content
        bot.reply_to(message, response_text)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Sorry, I encountered an error processing your request.")

# 5. Main Execution
if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Start Telegram Bot polling
    print("Bot is starting...")
    bot.infinity_polling()
