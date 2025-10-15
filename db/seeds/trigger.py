from bot.models.extensions.language.trigger import Trigger


def seed_database():
    trigger_words = ["linus", "#linus", "#torvalds", "#linustorvalds", "torvalds"]

    linus_trigger = Trigger.create(
        name="Linus",
        positive_emoji_code=":penguin:",
        negative_emoji_code=":pouting_face:",
    )
    for trigger_word in trigger_words:
        linus_trigger.add_trigger_word(trigger_word)

    Trigger.create(
        name='Grace',
        positive_emoji_code=':blush:',
        negative_emoji_code=':cry:',
    )
