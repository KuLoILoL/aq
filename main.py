import discord
from discord.ext import commands
import os

# Discordのインテント設定（Botがイベントを受け取るための許可）
intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容の取得を許可

# Bot本体の作成（接頭辞 ! でコマンドを認識）
bot = commands.Bot(command_prefix='!', intents=intents)

# 起動時に表示
@bot.event
async def on_ready():
    print(f'✅ Bot is ready: {bot.user}')

# シンプルなコマンド
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Discordトークンを環境変数から取得
bot.run(os.environ['DISCORD_TOKEN'])
