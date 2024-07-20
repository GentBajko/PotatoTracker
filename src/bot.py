from loguru import logger
import os
from datetime import datetime
from telebot import types, TeleBot
import pandas as pd
from db import TransactionService
from settings import config
from util import get_chat_name

bot = TeleBot(config.TELEGRAM_TOKEN)
transactions = TransactionService()


@bot.message_handler(commands=["menu"])
def menu(message):
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
        types.InlineKeyboardButton("Monthly Balance", callback_data="monthly_balance"),
    )
    keyboard.add(
        types.InlineKeyboardButton("Transaction History", callback_data="history"),
        types.InlineKeyboardButton("Monthly History", callback_data="monthly_history"),
    )
    keyboard.add(
        types.InlineKeyboardButton("Reset", callback_data="reset"),
        types.InlineKeyboardButton("Import History", callback_data="import"),
        types.InlineKeyboardButton("Export History", callback_data="export"),
    )

    bot.send_message(
        message.chat.id,
        "Welcome to PotatoTracker! What would you like to do?",
        reply_markup=keyboard,
    )


@bot.callback_query_handler(func=lambda call: call.data == "add_expense")
def add_expense(call):
    logger.debug(
        f"Callback query handler 'add_expense' called for chat_id: {call.message.chat.id}"
    )
    bot.send_message(
        chat_id=call.message.chat.id, text="Enter the source of the expense:"
    )
    bot.register_next_step_handler(call.message, process_category, "expense")


@bot.callback_query_handler(func=lambda call: call.data == "add_income")
def add_income(call):
    logger.debug(
        f"Callback query handler 'add_income' called for chat_id: {call.message.chat.id}"
    )
    bot.send_message(
        chat_id=call.message.chat.id, text="Enter the source of the income:"
    )
    bot.register_next_step_handler(call.message, process_category, "income")


def process_category(message, option):
    category = message.text
    logger.debug(f"Processing category: {category} for option: {option}")
    bot.send_message(
        chat_id=message.chat.id, text=f"Enter the amount of {option} for {category}:"
    )
    bot.register_next_step_handler(message, process_amount, option, category)


def process_amount(message, option, category):
    try:
        amount = float(message.text)
        author = message.from_user.username or message.from_user.first_name
        new_transaction = {
            "ChatId": message.chat.id,
            "Type": option.capitalize(),
            "Author": author,
            "Category": category,
            "Amount": amount,
            "Timestamp": datetime.now(),
        }
        logger.debug(f"Creating new transaction: {new_transaction}")
        transactions.create_transaction(new_transaction)
        bot.send_message(
            chat_id=message.chat.id, text=f"Added {option} of {amount} for {category}."
        )
    except ValueError:
        logger.debug("Invalid input for amount, not a valid number.")
        bot.send_message(
            chat_id=message.chat.id, text="Invalid input. Please enter a valid number."
        )


@bot.callback_query_handler(func=lambda call: call.data == "history")
def transaction_history(call):
    chat_name = get_chat_name(call.message)
    transaction_list = transactions.get_transactions(call.message.chat.id)
    if transaction_list:
        history_df = pd.DataFrame(transaction_list)
        last_20_transactions = history_df.tail(20).to_string(index=False)
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Last 20 transactions:\n\n{last_20_transactions}",
        )
    else:
        bot.send_message(
            chat_id=call.message.chat.id, text="No transaction history found."
        )


@bot.callback_query_handler(func=lambda call: call.data == "delete_entry")
def handle_delete_entry(call):
    bot.send_message(
        chat_id=call.message.chat.id, text="Enter the entry number you want to delete:"
    )
    bot.register_next_step_handler(
        call.message, lambda msg: delete_entry(msg, int(msg.text))
    )


def delete_entry(message, entry_number):
    chat_name = get_chat_name(message)
    transaction_list = transactions.get_transactions(message.chat.id)
    if transaction_list and 0 < entry_number <= len(transaction_list):
        entry_id = transaction_list[entry_number - 1]["_id"]
        transactions.remove_transaction(message.chat.id, entry_id)
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Entry {entry_number} deleted.",
        )
    else:
        bot.send_message(
            chat_id=message.chat.id, text="Invalid entry number. Please try again."
        )


