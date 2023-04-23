# Personal Finance Telegram Bot

A simple Telegram bot that helps you track your income, spending, balance, and transaction history.

## Features

- Add income or expense with the interactive menu.
- Edit or delete transaction entries.
- Check your current balance.
- View your transaction history.
- Reset your balance and transaction history.
- Import and export transaction history as a CSV file.

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
docker build -t personal-finance-bot .
```
4. Run the Docker container:
```sh
docker run --rm --name personal-finance-bot personal-finance-bot
```
or
```sh
make run
```
### Usage
To use the bot, send it commands in a private chat or mention it in a group chat with its username:

`/menu`: Opens the interactive menu to add income, expenses, edit or delete entries, check balance, view transaction history, and import or export history.

In group chats, use the format `/command@your_bot_username`, replacing `your_bot_username` with your bot's actual username.

License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/GentBajko/PotatoTracker/blob/master/LICENSE) file for details.