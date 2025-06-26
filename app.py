import os
import requests
from flask import Flask, request, Response
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def send_message(chat_id, text):
    """Send a message to a Telegram chat"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        logger.info(f"Message sent successfully to chat {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def get_start_message():
    """Get the welcome message"""
    return (
        "🤖 Welcome to the Scheduler Bot!\n\n"
        "Use /schedule to set reminders:\n"
        "Example: /schedule Remember to call mom 2024-12-25 09:00\n"
        "Format: /schedule <message> <YYYY-MM-DD> <HH:MM>"
    )

def get_default_message():
    """Get the help message"""
    return (
        "🤔 I didn't understand that command.\n"
        "/start - Show welcome message\n"
        "/help - Show this help message\n"
        "/schedule - Set reminders\n"
        "/format -  Get the format of the schedule function!\n"
        "💡 Tip: Send any other message for general info!"
    )

def get_format_message():
    """Get format message"""
    return (
        "/schedule Remember to call mom 2024-12-25 09:00"
    )

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhook requests"""
    try:
        json_data = request.get_json(force=True)
        
        # Extract message info
        if "message" in json_data:
            message = json_data["message"]
            chat_id = message["chat"]["id"]
            
            if "text" in message:
                user_text = message["text"]
                logger.info(f"Received message: {user_text} from chat {chat_id}")
                
                if user_text == "/start":
                    welcome_msg = get_start_message()
                    success = send_message(chat_id, welcome_msg)
                elif user_text == "/format":
                    default_message = get_format_message()
                    success = send_message(chat_id, default_message)
                elif user_text.startswith("/schedule"):
                    default_message = get_format_message()
                    success = send_message(chat_id, default_message)
                else:
                    default_message = get_default_message()
                    success = send_message(chat_id, default_message)

                if success:
                    return Response(status=200)
                else:
                    return Response(status=500)
        
        return Response(status=200)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return Response(status=500)

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}, 200

@app.route("/callback", methods=["POST"])
def callback():
    """Handle incoming messages from scheduler"""
    try:
        json_data = request.get_json(force=True)
        print(json_data)
        
        return Response(status=200)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return Response(status=500)

def setup_webhook():
    """Set up the webhook"""
    if not WEBHOOK_URL or not WEBHOOK_URL.startswith('http'):
        logger.info("No webhook URL provided, skipping webhook setup")
        return False
    
    try:
        webhook_url = WEBHOOK_URL + "/webhook"
        url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
        data = {"url": webhook_url}
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        logger.info(f"Webhook set successfully to: {webhook_url}")
        return True
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return False

if __name__ == "__main__":
    print("Starting Simple Telegram Bot...")
    print(f"Bot Token: {'✓ Set' if TOKEN else '✗ Missing'}")
    print(f"Webhook URL: {WEBHOOK_URL or 'Not set (OK for local testing)'}")
    
    if not TOKEN:
        print("Error: BOT_TOKEN is required!")
        exit(1)
    
    setup_webhook()
    
    port = int(os.getenv("PORT", 5000))
    print(f"Starting server on http://localhost:{port}")
    
    app.run(host="0.0.0.0", port=port, debug=False)