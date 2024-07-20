from pymongo import MongoClient
from bson import ObjectId
from settings import config
from loguru import logger

class TransactionService:
    def __init__(self):
        logger.debug("Initializing TransactionService")
        self.client = MongoClient(config.MONGO_URI)
        self.database = self.client[config.MONGO_DB]
        self._transactions = self.database["Transactions"]
        self._settings = self.database["Settings"]

    def get_transactions(self, chat_id):
        logger.debug(f"Fetching transactions for chat_id: {chat_id}")
        return list(self._transactions.find({"ChatId": chat_id}))

    def get_transaction(self, chat_id, id):
        logger.debug(f"Fetching transaction for chat_id: {chat_id} and id: {id}")
        return self._transactions.find_one({"ChatId": chat_id, "_id": ObjectId(id)})

    def get_history(self, chat_id):
        transactions = self.get_transactions(chat_id)
        logger.debug(f"Transaction history for chat_id: {chat_id}: {transactions}")
        return {"ChatId": chat_id, "Transactions": transactions}

    def create_transaction(self, transaction):
        logger.debug(f"Creating transaction: {transaction}")
        transaction["_id"] = ObjectId()
        self._transactions.insert_one(transaction)
        logger.debug(f"Transaction created with id: {transaction['_id']}")
        return transaction

    def update_transaction(self, chat_id, id, transaction_in):
        self._transactions.replace_one(
            {"ChatId": chat_id, "_id": ObjectId(id)}, transaction_in
        )

    def remove_transaction(self, chat_id, id):
        self._transactions.delete_one({"ChatId": chat_id, "_id": ObjectId(id)})

    def remove_all(self, chat_id):
        self._transactions.delete_many({"ChatId": chat_id})

    def save_settings(self, settings):
        existing_settings = self._settings.find_one({"ChatId": settings["ChatId"]})
        if existing_settings:
            if "Currency" in settings:
                existing_settings["Currency"] = settings["Currency"]

            if "SalaryDay" in settings:
                existing_settings["SalaryDay"] = settings["SalaryDay"]

            self._settings.replace_one(
                {"ChatId": settings["ChatId"]}, existing_settings
            )
            return existing_settings
        else:
            self._settings.insert_one(settings)
            return settings

    def get_settings(self, chat_id):
        return self._settings.find_one({"ChatId": chat_id})
