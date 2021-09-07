from discord import Embed
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Context
import requests


class Mtg(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.group(name="mtg", invoke_without_command=True)
    async def _mtg(self, ctx: Context):
        await ctx.send("mtg: No subcommand found...")

    @_mtg.command()
    async def card(self, ctx: Context, *search_text: str):
        search_text = " ".join(search_text)
        data = (
            requests.get(f"https://api.scryfall.com/cards/search?q={search_text}")
            .json()
            .get("data")
        )
        embed = self._card_embed(data)
        await ctx.send(embed=embed)

    def _card_embed(self, data: dict) -> Embed:
        if not data:
            embed = Embed(colour=0xFF0000, title="MTG Card Lookup")
            embed.add_field(
                name="***404***",
                value=f"No cards found.",
            )
        else:
            embed = Embed(colour=0x00FF00, title="MTG Card Lookup")
            try:
                card_names, set_names, legalities = list(
                    zip(
                        *[
                            [
                                card.get("name"),
                                card.get("set_name"),
                                ":no_entry:"
                                if "not" in card.get("legalities", {}).get("standard")
                                else ":white_check_mark:",
                            ]
                            for card in data
                        ]
                    )
                )
                embed.add_field(name="***Card Name***", value="\n".join(card_names))
                embed.add_field(name="***Set Name***", value="\n".join(set_names))
                embed.add_field(
                    name="***Standard Legal***", value="\n".join(legalities)
                )
                if len(data) == 1:
                    [card] = data
                    # Handle double-faced cards with thumbnail for now
                    if card.get("card_faces"):
                        embed.set_image(
                            url=card.get("card_faces")[0]
                            .get("image_uris", {})
                            .get("large")
                        )
                        embed.set_thumbnail(
                            url=card.get("card_faces")[1]
                            .get("image_uris", {})
                            .get("large")
                        )
                    else:
                        embed.set_image(url=card.get("image_uris", {}).get("large"))
            except Exception as e:
                embed.clear_fields()
                embed.add_field(name="***Error***", value=repr(e))
        return embed


def setup(bot):
    bot.add_cog(Mtg(bot))
