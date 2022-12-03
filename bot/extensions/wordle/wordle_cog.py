from emoji import emojize
from discord.ext.commands import Cog, Bot, Context, hybrid_group, has_permissions
from bot.extensions.command_error_handler import send_command_help
from bot.models.extensions.games.wordle_words import WordleWords
from bot.models.extensions.games.wordle import Wordle
from discord.ui import View, Button
from discord import Interaction, Embed, File, Message, ButtonStyle
from bot.extensions.wordle.wordle_game import WordleGuess, WordleGame
from bot.extensions.wordle.wordle_image import WordleImage
from typing import Any, List, Callable, Self
from pathlib import Path
from os import remove as remove_file
from lib.bidirectional_iterator import BidirectionalIterator
from datetime import datetime


class MenuStartButton(Button):
    def __init__(
        self,
        embed_callback: Callable,
        view_callback: Callable,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.label: str = 'Start'
        self._embed: Callable = embed_callback
        # _view is some built-in attribute in the parent class.
        self.__view: Callable = view_callback

    async def callback(self, interaction: Interaction) -> Any:
        embed: Embed = self._embed()
        view: ViewPage = self.__view()

        header_file = 'wordle_header.png'
        header_path = Path(f'./bot/assets/{header_file}')

        wordle_grid: File = File(fp=header_path, filename=header_file)

        embed.set_image(url=f'attachment://{header_file}')

        await interaction.response.edit_message(embed=embed, view=view, attachments=[wordle_grid])


class MenuCancelButton(Button):
    def __init__(self, button_callback: Callable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label: str = 'Cancel'
        self._cancel_callback: Callable = button_callback

    async def callback(self, interaction: Interaction) -> Any:
        await self._cancel_callback()


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
        self.add_item(MenuStartButton(embed_callback, view_callback))
        self.add_item(MenuCancelButton(cancel_callback))


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
        self._wordle: WordleGame = current_wordle
        self._image_gen: WordleImage = image_gen
        self._layout = None

    def set_layout(self, layout):
        self._layout = layout

    async def callback(self, interaction: Interaction) -> Any:
        if self._wordle.full_guess():
            processed_guess = self._wordle.take_guess()

            # False when the guess isn't valid
            if isinstance(processed_guess, bool):
                self.view.embed.description = '**Invalid guess**'
                return await interaction.response.edit_message(embed=self.view.embed, view=self.view)

            if WordleGame.check_win(processed_guess):
                points = (self._wordle.tries + 1) * 2
                win_embed = Embed(
                    title='**Wordle Game**',
                    description=f'**Congratulations!** You guessed the word correctly!\n'
                                f'The word was: **{self._wordle.word}**\n'
                                f'Points: **{points}**\n'
                                f'**Thanks for playing! You can try again tomorrow!**',
                )
                Wordle.update_database(str(interaction.user.id), points)

                return await interaction.response.edit_message(embed=win_embed, view=None, attachments=[])

            self._wordle.decrement_tries()
            if self._wordle.tries == 0:
                points = 1
                defeat_embed = Embed(
                    title='**Wordle Game**',
                    description=f'Unfortunately you didn\'t guess a word.\n'
                                f'The word was: **{self._wordle.word}**\n'
                                f'Points: **{points}**\n'
                                f'**Thanks for playing! You can try again tomorrow!**',
                )
                Wordle.update_database(str(interaction.user.id), points)

                return await interaction.response.edit_message(embed=defeat_embed, view=None, attachments=[])

            if self._layout is not None:
                for button in self._layout:
                    if isinstance(button, LetterButton):
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

            self._image_gen.set_processed_word(self._wordle.guess, processed_guess)
            self._image_gen.next_row()

            await self.view.change_embed_image(interaction, self._image_gen)

            self._wordle.clear_guess()

        else:
            self.view.embed.description = '**Invalid length**'
            return await interaction.response.edit_message(embed=self.view.embed, view=self.view)


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
        self._cancel = cancel_callback

    async def callback(self, interaction: Interaction) -> Any:
        await self._cancel()


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
        self._wordle = current_wordle
        self._image_gen = image_generator
        self._layout = None

    def set_layout(self, layout):
        self._layout = layout

    async def callback(self, interaction: Interaction) -> Any:
        if self._wordle.full_guess():
            if self._layout is not None:
                for button in self._layout:
                    if isinstance(button, LetterButton):
                        button.disabled = False

        self._image_gen.clear_row()
        self._wordle.clear_guess()

        self.view.embed.description = ''

        await self.view.change_embed_image(interaction, self._image_gen)


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

        self._image_gen = image_gen
        self._wordle = current_wordle
        self._layout = None
        self.label = letter

    def set_layout(self, layout):
        self._layout = layout

    async def callback(self, interaction: Interaction) -> Any:
        if self._image_gen.has_next_column():
            input_letter: str = self.label.title().lower()

            self._image_gen.append_letter(input_letter, WordleGuess.EMPTY)
            self._wordle.add_guess_letter(input_letter)

            # Check if after appending there is another column available
            if not self._image_gen.has_next_column():
                if self._layout is not None:
                    for button in self._layout:
                        if isinstance(button, LetterButton):
                            button.disabled = True

            await self.view.change_embed_image(interaction, self._image_gen)


class ArrowButton(Button):
    def __init__(
        self,
        direction: str,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.emoji: str = emojize(f':{direction}_arrow:')

    def set_view(self, view):
        self._view = view
        if self._view is None:
            self.disabled = True

    async def callback(self, interaction: Interaction) -> Any:
        await interaction.response.edit_message(embed=self.view.embed, view=self._view)


class ViewPage(View):
    def __init__(
        self,
        embed_callback: Callable,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._embed = embed_callback
        self._left_arrow: ArrowButton = ArrowButton('left')
        self._right_arrow: ArrowButton = ArrowButton('right')
        self.add_item(self.left_arrow)
        self.add_item(self.right_arrow)

    async def change_embed_image(
            self,
            interaction: Interaction,
            image_gen: WordleImage,
    ):
        file_name: str = f'{interaction.user.id}.png'
        grid_path: str = f'./tmp/{file_name}'

        image_gen.save(grid_path)

        file: File = File(fp=Path(grid_path), filename=file_name)

        self.embed.set_image(url=f'attachment://{file_name}')

        await interaction.response.edit_message(embed=self.embed, attachments=[file], view=self)

        remove_file(Path(grid_path))

    @property
    def embed(self) -> Embed:
        return self._embed()

    def add_button(self, button):
        self.add_item(button)

    @property
    def left_arrow(self) -> ArrowButton:
        return self._left_arrow

    @property
    def right_arrow(self) -> ArrowButton:
        return self._right_arrow


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

        self.__views: BidirectionalIterator[ViewPage] = BidirectionalIterator[ViewPage]([
            MenuView(self.game_embed, self.next_view, self.cancel),
            ViewPage(self.game_embed),
            ViewPage(self.game_embed),
        ])

    def game_embed(self) -> Embed:
        return self.__embeds['game']

    def menu_embed(self) -> Embed:
        return self.__embeds['menu']

    def next_view(self) -> View:
        """ Switches to the next view, and instantiates the view elements."""

        # Delete current MenuView
        self.__views.remove(self.__views.current)

        # Create Letter buttons in the 1st ViewPage
        for i in range(65, 78):
            self.__views.current.add_button(LetterButton(
                chr(i),
                self.__wordle,
                self.__image_gen,
            ))

        # Create Enter Button in the 1st ViewPage
        self.__views.current.add_button(WordleEnterButton(
            self.__wordle,
            self.__image_gen
        ))
        # Create Clear Button in the 1st ViewPage
        self.__views.current.add_button(WordleClearButton(
            self.__wordle,
            self.__image_gen
        ))
        # Create Cancel Button in the 1st ViewPage
        self.__views.current.add_button(WordleCancelButton(self.cancel))

        # Create Letter buttons in the 2nd ViewPage
        for i in range(78, 91):
            self.__views.last.add_button(LetterButton(
                chr(i),
                self.__wordle,
                self.__image_gen,
            ))

        # Create Enter Button in the 2nd ViewPage
        self.__views.last.add_button(WordleEnterButton(
            self.__wordle,
            self.__image_gen
        ))

        # Create Clear Button in the 2nd ViewPage
        self.__views.last.add_button(WordleClearButton(
            self.__wordle,
            self.__image_gen
        ))
        # Create Cancel Button in the 2nd ViewPage
        self.__views.last.add_button(WordleCancelButton(self.cancel))

        # Set the layout(view page items) for each button in the view page, except the ArrowButton
        for button in (self.__views.current.children + self.__views.last.children):
            if isinstance(button, LetterButton) \
               or isinstance(button, WordleClearButton) \
               or isinstance(button, WordleEnterButton):
                button.set_layout(self.__views.current.children + self.__views.last.children)

        # Set the respective views for the arrow buttons
        self.__views.current.left_arrow.set_view(None)
        self.__views.current.right_arrow.set_view(self.__views.last)
        self.__views.last.left_arrow.set_view(self.__views.current)
        self.__views.last.right_arrow.set_view(None)

        # Set the current view (1st ViewPage)
        return self.__views.current

    async def cancel(self):
        await self.__message.delete()

    async def on_timeout(self):
        await self.__message.edit(embed=self.__embeds['game'], view=self)

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
        """ If no invoked subcommand was executed """
        if ctx.invoked_subcommand is None:
            await send_command_help(ctx)

    async def user_date(self, ctx: Context) -> bool:
        """ Checks is the user has played before """
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

    # TODO: Add a cooldown for the command
    @wordle_group.command(name='play', help='Start a wordle game')
    async def play_command(self, ctx: Context) -> None:

        last_play_check = await self.user_date(ctx)
        if last_play_check:
            return

        image_generator = WordleImage()
        self.set_resource_paths(image_generator)

        view = PagedGameView(
            current_wordle=WordleGame(self.words, 6),
            image_gen=image_generator
        )

        await view.send(ctx, True)

    @wordle_group.command(name='leaderboard', help='Send a leaderboard of top N players')
    @has_permissions(administrator=True)
    async def leaderboard_command(self, ctx: Context, *, top: int) -> None:
        user_list = Wordle.all()
        users = {}
        for query in user_list:
            users[query.user_id] = query.points

        top_users = dict(sorted(users.items(), key=lambda item: item[1], reverse=True))
        top_users = list(zip(list(top_users.keys()), list(top_users.values())))

        leaderboard_embed = Embed(
            title=f"**Wordle Game Top {top} Leaderboard**",
            description=''
        )
        for position, top_user_data in enumerate(top_users[:top]):
            username = await self.bot.fetch_user(int(top_user_data[0]))
            leaderboard_embed.description += f"_{position + 1}._ **{username}**: **{top_user_data[1]}** points\n"

        await ctx.channel.send(embed=leaderboard_embed)


async def setup(bot):
    await bot.add_cog(WordleCog(bot))
