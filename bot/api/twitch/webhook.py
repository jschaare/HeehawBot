from discord import Webhook, AsyncWebhookAdapter, Embed
from twitchAPI.twitch import Twitch
from twitchAPI.webhook import TwitchWebHook
from twitchAPI.types import TwitchAuthorizationException
import asyncio, aiohttp

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

    def subscribe_users(self, user_webhook_list):
        if not self.authenticated:
            raise Exception
        #TODO handle exceptions
        user_data = self.twitch.get_users(logins=[user_webhook[0] for user_webhook in user_webhook_list])
        for user in user_data['data']:
            if not any(sub['id'] == user['id'] for sub in self.subscriptions):
                for user_webhook in user_webhook_list:
                    if user['display_name'].lower() == user_webhook[0].lower():
                        wbhk = user_webhook[1]
                        break
                    else:
                        wbhk = None
                if wbhk == None:
                    print(f"Failed to subscribe to {user['display_name']}")
                    return
                ret, uuid = self.hook.subscribe_stream_changed(user['id'], self.callback_stream_changed)
                if ret:
                    print(f"Subscribed to {user['display_name']}")
                    user['uuid'] = uuid
                    user['webhook'] = wbhk
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
        for user in self.subscriptions:
            if user['uuid'] == uuid:
                webhook_url = user['webhook']
                break
            else:
                print("Callback failed")
                return
        if twdata['type'] == 'live':
            emb = self.create_embed(twdata)
            loop = asyncio.get_event_loop()
            loop.create_task(self.post_discord(webhook_url, emb))

    def create_embed(self, twdata):
        return Embed(title=f"{twdata['user_name']}",
                     description=f"{twdata['user_name']} is streaming {twdata['game_name']}! Get in here!",
                     color=6570404,
                     url=f"https://twitch.tv/{twdata['user_name']}") \
                    .set_image(url=twdata['thumbnail_url'].format(width="1280", height="720"))

    async def post_discord(self, webhook_url, discord_embed):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(webhook_url, adapter=AsyncWebhookAdapter(session))
            await webhook.send(embed=discord_embed)
