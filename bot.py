import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from dotenv import load_dotenv
import os

load_dotenv()
# Replace YOUR_API_TOKEN with the token you received from the BotFather
API_TOKEN = os.getenv('TELEGRAM_TOKEN')

income = 0
history = []

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

SPEND_AMOUNT, SPEND_CATEGORY, INCOME_AMOUNT = range(3)


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Welcome to the Personal Finance bot!')


def income_command(update: Update, context: CallbackContext):
    global income
    if len(context.args) < 1:
        update.message.reply_text("Please provide the amount of income. Example: /income 100 Salary")
        return

    try:
        amount = float(context.args[0])
    except ValueError:
        update.message.reply_text("Invalid amount. Please provide a valid number. Example: /income 100 Salary")
        return

    income += amount
    history.append(('Income', amount))
    update.message.reply_text(f'You added {amount:.2f} to your income. Your balance is now {income:.2f}.')


def spend_command(update: Update, context: CallbackContext):
    global income
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
    income -= amount
    history.append(('Spend', amount, category))
    update.message.reply_text(f'You spent {amount:.2f} on "{category}". Your balance is now {income:.2f}.')


def balance_command(update: Update, context: CallbackContext):
    update.message.reply_text(f'Your current balance is {income:.2f}.')


def history_command(update: Update, context: CallbackContext):
    if not history:
        update.message.reply_text('No transactions yet.')
    else:
        msg = ''.join(
            f"{i}. {transaction[0]} ({transaction[2]}): {transaction[1]:.2f}\n"
            if transaction[0] == 'Spend'
            else f"{i}. {transaction[0]}: {transaction[1]:.2f}\n"
            for i, transaction in enumerate(history, start=1)
        )
        update.message.reply_text(msg)


def reset_command(update: Update, context: CallbackContext):
    global income, history
    income = 0
    history = []
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
