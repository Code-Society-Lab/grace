from discord.ext.commands import Cog, hybrid_command
from discord.app_commands import Choice, autocomplete
from discord import Embed, Interaction
from openai.api_resources.completion import Completion
import openai
from lib.config_required import cog_config_required


LANGUAGES = [
    "Python", "C", "C++", "Java", "Csharp", "R", "Ruby", "JavaScript", "Swift",
    "Go", "Kotlin", "Rust", "PHP", "ObjectiveC", "SQL", "Lisp", "Perl",
    "Haskell", "Erlang", "Scala", "Clojure", "Julia", "Elixir", "F#", "Bash"
]

@cog_config_required("openai", "api_key", "Generate yours [here](https://beta.openai.com/account/api-keys)")
class CodeGenerator(
    Cog, name="OpenAI", 
    description="Generate code using OpenAI API by providing a comment and language."):
    """A Cog that generate code using text."""
    def __init__(self, bot):
        self.bot = bot
        self.api_key = self.required_config

    async def language_autocomplete(self, interaction: Interaction, current: str) -> list[Choice[str]]:
        """Provide autocomplete suggestions for programming languages name.

        :param interaction: The interaction object.
        :type interaction: Interaction
        :param current: The current value of the input field.
        :type current: str
        :return: A list of `Choice` objects containing languages name.
        :rtype: list[Choice[str]]
        """
        if not current:
            return [
                Choice(name=lang.capitalize(), value=lang.capitalize())
                for lang in LANGUAGES[:25] if current.lower() in lang.lower()
            ]
        else:
            return [
                Choice(name=lang.capitalize(), value=lang.capitalize())
                for lang in LANGUAGES if current.lower() in lang.lower()
            ]

    @hybrid_command(
        name='code',
        help='Generate code by providing a comment and language.',
        usage="language={programming_language} comment={sentence}"
        )
    @autocomplete(language=language_autocomplete)
    async def code_generator(self, ctx, *, language: str, comment: str) -> None:
        """Generate code using OpenAI API by providing a comment and language.

        :param ctx: The context object.
        :type ctx: Context
        :param language: The programming language to generate code.
        :type language: str
        :param sentence: The comment to generate code.
        :type sentence: str
        :return: None
        """
        openai.api_key = self.api_key # ---- Get you KEY API here link[https://beta.openai.com/account/api-keys] ---- #

        embed = Embed(
                    color=self.bot.default_color
                )

        if openai.api_key:
            response = Completion.create(
                model="text-davinci-003",
                prompt=f"{comment} in {language}",
                temperature=0.7,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        
            code_generated = response["choices"][0]["text"]
            embed.add_field(
                    name=comment.capitalize(),
                    value=f"```{language}{code_generated}``` {ctx.author} | {language}",
                    inline=False
            )

            await ctx.send(embed=embed, ephemeral=False)

        else:
            embed.add_field(
                    name="Key API No Found!",
                    value="Generate yours here -> https://beta.openai.com/account/api-keys",
                    inline=False
            )

            await ctx.send(embed=embed, ephemeral=False)


async def setup(bot):
    await bot.add_cog(CodeGenerator(bot))
