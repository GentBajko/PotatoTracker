from loguru import logger
import os
from datetime import datetime
from telebot import types, TeleBot
import pandas as pd
from db import TransactionService
from settings import config
from util import get_chat_name


class BotHandler:
    def __init__(self, token):
        self.bot = TeleBot(token)
        self.transactions = TransactionService()
        self._register_handlers()

    def _register_handlers(self):
        self.bot.message_handler(commands=["menu"])(self.menu)
        self.bot.callback_query_handler(func=lambda call: call.data == "add_expense")(
            self.add_expense
        )
        self.bot.callback_query_handler(func=lambda call: call.data == "add_income")(
            self.add_income
        )
        self.bot.callback_query_handler(func=lambda call: call.data == "history")(
            self.transaction_history
        )
        self.bot.callback_query_handler(func=lambda call: call.data == "delete_entry")(
            self.handle_delete_entry
        )
        self.bot.callback_query_handler(func=lambda call: call.data == "edit_entry")(
            self.handle_edit_entry
        )
        self.bot.callback_query_handler(func=lambda call: call.data == "reset")(
            self.reset_history
        )
        self.bot.callback_query_handler(func=lambda call: call.data == "balance")(
            self.check_balance
        )
        self.bot.callback_query_handler(func=lambda call: call.data == "export")(
            self.handle_export
        )
        self.bot.callback_query_handler(func=lambda call: call.data == "import")(
            self.handle_import
        )

    def menu(self, message):
        keyboard = types.InlineKeyboardMarkup()
        buttons = [
            ("Add Income", "add_income"),
            ("Add Expense", "add_expense"),
            ("Delete Entry", "delete_entry"),
            ("Edit Entry", "edit_entry"),
            ("Check Balance", "balance"),
            ("Monthly Balance", "monthly_balance"),
            ("Transaction History", "history"),
            ("Monthly History", "monthly_history"),
            ("Reset", "reset"),
            ("Import History", "import"),
            ("Export History", "export"),
        ]
        for btn_text, callback in buttons:
            keyboard.add(types.InlineKeyboardButton(btn_text, callback_data=callback))
        self.bot.send_message(
            message.chat.id,
            "Welcome to PotatoTracker! What would you like to do?",
            reply_markup=keyboard,
        )

    def add_expense(self, call):
        logger.debug(
            f"Callback query handler 'add_expense' called for chat_id: {call.message.chat.id}"
        )
        self.bot.send_message(call.message.chat.id, "Enter the source of the expense:")
        self.bot.register_next_step_handler(
            call.message, self.process_category, "expense"
        )

    def add_income(self, call):
        logger.debug(
            f"Callback query handler 'add_income' called for chat_id: {call.message.chat.id}"
        )
        self.bot.send_message(call.message.chat.id, "Enter the source of the income:")
        self.bot.register_next_step_handler(
            call.message, self.process_category, "income"
        )

    def process_category(self, message, option):
        category = message.text
        logger.debug(f"Processing category: {category} for option: {option}")
        self.bot.send_message(
            message.chat.id, f"Enter the amount of {option} for {category}:"
        )
        self.bot.register_next_step_handler(
            message, self.process_amount, option, category
        )

    def process_amount(self, message, option, category):
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
            self.transactions.create_transaction(new_transaction)
            self.bot.send_message(
                message.chat.id, f"Added {option} of {amount} for {category}."
            )
        except ValueError:
            logger.debug("Invalid input for amount, not a valid number.")
            self.bot.send_message(
                message.chat.id, "Invalid input. Please enter a valid number."
            )

    def transaction_history(self, call):
        chat_name = get_chat_name(call.message)
        transaction_list = self.transactions.get_transactions(call.message.chat.id)
        if transaction_list:
            history_df = pd.DataFrame(transaction_list)
            last_20_transactions = history_df.tail(20).to_string(index=False)
            self.bot.send_message(
                call.message.chat.id, f"Last 20 transactions:\n\n{last_20_transactions}"
            )
        else:
            self.bot.send_message(call.message.chat.id, "No transaction history found.")

    def handle_delete_entry(self, call):
        self.bot.send_message(
            call.message.chat.id, "Enter the entry number you want to delete:"
        )
        self.bot.register_next_step_handler(call.message, self.delete_entry)

    def delete_entry(self, message):
        entry_number = int(message.text)
        chat_name = get_chat_name(message)
        transaction_list = self.transactions.get_transactions(message.chat.id)
        if transaction_list and 0 < entry_number <= len(transaction_list):
            entry_id = transaction_list[entry_number - 1]["_id"]
            self.transactions.remove_transaction(message.chat.id, entry_id)
            self.bot.send_message(message.chat.id, f"Entry {entry_number} deleted.")
        else:
            self.bot.send_message(
                message.chat.id, "Invalid entry number. Please try again."
            )

    def handle_edit_entry(self, call):
        self.bot.send_message(
            call.message.chat.id, "Enter the entry number you want to edit:"
        )
        self.bot.register_next_step_handler(call.message, self.request_edited_amount)

    def request_edited_amount(self, message):
        entry_number = int(message.text)
        self.bot.send_message(message.chat.id, "Enter the new amount for this entry:")
        self.bot.register_next_step_handler(message, self.edit_entry, entry_number)

    def edit_entry(self, message, entry_number):
        new_amount = float(message.text)
        chat_name = get_chat_name(message)
        transaction_list = self.transactions.get_transactions(message.chat.id)
        if transaction_list and 0 < entry_number <= len(transaction_list):
            entry = transaction_list[entry_number - 1]
            entry["Amount"] = new_amount
            self.transactions.update_transaction(chat_name, entry["_id"], entry)
            self.bot.send_message(message.chat.id, f"Entry {entry_number} updated.")
        else:
            self.bot.send_message(
                message.chat.id, "Invalid entry number. Please try again."
            )

    def reset_history(self, call):
        chat_name = get_chat_name(call.message)
        self.transactions.remove_all(call.message.chat.id)
        logger.info(f"Reset history for {chat_name}.")
        self.bot.send_message(call.message.chat.id, f"Reset history for {chat_name}.")

    def check_balance(self, call):
        chat_name = get_chat_name(call.message)
        transaction_list = self.transactions.get_transactions(call.message.chat.id)
        balance = sum(
            trans["Amount"] if trans["Type"] == "Income" else -trans["Amount"]
            for trans in transaction_list
        )
        logger.info(f"Check balance for {chat_name}. Current balance: {balance}")
        self.bot.send_message(
            call.message.chat.id, f"Your current balance is {balance}"
        )

    def handle_export(self, call):
        message = call.message
        chat_name = get_chat_name(message)
        transaction_list = self.transactions.get_transactions(message.chat.id)
        if transaction_list:
            history_df = pd.DataFrame(transaction_list)
            csv_file = f"{chat_name}_history.csv"
            history_df.to_csv(csv_file, index=False)
            with open(csv_file, "rb") as f:
                self.bot.send_document(message.chat.id, f)
            os.remove(csv_file)
            logger.info(f"Exported history for {chat_name}")
        else:
            self.bot.send_message(message.chat.id, "No transaction history found.")

    def handle_import(self, call):
        msg = self.bot.send_message(
            call.message.chat.id,
            "Please send the CSV file to import your transaction history.",
        )
        self.bot.register_next_step_handler(msg, self.import_history)

    def import_history(self, message):
        chat_name = get_chat_name(message)
        if not chat_name:
            return
        if message.document:
            file_id = message.document.file_id
            file_info = self.bot.get_file(file_id)
            downloaded_file = self.bot.download_file(file_info.file_path)
            csv_file = f"{chat_name}_history.csv"
            with open(csv_file, "wb") as f:
                f.write(downloaded_file)
            try:
                df = pd.read_csv(csv_file)
                records = df.to_dict("records")
                for record in records:
                    self.transactions.create_transaction(
                        {
                            "ChatId": message.chat.id,
                            "Type": record["Type"],
                            "Author": record["Author"],
                            "Category": record["Category"],
                            "Amount": record["Amount"],
                            "Timestamp": record["Timestamp"],
                        }
                    )
                self.bot.send_message(
                    message.chat.id, "Transaction history imported successfully."
                )
                logger.info(f"Imported history for {chat_name}")
            except Exception as e:
                self.bot.send_message(
                    message.chat.id, "An error occurred while importing the file."
                )
                logger.error(f"Import failed for user {chat_name}, error: {e}")
            finally:
                os.remove(csv_file)
        else:
            self.bot.send_message(message.chat.id, "Please send a valid CSV file.")
            logger.info(f"Invalid file received for user {chat_name}")

    def start(self):
        self.bot.polling(non_stop=True)


if __name__ == "__main__":
    bot_handler = BotHandler(config.TELEGRAM_TOKEN)
    bot_handler.start()
