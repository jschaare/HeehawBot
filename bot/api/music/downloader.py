from __future__ import unicode_literals
import youtube_dl, asyncio, os

ytdl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

class YTDownloader():
    def __init__(self, data):
        self.data = data
        self.title = data.get('title')
        self.url=data.get("url")
        self.thumbnail=data.get('thumbnail')
        self.duration=data.get('duration')

    @classmethod
    async def get_song(self, ytdl : youtube_dl.YoutubeDL, url, loop=None, stream=False):
        loop = loop if not None else asyncio.get_event_loop()
        ytdata = ytdl.extract_info(url, download = not stream)
        song_list = {}
        if 'entries' in ytdata:
            if len(ytdata['entries']) > 1:
                song_list={'queue' : [title['title'] for title in ytdata['entries']]}
                song_list['queue'].pop(0)
            ytdata=ytdata['entries'][0]
        filename = ytdata['url'] if stream else ytdl.prepare_filename(ytdata)
        return ytdata, filename, song_list

async def test():
    ytdl = youtube_dl.YoutubeDL(ytdl_opts)
    dl = await YTDownloader.get_song(ytdl, "https://youtu.be/NdqbI0_0GsM")
    print("finished")
    print(dl[1])
    print(dl[2])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())