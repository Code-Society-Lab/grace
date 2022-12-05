from enum import Enum
from typing import List, Dict
from random import choice as random_choice


class WordleGuess(Enum):
    GOOD = 1
    PARTIALLY = 2
    WRONG = 3
    EMPTY = 4


class WordleGame:
    """ Class with the game logic.

        :param words_list: The list of words to choose from
        :param tries: Amount of tries player has
    """

    WORDLE_LENGTH = 5

    def __init__(self, words_list: List[str], tries: int = 5) -> None:
        self.__tries: int = tries
        self.__words: List[str] = words_list
        self.__word: str = ''
        self.__guess: str = ''
        self.random_word()

    def add_guess_letter(self, letter: str):
        """ Appends letter to the current guess

            :param letter: Letter to append
        """
        if len(letter) != 1:
            print('Passed parameter must be a letter not a string.')
            return
        self.__guess += letter.lower()

    def is_full_guess(self) -> bool:
        """ Checks if the current guess is full/complete

            :returns: True if the guess is complete, otherwise False

            :rtype: bool
        """
        if len(self.__guess) == self.WORDLE_LENGTH:
            return True
        return False

    @staticmethod
    def has_user_won(processed_dict: dict) -> bool:
        """ User won if all the guess types are GOOD

            :returns: True if all the letters were guessed correctly, otherwise False

            :rtype: bool
        """
        for let_pos, guess_type in processed_dict.items():
            if guess_type != WordleGuess.GOOD:
                return False
        return True

    @property
    def word(self):
        return self.__word

    @property
    def guess(self):
        return self.__guess

    @property
    def tries(self):
        return self.__tries

    def clear_guess(self):
        """ Clears the current guess """
        self.__guess: str = ''

    def valid_guess(self) -> bool:
        """ Checks if the guess is valid, meaning that it exists in the bank of words """
        if self.__guess not in self.__words:
            return False
        return True

    def random_word(self) -> None:
        """ Chooses random word from the bank of words """
        self.__word = random_choice(self.__words)

    def decrement_tries(self):
        """ Decrements the tries count """
        self.__tries -= 1

    def process_guess(self) -> dict:
        """ Processes guess string

            :returns: Representation of a word:
            - WordleGuess.GOOD
            - WordleGuess.PARTIALLY
            - WordleGuess.WRONG
            - WordleGuess.EMPTY
            Each letter is in pair with it's position => (letter, index_pos)
            Example dict format: {(letter, index_pos): guess_type, ...} => {('b', 0): WordleGuess.PARTIALLY, ...}

            :rtype: dict
        """

        # Temporary word needed for handling the removal of letters in the word.
        tmp_word: str = self.__word
        # Letters that were already processed
        processed: List = []
        result: Dict = {}
        indexes_to_remove: List = []

        # Process GOOD letters
        for index, let in enumerate(self.__guess):
            if let == tmp_word[index]:
                if (let, index) not in processed:
                    result[(let, index)] = WordleGuess.GOOD
                    indexes_to_remove.append(index)
                    processed.append((let, index))

        # remove all the letters which were processed as GOOD ones
        tmp_word = ''.join([let for index, let in enumerate(tmp_word) if index not in indexes_to_remove])

        # Process PARTIALLY letters
        for index, let in enumerate(self.__guess):
            if let in tmp_word and (let, index) not in processed:
                result[(let, index)] = WordleGuess.PARTIALLY
                processed.append((let, index))

        # Process WRONG letters
        for index, let in enumerate(self.__guess):
            if (let, index) not in processed:
                result[(let, index)] = WordleGuess.WRONG
                processed.append((let, index))

        return result

    def take_guess(self) -> Dict | bool:
        """ Processes guess if it's valid

            :returns: False if the guess isn't valid, otherwise processed guess dict

            :rtype: bool | dict
        """
        valid: bool = self.valid_guess()
        if valid:
            return self.process_guess()
        else:
            return valid
