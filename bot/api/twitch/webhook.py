from twitchAPI.twitch import Twitch
from twitchAPI.webhook import TwitchWebHook
from twitchAPI.types import TwitchAuthorizationException
from discord import Embed
import asyncio, aiohttp

class DiscordTwitchCallback():
    #TODO pythonic getter/setters
    def __init__(self, username, channel, callback, loop):
        self.username = username
        self.channel = channel
        self.callback = callback
        self.loop = loop
        self.uuid = None
        self.data = {}

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.username == other.username
        else:
            return False

    def run_callback(self, discord_embed):
        asyncio.run_coroutine_threadsafe(self.callback(self.channel, discord_embed), self.loop)

class DiscordTwitchWebhook():
    def __init__(self, twitch_appid, twitch_secret, callback_url):
        self.discord_username = "Twitch Notification"
        self.twitch = Twitch(twitch_appid, twitch_secret)
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

    def subscribe_user(self, user : DiscordTwitchCallback):
        if not self.authenticated:
            raise Exception
        #TODO handle more exceptions
        
        user_data = self.twitch.get_users(logins=[user.username])
        user.data = user_data['data'][0]
        user.id = user.data['id']
        if user not in self.subscriptions:
            ret, user.uuid = self.hook.subscribe_stream_changed(user.id, self.callback_stream_changed)
            if ret:
                self.subscriptions.append(user)
            else:
                print(f"Failed to subscribe to {user.username}")

    def unsubscribe_user(self, user : DiscordTwitchCallback):
        #TODO
        return

    def start(self):
        self.hook.start()

    def stop(self):
        self.hook.unsubscribe_all(self.twitch)
        self.hook.stop()

    def callback_stream_changed(self, uuid, twdata):
        print('Callback for UUID ' + str(uuid), twdata)
        user = next((user for user in self.subscriptions if user.uuid == uuid), None)
        if user == None:
            print("Callback failed")
            return
        if twdata['type'] == 'live':
            emb = self.create_embed(twdata)
            user.run_callback(emb)

    def create_embed(self, twdata):
        return Embed(title=f"{twdata['user_name']}",
                     description=f"{twdata['user_name']} is streaming {twdata['game_name']}! Get in here!",
                     color=6570404,
                     url=f"https://twitch.tv/{twdata['user_name']}") \
                    .set_image(url=twdata['thumbnail_url'].format(width="1280", height="720"))
