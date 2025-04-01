import json
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackContext)
import configparser
import logging
from telegram import Bot
from telegram.utils.request import Request
from HKBU_chatgpt import HKBU_ChatGPT
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, request

app = Flask(__name__)

# Flask route for webhook3
@app.route('/webhook', methods=['POST'])
def webhook():
    global updater, dispatcher
    data = request.get_json()  # 获取 POST 请求的 JSON 数据
    # 将 webhook 数据传递给 Telegram 更新器的 Dispatcher
    update = Update.de_json(data, updater.bot)  # 解析来自 Telegram 的请求数据
    dispatcher.process_update(update)  # 使用 Dispatcher 来处理更新
    return 'OK', 200  # 返回响应，告诉 Telegram 请求已处理

def main():
    global updater, dispatcher
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')

    telegram_token = os.environ.get("ACCESS_TOKEN_TG")
    if not telegram_token:
        raise ValueError("Environment variable ACCESS_TOKEN_TG is not set")

    # Set up Telegram bot with webhook
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher

    # Firebase setup
    Firebase_key = os.environ.get("FIREBASE_CREDENTIALS")
    if not Firebase_key:
        raise ValueError("Environment variable FIREBASE_CREDENTIALS is not set")
    cred_dict = json.loads(Firebase_key)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

    # Initialize ChatGPT object
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)

    # Create handler for ChatGPT interaction
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # Define command handlers
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("delete", delete))
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Set up webhook for Telegram Bot
    webhook_url = os.environ.get("WEBHOOK_URL")  # This should be your server's public URL
    updater.bot.set_webhook(url=webhook_url + '/webhook')

    # Start Flask web server
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # Start the Flask app

def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')

def hello(update: Update, context: CallbackContext) -> None:
    """Send a hello message when the command /hello is issued."""
    msg = context.args[0]
    update.message.reply_text('Good day, ' + msg + '!')

def add(update: Update, context: CallbackContext) -> None:
    """Add a keyword to the database and increment its count."""
    try:
        db = firestore.client()
        msg = context.args[0]

        doc_ref = db.collection("keywords").document(msg)
        if doc_ref.get().exists:
            doc_ref.update({"count": firestore.Increment(1)})
        else:
            doc_ref.set({"count": 1})

        current_count = doc_ref.get().to_dict()['count']
        update.message.reply_text('You have said ' + msg + ' for ' + str(current_count) + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def delete(update: Update, context: CallbackContext) -> None:
    """Delete a keyword from the database."""
    try:
        db = firestore.client()
        msg = context.args[0]

        doc_ref = db.collection("keywords").document(msg)
        if doc_ref.get().exists:
            current_count = doc_ref.get().to_dict()['count']
            if current_count > 0 and current_count <= 1:
                update.message.reply_text('The keyword ' + msg + ' has been deleted ' + str(current_count) + ' time.')
                doc_ref.delete()
            elif current_count > 1:
                update.message.reply_text('The keyword ' + msg + ' has been deleted ' + str(current_count) + ' times.')
                doc_ref.delete()
        else:
            update.message.reply_text('The keyword ' + msg + ' does not exist.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /delete <keyword>')

def load_groups_data():
    """
    从数据库中加载所有群组信息，并将其转化为 ChatGPT 可理解的格式
    """
    db = firestore.client()
    groups_ref = db.collection("groups")  # 获取所有群组
    all_groups = groups_ref.stream()

    groups_data = []
    for doc in all_groups:
        group = doc.to_dict()
        group_info = f"群组名称: {group['name']}\n链接: {group['link']}\n标签: {', '.join(group['tags'])}"
        groups_data.append(group_info)

    # 将所有群组数据合并为一个大的文本块，ChatGPT 会理解这些信息
    return "\n\n".join(groups_data)

def equiped_chatgpt(update, context):
    """
    处理用户输入，基于 ChatGPT 推荐群组
    """
    user_message = update.message.text.strip()  # 获取用户消息
    group_keywords = ["群组", "群", "兴趣", "group", "chat group", 'groups']
    global chatgpt
    if any(keyword in user_message for keyword in group_keywords):
        # 加载所有群组数据
        groups_data = load_groups_data()

        # 将群组数据作为上下文传递给 ChatGPT
        context_for_gpt = f"以下是一些群组信息:\n\n{groups_data}\n\n用户问：{user_message}\n\n请根据用户的问题并推荐相关的群组：（翻译成用户所用的语言回答问题）"

        # 使用 ChatGPT 根据输入和群组数据生成推荐
        reply_message = chatgpt.submit(context_for_gpt)

    else:
        reply_message = chatgpt.submit(user_message)  # 使用 ChatGPT 生成回复
        logging.info("Update: " + str(update))
        logging.info("Context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)  # 发送 ChatGPT 回复

if __name__ == '__main__':
    main()
