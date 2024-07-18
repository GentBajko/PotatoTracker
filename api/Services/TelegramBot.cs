using System.Collections.Concurrent;
using Telegram.Bot;
using Telegram.Bot.Types;
using Telegram.Bot.Types.Enums;
using Telegram.Bot.Types.ReplyMarkups;
using api.Models;
using api.Services;
using MongoDB.Bson;

public class TelegramBotService
{
    private readonly ITelegramBotClient _botClient;
    private readonly TransactionService _transactionService;
    private readonly ConcurrentDictionary<long, UserState> _userStates;
    private readonly ConcurrentDictionary<long, List<Transaction>> _transactionCache;

    public TelegramBotService(string botToken)
    {
        _botClient = new TelegramBotClient(botToken);
        _transactionService = new TransactionService();
        _userStates = new ConcurrentDictionary<long, UserState>();
        _transactionCache = new ConcurrentDictionary<long, List<Transaction>>();
        using var cts = new CancellationTokenSource();

        _botClient.StartReceiving(HandleUpdateAsync, HandleErrorAsync, cancellationToken: cts.Token);

        Console.WriteLine("Bot is running... Press any key to stop");
        Console.ReadKey();
        cts.Cancel();
    }

    private async Task HandleUpdateAsync(ITelegramBotClient botClient, Update update, CancellationToken cancellationToken)
    {
        if (update.Type != UpdateType.Message)
            return;

        var message = update.Message;
        if (message.Type != MessageType.Text)
            return;

        var chatId = message.Chat.Id;
        var messageText = message.Text;

        try
        {
            if (_userStates.ContainsKey(chatId))
            {
                await HandleUserState(chatId, messageText);
            }
            else
            {
                switch (messageText.ToLower())
                {
                    case "/start":
                        await ShowMainMenu(chatId);
                        break;
                    case "/income":
                        await StartIncomeCommand(chatId);
                        break;
                    case "/expense":
                        await StartExpenseCommand(chatId);
                        break;
                    case "/history":
                        await HandleHistoryCommand(chatId);
                        break;
                    case "/remove":
                        await StartRemoveCommand(chatId);
                        break;
                    case "/settings":
                        await ShowSettingsMenu(chatId);
                        break;
                    case "/monthly":
                        await HandleMonthlyCommand(chatId);
                        break;
                    case "/expensehistory":
                        await HandleExpenseHistoryCommand(chatId);
                        break;
                    case "/incomehistory":
                        await HandleIncomeHistoryCommand(chatId);
                        break;
                    case "/balance":
                        await HandleBalanceCommand(chatId);
                        break;
                    case "/monthlybalance":
                        await HandleMonthlyBalanceCommand(chatId);
                        break;
                    default:
                        break;
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error handling update: {ex.Message}");
            await _botClient.SendTextMessageAsync(chatId, "An error occurred. Please try again.");
            _userStates.TryRemove(chatId, out _);
        }
    }

    private Task HandleErrorAsync(ITelegramBotClient botClient, Exception exception, CancellationToken cancellationToken)
    {
        Console.WriteLine(exception.Message);
        return Task.CompletedTask;
    }

    private async Task HandleExpenseHistoryCommand(long chatId)
    {
        var history = _transactionService.GetHistory(chatId.ToString());
        var expenses = history.Transactions.Where(t => t.Type == TransactionType.Expense).ToList();
        _transactionCache[chatId] = expenses;
        var response = string.Join("\n", expenses.Select((t, index) => $"{index + 1}. [{t.Date:yyyy-MM-dd}] ${t.Amount:F2} - {t.Description}"));
        await _botClient.SendTextMessageAsync(chatId, response);
    }

    private async Task HandleIncomeHistoryCommand(long chatId)
    {
        var history = _transactionService.GetHistory(chatId.ToString());
        var incomes = history.Transactions.Where(t => t.Type == TransactionType.Income).ToList();
        _transactionCache[chatId] = incomes;
        var response = string.Join("\n", incomes.Select((t, index) => $"{index + 1}. [{t.Date:yyyy-MM-dd}] ${t.Amount:F2} - {t.Description}"));
        await _botClient.SendTextMessageAsync(chatId, response);
    }

    private async Task HandleBalanceCommand(long chatId)
    {
        var history = _transactionService.GetHistory(chatId.ToString());
        var incomeSum = history.Transactions.Where(t => t.Type == TransactionType.Income).Sum(t => t.Amount);
        var expenseSum = history.Transactions.Where(t => t.Type == TransactionType.Expense).Sum(t => t.Amount);
        var balance = incomeSum - expenseSum;
        await _botClient.SendTextMessageAsync(chatId, $"Your balance is: ${balance:F2}");
    }

    private async Task HandleMonthlyBalanceCommand(long chatId)
    {
        var history = _transactionService.GetHistory(chatId.ToString());
        var currentMonth = DateTime.Now.Month;
        var currentYear = DateTime.Now.Year;

        var incomeSum = history.Transactions
            .Where(t => t.Type == TransactionType.Income && t.Date.Month == currentMonth && t.Date.Year == currentYear)
            .Sum(t => t.Amount);
        var expenseSum = history.Transactions
            .Where(t => t.Type == TransactionType.Expense && t.Date.Month == currentMonth && t.Date.Year == currentYear)
            .Sum(t => t.Amount);

        var balance = incomeSum - expenseSum;
        await _botClient.SendTextMessageAsync(chatId, $"Your balance for {DateTime.Now:MMMM yyyy} is: ${balance:F2}");
    }

    private async Task HandleUserState(long chatId, string messageText)
    {
        var userState = _userStates[chatId];

        try
        {
            switch (userState.CurrentStep)
            {
                case UserState.Step.IncomeAmount:
                    if (decimal.TryParse(messageText, out decimal incomeAmount))
                    {
                        userState.Transaction = new Transaction { ChatId = chatId.ToString(), Amount = incomeAmount };
                        userState.CurrentStep = UserState.Step.IncomeDescription;
                        await _botClient.SendTextMessageAsync(chatId, "Write the description");
                    }
                    else
                    {
                        await _botClient.SendTextMessageAsync(chatId, "Invalid amount. Please enter a valid number.");
                        _userStates.TryRemove(chatId, out _);
                    }
                    break;

                case UserState.Step.IncomeDescription:
                    userState.Transaction.Description = messageText;
                    userState.Transaction.Date = DateTime.Now;
                    userState.Transaction.Type = TransactionType.Income;
                    _transactionService.Create(userState.Transaction);
                    _userStates.TryRemove(chatId, out _);
                    await _botClient.SendTextMessageAsync(chatId, "Income recorded.");
                    break;

                case UserState.Step.ExpenseAmount:
                    if (decimal.TryParse(messageText, out decimal expenseAmount))
                    {
                        userState.Transaction = new Transaction { ChatId = chatId.ToString(), Amount = expenseAmount };
                        userState.CurrentStep = UserState.Step.ExpenseDescription;
                        await _botClient.SendTextMessageAsync(chatId, "Write the description");
                    }
                    else
                    {
                        await _botClient.SendTextMessageAsync(chatId, "Invalid amount. Please enter a valid number.");
                        _userStates.TryRemove(chatId, out _);
                    }
                    break;

                case UserState.Step.ExpenseDescription:
                    userState.Transaction.Description = messageText;
                    userState.Transaction.Date = DateTime.Now;
                    userState.Transaction.Type = TransactionType.Expense;
                    _transactionService.Create(userState.Transaction);
                    _userStates.TryRemove(chatId, out _);
                    await _botClient.SendTextMessageAsync(chatId, "Expense recorded.");
                    break;

                case UserState.Step.RemoveId:
                    // First, check if settings for SalaryDay exist
                    var settings = _transactionService.GetSettings(chatId.ToString());
                    DateTime fromDate;

                    if (settings?.SalaryDay != null)
                    {
                        // If settings exist, use SalaryDay to determine fromDate
                        fromDate = new DateTime(DateTime.Now.Year, DateTime.Now.Month - 1, settings.SalaryDay.Value);
                    }
                    else
                    {
                        // If no settings, default to the same day last month
                        fromDate = new DateTime(DateTime.Now.Year, DateTime.Now.Month - 1, DateTime.Now.Day);
                    }

                    // Fetch transactions from the determined fromDate
                    var transactions = _transactionService.Get(chatId.ToString())
                                        .Where(t => t.Date >= fromDate)
                                        .ToList();
                    _transactionCache[chatId] = transactions;

                    // Check if the messageText can be parsed into a valid index
                    if (int.TryParse(messageText, out int index) && _transactionCache.ContainsKey(chatId) && index > 0 && index <= _transactionCache[chatId].Count)
                    {
                        var transaction = _transactionCache[chatId][index - 1];
                        _transactionService.Remove(chatId.ToString(), transaction.Id);
                        _userStates.TryRemove(chatId, out _);
                        await _botClient.SendTextMessageAsync(chatId, "Transaction removed.");
                    }
                    else
                    {
                        await _botClient.SendTextMessageAsync(chatId, "Invalid index. Please enter a valid transaction number from the history:");
                    }
                    break;


                case UserState.Step.SettingsMenu:
                    await HandleSettingsMenu(chatId, messageText);
                    break;

                case UserState.Step.Currency:
                    userState.Settings.Currency = messageText;
                    _transactionService.SaveSettings(userState.Settings);
                    _userStates.TryRemove(chatId, out _);
                    await _botClient.SendTextMessageAsync(chatId, "Currency updated.");
                    break;

                case UserState.Step.SalaryDay:
                    if (int.TryParse(messageText, out int salaryDay) && salaryDay >= 1 && salaryDay <= 31)
                    {
                        userState.Settings.SalaryDay = salaryDay;
                        _transactionService.SaveSettings(userState.Settings);
                        _userStates.TryRemove(chatId, out _);
                        await _botClient.SendTextMessageAsync(chatId, "Salary day updated.");
                    }
                    else
                    {
                        await _botClient.SendTextMessageAsync(chatId, "Invalid day. Please enter a valid day of the month (1-31):");
                        _userStates.TryRemove(chatId, out _);
                    }
                    break;
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error handling user state: {ex.Message}");
            await _botClient.SendTextMessageAsync(chatId, "An error occurred. Please try again.");
            _userStates.TryRemove(chatId, out _);
        }
    }

    private async Task ShowMainMenu(long chatId)
    {
        var keyboard = new ReplyKeyboardMarkup(new[]
        {
            new KeyboardButton[] { "/income", "/expense" },
            new KeyboardButton[] { "/history", "/remove" },
            new KeyboardButton[] { "/settings", "/monthly" },
            new KeyboardButton[] { "/expensehistory", "/incomehistory" },
            new KeyboardButton[] { "/balance", "/monthlybalance" }
        })
        {
            ResizeKeyboard = true,
            OneTimeKeyboard = true
        };

        await _botClient.SendTextMessageAsync(chatId, "Choose an option:", replyMarkup: keyboard);
    }

    private async Task StartIncomeCommand(long chatId)
    {
        _userStates[chatId] = new UserState { CurrentStep = UserState.Step.IncomeAmount };
        await _botClient.SendTextMessageAsync(chatId, "What is the income amount?");
    }

    private async Task StartExpenseCommand(long chatId)
    {
        _userStates[chatId] = new UserState { CurrentStep = UserState.Step.ExpenseAmount };
        await _botClient.SendTextMessageAsync(chatId, "What is the expense amount?");
    }

    private async Task StartRemoveCommand(long chatId)
    {
        _userStates[chatId] = new UserState { CurrentStep = UserState.Step.RemoveId };
        await _botClient.SendTextMessageAsync(chatId, "Enter the number of the transaction to remove (as shown in the history):");
    }

    private async Task ShowSettingsMenu(long chatId)
    {
        var keyboard = new ReplyKeyboardMarkup(new[]
        {
            new KeyboardButton("Currency"),
            new KeyboardButton("Salary Day")
        })
        {
            ResizeKeyboard = true,
            OneTimeKeyboard = true
        };

        _userStates[chatId] = new UserState { CurrentStep = UserState.Step.SettingsMenu, Settings = new Settings { ChatId = chatId.ToString() } };
        await _botClient.SendTextMessageAsync(chatId, "Choose a setting to update:", replyMarkup: keyboard);
    }

    private async Task HandleSettingsMenu(long chatId, string messageText)
    {
        switch (messageText.ToLower())
        {
            case "currency":
                _userStates[chatId].CurrentStep = UserState.Step.Currency;
                await _botClient.SendTextMessageAsync(chatId, "Enter your preferred currency:");
                break;

            case "salary day":
                _userStates[chatId].CurrentStep = UserState.Step.SalaryDay;
                await _botClient.SendTextMessageAsync(chatId, "Enter your salary day (1-31):");
                break;

            default:
                await ShowSettingsMenu(chatId);
                break;
        }
    }

    private async Task HandleHistoryCommand(long chatId)
    {
        var history = _transactionService.GetHistory(chatId.ToString());
        _transactionCache[chatId] = history.Transactions;
        var response = string.Join("\n", history.Transactions.Select((t, index) => $"{index + 1}. [{t.Date:yyyy-MM-dd}] ${t.Amount:F2} - {t.Description}"));
        await _botClient.SendTextMessageAsync(chatId, response);
    }

    private async Task HandleMonthlyCommand(long chatId)
    {
        var settings = _transactionService.GetSettings(chatId.ToString());
        if (settings?.SalaryDay != null)
        {
            DateTime fromDate = new DateTime(DateTime.Now.Year, DateTime.Now.Month - 1, settings.SalaryDay.Value);
            var transactions = _transactionService.Get(chatId.ToString())
                .Where(t => t.Date >= fromDate)
                .ToList();
            _transactionCache[chatId] = transactions;
            var response = string.Join("\n", transactions.Select((t, index) => $"{index + 1}. [{t.Date:yyyy-MM-dd}] ${t.Amount:F2} - {t.Description}"));
            await _botClient.SendTextMessageAsync(chatId, response);
        }
        else
        {
            await _botClient.SendTextMessageAsync(chatId, "You need to set your salary day first. Use /settings to set it.");
        }
    }

    private class UserState
    {
        public enum Step
        {
            IncomeAmount,
            IncomeDescription,
            ExpenseAmount,
            ExpenseDescription,
            RemoveId,
            SettingsMenu,
            Currency,
            SalaryDay
        }

        public Step CurrentStep { get; set; }
        public Transaction Transaction { get; set; }
        public Settings Settings { get; set; }
    }
}
