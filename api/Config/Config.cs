using dotenv.net;

namespace api.Config
{
    public class Config
    {
        public Config()
        {
            DotEnv.Load();
            Console.WriteLine($"MONGO_URI: {MONGO_URI}");
            Console.WriteLine($"MONGO_DB: {MONGO_DB}");
            Console.WriteLine($"TELEGRAM_TOKEN: {TELEGRAM_TOKEN}");
        }

        public static string MONGO_URI => Environment.GetEnvironmentVariable("MONGO_URI") ?? "mongodb://localhost:27017/potatotracker";
        public static string MONGO_DB => Environment.GetEnvironmentVariable("MONGO_DB") ?? "potatotracker";
        public static string TELEGRAM_TOKEN => Environment.GetEnvironmentVariable("TELEGRAM_TOKEN") ?? "";
    }
}