@bot.callback_query_handler(func=lambda call: call.data == "edit_entry")
def handle_edit_entry(call):
    bot.send_message(
        chat_id=call.message.chat.id, text="Enter the entry number you want to edit:"
    )
    bot.register_next_step_handler(
        call.message, lambda msg: request_edited_amount(msg, int(msg.text))
    )


def request_edited_amount(message, entry_number):
    bot.send_message(
        chat_id=message.chat.id, text="Enter the new amount for this entry:"
    )
    bot.register_next_step_handler(
        message, lambda msg: edit_entry(msg, entry_number, float(msg.text))
    )


def edit_entry(message, entry_number, new_amount):
    chat = get_chat_name(message)
    transaction_list = transactions.get_transactions(message.chat.id)
    new_amount = float(new_amount)
    if transaction_list and 0 < entry_number <= len(transaction_list):
        entry = transaction_list[entry_number - 1]
        entry["Amount"] = new_amount
        transactions.update_transaction(chat, entry["_id"], entry)
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Entry {entry_number} updated.",
        )
    else:
        bot.send_message(
            chat_id=message.chat.id, text="Invalid entry number. Please try again."
        )


@bot.callback_query_handler(func=lambda call: call.data == "reset")
def reset_history(call):
    chat_name = get_chat_name(call.message)
    transactions.remove_all(call.message.chat.id)
    logger.info(f"Reset history for {chat_name}.")
    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Reset history for {chat_name}.",
    )


@bot.callback_query_handler(func=lambda call: call.data == "balance")
def check_balance(call):
    chat_name = get_chat_name(call.message)
    transaction_list = transactions.get_transactions(call.message.chat.id)
    balance = sum(
        trans["Amount"] if trans["Type"] == "Income" else -trans["Amount"]
        for trans in transaction_list
    )
    logger.info(f"Check balance for {chat_name}. Current balance: {balance}")
    bot.send_message(
        chat_id=call.message.chat.id,
        text=f"Your current balance is {balance}",
    )


@bot.callback_query_handler(func=lambda call: call.data == "export")
def handle_export(call):
    message = call.message
    chat_name = get_chat_name(message)
    transaction_list = transactions.get_transactions(message.chat.id)
    if transaction_list:
        history_df = pd.DataFrame(transaction_list)
        csv_file = f"{chat_name}_history.csv"
        history_df.to_csv(csv_file, index=False)
        with open(csv_file, "rb") as f:
            bot.send_document(message.chat.id, f)
        os.remove(csv_file)
        logger.info(f"Exported history for {chat_name}")
    else:
        bot.send_message(message.chat.id, text="No transaction history found.")


@bot.callback_query_handler(func=lambda call: call.data == "import")
def handle_import(call):
    msg = bot.send_message(
        call.message.chat.id,
        "Please send the CSV file to import your transaction history.",
    )
    bot.register_next_step_handler(msg, import_history)


def import_history(message):
    chat_name = get_chat_name(message)
    if not chat_name:
        return
    if message.document:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        csv_file = f"{chat_name}_history.csv"

        with open(csv_file, "wb") as f:
            f.write(downloaded_file)

        try:
            df = pd.read_csv(csv_file)
            records = df.to_dict("records")
            for record in records:
                transactions.create_transaction(
                    {
                        "ChatId": message.chat.id,
                        "Type": record["Type"],
                        "Author": record["Author"],
                        "Category": record["Category"],
                        "Amount": record["Amount"],
                        "Timestamp": record["Timestamp"],
                    }
                )
            bot.send_message(
                message.chat.id,
                f"Transaction history imported successfully.",
            )
            logger.info(f"Imported history for {chat_name}")
        except Exception as e:
            bot.send_message(chat_name, "An error occurred while importing the file.")
            logger.error(f"Import failed for user {chat_name}, error: {e}")
        finally:
            os.remove(csv_file)
    else:
        bot.send_message(chat_name, "Please send a valid CSV file.")
        logger.info(f"Invalid file received for user {chat_name}")


if __name__ == "__main__":
    bot.polling(non_stop=True)
