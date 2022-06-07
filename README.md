
# Grace
Grace is the official Code Society discord bot. The goal is to allow every member of the Code Society to participate in the development of the server's bot. 

---

## Installation
Installing Grace is fairly simple. You can do it in three short step.

0. [Install Python and dependencies](#install-Python-and-dependencies)
1. [Set up your app and token](#set-up-your-app-and-token)
2. [Configure the database](#configure-the-database)


### Install Python and dependencies
0. The first step is pretty simple, install [Python](https://www.python.org/downloads/). You need to install Python 3.0 or
higher.

1. In the `grace` directory project, open a terminal (Linus/MacOS) or cmd (Windows) and execute `pip install -e .` 
(recommend for development) or `pip install .` to install all the dependencies needed in order to make the bot work. 
Wait until the process is finished.

### Set up your app and token
First, if you didn't already do it, [register](https://discord.com/developers/docs/getting-started#creating-an-app) your 
bot with Discord. Then, create a file called `.env` in the project directory. Open your new `.env` file and add 
`DISCORD_TOKEN=<Your token>` inside. (Replace <You token> by your discord token).

> It's imperative that you don't share that file nor the information inside it to anyone. 

### Configure the database
In order for the bot to work, you need to connect it to a database. SQLite, MySQL/MariaDB, PostgresSQL, Oracle and 
Microsoft SQL Server are all supported. ([Supported dialects](https://docs.sqlalchemy.org/en/14/dialects/index.html)) 

You can have three database configurations, one for each environment. Each section is delimited by 
`[database.<environment>]`. 

To set up the connection to your database, create a new file in the `config` folder and call it `database.cfg`. You can 
have three database configurations, one for each environment. Each section is delimited by `[database.<environment>]`. 

The next mandatory step is to set up the _adapter dialect + drivers (optional)_. The rest will depend on your database.
Bellow, you'll find example for common configuration (note that you need to replace the values for your database values).

> You can also use `config/database.template.cfg` to help you set up your database.

#### SQLite Database
```ini
[database.development]
adapter = sqlite
database = grace.db
```

#### Mysql server
```ini
[database.development]
adapter = mysql
user = grace
password = GraceHopper1234
host = localhost
port = 3306
```

#### Postgresql server
```ini
[database.development]
adapter = postgresql+psycopg2
user = grace
password = GraceHopper1234
host = localhost
port = 5432
```

#### Creating the tables and seeding the database
The last step is to create the tables and add data to the database. Simple execut the following commands :
- `grace db create`
- `grace db seed`

---

## Usage
The bot comes with a script to **manage** it.

### Basic Commands:
- **Bot Command(s)**:
  - `start` : Starts the bot (`ctrl+c` to stop the bot)
- **Database Command(s)**:
    - `db create` : Creates the database and the tables
    - `db drop` : Deletes the tables and the database
    - `db seed` : Seeds the tables (Initialize the default values)
    
All commands can take the optional `-e` argument with a string to define the environment.<br>
Available environment: (production [default], development, test)

> We recommend using "development" when you're in the development process

---

## Contribution
As mentioned in the description, we invite everyone to participate in the development of the bot. You can contribute to the project by simply opening an issue, by improving some current features or even by adding your own features.
Before contributing please refer to our [contribution guidelines](https://github.com/Code-Society-Lab/grace/blob/main/docs/CONTRIBUTING.md) and [Code of Conduct for contributor (temporary unavailable)](#).

---

## Support
For any other issues or questions feel free to [join](https://discord.gg/6GEF9H9m) our server and have a chat with us.
