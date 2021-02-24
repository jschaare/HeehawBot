from discord.ext import commands
from bot.bot import Bot
from bot.utils import config
from bot.api.twitch.webhook import DiscordTwitchWebhook, DiscordTwitchCallback
from pyngrok import ngrok
import asyncio

class TwitchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webhook_name = "Twitch Notification"

        cfg = config.get_config()
        callback_url = ngrok.connect(cfg['ngrok_port']).public_url

        self.callback_url = callback_url.replace('http', 'https')
        print(self.callback_url)
        print(cfg['twitch_appid'])
        self.dtw = DiscordTwitchWebhook(cfg['twitch_appid'], cfg['twitch_secret'], self.callback_url)
        self._startup()

    def _startup(self):
        self.dtw.authenticate()
        self.dtw.start()

    def _shutdown(self):
        self.dtw.stop()
        ngrok.disconnect(self.callback_url)

    @commands.group(name='twitch', invoke_without_command=True)
    async def _twitch(self, ctx):
        #TODO: print usage stuff
        await ctx.send("Nice.")

    @_twitch.command()
    async def subscribe(self, ctx, username : str):
        self.dtw.subscribe_users([(username, ctx.message.channel, self.post, asyncio.get_event_loop())])
        await ctx.send(f"Subscribed to user: {username}")

    @_twitch.command()
    async def sub(self, ctx, username : str):
        user = DiscordTwitchCallback(username, ctx.message.channel, self.post, asyncio.get_event_loop())
        self.dtw.subscribe_user(user)
        await ctx.send(f"Subscribed to user: {username}")

    async def post(self, chan, emb):
        await chan.send(embed=emb)


def setup(bot):
    bot.add_cog(TwitchCog(bot))