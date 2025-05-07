import discord
from discord.ext import commands
import os
import random
import json

intents = discord.Intents.default()
intents.message\_content = True

bot = commands.Bot(command\_prefix='/', intents=intents)

@bot.event
async def on\_ready():
print(f'✅ Bot is ready: {bot.user}')

# 🔹 ボタン付きの処理用ビュー

class MyButtonView(discord.ui.View):
@discord.ui.button(label="挨拶", style=discord.ButtonStyle.primary)
async def button\_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
await interaction.response.send\_message("# ドカーン💥", ephemeral=True)

# 🔹 コマンド関数

async def hello\_command(ctx):
await ctx.send("ハロー")

async def button\_command(ctx):
view = MyButtonView()
await ctx.send("おはようございます！", view=view)

# 🔹 コマンドマップ

command\_map = {
"hello": hello\_command,
"おはよう": button\_command
}

for name, handler in command\_map.items():
bot.command(name=name)(handler)

@bot.event
async def on\_message(message):
if message.author.bot:
return

```
if "大丈夫？" in message.content:
    rand = random.random()
    if rand < 0.9:
        response = "俺なら大丈夫だぜ"
    else:
        response = "大丈夫なわけねえだろ"
    await message.channel.send(response)

await bot.process_commands(message)
```

DATA\_FILE = "player\_data.json"
player\_data = {}

def load\_data():
global player\_data
if os.path.exists(DATA\_FILE):
with open(DATA\_FILE, "r", encoding="utf-8") as f:
player\_data = json.load(f)

# ここから戦闘ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー



bot.run(os.environ\['DISCORD\_TOKEN'])
