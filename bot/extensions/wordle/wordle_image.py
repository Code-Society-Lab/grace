# WORDLE GRID IMAGE GENERATOR BASED ON THE GUESSED LETTERS #
from typing import Dict, List, Tuple, Optional

from PIL import Image
from pathlib import Path
from bot.extensions.wordle.wordle_game import WordleGuess, WordleGame, WORDLE_PROCESSED_DICT
from logging import error


class WordleImage:
    """ Image generating class for wordle game """

    IMAGE_HORIZONTAL_SPACE: int = 70
    IMAGE_VERTICAL_SPACE: int = 70

    def __init__(self):
        self.__header_default: Image = None
        self.__header: Image = None
        self.__current_row: int = 0
        self.__current_column: int = 0
        self.__history: Dict[str, WORDLE_PROCESSED_DICT] = {}
        self.__paths: Dict[WordleGuess, str] = {}

    def set_header_path(self, path: str):
        """Sets the path of the header/grid image

        :param path: Path to the header image
        """
        self.__header_default = Image.open(Path(path))
        self.__header = self.__header_default.copy()

    def set_cell_path(self, guess_type: WordleGuess, path: str):
        """Sets the path to the letter images of the respective guess type

        :param guess_type: Wordle guess type
        :param path: Path to the assets with the respective guess type
        """
        self.__paths[guess_type] = path

    def set_processed_word(self, word: str, processed_dict: WORDLE_PROCESSED_DICT):
        """Sets the colors depending on the guess type: GOOD, PARTIAL or WRONG

        :param word: The word to be set
        :param processed_dict:
        """
        elements: List[Tuple[str, int, WordleGuess]] = []
        for index, let in enumerate(word.lower()):
            elements.append((let, index, processed_dict[(let, index)]))

        self.__current_column = 0
        for (letter, index, guess_type) in elements:
            self.append_letter(letter, guess_type)

        self.__history[word] = processed_dict

    def has_next_column(self) -> bool:
        """

        :returns: True if the next cell exists, otherwise False
        """
        return self.__current_column <= WordleGame.WORDLE_LENGTH - 1

    def next_row(self):
        self.__current_column = 0
        self.__current_row += 1

    def clear_row(self):
        """ Resets all the parameters, redraws the grid, excluding the last one that wasn't yet set """
        self.__header = self.__header_default.copy()
        self.__current_column = 0
        self.__current_row = 0
        if self.__history != {}:
            current_history = self.__history.copy()
            self.__history = {}
            for word, processed_dict in current_history.items():
                self.set_processed_word(word, processed_dict)
                self.next_row()

    def append_letter(self, letter: str, guess_type: WordleGuess):
        """ Appends the letter to the grid image """
        if len(letter) != 1:
            error('Pass a letter, not a string.')
            return

        if self.__current_column >= WordleGame.WORDLE_LENGTH:
            error('No more columns to append to. Move to the next row.')
            return

        if not letter.islower():
            letter = letter.lower()

        if self.__header is None:
            error('Header path is not initialized. Use set_header_path()')
            return

        if len(self.__paths) != 4:
            error('Not all cell assets paths were initialized. Make sure you initialized them. Use set_cell_path()')
            return

        letter_image: Image = Image.open(Path(f'{self.__paths[guess_type]}/{letter}.png'))
        self.__header.paste(
            letter_image,
            (
                2 + (self.__current_column * self.IMAGE_HORIZONTAL_SPACE),
                2 + (self.__current_row * self.IMAGE_VERTICAL_SPACE)
            )
        )

        self.__current_column += 1

    def save(self, file_path: str):
        """ Saves the image file with current settings """
        self.__header.save(Path(file_path), quality=95)
