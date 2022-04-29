from discord import Member
from discord.ext.commands import Cog, command, has_permissions
from bot.helpers.log_helper import log


class ModerationCog(Cog, name="moderation", description="Collection of administrative use commands."):
    def __init__(self, bot):
        self.bot = bot

    @command(name='kick', help="Allows a staff member to kick a user based on their behaviour.")
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, reason="No reason given"):
        log_event = log(self.bot, "KICK", f"{member.mention} has been kicked.")
        log_event.add_field("Issuer: ", ctx.author)
        log_event.add_field("Reason: ", reason)

        await ctx.guild.kick(user=member)
        await log_event

    @command(name='ban', help="Allows a staff member to ban a user based on their behaviour.")
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: Member, reason="No reason"):
        log_event = log(self.bot, "BAN", f"{member.mention} has been banned.")
        log_event.add_field("Issuer: ", ctx.author.mention)
        log_event.add_field("Reason: ", reason)

        await ctx.guild.ban(user=member), log_event

    @command(name='unban', help="Allows a staff member to unban a user.")
    @has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)

        await ctx.guild.unban(user)
        await log(self.bot, "UNBAN", f"{user.name} has been unbanned.")

    @command(name='purge', help="Deletes n amount of messages.")
    @has_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int):
        await ctx.message.delete()
        await ctx.channel.purge(limit=limit)
        await log(self.bot, "PURGE", f"{limit} message(s) purged by {ctx.author.mention} in {ctx.channel.mention}")


def setup(bot):
    bot.add_cog(ModerationCog(bot))
