from typing import Optional
import re

from discord.ext.commands import Cog, hybrid_command, Context
from discord import Embed, Message

from bot.extensions.command_error_handler import send_command_help
from bot.services.mermaid_service import generate_mermaid_diagram


class MermaidCog(Cog, name="Mermaid", description="Generates mermaid diagrams"):
    def __init__(self, bot):
        self.bot = bot
        self.mermaid_codeblock_regex = re.compile(r"```mermaid([\S\s]*)```")
        self.codeblock_regex = re.compile(r"```([\S\s]*)```")
        
    def generate_diagram_embed(self, diagram: str) -> Embed:
        """ First, we make sure that the API url returns OK (200) response code
        If OK, we return an embed with the image that'll be fetched from the API url
        If not OK, we return an embed with the error code
        
        :param script: Mermaid script
        :type script: str
        :rtype: Embed
        """
        embed = Embed()
        diagram_url = generate_mermaid_diagram(diagram)

        if diagram_url:
            embed.set_image(url=diagram_url)
        else:
            embed.title = "Mermaid compilation error"
            embed.description = "An error occurred while generating the diagram. Please, make sure there is no syntax error.\n\nhttps://mermaid.js.org/intro/getting-started.html"

        return embed

    def parse_code_block(
            self, 
            string: str,
            mermaid_block: bool = False,
            from_start: bool = False,
        ) -> str:
        """ Finds a code block in 'string'

        :example:
        ```
        THIS IS
        A CODE BLOCK
        ```

        ```mermaid
        THIS IS
        A MERMAID CODE BLOCK
        ```
        
        :param string: String from which the code block will be extracted
        :type script: str
        :param from_start: True to match the code block from the start of the string, False to match it in the whole string
        :type script: bool

        :returns: Matched code block value
        :rtype: str
        """
        codeblock_match = None

        if mermaid_block:
            codeblock_match = self.mermaid_codeblock_regex.search(string)
        elif from_start:
            codeblock_match = self.codeblock_regex.match(string)
        else:
            codeblock_match = self.codeblock_regex.search(string)

        print(codeblock_match)

        if codeblock_match:
            return codeblock_match.group(1)

        return ''

    @hybrid_command(
        name="mermaid", 
        description="Generates a diagram from mermaid script",
        help="""
        If you'd like to generate mermaid diagram image from a code block in a message, reply to the message with ::mermaid
        """
    )
    async def mermaid_command(self, ctx: Context, *, script_block: Optional[str]):
        """ Pass a discord code block with mermaid script inside to generate diagram image
        Or reply to a message containing the code block

        :param ctx: Invocation context
        :type ctx: Context
        :param script_block: Mermaid script to generate the diagram image from
        :type script_block: Optional[str]
        """
        diagram = None

        if not ctx.message.reference and script_block:
            diagram = self.parse_code_block(script_block, from_start=True)
        elif ctx.message.reference and not script_block:
            # Mermaid command on reply
            ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            diagram = self.parse_code_block(ref_msg.content)

        if not diagram:
            send_command_help(ctx)

        await ctx.reply(embed=self.generate_diagram_embed(diagram))

    @Cog.listener()
    async def on_message(self, message: Message):
        """ If mermaid code block is found in the message, the diagram image will be generated automatically

        :param message: User message
        :type message: Message
        """
        if message.author.id != self.bot.user.id:
            # Making sure there're no other messages referenced, and no mermaid command
            if message.reference or message.content.find(f"{self.bot.command_prefix}mermaid") != -1:
                return

            ctx = await self.bot.get_context(message)
            diagram = self.parse_code_block(message.content, mermaid_block=True)
            if not diagram:
                return

            await ctx.reply(embed=self.generate_diagram_embed(diagram))

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        """ If the message being modified contains mermaid code block, the diagram image will be regenerated automatically

        :param before: Old message
        :type before: Message
        :param after: Edited message
        :type after: Message
        """
        diagram = self.parse_code_block(after.content, mermaid_block=True)
        if not diagram:
            return

        ctx = await self.bot.get_context(after)
        await ctx.reply(embed=self.generate_diagram_embed(diagram))


async def setup(bot):
    await bot.add_cog(MermaidCog(bot))
