import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from telebot import types, TeleBot
import pandas as pd
import chardet

load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_TEST")

balance = {}
history = {}
os.makedirs("potato", exist_ok=True)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

bot = TeleBot(API_TOKEN)


def handle_message(message):
    chat = message.chat
    if chat.type == "private":
        return chat.username
    elif chat.type in ["group", "supergroup"]:
        return chat.title


def create_entry(message):
    chat = handle_message(message)
    if chat not in history.keys():
        history[chat] = []
        balance[chat] = 0
        logging.info(f"Created new entry for {chat}.")
    return chat


@bot.message_handler(commands=["menu"])
def menu(message):
    create_entry(message)
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton("Add Income", callback_data="add_income"),
        types.InlineKeyboardButton("Add Expense", callback_data="add_expense"),
    )
    keyboard.add(
        types.InlineKeyboardButton("Delete Entry", callback_data="delete_entry"),
        types.InlineKeyboardButton("Edit Entry", callback_data="edit_entry"),
    )
    keyboard.add(
        types.InlineKeyboardButton("Check Balance", callback_data="balance"),
        types.InlineKeyboardButton("Transaction History", callback_data="history"),
    )
    keyboard.add(
        types.InlineKeyboardButton("Reset", callback_data="reset"),
        types.InlineKeyboardButton("Import History", callback_data="import"),
        types.InlineKeyboardButton("Export History", callback_data="export"),
    )

    bot.send_message(
        message.chat.id, "Welcome to the Personal Finance bot!", reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data == "add_expense")
def add_expense(call):
    bot.send_message(
        chat_id=call.message.chat.id, text="Enter the source of the expense:"
    )
    bot.register_next_step_handler(call.message, process_category, "expense")


@bot.callback_query_handler(func=lambda call: call.data == "add_income")
def add_expense(call):
    bot.send_message(
        chat_id=call.message.chat.id, text="Enter the source of the income:"
    )
    bot.register_next_step_handler(call.message, process_category, "income")


def process_category(message, option):
    category = message.text
    bot.send_message(
        chat_id=message.chat.id, text=f"Enter the amount of {option} for {category}:"
    )
    bot.register_next_step_handler(message, process_amount, option, category)


def process_amount(message, option, category):
    try:
        amount = float(message.text)
        chat = create_entry(message)
        author = message.from_user.username or message.from_user.first_name
        if option == "income":
            balance[chat] += amount
        if option == "expense":
            balance[chat] -= amount
        logging.info(
            f"Added {option} of {amount} for {category} in {chat}. New balance: {balance[chat]}"
        )
        history[chat].append(
            {
                "id": len(history[chat]) + 1,
                "type": option.capitalize(),
                "author": author,
                "category": option,
                "amount": amount,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        )
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Added expense of {amount} for {option}. Your new balance is {balance[chat]}",
        )
        save_data()
    except ValueError:
        bot.send_message(
            chat_id=message.chat.id, text="Invalid input. Please enter a valid number."
        )


@bot.callback_query_handler(func=lambda call: call.data == "history")
def transaction_history(call):
    history_df = pd.concat({k: pd.DataFrame(v) for k, v in history.items()}, axis=0)
    history_df.reset_index(drop=True, inplace=True)
    history_df.index += 1  # Optional: start index from 1 instead of 0
    last_20_transactions = history_df.tail(20).to_string(index=False)  # Remove index from the displayed string
    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Last 20 transactions:\n\n{last_10_transactions}",
    )


def delete_entry(message, entry_number):
    chat = handle_message(message)
    if chat in history.keys() and 0 < entry_number <= len(history[chat]):
        entry = history[chat][entry_number - 1]
        if entry["type"] == "income":
            balance[chat] -= entry["amount"]
        else:
            balance[chat] += entry["amount"]
        history[chat].pop(entry_number - 1)
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Entry {entry_number} deleted. Your new balance is {balance[chat]}",
        )
        logging.info(
            f"Deleted entry {entry_number} in {chat}. New balance: {balance[chat]}"
        )
    else:
        bot.send_message(
            chat_id=message.chat.id, text="Invalid entry number. Please try again."
        )


def edit_entry(message, entry_number, new_amount):
    chat = handle_message(message)
    new_amount = float(new_amount)
    if chat in history.keys() and 0 < entry_number <= len(history[chat]):
        entry = history[chat][entry_number - 1]
        if entry["type"] == "income":
            balance[chat] -= entry["amount"]
            balance[chat] += new_amount
        else:
            balance[chat] += entry["amount"]
            balance[chat] -= new_amount
        entry["amount"] = new_amount
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Entry {entry_number} updated. Your new balance is {balance[chat]}",
        )
        logging.info(
            f"Updated entry {entry_number} in {chat}. New balance: {balance[chat]}"
        )
    else:
        bot.send_message(
            chat_id=message.chat.id, text="Invalid entry number. Please try again."
        )


@bot.callback_query_handler(func=lambda call: call.data == "delete_entry")
def handle_delete_entry(call):
    bot.send_message(
        chat_id=call.message.chat.id, text="Enter the entry number you want to delete:"
    )
    bot.register_next_step_handler(
        call.message, lambda msg: delete_entry(msg, int(msg.text))
    )


