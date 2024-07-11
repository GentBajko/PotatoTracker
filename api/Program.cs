using dotenv.net;
using api.Services;

class Program
{
    static void Main(string[] args)
    {
        DotEnv.Load(); // Load environment variables from .env file

        var botToken = Environment.GetEnvironmentVariable("TELEGRAM_TOKEN");

        if (string.IsNullOrEmpty(botToken))
        {
            Console.WriteLine("TELEGRAM_TOKEN is not set in .env file");
            return;
        } else {
            var telegramBotService = new TelegramBotService(botToken);
        }
    }
}
