# Contributing to the project
We want everybody to be able to contribute to our projects whatever your level or programming experiance is. Don't hesitate to ask for help on the Code Society's [Discord server](https://discord.gg/6GEF9H9m) whatever the problem is.

### How you can contribute?
You can contribute to this project in the follwing ways 
- [Reporting a bug](#report-a-bug)
- [Proposing new features](#propose-a-new-feature)
- [Submitting a fix](#add-changes)
- [Adding changes](#add-changes)

## Report a bug
- Open an [issue](https://github.com/Code-Society-Lab/grace/issues) follwing the **bug template**. 
- Communicate directly with us on the Code Society's [Discord server](https://discord.gg/6GEF9H9m).
- Fix the bug directly. To do so, follow [add a changes](#add-changes).

## Propose a new feature.
- Open an [issue](https://github.com/Code-Society-Lab/grace/issues) follwing the **feature request template**.
- Communicate directly with us on the Code Society's [Discord server](https://discord.gg/6GEF9H9m).

## Add changes
### Setting up the bot
- Read the [Code of conduct](#).
- Install the python version supported by the bot. You can find the version in `setup.py` or by reading the [wiki](https://github.com/Code-Society-Lab/grace/wiki).
- Configure you bot following [Discord's documentation](https://discord.com/developers/docs/intro). (Note that you need to test your change(s) in a private server)
- In the main directory of the project, execute in a command line (Windows) or terminal (Linux/MacOS) `pip install .` to install all the dependencies needed.
- Finally, insert your token in the `.env` file like so `DISCORD_TOKEN=<Your token>`. If the file doesn't exist simply create one.

Once all is setup, you can bring your bot to life by executing `python bot/`.

### Before adding your changes
- Verify that there is no [issue](https://github.com/Code-Society-Lab/grace/issues) already created for the changes you want to bring. If there is and no one is assigned to the issue, assign it to yourself. 
- If there's no issue corresponding, [create one](https://github.com/Code-Society-Lab/grace/issues/new/choose). Don't forget to assign yourself the issue.

### Adding your changes
- Start by [Forking the repository](https://docs.github.com/en/github/getting-started-with-github/quickstart/fork-a-repo). 
- From your forked repository, apply your changes to the code. Don't forget to [setup](#setting-up-the-bot) your bot to test it.
- When you changes are done, [open a PR](#open-a-pull-request).

#### Submit your PR
Once your PR is submited, we (the staff) will [review](#review) it with you. The first thing you're going to want to do is a [self review](#self-review).

## Review
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
- Test your changes to ensure there's not bugs.

#### What to do after your PR is merged?
Congratulate yourself, you did it! The Code Socitety thank you for helping us improve our community.

## Open a Pull Request
- The name of the PR must be the same as the issue related to the PR.
- The PR must be linked to the opened issue.
- The PR must describe what change have been done.
  - Images or examples of the changes are more than welcome if necessary.

## Code guidelines
- The code must follow Python's [PEP-0008](https://www.python.org/dev/peps/pep-0008/).
- The code must be consistent and use descriptive names.
- The code must try to be the most modular as possible.

_In case of doubt, don't hesitate to ask for help on the [Discord server](https://discord.gg/6GEF9H9m)._

## Additional informations
- All development has been tested on **Linux**. Running the bot on **Windows** could cause some issues or unexpected results. 
- Note that **we reserve the right** to close and/or refuse any issue (Don't worry we will indicate why).
- Even after your PRs are merged, it may take some time to be applied on the server since the changes needs to be tested before entering in production. 


