from discord.ext import commands
from bot.bot import Bot

from discord import Webhook, AsyncWebhookAdapter, Embed
from twitchAPI.twitch import Twitch
from twitchAPI.webhook import TwitchWebHook
from twitchAPI.types import TwitchAuthorizationException
import asyncio

class DiscordTwitchWebhook():
    def __init__(self, twitch_appid, twitch_secret, discord_webhook, callback_url):
        self.twitch = Twitch(twitch_appid, twitch_secret)
        self.discord_webhook = discord_webhook
        self.callback_url = callback_url
        self.hook = TwitchWebHook(callback_url, twitch_appid, 8080)
        self.authenticated = False
        self.subscriptions = []

    def authenticate(self):
        self.authenticated = False
        try:
            self.twitch.authenticate_app([])
            self.hook.authenticate(self.twitch)
        except TwitchAuthorizationException:
            print("Twitch authentication failed")
        except RuntimeError:
            print("Webhook must be https")
        else:
            self.authenticated = True
        return self.authenticated

    def subscribe_users(self, user_list):
        if not self.authenticated:
            raise Exception
        #TODO handle exceptions
        user_data = self.twitch.get_users(logins=user_list)
        for user in user_data['data']:
            if not any(sub['id'] == user['id'] for sub in self.subscriptions):
                ret, uuid = self.hook.subscribe_stream_changed(user['id'], self.callback_stream_changed)
                if ret:
                    print(f"Subscribed to {user['display_name']}")
                    user['uuid'] = uuid
                    self.subscriptions.append(user)
                else:
                    print(f"Failed to subscribe to {user['display_name']}")

    def unsubscribe_users(self, user_list):
        #TODO
        return

    def start(self):
        self.hook.start()

    def stop(self):
        self.hook.unsubscribe_all(self.twitch)
        self.hook.stop()

    def callback_stream_changed(self, uuid, twdata):
        print('Callback for UUID ' + str(uuid))
        print(twdata)
        if twdata['type'] == 'live':
            emb = self.create_embed(twdata)
            loop = asyncio.get_event_loop()
            loop.create_task(self.post_discord(self.discord_webhook, emb))

    def create_embed(self, twdata):
        return Embed(title=f"{twdata['user_name']}",
                     description=f"{twdata['user_name']} is streaming {twdata['game_name']}! Get in here!",
                     color=6570404,
                     url=f"https://twitch.tv/{twdata['user_name']}") \
                    .set_image(url=twdata['thumbnail_url'].format(width="1280", height="720"))

    async def post_discord(self, discord_embed):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(webhook_url, adapter=AsyncWebhookAdapter(session))
            await webhook.send(username=self.discord_username, embed=discord_embed)

class TwitchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='twitch', invoke_without_command=True)
    async def _twitch(self, ctx):
        #TODO: print usage stuff
        await ctx.send("Nice.")

    @_twitch.command()
    async def whoami(self, ctx):
        response = f"Hey there, {ctx.author.display_name}!"
        await ctx.send(response)

def setup(bot):
    bot.add_cog(TwitchCog(bot))