import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_TOKEN')

balance = {}
history = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

SPEND_AMOUNT, SPEND_CATEGORY, INCOME_AMOUNT = range(3)


def handle_message(update: Update, context: CallbackContext):
    chat = update.message.chat
    if chat.type == 'private':
        return chat.username
    elif chat.type in ['group', 'supergroup']:
        return chat.title


def create_entry(update: Update, context: CallbackContext):
    chat = handle_message(update, context)
    if chat not in history.keys():
        history[chat] = []
        balance[chat] = 0
        logging.info(f'Created new entry for {chat}.')
    return chat


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Welcome to the Personal Finance bot!')


def income_command(update: Update, context: CallbackContext):
    chat = create_entry(update, context)
    global balance
    date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    user = update.message.from_user.name
    if len(context.args) < 1:
        update.message.reply_text("Please provide the amount of income. Example: /income 100 Salary")
        return

    try:
        amount = float(context.args[0])
    except ValueError:
        update.message.reply_text("Invalid amount. Please provide a valid number. Example: /income 100 Salary")
        return
    category = " ".join(context.args[1:])
    balance[chat] += amount
    history[chat].append(('Income', amount, user, category, date))
    logging.info(f'{user} added {amount:.2f} to income. The balance of {chat} is now {balance[chat]:.2f}.')
    update.message.reply_text(f'{user} added {amount:.2f} to your income. Your balance is now {balance[chat]:.2f}.')


def spend_command(update: Update, context: CallbackContext):
    chat = create_entry(update, context)
    global balance
    date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    user = update.message.from_user.name
    if len(context.args) < 2:
        update.message.reply_text("Please provide the amount and category. Example: /spend 100 Groceries and food")
        return

    try:
        amount = float(context.args[0])
    except ValueError:
        update.message.reply_text(
            "Invalid amount. Please provide a valid number. Example: /spend 100 Groceries and food")
        return

    category = " ".join(context.args[1:])
    balance[chat] -= amount
    history[chat].append(('Expense', amount, user, category, date))
    logging.info(f'{user} spent {amount:.2f} to income. The balance of {chat} is now {balance[chat]:.2f}.')
    update.message.reply_text(f'{user} spent {amount:.2f} on {category}. Your balance is now {balance[chat]:.2f}.')


def balance_command(update: Update, context: CallbackContext):
    chat = create_entry(update, context)
    logging.info(f'Current {chat} is {balance[chat]:.2f}.')
    update.message.reply_text(f'Your current balance is {balance[chat]:.2f}.')


def history_command(update: Update, context: CallbackContext):
    chat = create_entry(update, context)
    if not history[chat]:
        update.message.reply_text('No transactions yet.')
    else:
        msg = ''.join(
            f"{i}. {transaction[0]} {transaction[1]:.2f} {transaction[3]} {transaction[4]} - {transaction[2]}\n"
            for i, transaction in enumerate(history[chat], start=1)
        )
        logging.info(f'{chat} history: {msg}.')
        update.message.reply_text(msg)


def reset_command(update: Update, context: CallbackContext):
    chat = create_entry(update, context)
    global balance, history
    balance[chat] = 0
    history[chat] = []
    update.message.reply_text("Income and history have been reset.")


def main():
    updater = Updater(API_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('in', income_command, pass_args=True))
    dp.add_handler(CommandHandler('out', spend_command, pass_args=True))
    dp.add_handler(CommandHandler('balance', balance_command))
    dp.add_handler(CommandHandler('history', history_command))
    dp.add_handler(CommandHandler('reset', reset_command))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
