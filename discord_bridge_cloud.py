import discord
import requests
import os
import logging

logging.basicConfig(
          level=logging.INFO,
          format="%(asctime)s [%(levelname)s] %(message)s"
)

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
N8N_WEBHOOK_URL = os.environ["N8N_WEBHOOK_URL"]
ALLOWED_CHANNEL_ID = os.environ.get("ALLOWED_CHANNEL_ID", "")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
          logging.info(f"Bot online: {client.user}")
          logging.info(f"n8n webhook: {N8N_WEBHOOK_URL}")


@client.event
async def on_message(message):
          if message.author == client.user:
                        return
                    if ALLOWED_CHANNEL_ID and str(message.channel.id) != ALLOWED_CHANNEL_ID:
                                  return
                              content = message.content.strip()
    if not content.startswith("/"):
                  return
              logging.info(f"Command: {content} from {message.author.name}")
    payload = {
                  "content": content,
                  "userId": str(message.author.id),
                  "username": message.author.name,
                  "channelId": str(message.channel.id),
                  "timestamp": message.created_at.isoformat()
    }
    try:
                  resp = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=8)
                  logging.info(f"n8n response: {resp.status_code}")
                  await message.add_reaction("⚙️")
except Exception as e:
        logging.error(f"Forward failed: {e}")
        await message.add_reaction("❌")


client.run(BOT_TOKEN)
