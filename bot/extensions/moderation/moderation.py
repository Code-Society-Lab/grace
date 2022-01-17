from discord import Member
import datetime
from json import loads
from turtle import title
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands import Cog, command, cooldown, has_permissions
from discord import Embed


class ModerationCog(Cog, name="moderation", description="Collection of administrative use commands."):
    def __init__(self, bot):
        self.bot = bot

    @command(name='kick', help="Allows a staff member to kick a user based on their behaviour.")
    @cooldown(1, 5, BucketType.user)
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, reason="No reason"):
            guild = ctx.guild
            embed = Embed(title="Grace Moderation - KICK", description=f"{member.mention} has been kicked.", timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Reason: ", value=str(reason), inline=False)
            await ctx.reply(embed=embed)
            await guild.kick(user=member)

    @command(name='ban', help="Allows a staff member to ban a user based on their behaviour.")
    @cooldown(1, 5, BucketType.user)
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: Member, reason="No reason"):
            guild = ctx.guild
            embed = Embed(title="Grace Moderation - BAN", description=f"{member.mention} has been banned.", timestamp=datetime.datetime.utcnow())
            embed.add_field(name="Reason: ", value=str(reason), inline=False)
            await ctx.reply(embed=embed)
            await guild.ban(user=member)

    @command(name='unban', help="Allows a staff member to unban a user.")
    @has_permissions(ban_members=True)
    async def unban(self, ctx, id: int):
        user = await self.bot.fetch_user(id)
        await ctx.guild.unban(user)
        embed = Embed(title="Grace Moderation - UNBAN", description=f"{user.name} has been unbanned.", timestamp=datetime.datetime.utcnow())
        await ctx.reply(embed=embed)

    @command(name='purge', help="Deletes n amount of messages.")
    @has_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int):
        await ctx.channel.purge(limit=limit)
        embed = Embed(title="Grace Moderation - PURGE", description=f"Chat cleared by {ctx.author.mention}")
        await ctx.send(embed=embed)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(ModerationCog(bot))
