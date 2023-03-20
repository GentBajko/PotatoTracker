# Personal Finance Telegram Bot

A simple Telegram bot that helps you track your income, spending, balance, and transaction history.

## Features

- Add income with `/in [amount] [origin]`.
- Spend money and specify where you spent it with `/spend [amount] [category]`.
- Check your current balance with `/balance`.
- View your transaction history with `/history`.
- Reset your balance and transaction history with `/reset`.

## Prerequisites

- [Python 3.9+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started) (optional)

## Installation

### Without Docker

1. Clone this repository or download the files.

2. Install the required Python packages:

```sh
pip install -r requirements.txt
```
3. Replace YOUR_API_TOKEN in bot.py with your Telegram bot API token obtained from the BotFather.

4. Run the Python script:

```sh
python bot.py
```

### With Docker

1. Clone this repository or download the files.
2. Replace YOUR_API_TOKEN in bot.py with your Telegram bot API token obtained from the BotFather.
3. Build the Docker image:

```sh
docker build -t potato-tracker .
```
or

```sh
make build
```
4. Run the Docker container:

```sh
docker run -rm --name potato-tracker potato-tracker
```
or

```sh
make run
```

# Usage
To use the bot, send it commands in a private chat or mention it in a group chat with its username:

`/in [amount]`: Add income.

`/out [amount] [category]`: Spend money and specify the spending category.

`/balance`: Check your current balance.

`/history`: View your transaction history.

`/reset`: Reset your balance and transaction history.

In group chats, use the format `/command@`, replacing your_bot_username with your bot's actual username.

# License

This project is licensed under the MIT License. See the LICENSE file for details.