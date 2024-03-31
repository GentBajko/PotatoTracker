using api.Models.schema;
using MongoDB.Driver;

namespace api.Services
{
    public class ConnectToMongo
    {
        public IMongoDatabase Database { get; private set; }

        public ConnectToMongo()
        {
            var client = new MongoClient(Config.Config.MONGO_URI);
            Database = client.GetDatabase(Config.Config.MONGO_DB);
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