@bot.callback_query_handler(func=lambda call: call.data == "edit_entry")
def handle_edit_entry(call):
    bot.send_message(
        chat_id=call.message.chat.id, text="Enter the entry number you want to edit:"
    )
    bot.register_next_step_handler(
        call.message, lambda msg: request_new_amount(msg, int(msg.text))
    )


def request_new_amount(message, entry_number):
    bot.send_message(
        chat_id=message.chat.id, text="Enter the new amount for this entry:"
    )
    bot.register_next_step_handler(
        message, lambda msg: edit_entry(msg, entry_number, float(msg.text))
    )


def save_data(folder_name="potato"):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    balance_df = pd.DataFrame(list(balance.items()), columns=["chat", "balance"])
    balance_df.to_csv(os.path.join(folder_name, "balance.csv"), index=False)

    history_df = pd.concat({k: pd.DataFrame(v) for k, v in history.items()}, axis=0)
    history_df.reset_index(drop=True, inplace=True)
    history_df.to_csv(os.path.join(folder_name, "history.csv"), index=False)


def load_data(folder_name="potato"):
    balance_file = os.path.join(folder_name, "balance.csv")
    history_file = os.path.join(folder_name, "history.csv")

    if os.path.exists(balance_file):
        balance_df = pd.read_csv(balance_file)
        balance.update(balance_df.set_index("chat").to_dict()["balance"])

    if os.path.exists(history_file):
        history_df = pd.read_csv(history_file)
        for chat, group in history_df.groupby("chat"):
            history[chat] = group.to_dict("records")


@bot.callback_query_handler(func=lambda call: call.data == "reset")
def reset_history(call):
    chat = handle_message(call.message)
    balance[chat] = 0
    history[chat] = []
    logging.info(f"Reset history for {chat}. New balance: {balance[chat]}")
    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Reset history for {chat}. Your new balance is {balance[chat]}",
    )


@bot.callback_query_handler(func=lambda call: call.data == "balance")
def check_balance(call):
    chat = handle_message(call.message)
    logging.info(f"Check balance for {chat}. Current balance: {balance[chat]}")
    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Your current balance is {balance[chat]}",
    )


def export_history(message):
    user_id = message.chat.id
    csv_file = f"potato/{user_id}_history.csv"

    try:
        history_df = pd.concat({k: pd.DataFrame(v) for k, v in history.items()}, axis=0)
        history_df.reset_index(drop=True, inplace=True)
        history_df.to_csv(csv_file, index=False)
        with open(csv_file, "rb") as f:
            bot.send_document(user_id, f)
        os.remove(csv_file)
        logging.info(f"Exported history for user {user_id}")
    except FileNotFoundError:
        bot.send_message(user_id, "No transaction history found.")
        logging.info(f"No transaction history found for user {user_id}")


def import_history(message):
    chat = create_entry(message)
    csv_file = f"potato/{chat}_history.csv"

    if message.document:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open(csv_file, "wb") as f:
            f.write(downloaded_file)

        try:
            with open(csv_file, "rb") as f:
                encoding_result = chardet.detect(f.read())
            file_encoding = encoding_result["encoding"]

            df = pd.read_csv(csv_file, encoding=file_encoding)
            records = df.to_dict("records")
            for i, record in enumerate(records, start=1):
                history[chat].append(
                    {
                        "id": i,
                        "author": record["author"],
                        "type": record["type"],
                        "amount": record["amount"],
                        "timestamp": record["timestamp"],
                        "category": record["category"],
                    }
                )
            income_sum = round(sum(
                record["amount"] for record in history[chat] if record["type"] == "Income"
            ), 2)
            expense_sum = round(sum(
                record["amount"] for record in history[chat] if record["type"] == "Expense"
            ), 2)
            balance[chat] = round(income_sum - expense_sum, 2)
            bot.send_message(
                message.chat.id,
                f"Transaction history imported successfully. New balance: {balance[chat]}",
            )
            save_data()
            logging.info(
                f"Imported history for user {chat}. New balance: {balance[chat]}"
            )
        except pd.errors.EmptyDataError:
            bot.send_message(chat, "The imported file is empty or corrupted.")
            logging.warning(f"Import failed for user {chat}, empty or corrupted file.")
        except Exception as e:
            bot.send_message(chat, "An error occurred while importing the file.")
            logging.error(f"Import failed for user {chat}, error: {e}")
    else:
        bot.send_message(chat, "Please send a valid CSV file.")
        logging.info(f"Invalid file received for user {chat}")


@bot.callback_query_handler(func=lambda call: call.data == "export")
def handle_export(call):
    export_history(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "import")
def handle_import(call):
    msg = bot.send_message(
        call.message.chat.id,
        "Please send the CSV file to import your transaction history.",
    )
    bot.register_next_step_handler(msg, import_history)


if __name__ == "__main__":
    import contextlib

    with contextlib.suppress(Exception):
        load_data()
    bot.polling(non_stop=True)
