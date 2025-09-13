from typing import Optional
import re

from discord.ext.commands import Cog, command, Context
from discord import Embed, Message

from bot.extensions.command_error_handler import send_command_help
from bot.services.mermaid_service import generate_mermaid_diagram


class MermaidCog(Cog, name="Mermaid", description="Generates mermaid diagrams"):
    def __init__(self, bot):
        self.bot = bot
        self.mermaid_codeblock_pattern = r"```mermaid\n(.*?)```"
        self.codeblock_pattern = r"```\n(.*?)```"
        
    def generate_diagram_embed(self, diagram: str) -> Embed:
        """ First, we make sure that the API url returns OK (200) response code
        If OK, we return an embed with the image that'll be fetched from the API url
        If not OK, we return an embed with the error code
        
        :param diagram: Mermaid script
        :type diagram: str
        :rtype: Embed
        """
        embed = Embed()
        diagram_url = generate_mermaid_diagram(diagram)

        if diagram_url:
            embed.title = "Diagram";
            embed.set_image(url=diagram_url)
        else:
            embed.title = "Mermaid compilation error"
            embed.description = "An error occurred while generating the diagram. Please, make sure there is no syntax error.\n\nhttps://mermaid.js.org/intro/getting-started.html"

        return embed

    def extract_code_block(
            self, 
            content: str,
            require_mermaid_tag: bool = False,
        ) -> str:
        """ Extracts a code block from 'content'

        :example:
        ```
        THIS IS
        A CODE BLOCK
        ```

        ```mermaid
        THIS IS
        A MERMAID CODE BLOCK
        ```
        
        :param content: String from which the code block will be extracted
        :type content: str
        :param require_mermaid_tag: Whether mermaid tag is required in a code block or not
        :type require_mermaid_tag: bool

        :returns: Matched code block value
        :rtype: str
        """
        if require_mermaid_tag:
            if codeblock_match := re.search(self.mermaid_codeblock_pattern, content, re.DOTALL):
                return codeblock_match.group(1).strip()
        elif codeblock_match := re.search(self.codeblock_pattern, content, re.DOTALL):
            return codeblock_match.group(1).strip()

        return ''

    @command(name="mermaid", help="Generate a diagram from mermaid script", usage="՝՝՝\nMermaid script goes here...\n՝՝՝")
    async def mermaid(self, ctx: Context, *, content: Optional[str]):
        """ Generates a diagram from mermaid script
        Reply with this command to a message that contains a code block with mermaid script to generate a diagram from it    

        :param ctx: Invocation context
        :type ctx: Context
        :param content: Code block containing mermaid script
        :type content: Optional[str]
        """
        diagram = None

        if not ctx.message.reference and content:
            diagram = self.extract_code_block(content)
        elif ctx.message.reference and not content:
            # Mermaid command on reply
            ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            diagram = self.extract_code_block(ref_msg.content)

        if not diagram:
            return await send_command_help(ctx)

        await ctx.reply(embed=self.generate_diagram_embed(diagram))

    @Cog.listener()
    async def on_message(self, message: Message):
        """ If mermaid code block is found in the message, the diagram image will be generated automatically

        :param message: User message
        :type message: Message
        """
        if message.author.id == self.bot.user.id:
            return

        ctx = await self.bot.get_context(message)

        # Making sure there're no messages referenced, and no mermaid command being executed so that it doesn't overlap with the function that executes the command
        if message.reference or ctx.command:
            return

        diagram = self.extract_code_block(message.content, require_mermaid_tag=True)
        if diagram:
            await ctx.reply(embed=self.generate_diagram_embed(diagram))

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        """ If the message being modified contains mermaid code block, the diagram image will be regenerated automatically

        :param before: Old message
        :type before: Message
        :param after: Edited message
        :type after: Message
        """
        diagram = self.extract_code_block(after.content, require_mermaid_tag=True)
        if diagram:
            ctx = await self.bot.get_context(after)
            await ctx.reply(embed=self.generate_diagram_embed(diagram))


async def setup(bot):
    await bot.add_cog(MermaidCog(bot))
