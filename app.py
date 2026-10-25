import os
import sys
import threading
import asyncio
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from dotenv import load_dotenv

import discord
from discord.ext import tasks

from src import feed_collector
from src import config
from src.discord_sender import send_embeds

# -------------------------------.
# 必要モジュールのセットアップ.
c = config.config()
c.load()

interval_time = c.get_check_interval_minutes()

feed = feed_collector.feed_collector()
feed.load_config(".config/config.json")

# -------------------------------.
# Discord のセットアップ
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    # 起動通知.
    print("===== [Login Discord] =====")
    print("End bot [CTRL + c]")
    loop.start()

@tasks.loop(minutes=interval_time)
async def loop():
    print("===== [Send Message] =====")
    topics = feed.get_topics()
    if len(topics) == 0:
        print("[LOG] Not topics is skip send")
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if not channel == None:
        await send_embeds(channel, topics)
    else:
        print("[ERROR] channel is None, check CHANNEL_ID={}.", format(DISCORD_CHANNEL_ID))

# -------------------------------.
# タスクトレイのセットアップ
discord_loop = None
def run_discord_bot():
    global discord_loop
    discord_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(discord_loop)
    try:
        discord_loop.run_until_complete(client.run(DISCORD_TOKEN))
    except Exception as e:
        print(f"[ERROR] Discord Error{e}")

def create_image():
    image = Image.open("icons/news_tray_icon.png")
    return image

def on_quit(icon, item):
    global discord_loop
    asyncio.run_coroutine_threadsafe(client.close(), discord_loop)
    icon.stop()


def setup_tray():
    global feed
    menu = (
            item("Status: Running", lambda: None, enabled=False),
            item("Update Config", feed.update_config),
            item("Exit", on_quit),
            )
    icon = pystray.Icon("Discord News Bot", create_image(), "Discord News Bot", menu)
    icon.run()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_discord_bot, daemon=True)
    bot_thread.start()

    setup_tray()


