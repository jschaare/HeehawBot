import datetime
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context


class Poll(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @property
    def reactions(self):
        return {
            1: "1️⃣",
            2: "2️⃣",
            3: "3️⃣",
            4: "4️⃣",
            5: "5️⃣",
            6: "6️⃣",
            7: "7️⃣",
            8: "8️⃣",
            9: "9️⃣",
            10: "🔟",
        }

    @commands.command()
    async def poll(self, ctx: Context, info: str, *options):
        await ctx.message.delete()

        if len(options) < 2:
            return await ctx.send(
                f"Need at least two choices to make a poll, {ctx.author.display_name}"
            )
        elif len(options) > 10:
            return await ctx.send(
                f"Way too many choices. Try less than 10, {ctx.author.display_name}"
            )

        desc_str = f"**{info}**\n\n" + "\n\n".join(
            f"{self.reactions[i]}: {option}"
            for i, option in enumerate(options, start=1)
        )

        embed = Embed(description=desc_str, timestamp=datetime.datetime.utcnow())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        pollmsg = await ctx.send(embed=embed)
        for i in range(len(options)):
            await pollmsg.add_reaction(self.reactions[i + 1])


def setup(bot):
    bot.add_cog(Poll(bot))
