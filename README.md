
# Grace
Grace is the official Code Society discord bot. The goal is to allow every member of the Code Society to participate in the development of the server's bot. 

## Installation
Installing Grace is fairly simple.

0. Install [Python](https://www.python.org/downloads/). Note that the bot is developed under Python 3.0+ so be sure to have a recent version of Python.
1. In the `grace` directory do `pip install .` in a command line (windows) or terminal (Linux/MacOS) to install all the dependencies needed in order to make the bot work. 
2. In the same directory, create an environment file called `.env`. This file will contain your bot token. (The token is necessary to communicate with Discord. [Discord docs](https://discord.com/developers/docs))

```.env
DISCORD_TOKEN=<Your token>
```

## Usage
To run the bot, open a terminal or cli, enter and execute `python bot/`.
Note that the bot must be added to a server in order to use it. Please refer to [Discord's docs](https://discord.com/developers/docs) to get help setting up your bot.

The default bot prefix is `::`. To see the available commands, type, in Discord, `::help`.

For now, `pip install .` must be run before `python bot/` when running the bot. Running the directory as a script in pycharm's run configuration will work too. This is liable to change.

## Contribution
As mentioned in the description, we invite everyone to participate in the development of the bot. You can contribute to the project by simply opening an issue, by improving some current features or even by adding your own features.
Before contributing please refer to our [contribution guidelines](https://github.com/Code-Society-Lab/grace/blob/main/docs/CONTRIBUTING.md) and [Code of Conduct for contributor (temporary unavailable)](#).

## Support
For any other issues or questions feel free to [join](https://discord.gg/6GEF9H9m) our server and have a chat with us.
