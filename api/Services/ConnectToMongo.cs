using MongoDB.Driver;
using MongoDB.Bson;
using MongoDB.Driver.Linq;
using api.Models;


namespace api.Services
{
    public class ConnectToMongo
    {
        public IMongoDatabase Database { get; private set; }
        private readonly ILogger<ConnectToMongo> _logger;

        public ConnectToMongo()
        {
            _logger = new Logger<ConnectToMongo>(new LoggerFactory());
            var client = new MongoClient(Config.Config.MONGO_URI);
            var databaseName = "potatotracker";

            var databaseNames = client.ListDatabaseNames().ToList();
            _logger.LogInformation(Config.Config.MONGO_DB);
            Database = client.GetDatabase(databaseName);
            var Transactions = Database.GetCollection<Transaction>("Transactions");
        }

        public IMongoCollection<T> GetCollection<T>(string collectionName)
        {
            return Database.GetCollection<T>(collectionName);
        }

        public void DropCollection(string collectionName)
        {
            Database.DropCollection(collectionName);
        }

        public void DropDatabase()
        {
            Database.Client.DropDatabase(Database.DatabaseNamespace.DatabaseName);
        }

        public void DropAllCollections()
        {
            foreach (var collection in Database.ListCollectionNames().ToList())
            {
                Database.DropCollection(collection);
            }
        }

        public void DropAllDatabases()
        {
            foreach (var database in Database.Client.ListDatabaseNames().ToList())
            {
                Database.Client.DropDatabase(database);
            }
        }

        public void DropAll()
        {
            DropAllCollections();
            DropAllDatabases();
        }
    }
}