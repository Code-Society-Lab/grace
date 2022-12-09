from typing import List
from discord import Member, Embed
from discord.ext.commands import Cog, Context, cooldown, BucketType, hybrid_group, has_permissions
from sqlalchemy.orm import Query
from bot.grace import Grace
from bot.models.extensions.thank import Thank
from build.lib.bot.extensions.command_error_handler import send_command_help


class ThankCog(Cog):
    def __init__(self, bot: Grace):
        self.bot: Grace = bot

    @hybrid_group(name="thank", help="Thank commands", invoke_without_command=True)
    async def thank_group(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await send_command_help(ctx)

    @thank_group.command(name='send', description='Send a thank you to a person')
    @cooldown(1, 1, BucketType.user)
    async def thank(self, ctx: Context, *, member: Member):
        if member.id == self.bot.user.id:
            return await ctx.send(f"{ctx.author.display_name}, thank you 😊", ephemeral=True)

        if ctx.author.id == member.id:
            return await ctx.send('You cannot thank yourself.', ephemeral=True)

        thank: Thank = Thank.get_by(member_id=member.id)

        if thank:
            thank.count += 1
            thank.save()
        else:
            thank = Thank.create(member_id=member.id, count=1)

        thank_embed: Embed = Embed(
            title="INFO",
            color=self.bot.default_color,
            description=f"{member.display_name}, you were thanked by **{ctx.author.display_name}**\n"
                        f"Now, your thank count is: **{thank.count}**"
        )

        await member.send(embed=thank_embed)
        await ctx.interaction.response.send_message(f"Successfully thanked **@{member.display_name}**", ephemeral=True)

    @thank_group.command(name='leaderboard', description='Shows top n helpers.')
    @has_permissions(administrator=True)
    async def thank_leaderboard(self, ctx: Context, *, top: int):
        helpers: List[Query] = Thank.query().order_by(Thank.count.desc()).all()
        if not helpers:
            return await ctx.reply('No helpers found.', ephemeral=True)

        top = min(len(helpers), top)
        if top <= 0:
            return await ctx.reply('The top parameter must have value of at least 1.', ephemeral=True)

        leaderboard_embed: Embed = Embed(
            title=f"Helpers Leaderboard Top {top}",
            description='',
            color=self.bot.default_color
        )

        for position in range(top):
            member = helpers[position]
            member_nickname = (await self.bot.fetch_user(member.member_id)).display_name
            leaderboard_embed.description += '{}. **{}**: **{}** with {} thank count.\n' \
                                                .format(position + 1, member_nickname, member.rank, member.count)

        await ctx.reply(embed=leaderboard_embed)

    @thank_group.command(name='rank', description='Shows your current thank rank.')
    async def thank_rank(self, ctx: Context, *, member: Member = None):
        if not member or member.id == ctx.author.id:
            await self.send_author_rank(ctx)
        elif member.id == self.bot.user.id:
            await self.send_bot_rank(ctx)
        else:
            await self.send_member_rank(ctx, member)

    async def send_bot_rank(self, ctx: Context):
        rank_embed = Embed(title="Grace RANK", color=self.bot.default_color)
        rank_embed.description = "Grace has a range of commands that can help you greatly!\n" \
                                 "Rank: **Bot**"

        await ctx.reply(embed=rank_embed, ephemeral=True)

    async def send_author_rank(self, ctx: Context):
        rank_embed = Embed(title="YOUR RANK", color=self.bot.default_color)
        thank = Thank.get_by(member_id=ctx.author.id)

        if not thank:
            rank_embed.description = "You haven't been thanked yet."
        else:
            rank_embed.description = f"Your rank is: **{thank.rank}**\n" \
                                     f"Your thank count is: {thank.count}"

        await ctx.reply(embed=rank_embed, ephemeral=True)

    async def send_member_rank(self, ctx: Context, member: Member):
        rank_embed = Embed(title=f"{member.display_name} RANK", color=self.bot.default_color)
        thank = Thank.get_by(member_id=member.id)

        if not thank:
            rank_embed.description = f"User **@{member.display_name}** hasn't been thanked yet."
        else:
            rank_embed.description = f"User **@{member.display_name}** has rank: **{thank.rank}**"

        await ctx.reply(embed=rank_embed, ephemeral=True)


async def setup(bot: Grace):
    await bot.add_cog(ThankCog(bot))