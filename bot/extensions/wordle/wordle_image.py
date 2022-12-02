# WORDLE GRID IMAGE GENERATOR BASED ON THE GUESSED LETTERS #

from PIL import Image
from pathlib import Path
from bot.extensions.wordle.wordle_game import WordleGuess, WordleGame
from logging import error


class WordleImage:
    IMAGE_HORIZONTAL_SPACE = 70
    IMAGE_VERTICAL_SPACE = 70

    def __init__(self):
        self._header_default = None
        self._header = None
        self._current_row = 0
        self._current_column = 0
        self._history = {}
        self._paths = {}

    def set_header_path(self, path: str):
        """ Sets the path of the header/grid image """
        self._header_default = Image.open(Path(path))
        self._header = self._header_default.copy()

    def set_cell_path(self, guess_type: WordleGuess, path: str) -> None:
        """ Sets the path to the letter images of the respective guess type """
        self._paths[guess_type] = path

    def set_processed_word(self, word: str, processed_dict: dict) -> None:
        """ Sets the colors depending on the guess type: GOOD, PARTIAL or WRONG """
        elements = []
        for index, let in enumerate(word.lower()):
            elements.append((let, index, processed_dict[(let, index)]))

        self._current_column = 0
        for (letter, index, guess_type) in elements:
            self.append_letter(letter, guess_type)

        self._history[word] = processed_dict

        # TODO: Maybe return automatic next row

    def has_next_column(self):
        return self._current_column <= WordleGame.WORDLE_LENGTH - 1

    def has_next_row(self):
        return self._current_row <= 5

    def next_row(self):
        self._current_column = 0
        self._current_row += 1

    def clear_row(self):
        """ Resets all the parameters, redraws the grid, excluding the last one that wasn't yet set """
        self._header = self._header_default.copy()
        self._current_column = 0
        self._current_row = 0
        if self._history != {}:
            current_history = self._history.copy()
            self._history = {}
            for word, processed_dict in current_history.items():
                self.set_processed_word(word, processed_dict)
                self.next_row()

    def append_letter(self, letter: str, guess_type: WordleGuess) -> None:
        """ Appends the letter to the grid image """
        if len(letter) != 1:
            error('Pass a letter, not a string.')
            return

        if self._current_column >= WordleGame.WORDLE_LENGTH:
            error('No more columns to append to. Move to the next row.')
            return

        if not letter.islower():
            error('Letter must be lowercase.')
            return

        if self._header is None:
            error('Header path is not initialized. Use set_header_path()')
            return

        if len(self._paths) != 4:
            error('Not all cell assets paths were initialized. Make sure you initialized them. Use set_cell_path()')
            return

        letter_image = Image.open(Path(f'{self._paths[guess_type]}/{letter}.png'))
        self._header.paste(
            letter_image,
            (
                2 + (self._current_column * self.IMAGE_HORIZONTAL_SPACE),
                2 + (self._current_row * self.IMAGE_VERTICAL_SPACE)
            )
        )

        self._current_column += 1

    def save(self, file_path: str) -> None:
        """ Saves the image file with current settings """
        self._header.save(Path(file_path), quality=95)
