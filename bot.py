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


def ask_income_amount(update: Update, context: CallbackContext):
    update.message.reply_text("How much income do you want to add?")
    return INCOME_AMOUNT


def income_command(update: Update, context: CallbackContext):
    global income
    amount = float(update.message.text)
    income += amount
    history.append(('Income', amount))
    update.message.reply_text(f'You added {amount:.2f} to your income. Your balance is now {income:.2f}.')
    return ConversationHandler.END


def ask_spend_amount(update: Update, context: CallbackContext):
    update.message.reply_text("How much did you spend?")
    return SPEND_AMOUNT


def ask_spend_category(update: Update, context: CallbackContext):
    amount = float(update.message.text)
    context.user_data['spend_amount'] = amount
    update.message.reply_text("Where did you spend the money?")
    return SPEND_CATEGORY


def spend_command(update: Update, context: CallbackContext):
    global income
    amount = context.user_data['spend_amount']
    category = update.message.text
    income -= amount
    history.append(('Spend', amount, category))
    update.message.reply_text(f'You spent {amount:.2f} on "{category}". Your balance is now {income:.2f}.')
    return ConversationHandler.END


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

    income_handler = ConversationHandler(
        entry_points=[CommandHandler('income', ask_income_amount)],
        states={
            INCOME_AMOUNT: [MessageHandler(Filters.text & ~Filters.command, income_command)],
        },
        fallbacks=[],
    )
    dp.add_handler(income_handler)

    spend_handler = ConversationHandler(
        entry_points=[CommandHandler('spend', ask_spend_amount)],
        states={
            SPEND_AMOUNT: [MessageHandler(Filters.text & ~Filters.command, ask_spend_category)],
            SPEND_CATEGORY: [MessageHandler(Filters.text & ~Filters.command, spend_command)],
        },
        fallbacks=[],
    )
    dp.add_handler(spend_handler)

    dp.add_handler(CommandHandler('balance', balance_command))
    dp.add_handler(CommandHandler('history', history_command))
    dp.add_handler(CommandHandler('reset', reset_command))

    updater.start_polling()
    updater.idle()
