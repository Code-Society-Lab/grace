from enum import Enum
from typing import List
from random import choice as random_choice


class WordleGuess(Enum):
    GOOD = 1
    PARTIALLY = 2
    WRONG = 3
    EMPTY = 4


class WordleGame:
    WORDLE_LENGTH = 5

    def __init__(self, words_list: List[str], tries: int = 5) -> None:
        self._tries = tries
        self._words = words_list
        self._word = ''
        self._guess = ''
        self.random_word()

    def add_guess_letter(self, letter: str):
        if len(letter) != 1:
            print('Passed parameter must be a letter not a string.')
            return
        self._guess += letter

    def full_guess(self):
        if len(self._guess) == self.WORDLE_LENGTH:
            return True
        return False

    @staticmethod
    def check_win(processed_dict: dict) -> bool:
        for let_pos, guess_type in processed_dict.items():
            if guess_type != WordleGuess.GOOD:
                return False
        return True

    @property
    def word(self):
        return self._word

    @property
    def guess(self):
        return self._guess

    @property
    def tries(self):
        return self._tries

    def clear_guess(self):
        self._guess = ''

    def valid_guess(self, guess: str) -> bool:
        if guess not in self._words:
            return False
        return True

    def random_word(self) -> None:
        self._word = random_choice(self._words)

    def decrement_tries(self):
        self._tries -= 1

    def process_guess(self, guess: str) -> dict:
        """ Returns representation of a word:
            - WordleGuess.GOOD
            - WordleGuess.PARTIALLY
            - WordleGuess.WRONG
            - WordleGuess.EMPTY
            Each letter is in pair with it's position => (letter, index_pos)
        """

        # Temporary word needed for handling the removal of letters in the word.
        tmp_word = self._word
        # Letters that were already processed
        processed = []
        result = {}
        indexes_to_remove = []

        # Process GOOD letters
        for index, let in enumerate(guess):
            if let == tmp_word[index]:
                if (let, index) not in processed:
                    result[(let, index)] = WordleGuess.GOOD
                    indexes_to_remove.append(index)
                    processed.append((let, index))

        # remove all the letters which were processed as GOOD ones
        tmp_word = ''.join([let for index, let in enumerate(tmp_word) if index not in indexes_to_remove])

        # Process PARTIALLY letters
        for index, let in enumerate(guess):
            if let in tmp_word and (let, index) not in processed:
                result[(let, index)] = WordleGuess.PARTIALLY
                processed.append((let, index))

        # Process WRONG letters
        for index, let in enumerate(guess):
            if (let, index) not in processed:
                result[(let, index)] = WordleGuess.WRONG
                processed.append((let, index))

        return result

    def take_guess(self) -> dict | bool:
        guess: str = self._guess.lower()
        valid: bool = self.valid_guess(guess)
        if valid:
            return self.process_guess(guess)
        else:
            return valid
