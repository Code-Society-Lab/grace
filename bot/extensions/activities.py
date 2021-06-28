from discord.ext.commands import Cog, command
import os
import requests
import json
import discord

class activities(Cog, name="Activities",description="Commands regarding Discord Activities in VC" ):
    def __init__(self, bot):
        self.bot = bot

    @command(name='youtube', help='Will enable Youtube Together in VC', usage='youtube')
    async def youtube(self, ctx):
        try:
            channel = ctx.author.voice.channel
            url = f"https://discord.com/api/v9/channels/{channel.id}/invites"
            p = {
                'max_age': 86400,
                'max_uses': 0,
                'target_application_id': '755600276941176913', 
                'target_type': 2,
                'temporary': False,
                        'validate': None
            }
            headers={'content-type': 'application/json','Authorization': f"Bot {os.getenv('DISCORD_TOKEN')}"}
            r=requests.post(url, data=json.dumps(p), headers=headers)
            
            embed = discord.Embed(title="Youtube Together",colour=discord.Colour(0xFF0000))
            embed.description = f"[Click Here to Join Youtube Together in the VC](https://discord.com/invite/{r.json()['code']})"
            await ctx.send(embed=embed)
        except AttributeError:
             await ctx.reply("You Are not in a VC")
        except Exception as e:
             await ctx.send("There is some error in starting Youtube Togther or I don't have permission to create invite in that channel")


def setup(bot):
    bot.add_cog(activities(bot))
