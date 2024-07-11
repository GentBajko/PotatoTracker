using api.Models;
using MongoDB.Driver;
using MongoDB.Bson;
using System.Collections.Generic;

namespace api.Services
{
    public class TransactionService
    {
        private readonly IMongoCollection<Transaction> _transactions;
        private readonly IMongoCollection<Settings> _settings;

        public TransactionService()
        {
            var MongoInstance = new ConnectToMongo();
            var database = MongoInstance.Database;
            _transactions = database.GetCollection<Transaction>("Transactions");
            _settings = database.GetCollection<Settings>("Settings");
        }

        public List<Transaction> Get(string chatId)
        {
            return _transactions.Find(transaction => transaction.ChatId == chatId).ToList();
        }

        public Transaction Get(string chatId, ObjectId id)
        {
            return _transactions.Find(transaction => transaction.ChatId == chatId && transaction.Id == id).FirstOrDefault();
        }

        public History GetHistory(string chatId)
        {
            var transactions = Get(chatId);
            return new History { ChatId = chatId, Transactions = transactions };
        }

        public Transaction Create(Transaction transaction)
        {
            transaction.Id = ObjectId.GenerateNewId();
            _transactions.InsertOne(transaction);
            return transaction;
        }

        public void Update(string chatId, ObjectId id, Transaction transactionIn)
        {
            _transactions.ReplaceOne(transaction => transaction.ChatId == chatId && transaction.Id == id, transactionIn);
        }

        public void Remove(string chatId, ObjectId id)
        {
            _transactions.DeleteOne(transaction => transaction.ChatId == chatId && transaction.Id == id);
        }

        public Settings SaveSettings(Settings settings)
        {
            var existingSettings = _settings.Find(s => s.ChatId == settings.ChatId).FirstOrDefault();
            if (existingSettings != null)
            {
                if (settings.Currency != null)
                {
                    existingSettings.Currency = settings.Currency;
                }

                if (settings.SalaryDay.HasValue)
                {
                    existingSettings.SalaryDay = settings.SalaryDay;
                }

                _settings.ReplaceOne(s => s.ChatId == settings.ChatId, existingSettings);
                return existingSettings;
            }
            else
            {
                _settings.InsertOne(settings);
                return settings;
            }
        }

        public Settings GetSettings(string chatId)
        {
            return _settings.Find(s => s.ChatId == chatId).FirstOrDefault();
        }
    }
}
