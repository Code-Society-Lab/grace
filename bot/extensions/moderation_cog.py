from discord import Member
from discord.ext.commands import Cog, command, has_permissions
from bot.helpers.log_helper import danger


class ModerationCog(Cog, name="moderation", description="Collection of administrative commands."):
    def __init__(self, bot):
        self.bot = bot

    def get_moderation_channel(self):
        return self.bot.get_channel_by_name("moderation_logs")

    @command(name='kick', help="Allows a staff member to kick a user based on their behaviour.")
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, reason="No reason given"):
        log = danger("KICK", f"{member.mention} has been kicked.")
        log.add_field("Issuer: ", ctx.author)
        log.add_field("Reason: ", reason)

        await ctx.guild.kick(user=member)
        await log.send(self.get_moderation_channel())

    @command(name='ban', help="Allows a staff member to ban a user based on their behaviour.")
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: Member, reason="No reason"):
        log = danger("BAN", f"{member.mention} has been banned.")
        log.add_field("Issuer: ", ctx.author.mention)
        log.add_field("Reason: ", reason)

        await ctx.guild.ban(user=member)
        await log.send(self.get_moderation_channel())

    @command(name='unban', help="Allows a staff member to unban a user.")
    @has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        log = danger("UNBAN", f"{user.name} has been unbanned.")

        await ctx.guild.unban(user)
        await log.send(self.get_moderation_channel())

    @command(name='purge', help="Deletes n amount of messages.")
    @has_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int, member: Member = None):
        log = danger("PURGE", f"{limit} message(s) purged by {ctx.author.mention} in {ctx.channel.mention}")

        if member:
            async for message in ctx.channel.history(limit=limit):
                if message.author == member:
                    await message.delete()
        else:
            await ctx.channel.purge(limit=limit)
        await log.send(self.get_moderation_channel())


def setup(bot):
    bot.add_cog(ModerationCog(bot))
