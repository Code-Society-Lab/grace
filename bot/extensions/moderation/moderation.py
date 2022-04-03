from discord import Member
from datetime import datetime
from discord.ext.commands import Cog, command, has_permissions
from discord import Embed


class ModerationCog(Cog, name="moderation", description="Collection of administrative use commands."):
    def __init__(self, bot):
        self.bot = bot

    @command(name='kick', help="Allows a staff member to kick a user based on their behaviour.")
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, reason="No reason"):
        channel = self.bot.get_channel(self.bot.config.get_channel(name="moderation_logs").channel_id)
        embed = Embed(
            title="Grace Moderation - KICK",
            description=f"{member.mention} has been kicked.",
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Reason: ", value=str(reason), inline=False)

        await channel.reply(embed=embed)
        await ctx.guild.kick(user=member)

    @command(name='ban', help="Allows a staff member to ban a user based on their behaviour.")
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: Member, reason="No reason"):
        channel = self.bot.get_channel(self.bot.config.get_channel(name="moderation_logs").channel_id)
        embed = Embed(
            title="Grace Moderation - BAN",
            description=f"{member.mention} has been banned.",
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Reason: ", value=str(reason), inline=False)

        await channel.send(embed=embed)
        await ctx.guild.ban(user=member)

    @command(name='unban', help="Allows a staff member to unban a user.")
    @has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)
        channel = self.bot.get_channel(self.bot.config.get_channel(name="moderation_logs").channel_id)
        embed = Embed(
            title="Grace Moderation - UNBAN",
            description=f"{user.name} has been unbanned.",
            timestamp=datetime.utcnow()
        )

        await ctx.guild.unban(user)
        await channel.send(embed=embed)

    @command(name='purge', help="Deletes n amount of messages.")
    @has_permissions(manage_messages=True)
    async def purge(self, ctx, limit: int):
        channel = self.bot.get_channel(self.bot.config.get_channel(name="moderation_logs").channel_id)
        embed = Embed(
            title="Grace Moderation - PURGE",
            description=f"Chat cleared by {ctx.author.mention}",
            timestamp=datetime.utcnow()
        )

        await ctx.channel.purge(limit=limit)
        await channel.send(embed=embed)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(ModerationCog(bot))
