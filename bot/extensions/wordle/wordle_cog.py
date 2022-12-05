from emoji import emojize
from itertools import islice as slice_dict
from discord.ext.commands import Cog, Bot, Context, hybrid_group, has_permissions
from bot.extensions.command_error_handler import send_command_help
from bot.models.extensions.games.wordle_words import WordleWords
from bot.models.extensions.games.wordle import Wordle
from discord.ui import View, Button
from discord import Interaction, Embed, File, Message, ButtonStyle
from bot.extensions.wordle.wordle_game import WordleGuess, WordleGame
from bot.extensions.wordle.wordle_image import WordleImage
from typing import Any, Callable
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
        self.next_embed = embed_callback
        self.next_view = view_callback
        self.cancel_callback = cancel_callback

        self.add_item(MenuStartButton())
        self.add_item(MenuCancelButton())


class WordleEnterButton(Button):
    def __init__(
        self,
        current_wordle: WordleGame,
        image_gen: WordleImage,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.label: str = 'Enter'
        self.style: ButtonStyle = ButtonStyle.green
        self.__wordle: WordleGame = current_wordle
        self.__image_gen: WordleImage = image_gen
        self.__layout = None

    def set_layout(self, layout):
        self.__layout = layout

    async def has_user_tries(self, interaction: Interaction) -> bool:
        """Checks whether user has any tries left

        :param interaction: User interaction with button

        :returns: False if user has no tries left, otherwise True

        :rtype: bool
        """

        if self.__wordle.tries == 0:
            points = 1
            defeat_embed = Embed(
                title='**Wordle Game**',
                description=f'Unfortunately you didn\'t guess a word.\n'
                            f'The word was: **{self.__wordle.word}**\n'
                            f'Points: **{points}**\n'
                            f'**Thanks for playing! You can try again tomorrow!**',
            )
            Wordle.update_database(str(interaction.user.id), points)

            await interaction.response.edit_message(embed=defeat_embed, view=None, attachments=[])
            return False
        return True

    async def has_user_won(self, processed_guess: dict, interaction: Interaction) -> bool:
        """Checks if user won

        :param processed_guess: Guess converted into dict format:
                                {guess_letter: guess_type, ...} => {'a': WordleGuess.GOOD, ...}
        :param interaction: User interaction with button

        :returns: True if user has won(guessed the word correctly), otherwise False

        :rtype: bool
        """
        if not WordleGame.has_user_won(processed_guess):
            return False

        points = (self.__wordle.tries + 1) * 2
        win_embed = Embed(
            title='**Wordle Game**',
            description=f'**Congratulations!** You guessed the word correctly!\n'
                        f'The word was: **{self.__wordle.word}**\n'
                        f'Points: **{points}**\n'
                        f'**Thanks for playing! You can try again tomorrow!**',
        )
        Wordle.update_database(str(interaction.user.id), points)

        await interaction.response.edit_message(embed=win_embed, view=None, attachments=[])
        return True

    def change_buttons_color(self, processed_guess: dict):
        """ Changes the color of the buttons depending on the guessed letters and enables them """
        if self.__layout is None:
            return

        for button in self.__layout:
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

    async def is_guess_valid(self, processed_guess: dict | bool, interaction: Interaction) -> bool:
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
        if not self.__wordle.is_full_guess():
            self.view.embed.description = '**Invalid length**'
            return await interaction.response.edit_message(embed=self.view.embed, view=self.view)

        processed_guess = self.__wordle.take_guess()

        if not await self.is_guess_valid(processed_guess, interaction):
            return

        if await self.has_user_won(processed_guess, interaction):
            return

        self.__wordle.decrement_tries()
        if not await self.has_user_tries(interaction):
            return

        self.change_buttons_color(processed_guess)

        self.__image_gen.set_processed_word(self.__wordle.guess, processed_guess)
        self.__image_gen.next_row()

        await self.view.change_embed_image(interaction, self.__image_gen)

        self.__wordle.clear_guess()


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
        self.__cancel = cancel_callback

    async def callback(self, interaction: Interaction) -> Any:
        await self.__cancel()


class WordleClearButton(Button):
    def __init__(
        self,
        current_wordle: WordleGame,
        image_generator: WordleImage,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.label = 'Clear'
        self.style = ButtonStyle.primary
        self.__wordle = current_wordle
        self.__image_gen = image_generator
        self.__layout = None

    def set_layout(self, layout):
        self.__layout = layout

    def try_to_enable_buttons(self):
        """ Enables all the letter buttons if the row is full"""
        if self.__layout is None:
            return

        if self.__wordle.is_full_guess():
            for button in self.__layout:
                if isinstance(button, LetterButton):
                    button.disabled = False

    async def callback(self, interaction: Interaction) -> Any:
        self.try_to_enable_buttons()

        self.__image_gen.clear_row()
        self.__wordle.clear_guess()

        self.view.embed.description = ''

        await self.view.change_embed_image(interaction, self.__image_gen)


class LetterButton(Button):
    def __init__(
        self,
        letter: str,
        current_wordle: WordleGame,
        image_gen: WordleImage,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        if len(letter) != 1:
            raise Exception('Letter button must only be passed a letter.')

        self.__image_gen = image_gen
        self.__wordle = current_wordle
        self.__layout = None
        self.label = letter

    def set_layout(self, layout):
        """ Sets the layout(List) with the buttons of both ViewPages """
        self.__layout = layout

    def try_to_disable_buttons(self):
        """ Disables all the letter buttons in case current grid row is full/complete """
        if self.__layout is None:
            return

        if not self.__image_gen.has_next_column():
            for button in self.__layout:
                if isinstance(button, LetterButton):
                    button.disabled = True

    async def callback(self, interaction: Interaction) -> Any:
        if self.__image_gen.has_next_column():
            self.__image_gen.append_letter(self.label, WordleGuess.EMPTY)
            self.__wordle.add_guess_letter(self.label)

            self.try_to_disable_buttons()

            await self.view.change_embed_image(interaction, self.__image_gen)


class ArrowButton(Button):
    def __init__(
        self,
        direction: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.emoji: str = emojize(f':{direction}_arrow:')
        self.__direction = direction

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
        has_previous_callback: Callable,
        has_next_callback: Callable,
        previous_view_callback: Callable,
        next_view_callback: Callable,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.__embed = embed_callback
        self.__has_previous = has_previous_callback
        self.__has_next = has_next_callback
        self.__previous = previous_view_callback
        self.__next = next_view_callback
        self.__left_arrow: ArrowButton = ArrowButton('left')
        self.__right_arrow: ArrowButton = ArrowButton('right')
        self.add_item(self.__left_arrow)
        self.add_item(self.__right_arrow)

    def update_arrow_buttons(self):
        self.__left_arrow.disabled = not self.__has_previous()
        self.__right_arrow.disabled = not self.__has_next()

    def next_view(self):
        return self.__next()

    def previous_view(self):
        return self.__previous()

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
        self.__message: Message | None = None
        self.__embeds: dict = {
            'menu': Embed(title='**Welcome to Wordle!**'),
            'game': Embed()
        }

        self.__views: BidirectionalIterator[View] = BidirectionalIterator[View]([
            MenuView(self.game_embed, self.next_view, self.cancel)
        ])

        self.create_view_pages()

    def create_view_page(self, letter_range_start: int, letter_range_end: int) -> ViewPage:
        view_page = ViewPage(
            self.game_embed,
            self.__views.has_previous,
            self.__views.has_next,
            self.__views.previous,
            self.__views.next,
        )

        for i in range(letter_range_start, letter_range_end):
            view_page.add_item(LetterButton(
                chr(i),
                self.__wordle,
                self.__image_gen,
            ))

        view_page.add_item(WordleEnterButton(
            self.__wordle,
            self.__image_gen,
        ))

        view_page.add_item(WordleClearButton(
            self.__wordle,
            self.__image_gen,
        ))

        view_page.add_item(WordleCancelButton(self.cancel))

        return view_page

    def create_view_pages(self):
        view_page1 = self.create_view_page(65, 78)
        view_page2 = self.create_view_page(78, 91)

        view_pages_children = view_page1.children + view_page2.children
         # Set the layout(view page items) for each button in the view page, except the ArrowButton
        for button in view_pages_children:
            if isinstance(button, WordleCancelButton) or isinstance(button, ArrowButton):
                continue

            button.set_layout(view_pages_children)

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
        # await self.__message.edit(embed=self.__embeds['game'], view=self)
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

        top_users = list(sorted(users, key=lambda item: item[1], reverse=True))

        leaderboard_embed = Embed(title=f"**Wordle Game Top {top} Leaderboard**", description='')
        for position, (user_id, points) in enumerate(top_users):
            username = (await self.bot.fetch_user(int(user_id))).display_name
            leaderboard_embed.description += f"_{position + 1}._ **{username}**: **{points}** points\n"

        await ctx.interaction.response.send_message(embed=leaderboard_embed)


async def setup(bot):
    await bot.add_cog(WordleCog(bot))
