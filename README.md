
# Grace
Grace is the official Code Society discord bot. The goal is to allow every member of the Code Society to participate in the development of the server's bot. 

## Installation
Installing Grace is fairly simple.

0. Install [Python](https://www.python.org/downloads/). Note that the bot is developed under Python 3.0+ so be sure to have a recent version of Python.
1. In the `grace` directory project do, open a terminal (Linus/MacOS) or cmd (Windows) and execute `pip install -e .` (recommend for development) or `pip install .` to install all the dependencies needed in order to make the bot work. 
2. In the same directory, create an environment file called `.env`. This file will contain your bot token. (The token is necessary to communicate with Discord. [Discord docs](https://discord.com/developers/docs))

```.env
DISCORD_TOKEN=<Your token>
BOT_ENV=<production, development, test> # optional
```

## Usage
The bot comes with a script to **manage** it.

### Basic Commands:
- **Bot Command(s)**:
  - `start` : Starts the bot (`ctrl+c` to stop the bot)
- **Database Command(s)**:
    - `db create` : Creates the database and the tables
    - `db delete` : Deletes the tables and the database
    - `db seed` : Seeds the database tables (Initialize the default values)
    
All commands can takes the optional `-e` argument with a string to define the environment.<br>
Available environment: (production [default], development, test)

### Configuring the database
First, you need to configure the database in order for the bot to connect to it. Edit `config/database.py` and replace
the information by yours

- **Adapter**: The database type you're using (ex. postgresql, mysql, sqlite, ...) 
- **User**: The username of your database user
- **Password**: The password of the database user
- **host**: The database server host (in general it's `localhost`)
- **database**: The name of your database. (Should not be changed)

Second, execute the database creation command, `grace db create`.

Finally, seed the database by executing `grace db seed`.


You can now start the bot by executing `grace start`. Once the bot is up and running you can execute the commands by using the default prefix (`::`) or by pinging the bot. (Ex. `::help` or `@Grace help`)

_**N.B.** The bot must be added to a server in order to use it. Please refer to [Discord's docs](https://discord.com/developers/docs) to get help setting up your bot._

## Contribution
As mentioned in the description, we invite everyone to participate in the development of the bot. You can contribute to the project by simply opening an issue, by improving some current features or even by adding your own features.
Before contributing please refer to our [contribution guidelines](https://github.com/Code-Society-Lab/grace/blob/main/docs/CONTRIBUTING.md) and [Code of Conduct for contributor (temporary unavailable)](#).

## Support
For any other issues or questions feel free to [join](https://discord.gg/6GEF9H9m) our server and have a chat with us.
