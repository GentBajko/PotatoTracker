import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from datetime import datetime
import pickle
import os
import csv

load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_TOKEN')

balance = {}
history = {}
os.makedirs('potato', exist_ok=True)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

SPEND_AMOUNT, SPEND_CATEGORY, INCOME_AMOUNT = range(3)


def handle_message(update: Update, context: CallbackContext):
    if update.message:
        chat = update.message.chat
    elif update.callback_query:
        chat = update.callback_query.message.chat
    else:
        return None

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
    keyboard = [
        [
            InlineKeyboardButton("Add Income", callback_data='in'),
            InlineKeyboardButton("Spend Money", callback_data='out')
        ],
        [
            InlineKeyboardButton("Check Balance", callback_data='balance'),
            InlineKeyboardButton("Transaction History", callback_data='history')
        ],
        [
            InlineKeyboardButton("Reset", callback_data='reset')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Welcome to the Personal Finance bot!', reply_markup=reply_markup)


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
    save_data()


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
    save_data()


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
        save_data()


def reset_command(update: Update, context: CallbackContext):
    chat = create_entry(update, context)
    global balance, history
    balance[chat] = 0
    history[chat] = []
    update.message.reply_text("Income and history have been reset.")
    save_data()


def save_data():
    with open('potato/balance.pickle', 'wb') as f:
        pickle.dump(balance, f)
    with open('potato/history.pickle', 'wb') as f:
        pickle.dump(history, f)


def load_data():
    global balance, history
    try:
        with open('potato/balance.pickle', 'rb') as f:
            balance = pickle.load(f)
        with open('potato/history.pickle', 'rb') as f:
            history = pickle.load(f)
    except FileNotFoundError:
        balance = {}
        history = {}


def edit_entry_command(update: Update, context: CallbackContext):
    chat = create_entry(update, context)

    if len(context.args) < 2:
        update.message.reply_text("Please provide the entry number and new amount. Example: /edit 1 200")
        return

    try:
        entry_number = int(context.args[0]) - 1
        new_amount = float(context.args[1])
    except ValueError:
        update.message.reply_text("Invalid input. Please provide a valid entry number and amount.")
        return

    if entry_number < 0 or entry_number >= len(history[chat]):
        update.message.reply_text("Invalid entry number. Please provide a valid entry number.")
        return

    transaction = history[chat][entry_number]
    balance_change = new_amount - transaction[1]

    balance[chat] += balance_change

    history[chat][entry_number] = (transaction[0], new_amount, transaction[2], transaction[3], transaction[4])

    update.message.reply_text(f"Entry {entry_number + 1} has been updated. Your balance is now {balance[chat]:.2f}.")


def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    command = query.data
    if command == 'in':
        income_command(update, context)
    elif command == 'out':
        spend_command(update, context)
    elif command == 'balance':
        balance_command(update, context)
    elif command == 'history':
        history_command(update, context)
    elif command == 'reset':
        reset_command(update, context)
    elif command == 'edit':
        edit_entry_command(update, context)
    elif command == 'delete':
        delete_entry_command(update, context)


def delete_entry_command(update: Update, context: CallbackContext):
    chat = create_entry(update, context)

    if len(context.args) < 1:
        update.message.reply_text("Please provide the entry number to delete. Example: /delete 1")
        return

    try:
        entry_number = int(context.args[0]) - 1
    except ValueError:
        update.message.reply_text("Invalid entry number. Please provide a valid entry number.")
        return

    if entry_number < 0 or entry_number >= len(history[chat]):
        update.message.reply_text("Invalid entry number. Please provide a valid entry number.")
        return

    transaction = history[chat].pop(entry_number)
    balance_change = transaction[1] if transaction[0] == 'Income' else -transaction[1]

    balance[chat] -= balance_change

    update.message.reply_text(f"Entry {entry_number + 1} has been deleted. Your balance is now {balance[chat]:.2f}.")


def export_csv_command(update: Update, context: CallbackContext):
    chat = create_entry(update, context)

    if not history[chat]:
        update.message.reply_text("No transactions to export.")
        return

    csv_file = f"{chat}_history.csv"
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Type", "Amount", "User", "Category", "Date"])
        for transaction in history[chat]:
            writer.writerow(transaction)
    with open(csv_file, 'rb') as file:
        update.message.reply_document(file, filename=csv_file)
    os.remove(csv_file)


def show_buttons(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Income", callback_data="income"),
            InlineKeyboardButton("Expense", callback_data="expense"),
        ],
        [
            InlineKeyboardButton("Balance", callback_data="balance"),
            InlineKeyboardButton("History", callback_data="history"),
        ],
        [
            InlineKeyboardButton("Reset", callback_data="reset"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Choose an action:", reply_markup=reply_markup)


def main():
    updater = Updater(API_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(CommandHandler('in', income_command, pass_args=True))
    dp.add_handler(CommandHandler('out', spend_command, pass_args=True))
    dp.add_handler(CommandHandler('balance', balance_command))
    dp.add_handler(CommandHandler('history', history_command))
    dp.add_handler(CommandHandler('reset', reset_command))
    dp.add_handler(CommandHandler('edit', edit_entry_command, pass_args=True))
    dp.add_handler(CommandHandler('delete', delete_entry_command, pass_args=True))
    dp.add_handler(CommandHandler('export', export_csv_command))
    dp.add_handler(CommandHandler('buttons', show_buttons))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
