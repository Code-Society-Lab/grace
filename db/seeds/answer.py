from bot.models.extensions.fun.answer import Answer


def seed_database():
    initial_answers = [
        "Hell no.",
        "Prolly not.",
        "Idk bro.",
        "Prolly.",
        "Hell yeah my dude.",
        "It is certain.",
        "It is decidedly so.",
        "Without a Doubt.",
        "Definitely.",
        "You may rely on it.",
        "As i see it, Yes.",
        "Most Likely.",
        "Outlook Good.",
        "Yes!",
        "No!",
        "Signs a point to Yes!",
        "Reply Hazy, Try again.",
        "IDK m8 try again.",
        "Better not tell you know.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't Count on it.",
        "My reply is No.",
        "My sources say No.",
        "Outlook not so good.",
        "Very Doubtful"
    ]

    for answer in initial_answers:
        Answer.create(answer=answer)
