from discord import Embed


class QueueEmbed:
    def __init__(self, queue):
        self.queue = queue

    def embed(self):
        msg = "Songs:\n"
        if len(self.queue) > 0:
            for i, song in enumerate(self.queue):
                url = song.get("url")
                title = song.get("title")
                if len(title) > 50:
                    title = title[:47] + "..."
                msg += f"{i+1}. [{title}]({url})\n"
        else:
            msg += "Nothing in queue!"
        return Embed(title="Coming Up", description=msg)
