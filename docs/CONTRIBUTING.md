# Contributing to the project
We want everybody to be able to contribute to our projects whatever your level or programming experiance is. Don't hesitate to ask for help on the Code Society's [Discord server](https://discord.gg/6GEF9H9m) whatever the problem is.

## How you can contribute?
You can contribute to this project in the follwing ways 
- [Reporting a bug](#report-a-bug)
- [Proposing new features](#propose-a-new-feature)
- [Adding changes/Submitting a fix](#add-changes-or-submitting-a-fix)
- [Additional information](#additional-information)

## Report a bug
- Open an [issue](https://github.com/Code-Society-Lab/grace/issues) follwing the **bug template**. 
- Communicate directly with us on the Code Society's [Discord server](https://discord.gg/6GEF9H9m).
- Fix the bug directly. To do so, follow [add a changes](#add-changes).

---

## Propose a new feature.
- Open an [issue](https://github.com/Code-Society-Lab/grace/issues) follwing the **feature request template**.
- Communicate directly with us on the Code Society's [Discord server](https://discord.gg/6GEF9H9m).

---

## Add changes or Submitting a fix
### Setting up the bot
Installing Grace is fairly simple. You can do it in three short step.

0. [Install Python and dependencies](#install-python-and-dependencies)
1. [Set up your app and token](#set-up-your-app-and-token)
2. [Configuring the database](#configuring-the-database)

#### Install Python and dependencies
0. The first step is pretty simple, install [Python](https://www.python.org/downloads/). You need to install Python 3.0 or
higher.

1. In the `grace` directory project, open a terminal (Linus/MacOS) or cmd (Windows) and execute `pip install -e .` 
(recommend for development) or `pip install .` to install all the dependencies needed in order to make the bot work. 
Wait until the process is finished.

#### Set up your app and token
First, if you didn't already do it, [register](https://discord.com/developers/docs/getting-started#creating-an-app) your 
bot with Discord. Then, create a file called `.env` in the project directory. Open your new `.env` file and add 
`DISCORD_TOKEN=<Your token>` inside. (Replace <You token> by your discord token).

> Do not share that file nor the information inside it to anyone. 

#### Configuring the database
In order for the bot to work, you need to connect it to a database. SQLite, MySQL/MariaDB, PostgresSQL, Oracle and 
Microsoft SQL Server are all supported. ([Supported dialects](https://docs.sqlalchemy.org/en/14/dialects/index.html)) 

To set up the connection to your database, create a new file in the `config` folder and call it `database.cfg`. You can 
have three database configurations, one for each environment. Each section is delimited by `[database.<environment>]`. 

The next step is to set up the _adapter dialect + drivers (optional)_. The rest will depend on your database.
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
The last step is to create the tables and add data to them. Simply execute the following commands :
- `grace db create`
- `grace db seed`

### Before adding your changes
- Verify that there is no [issue](https://github.com/Code-Society-Lab/grace/issues) already created for the changes you want to bring. If there is and no one is assigned to the issue, assign it to yourself. 
- If there's no issue corresponding, [create one](https://github.com/Code-Society-Lab/grace/issues/new/choose). Don't forget to assign yourself the issue.

### Adding your changes
- Start by [Forking the repository](https://docs.github.com/en/github/getting-started-with-github/quickstart/fork-a-repo). 
- From your forked repository, apply your changes to the code. Don't forget to [setup](#setting-up-the-bot) your bot to test it.
- When you changes are done, [open a PR](#open-a-pull-request).

#### Submit your PR
Once your PR is submited, we (the staff) will [review](#review) it with you. The first thing you're going to want to do is a [self review](#self-review).

### Review
We review every Pull Request. The purpose of reviews is to create the best code possible and ensure that the code is secured and respect the guidelines.

- Reviews are always respectful, acknowledging that everyone did the best possible job with the knowledge they had at the time.<br>
- Reviews discuss content, not the person who created it.<br>
- Reviews are constructive and start conversation around feedback.

#### Self review
You should always review your own PR first.

#### How to self review my code?
- Confirm that the changes meet the user experience and goals of the bot.
- Ensure that your code is **clean** and follows Python's [PEP-0008](https://www.python.org/dev/peps/pep-0008/).
- Verify your code for grammar and spelling mistakes (The code and the text must be in **English**).
- Test your changes to ensure there's no bugs.

#### What to do after your PR is merged?
Congratulate yourself, you did it! The Code Society thank you for helping us improve our community.

### Open a Pull Request
- The name of the PR must be the same as the issue related to the PR.
- The PR must be linked to the opened issue.
- The PR must describe what change have been done.
  - Images or examples of the changes are more than welcome if necessary.

### Code guidelines
- The code must follow Python's [PEP-0008](https://www.python.org/dev/peps/pep-0008/).
- The code must be consistent and use descriptive names.
- The code must try to be the most modular as possible.

_In case of doubt, don't hesitate to ask for help on the [Discord server](https://discord.gg/6GEF9H9m)._

---

## Additional information
- All development has been tested on **Linux**. Running the bot on **Windows** could cause some issues or unexpected results. 
- Note that **we reserve the right** to close and/or refuse any issue (Don't worry we will indicate why).
- Even after your PRs are merged, it may take some time to be applied on the server since the changes needs to be tested before entering in production. 


