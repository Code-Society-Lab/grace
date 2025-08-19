
# Grace
[![Join on Discord](https://discordapp.com/api/guilds/823178343943897088/widget.png?style=shield)](https://discord.gg/code-society-823178343943897088)
[![Grace tests](https://github.com/Code-Society-Lab/grace/actions/workflows/grace.yml/badge.svg?branch=main)](https://github.com/Code-Society-Lab/grace/actions/workflows/grace.yml)
[![Last Updated](https://img.shields.io/github/last-commit/code-society-lab/grace.svg)](https://github.com/code-society-lab/grace/commits/main)

Grace is the official Code Society discord bot. The goal is to give our members the opportunity to participate in the
development of the server's bot and contribute to a team project while also improving it.

---

## Installation
Installing Grace is fairly simple. You can do it in three short step.

0. [Install Python and dependencies](#0-install-python-and-dependencies)
1. [Set up your app and token](#1-set-up-your-app-and-token)
2. [Start the bot](#2-start-the-bot)

### 0. Python and Dependencies
Install [Python](https://www.python.org/downloads/). Python 3.10 or higher is required.

> [!NOTE]
> We highly recommend that you set up a virtual environment to work on Grace.
> https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

In the `grace` directory, open a terminal (Linus/MacOS) or cmd (Windows) and execute `pip install -e .` 
(recommended for development) or `pip install .`. 

### 1. Set up your App and Token
If you did not already do it, [create](https://discord.com/developers/docs/getting-started#creating-an-app) your Discord 
bot. Then, create a file called `.env` in the project directory, open it and add 
`DISCORD_TOKEN=<Your token>`. (Replace <Your token> by your discord token).

> [!CAUTION]
> Do not share that file nor the information inside with anyone.

### 2. Run the Bot
The last part is to execute the bot. Execute `grace run` to run Grace in development mode. The rest
of the installation should complete itself and start the bot.

> [!NOTE]
> If the grace command is unrecognized, be sure that you installed the bot properly.

## Script Usage
- **Bot Command(s)**:
  - `grace run` : Starts the bot (`ctrl+c` to stop)
- **Database Command(s)**:
    - `grace db create` : Creates the database
    - `grace db drop`   : Deletes the database
    - `grace db up`     : Upgrade to latest migration
    - `grace db down`   : Downgrade to previous migration
    - `grace db seed`   : Seeds the tables

Run `grace --help` for more information.
---

## Advance configurations
For advance configurations, visit the [wiki](https://github.com/Code-Society-Lab/grace/wiki)

## Contribution
As mentioned in the description, we invite everyone to participate in the development of the bot. You can contribute to the project by simply opening an issue, by improving some current features or even by adding your own features.
Before contributing please refer to our [contribution guidelines](https://github.com/Code-Society-Lab/grace/blob/main/docs/CONTRIBUTING.md) and [Code of Conduct for contributor (temporary unavailable)](#).

---

## Troubleshooting
If you're getting unexpected result, visit the wiki's [troubleshooting](https://github.com/Code-Society-Lab/grace/wiki/Troubleshooting)
page. For any other problems or questions ask us on our [discord  server](https://discord.gg/code-society-823178343943897088).
