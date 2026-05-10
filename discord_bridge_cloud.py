"""
Discord → n8n 橋接腳本（雲端版）
部署於 Railway，所有設定透過環境變數注入，永不需要改 URL。
"""

import discord
import requests
import os
import logging
from datetime import datetime

logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s [%(levelname)s] %(message)s"
)

# 從環境變數讀取（Railway 會自動注入）
BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
N8N_WEBHOOK_URL = os.environ["N8N_WEBHOOK_URL"]  # https://xxx.up.railway.app/webhook/discord-command

# 選填：只監聽特定頻道（設為空字串則監聽全部）
ALLOWED_CHANNEL_ID = os.environ.get("ALLOWED_CHANNEL_ID", "")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
      logging.info(f"✅ Discord Bot 上線：{client.user}")
      logging.info(f"📡 n8n Webhook：{N8N_WEBHOOK_URL}")


@client.event
async def on_message(message):
      if message.author == client.user:
                return

      # 頻道過濾
      if ALLOWED_CHANNEL_ID and str(message.channel.id) != ALLOWED_CHANNEL_ID:
                return

      content = message.content.strip()

    if not content.startswith("/"):
              return

    logging.info(f"指令: {content} | 來自: {message.author.name}")

    payload = {
              "content": content,
              "userId": str(message.author.id),
              "username": message.author.name,
              "channelId": str(message.channel.id),
              "timestamp": message.created_at.isoformat()
    }

    try:
              resp = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=8)
              logging.info(f"n8n 回應：{resp.status_code}")
              await message.add_reaction("⚙️")
except Exception as e:
          logging.error(f"轉發失敗：{e}")
          await message.add_reaction("❌")


client.run(BOT_TOKEN)
