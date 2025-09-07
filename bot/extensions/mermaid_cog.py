from discord.ext.commands import Cog, hybrid_command, Context
from discord import Embed, Message
from bot.extensions.command_error_handler import send_command_help
from typing import Optional
import re
import requests
import base64


class MermaidCog(Cog, name="Mermaid", description="Generates mermaid diagrams"):
    def __init__(self, bot):
        self.bot = bot
        self.MERMAID_API = "https://mermaid.ink/img/"
        self.mermaid_codeblock_regex = re.compile(r"```mermaid([\S\s]*)```")
        self.codeblock_regex = re.compile(r"```([\S\s]*)```")

    def mermaid_script_to_base64(self, script: str) -> str:
        """ Converts script string to base64 encoding 
        
        :param script: String to be converted
        :type script: str

        :returns: Converted string
        :rtype: str
        """
        scriptbytes = script.encode("utf8")
        base64_bytes = base64.urlsafe_b64encode(scriptbytes)
        base64_string = base64_bytes.decode("ascii")
        return base64_string

    def get_api_url(self, script: str) -> str:
        """ Constructs mermaid ink API url to generate mermaid diagram image
        
        :param script: Mermaid script from which the diagram will be generated
        :type script: str

        :returns: Mermaid ink API url
        :rtype: str
        """
        return self.MERMAID_API + self.mermaid_script_to_base64(script)
        
    def create_mermaid_embed(self, script: str) -> Embed:
        """ First, we make sure that the API url returns OK (200) response code
        If OK, we return an embed with the image that'll be fetched from the API url
        If not OK, we return an embed with the error code
        
        :param script: Mermaid script
        :type script: str
        :rtype: Embed
        """
        mermaid_api_url = self.get_api_url(script)

        image_data = requests.get(mermaid_api_url)
        status_code = image_data.status_code

        embed = Embed()

        print("Got status code:", status_code)
        if status_code in [400, 404]:
            embed.title = "Mermaid compilation error"
            embed.description = "Unknown diagram"
            return embed
        elif status_code != 200:
            embed.title = "Mermaid compilation error"
            embed.description = f"Unknown API error. Status code: {status_code}"
            return embed

        embed.set_image(url=mermaid_api_url)
        return embed

    def parse_code_block(self, string: str, from_start: bool = False) -> str:
        """ Finds a code block in 'string'

        :example:
        ```
        THIS IS
        A CODE BLOCK
        ```
        
        :param string: String from which the code block will be extracted
        :type script: str
        :param from_start: True to match the code block from the start of the string, False to match it in the whole string
        :type script: bool

        :returns: Matched code block value
        :rtype: str
        """
        codeblock_match = None
        if from_start:
            codeblock_match = self.codeblock_regex.match(string)
        else:
            codeblock_match = self.codeblock_regex.search(string)

        if codeblock_match:
            return codeblock_match.group(1)

        return ''

    def parse_mermaid_code_block(self, string: str) -> str:
        """ Finds a mermaid code block in 'string' and returns its value

        :example:
        ```mermaid
        THIS IS A MERMAID CODE BLOCK
        ```
        
        :param string: String from which the mermaid code block will be extracted
        :type script: str

        :returns: Matched code block value
        :rtype: str
        """
        codeblock_match = self.mermaid_codeblock_regex.search(string)
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
        # Mermaid command with a code block containing mermaid script
        if not ctx.message.reference and script_block:
            # ::mermaid ``` <SCRIPT> ```
            mermaid_script = self.parse_code_block(script_block, from_start=True)
            if not mermaid_script:
                return await send_command_help(ctx)

            await ctx.reply(embed=self.create_mermaid_embed(mermaid_script))
        # Mermaid command with no code block but with a referenced message containing mermaid code block
        elif ctx.message.reference and not script_block:
            # Generate mermaid schema from referenced message
            ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            mermaid_script = self.parse_code_block(ref_msg.content)
            if not mermaid_script:
                return

            await ctx.reply(embed=self.create_mermaid_embed(mermaid_script))
        elif ctx.message.reference and script_block:
            pass

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
            mermaid_script = self.parse_mermaid_code_block(message.content)
            if not mermaid_script:
                return

            await ctx.reply(embed=self.create_mermaid_embed(mermaid_script))

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        """ If the message being modified contains mermaid code block, the diagram image will be regenerated automatically

        :param before: Old message
        :type before: Message
        :param after: Edited message
        :type after: Message
        """
        mermaid_script = self.parse_mermaid_code_block(after.content)
        if not mermaid_script:
            return

        ctx = await self.bot.get_context(after)
        await ctx.reply(embed=self.create_mermaid_embed(mermaid_script))


async def setup(bot):
    await bot.add_cog(MermaidCog(bot))
