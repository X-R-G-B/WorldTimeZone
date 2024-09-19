import asyncio
import os

import hikari
import lightbulb
from hikari import Intents
from lightbulb.ext import tasks

if os.name != "nt":
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

INTENTS = Intents.GUILD_MEMBERS | Intents.GUILDS

bot = lightbulb.BotApp(
    os.environ["BOT_TOKEN"],
    intents=INTENTS,
    banner=None,
)
tasks.load(bot)


@bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    print("WorldTimeZone Ready!!")


bot.load_extensions("extensions.ping")
bot.load_extensions("extensions.world_clock")


if __name__ == "__main__":
    bot.run()
