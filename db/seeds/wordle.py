from bot.models.extensions.games.wordle import Wordle
from bot.models.extensions.games.wordle_words import WordleWords
from os import getcwd

def seed_database():
	"""The seed function. This function is needed in order for the seed to be executed"""
	# TODO: Might want to filter duplicates
	with open('./db/seeds/wordsbank.txt', 'r', encoding='utf8') as file:
		words = list(map(lambda word: word.strip(), file.read().split('\n')))

	for word in words:
		WordleWords.add_word(word=word, id=words.index(word))

	