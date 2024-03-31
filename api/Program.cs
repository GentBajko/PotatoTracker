using api.Controllers;
using api.Services;
using dotenv.net;

DotEnv.Load();

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Register the TransactionService and TelegramBotController
builder.Services.AddSingleton<ConnectToMongo>();
builder.Services.AddSingleton<TransactionService>();
builder.Services.AddControllers(); // Register controllers

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseRouting();
app.UseEndpoints(endpoints =>
{
    endpoints.MapControllers();
});

app.Run();