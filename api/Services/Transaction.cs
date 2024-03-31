using api.Models;
using MongoDB.Driver;

namespace api.Services
{
    public class TransactionService
    {
        private readonly IMongoCollection<Transaction> _transactions;

        public TransactionService(IMongoClient client)
        {
            var MongoInstance = new ConnectToMongo();
            var database = MongoInstance.Database;
            _transactions = database.GetCollection<Transaction>("Transactions");
        }

        public List<Transaction> Get(string chatId)
        {
            return _transactions.Find(transaction => transaction.ChatId == chatId).ToList();
        }

        public Transaction Get(string chatId, int id)
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
            _transactions.InsertOne(transaction);
            return transaction;
        }

        public void Update(string chatId, int id, Transaction transactionIn)
        {
            _transactions.ReplaceOne(transaction => transaction.ChatId == chatId && transaction.Id == id, transactionIn);
        }

        public void Remove(string chatId, int id)
        {
            _transactions.DeleteOne(transaction => transaction.ChatId == chatId && transaction.Id == id);
        }
    }
}