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

# 在国内要设置代理，updater对象也要更新
# proxy1 = {
#     'proxy_url': 'http://127.0.0.1:10809',  # 代理地址
# }
# request = Request(proxy_url=proxy1['proxy_url'])
# # 在国内要设置 HTTP/HTTPS 代理
# os.environ["http_proxy"] = "http://127.0.0.1:10809"
# os.environ["https_proxy"] = "http://127.0.0.1:10809"

def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')

    telegram_token = os.environ.get("ACCESS_TOKEN_TG")
    if not telegram_token:
        raise ValueError("环境变量 ACCESS_TOKEN_TG 未设置")
    # 在香港用这个updater
    updater = Updater(token=telegram_token, use_context=True)

    # # 在国内用这个updater,python-telegram-bot 13.7 不能直接用updater来传入request需要经过Bot对象
    # ## 创建Bot对象时传入代理
    # bot = Bot(token=config['TELEGRAM']['ACCESS_TOKEN'], request=request)
    # ## 使用Bot对象来创建Updater对象
    # updater = Updater(bot=bot, use_context=True)

    dispatcher = updater.dispatcher

    # 连接Firebase数据库
    Firebase_key = os.environ.get("FIREBASE_CREDENTIALS")
    if not Firebase_key:
        raise ValueError("环境变量 FIREBASE_CREDENTIALS 未设置")
    cred = credentials.Certificate(Firebase_key)
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

    # Start the bot
    updater.start_polling()
    updater.idle()

def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def echo(update, context):
    reply_message = update.message.text.upper()
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
        logging.info(context.args[0])
        msg = context.args[0]  # /add keyword <-- this should store the keyword

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
        logging.info(context.args[0])
        msg = context.args[0]  # /delete keyword <-- this should delete the keyword

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

if __name__ == '__main__':
    main()
