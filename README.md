# UBNetDef Discord Bot

A versatile Discord bot that provides utilities for role management, jokes, incident reporting, and more. It is designed to automate tasks like role removal, deliver bad jokes, and help manage incidents within a server.

## Features
- **Role Management**: Remove roles from all members with a confirmation prompt.
- **Bad Jokes**: Retrieve a specified number of random bad jokes.
- **Incident Reporting**: Report incidents like misconfigurations with detailed embeds.
- **Custom Commands**: A variety of customizable commands for user interaction.

## Prerequisites
Before setting up the bot, ensure you have the following installed:
- Python 3.x
- pip (Python package installer)
- [Discord Developer Portal](https://discord.com/developers/applications) account to create the bot

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Dark-Avenger-Reborn/UBNetDef-Discord-Bot.git
cd UBNetDef-Discord-Bot
```

### 2. Install dependencies
Install the required Python packages listed in the `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the root directory of the project. Add your bot's token and webhook URL:
```bash
SECRET_DISCORD_KEY=YOUR_BOT_TOKEN
WEBHOOK_URL=YOUR_WEBHOOK_URL
```

- **`SECRET_DISCORD_KEY`**: Your Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications).
- **`WEBHOOK_URL`**: A webhook URL for logging or notifications (you can get this from Discord Webhooks).

### 4. Set up the bot token:
Ensure that the bot token is correctly added in your `.env` file.

### 5. Run the bot
Start the bot by running:
```bash
python main.py
```

## Commands

### `/remove_role`
Removes a specified role from everyone in the server.

- **Permissions Required**: Only authorized users can execute this command.
- **Confirmation Required**: The bot will ask for confirmation before removing the role.

### `/bad_joke [quantity]`
Get a specified quantity of random bad jokes.

- **Usage**: `/bad_joke 3` to get 3 jokes.

## Contributing

Feel free to fork this repository, open issues, or submit pull requests if you'd like to contribute improvements or add new features!

---

### Acknowledgments
- **Libraries**: `discord.py`, `dotenv`, `requests`, and others.
