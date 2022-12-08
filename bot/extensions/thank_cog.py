from typing import Optional, Union
from discord import Member, Embed, User
from discord.ext.commands import Cog, hybrid_command, Context, cooldown, BucketType
from bot.grace import Grace
from bot.models.extensions.thank.thank import Thank


class ThankCog(Cog):
    def __init__(self, bot: Grace):
        self.bot = bot

    def get_user_title(self, thank_count: int) -> str:
        if thank_count in range(1, 11):
            return 'Intern'
        elif thank_count in range(11, 21):
            return 'Helper'
        elif thank_count in range(21, 31):
            return 'Vetted helper'
        elif thank_count > 30:
            return 'Expert'
        else:
            return 'Unknown'

    @hybrid_command(name='thank_stats', description='Shows your current thank level.')
    @cooldown(1, 20, BucketType.user)
    async def thank_stats(self, ctx: Context, *, user_or_member: Optional[Union[Member, User]] = None):
        stats_embed = Embed(title="Stats")

        if user_or_member is None or ctx.author.id == user_or_member.id:
            if not Thank.does_member_exist(str(ctx.author.id)):
                stats_embed.description = "You haven't been thanked yet."
            else:
                thank_count = Thank.retrieve_member_thank_count(str(ctx.author.id))
                stats_embed.description = f"Your title is: **{self.get_user_title(thank_count)}**\nYour thank count is: {thank_count}"
        else:
            if user_or_member.id == self.bot.user.id:
                stats_embed.description = "Grace has a range of commands that can help you greatly!"
                return await ctx.reply(embed=stats_embed, ephemeral=True)

            if not Thank.does_member_exist(str(user_or_member.id)):
                stats_embed.description = f"User **@{user_or_member.display_name}** hasn't helped anyone yet."
            else:
                thank_count = Thank.retrieve_member_thank_count(str(user_or_member.id))
                stats_embed.description = f"User **@{user_or_member.display_name}** has title: **{self.get_user_title(thank_count)}**"

        await ctx.reply(embed=stats_embed, ephemeral=True)

    @hybrid_command(name='thank', description='Thank a person')
    @cooldown(1, 600, BucketType.user)
    async def thank(self, ctx: Context, *, user_or_member: Union[Member, User]):
        if user_or_member.id == self.bot.user.id:
            return await ctx.send("😊", ephemeral=True)

        if ctx.author.id == user_or_member.id:
            return await ctx.send('You cannot thank yourself.', ephemeral=True)

        user_id = str(user_or_member.id)
        if Thank.does_member_exist(user_id):
            Thank.increment_member_thank_count(user_id)
        else:
            Thank.add_member(user_id, 1)

        thank_embed = Embed(
            title="INFO",
            description=f"{user_or_member.display_name}, you were thanked by **{ctx.author.display_name}**\n"
                        f"Now, your thank count is: **{Thank.retrieve_member_thank_count(user_id)}**"
        )

        await user_or_member.send(embed=thank_embed)
        await ctx.interaction.response.send_message(f"Successfully thanked **@{user_or_member.display_name}**", ephemeral=True)


async def setup(bot: Grace):
    await bot.add_cog(ThankCog(bot))