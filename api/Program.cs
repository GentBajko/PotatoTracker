using api.Config;
using api.Controllers;
using api.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Register the TransactionService and TelegramBotController
builder.Services.AddSingleton<TransactionService>();
builder.Services.AddSingleton<TelegramBotController>();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

// Start the Telegram bot when the application starts
app.Services.GetRequiredService<IHostApplicationLifetime>().ApplicationStarted.Register(() =>
{
    var botController = app.Services.GetRequiredService<TelegramBotController>();
    botController.StartBot();
});

app.Run();