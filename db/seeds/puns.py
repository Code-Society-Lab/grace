from bot.models.extensions.language.pun import Pun


def seed_database():
    pun_specs = [{
        'text': "What do you call a person who hates hippos because they're so hateful? Hippo-critical.",
        'pun_words': [
            {'word': 'hippo', 'emoji_code': ':hippopotamus:'},
            {'word': 'critical', 'emoji_code': ':thumbs_down:'}
        ]
    }, {
        'text': "You call a bad discord mod an admin-is-traitor.",
        'pun_words': [
            {'word': 'admin', 'emoji_code': ':hammer:'},
            {'word': 'traitor', 'emoji_code': ':hammer:'}
        ]
    }, {
        'text': "Games like nerdlegame are a form of mathochism.",
        'pun_words': [
            {'word': 'math', 'emoji_code': ':1234:'},
            {'word': 'masochism', 'emoji_code': ':knife:'}
        ]
    }]

    for pun_spec in pun_specs:
        pun = Pun.create(text=pun_spec['text'])

        for pun_word in pun_spec['pun_words']:
            pun.add_pun_word(pun_word['word'], pun_word['emoji_code'])
