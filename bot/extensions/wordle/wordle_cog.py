from emoji import emojize
from discord.ext.commands import Cog, Bot, Context, hybrid_group, has_permissions
from bot.extensions.command_error_handler import send_command_help
from bot.models.extensions.games.wordle_words import WordleWords
from bot.models.extensions.games.wordle import Wordle
from discord.ui import View, Button, Item
from discord import Interaction, Embed, File, Message, ButtonStyle
from bot.extensions.wordle.wordle_game import WordleGuess, WordleGame
from bot.extensions.wordle.wordle_image import WordleImage
from typing import Any, Callable, List, Optional, Dict, Self
from pathlib import Path
from os import remove as remove_file
from lib.bidirectional_iterator import BidirectionalIterator
from datetime import datetime


class MenuStartButton(Button):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.label: str = 'Start'

    async def callback(self, interaction: Interaction) -> Any:
        embed: Embed = self.view.next_embed()
        view: View = self.view.next_view()

        header_file = 'wordle_header.png'
        header_path = Path(f'./bot/assets/{header_file}')

        wordle_grid: File = File(fp=header_path, filename=header_file)

        embed.set_image(url=f'attachment://{header_file}')

        await interaction.response.edit_message(embed=embed, view=view, attachments=[wordle_grid])


class MenuCancelButton(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label: str = 'Cancel'

    async def callback(self, interaction: Interaction) -> Any:
        await self.view.cancel_callback()


class MenuView(View):
    def __init__(
        self,
        embed_callback: Callable,
        view_callback: Callable,
        cancel_callback: Callable,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.next_embed: Callable = embed_callback
        self.next_view: Callable = view_callback
        self.cancel_callback: Callable = cancel_callback

        self.add_item(MenuStartButton())
        self.add_item(MenuCancelButton())


class WordleEnterButton(Button):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.label: str = 'Enter'
        self.style: ButtonStyle = ButtonStyle.green
    async def has_user_tries(self, interaction: Interaction) -> bool:
        """Checks whether user has any tries left

        :param interaction: User interaction with button

        :returns: False if user has no tries left, otherwise True

        :rtype: bool
        """
        wordle = self.view.wordle
        if wordle.tries == 0:
            points = 1
            defeat_embed = Embed(
                title='**Wordle Game**',
                description=f'Unfortunately you didn\'t guess a word.\n'
                            f'The word was: **{wordle.word}**\n'
                            f'Points: **{points}**\n'
                            f'**Thanks for playing! You can try again tomorrow!**',
            )
            Wordle.update_database(str(interaction.user.id), points)

            await interaction.response.edit_message(embed=defeat_embed, view=None, attachments=[])
            return False
        return True

    async def has_user_won(self, processed_guess: Dict[Any, WordleGuess], interaction: Interaction) -> bool:
        """Checks if user won

        :param processed_guess: Guess converted into dict format:
                                {guess_letter: guess_type, ...} => {'a': WordleGuess.GOOD, ...}
        :param interaction: User interaction with button

        :returns: True if user has won(guessed the word correctly), otherwise False

        :rtype: bool
        """
        if not WordleGame.has_user_won(processed_guess):
            return False

        wordle = self.view.wordle
        points = (wordle.tries + 1) * 2
        win_embed = Embed(
            title='**Wordle Game**',
            description=f'**Congratulations!** You guessed the word correctly!\n'
                        f'The word was: **{wordle.word}**\n'
                        f'Points: **{points}**\n'
                        f'**Thanks for playing! You can try again tomorrow!**',
        )
        Wordle.update_database(str(interaction.user.id), points)

        await interaction.response.edit_message(embed=win_embed, view=None, attachments=[])
        return True

    def change_buttons_color(self, processed_guess: Dict[Any, WordleGuess]):
        """ Changes the color of the buttons depending on the guessed letters and enables them """
        for button in self.view.layout:
            if not isinstance(button, LetterButton):
                continue
            button.disabled = False
            letter = button.label.lower()
            # Find all the letters of a button label in the processed dict
            letters = dict(filter(lambda x: x[0][0] == letter, processed_guess.items()))
            for _, guess_type in letters.items():
                # Change according to the correct answers hierarchy
                if guess_type == WordleGuess.GOOD:
                    button.style = ButtonStyle.green
                elif guess_type == WordleGuess.PARTIALLY:
                    if button.style == ButtonStyle.danger or \
                       button.style == ButtonStyle.gray:
                        button.style = ButtonStyle.primary
                else:
                    if button.style == ButtonStyle.gray:
                        button.style = ButtonStyle.danger

    async def is_guess_valid(
            self,
            processed_guess: Dict[Any, WordleGuess] | bool,
            interaction: Interaction
    ) -> bool:
        """Checks if the user's guess is valid

        :param processed_guess: Guess converted into dict format:
                                {guess_letter: guess_type, ...} => {'a': WordleGuess.GOOD, ...}
        :param interaction: User interaction with button

        :returns: True if the guess is valid, otherwise False

        :rtype: bool
        """
        if isinstance(processed_guess, bool):
            self.view.embed.description = '**Invalid guess**'
            await interaction.response.edit_message(embed=self.view.embed, view=self.view)
            return False
        return True

    async def callback(self, interaction: Interaction) -> Any:
        wordle = self.view.wordle
        image_gen = self.view.image_generator

        if not wordle.is_full_guess():
            self.view.embed.description = '**Invalid length**'
            return await interaction.response.edit_message(embed=self.view.embed, view=self.view)

        processed_guess = wordle.take_guess()

        if not await self.is_guess_valid(processed_guess, interaction):
            return

        if await self.has_user_won(processed_guess, interaction):
            return

        wordle.decrement_tries()
        if not await self.has_user_tries(interaction):
            return

        self.change_buttons_color(processed_guess)

        image_gen.set_processed_word(wordle.guess, processed_guess)
        image_gen.next_row()

        await self.view.change_embed_image(interaction, image_gen)

        self.view.wordle.clear_guess()


class WordleCancelButton(Button):
    def __init__(
        self,
        cancel_callback: Callable,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.label = 'Cancel'
        self.style = ButtonStyle.danger
        self.__cancel: Callable = cancel_callback

    async def callback(self, interaction: Interaction) -> Any:
        await self.__cancel()


class WordleClearButton(Button):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.label = 'Clear'
        self.style = ButtonStyle.primary

    def try_to_enable_buttons(self):
        """ Enables all the letter buttons if the row is full"""
        if self.view.wordle.is_full_guess():
            for button in self.view.layout:
                if isinstance(button, LetterButton):
                    button.disabled = False

    async def callback(self, interaction: Interaction) -> Any:
        self.try_to_enable_buttons()

        self.view.image_generator.clear_row()
        self.view.wordle.clear_guess()

        self.view.embed.description = ''

        await self.view.change_embed_image(interaction, self.view.image_generator)


class LetterButton(Button):
    def __init__(
        self,
        letter: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        if len(letter) != 1:
            raise Exception('Letter button must only be passed a letter.')

        self.label = letter

    def try_to_disable_buttons(self):
        """ Disables all the letter buttons in case current grid row is full/complete """
        if not self.view.image_generator.has_next_column():
            for button in self.view.layout:
                if isinstance(button, LetterButton):
                    button.disabled = True

    async def callback(self, interaction: Interaction) -> Any:
        image_gen = self.view.image_generator
        wordle = self.view.wordle

        if image_gen.has_next_column():
            image_gen.append_letter(self.label, WordleGuess.EMPTY)
            wordle.add_guess_letter(self.label)

            self.try_to_disable_buttons()

            await self.view.change_embed_image(interaction, image_gen)


class ArrowButton(Button):
    def __init__(
        self,
        direction: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.emoji: str = emojize(f':{direction}_arrow:')
        self.__direction: str = direction

    async def callback(self, interaction: Interaction) -> Any:
        view = None
        if self.__direction == 'left':
            view = self.view.previous_view()
        elif self.__direction == 'right':
            view = self.view.next_view()
        view.update_arrow_buttons()

        await interaction.response.edit_message(embed=self.view.embed, view=view)


class ViewPage(View):
    def __init__(
        self,
        embed_callback: Callable,
        current_wordle: WordleGame,
        image_generator: WordleImage,
        has_previous_callback: Callable,
        has_next_callback: Callable,
        previous_view_callback: Callable,
        next_view_callback: Callable,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.__embed: Callable = embed_callback
        self.__wordle: WordleGame = current_wordle
        self.__image_generator: WordleImage = image_generator
        self.__has_previous: Callable = has_previous_callback
        self.__has_next: Callable = has_next_callback
        self.__previous: Callable = previous_view_callback
        self.__next: Callable = next_view_callback
        self.__layout: Optional[List[Item]] = None
        self.__left_arrow: ArrowButton = ArrowButton('left')
        self.__right_arrow: ArrowButton = ArrowButton('right')
        self.add_item(self.__left_arrow)
        self.add_item(self.__right_arrow)

    def update_arrow_buttons(self):
        self.__left_arrow.disabled = not self.__has_previous()
        self.__right_arrow.disabled = not self.__has_next()

    def next_view(self) -> "ViewPage":
        return self.__next()

    def previous_view(self) -> "ViewPage":
        return self.__previous()

    @property
    def wordle(self) -> WordleGame:
        return self.__wordle

    @property
    def image_generator(self) -> WordleImage:
        return self.__image_generator

    @property
    def layout(self) -> List[Item]:
        """ Sets the layout(List) with the buttons of both ViewPages """
        return self.__layout

    @layout.setter
    def layout(self, buttons_layout: List[Item]):
        self.__layout = buttons_layout

    async def change_embed_image(self, interaction: Interaction, image_gen: WordleImage):
        file_name: str = f'{interaction.user.id}.png'
        grid_path: str = f'./tmp/{file_name}'

        image_gen.save(grid_path)

        file: File = File(fp=Path(grid_path), filename=file_name)

        self.embed.set_image(url=f'attachment://{file_name}')

        await interaction.response.edit_message(embed=self.embed, attachments=[file], view=self)

        remove_file(Path(grid_path))

    @property
    def embed(self) -> Embed:
        return self.__embed()


class PagedGameView(View):
    def __init__(
        self,
        current_wordle: WordleGame,
        image_gen: WordleImage
    ):
        super().__init__()

        self.__image_gen: WordleImage = image_gen
        self.__wordle: WordleGame = current_wordle
        self.__message: Optional[Message] = None
        self.__embeds: Dict[str, Embed] = {
            'menu': Embed(title='**Welcome to Wordle!**'),
            'game': Embed()
        }
        self.__views: BidirectionalIterator[View] = BidirectionalIterator[View]([
            MenuView(self.game_embed, self.next_view, self.cancel)
        ])

        self.create_view_pages()

    def create_view_page(self, letter_range_start: int, letter_range_end: int) -> ViewPage:
        """ Creates ViewPage with range of letter buttons """
        view_page: ViewPage = ViewPage(
            self.game_embed,
            self.__wordle,
            self.__image_gen,
            self.__views.has_previous,
            self.__views.has_next,
            self.__views.previous,
            self.__views.next,
        )

        for i in range(letter_range_start, letter_range_end):
            view_page.add_item(LetterButton(chr(i)))

        view_page.add_item(WordleEnterButton())
        view_page.add_item(WordleClearButton())
        view_page.add_item(WordleCancelButton(self.cancel))

        return view_page

    def create_view_pages(self):
        view_page1: ViewPage = self.create_view_page(65, 78)
        view_page2: ViewPage = self.create_view_page(78, 91)

        view_pages_children: List[Item] = view_page1.children + view_page2.children

        view_page1.layout = view_pages_children
        view_page2.layout = view_pages_children

        self.__views.add(view_page1)
        self.__views.add(view_page2)

        view_page1.update_arrow_buttons()

    def game_embed(self) -> Embed:
        return self.__embeds['game']

    def menu_embed(self) -> Embed:
        return self.__embeds['menu']

    def next_view(self) -> View:
        """ Removes MenuView """
        self.__views.remove(self.__views.current)
        return self.__views.current

    async def cancel(self):
        await self.__message.delete()

    async def on_timeout(self):
        await self.cancel()

    async def send(self, ctx: Context, ephemeral: bool = True):
        self.__message = await ctx.reply(
            embed=self.__embeds['menu'],
            view=self.__views.current,
            ephemeral=ephemeral
        )


class WordleCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.words = list(map(lambda query: query.word, WordleWords.all()))

    @hybrid_group(name='wordle', help='All wordle commands')
    async def wordle_group(self, ctx: Context) -> None:
        if ctx.invoked_subcommand is None:
            await send_command_help(ctx)

    async def has_user_played(self, ctx: Context) -> bool:
        user_query = Wordle.get_by(user_id=ctx.interaction.user.id)
        if user_query is not None:
            last_play_date = user_query.play_date
            present_date = datetime.now()
            time_delta = present_date - last_play_date

            if time_delta.days < 1:
                user_name = self.bot.get_user(int(user_query.user_id)).display_name
                early_embed = Embed(
                    title='**Wordle Game**',
                    description=f'**{user_name}**\n'
                                f'Points: **{user_query.points}**\n'
                                f'_You can try tomorrow at the same time you played the last game!_'
                )
                await ctx.interaction.response.send_message(embed=early_embed, ephemeral=True)
                return True

        return False

    def set_resource_paths(self, image_gen: WordleImage):
        """ Sets the asset paths of the image generator """
        image_gen.set_header_path('./bot/assets/wordle_header.png')
        image_gen.set_cell_path(WordleGuess.GOOD, './bot/assets/good_letters')
        image_gen.set_cell_path(WordleGuess.PARTIALLY, './bot/assets/partial_letters')
        image_gen.set_cell_path(WordleGuess.WRONG, './bot/assets/wrong_letters')
        image_gen.set_cell_path(WordleGuess.EMPTY, './bot/assets/empty_letters')

    @wordle_group.command(name='play', help='Start a wordle game')
    async def play_command(self, ctx: Context) -> None:
        if await self.has_user_played(ctx):
            return

        image_generator = WordleImage()
        self.set_resource_paths(image_generator)

        view = PagedGameView(
            current_wordle=WordleGame(self.words, 6),
            image_gen=image_generator
        )

        await view.send(ctx)

    @wordle_group.command(name='leaderboard', help='Send a leaderboard of top N players')
    @has_permissions(administrator=True)
    async def leaderboard_command(self, ctx: Context, *, top: int) -> None:
        user_list = Wordle.all()
        users = []

        for query in user_list:
            if query.user_id is None:
                continue
            users.append((query.user_id, query.points))

        if not users:
            return ctx.interaction.response.send_message('No players found.', ephemeral=True)

        top_users = list(sorted(users, key=lambda item: item[1], reverse=True))

        leaderboard_embed = Embed(title=f"**Wordle Game Top {top} Leaderboard**", description='')
        for position, (user_id, points) in enumerate(top_users):
            username = (await self.bot.fetch_user(int(user_id))).display_name
            leaderboard_embed.description += f"_{position + 1}._ **{username}**: **{points}** points\n"

        await ctx.interaction.response.send_message(embed=leaderboard_embed)


async def setup(bot):
    await bot.add_cog(WordleCog(bot))
