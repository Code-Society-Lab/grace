from bot.models.extensions.fun.language.trigger import Trigger


def seed_database():
    trigger_words = [
        "linus",
        "#linus",
        "#torvalds",
        "#linustorvalds",
        "torvalds"
    ]

    linus_trigger = Trigger(
        name="Linus",
        positive_emoji_code=":penguin:",
        negative_emoji_code=':rage:',
    )

    linus_trigger.save()

    for trigger_word in trigger_words:
        linus_trigger.add_trigger_word(trigger_word)

