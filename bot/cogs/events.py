from discord.ext import commands
from discord import Embed
from bot.bot import Bot
from datetime import datetime
import asyncio

class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def event(self, ctx, event_name, event_time, *, event_str):
        #~event skrrrt 2020y10m22d19h55m this is a test message
        e_check = "✅"
        e_wc = "♿"
        del_delay = 10
        
        now = datetime.today()
        tz_str = now.astimezone().tzname()
        event_time = datetime.strptime(eventtime, "%Yy%mm%dd%Hh%Mm")
        if (event_time < now):
            await ctx.send("Error: time is in the past")
            return
        delta = event_time - now
        secs = delta.seconds

        post = format_eventpost(ctx.message.author, event_name, event_time, event_str)

        msg = await ctx.send(embed=post)
        await msg.add_reaction(e_check)
        await msg.add_reaction(e_wc)

        await asyncio.sleep(del_delay)
        await ctx.message.delete()
        await asyncio.sleep(secs-del_delay)

        msg = await ctx.channel.fetch_message(msg.id)
        for react in msg.reactions:
            if react.emoji == e_check:
                users = await react.users().flatten()
                for u in users:
                    if not u.bot:
                        await u.send(embed=post)

    def format_eventpost(self, author, eventname, eventtime, eventstr):
        if author.nick:
            post_author = f"{author.nick} ({author})"
        else:
            post_author = f"{author}"

        post = Embed(colour=0x00FF00, title=eventname) \
            .set_footer(text=f"message {post_author} for details")
        post.description = \
            f"***Time***\n{eventtime} {tz_str}\n" \
            f"***Description***\n{eventstr}\n"
        return post

def setup(bot):
    bot.add_cog(Events(bot))