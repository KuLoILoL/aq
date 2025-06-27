import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import random
import json

# sample text HelloWorlds

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is ready: {bot.user}')

# 永続化ファイルの場所を Northflank に合わせる

VALUE_PATH = "/app/data/bot_value.json"

# 読み込み

if os.path.exists(VALUE_PATH):
    with open(VALUE_PATH, "r") as f:
        bot_data = json.load(f)
else:
    bot_data = {"value": 10000}

# 保存する関数（使い回しできる）

def save_data():
    with open(VALUE_PATH, "w") as f:
        json.dump(bot_data, f)

intents = discord.Intents.default()
intents.message_content = True

# 🌞 朝用ビュー（挨拶ボタン）

class MyButtonView(discord.ui.View):
    @discord.ui.button(label="挨拶", style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("# ドカーン💥", ephemeral=True)

    # 🌙 夜用ビュー（おやすみくじボタン）

user_button_click_count = {}

class NightView(discord.ui.View):
    @discord.ui.button(label="おやすみくじ", style=discord.ButtonStyle.success)
    async def lucky_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id

        # ユーザーの押下回数を管理
        if user_id not in user_button_click_count:
            user_button_click_count[user_id] = 0

        # 2回までボタンを押せるように制限
        if user_button_click_count[user_id] >= 3:
            await interaction.response.send_message(f"{interaction.user.mention} はよ寝ろ", ephemeral=True)
            return

        colors = [
            "明日は何もいいことありません",
            "明日はいいことあります",
            "明日のラッキーカラーは赤です",
            "明日のラッキーカラーは青です。",
            "明日のラッキーナンバーは5です。",
            "明日は中吉です。",
            "明日は大吉です。",
            "明日は大凶です。"
        ]
        await interaction.response.send_message(f"{interaction.user.mention} {random.choice(colors)}")
        user_button_click_count[user_id] += 1

# 💬 各コマンドの処理

async def hello_command(ctx):
    await ctx.send("ハロー")

async def button_command(ctx):
    view = MyButtonView()
    await ctx.send("おはようございます！", view=view)

async def oyasumi_command(ctx):
    view = NightView()
    await ctx.send("おやすみなさい。ぐ～", view=view)

async def ishiba_command(ctx):
    embed = discord.Embed(title="💥🔫")
    embed.set_image(url="https://images-ext-1.discordapp.net/external/xxHwpmL3IVQc_lho1AAo3nSLAtBULhzeJjXzqNQnP-Q/https/i.imgur.com/Gx4WaWK.png?format=webp&quality=lossless&width=381&height=375")
    await ctx.send(embed=embed)

# ✅ コマンド登録

command_map = {
"hello": hello_command,
"おはよう": button_command,
"おやすみ": oyasumi_command,
"石破茂暗殺": ishiba_command
}

for name, handler in command_map.items():
    bot.command(name=name)(handler)

# 🤖 自動応答

@bot.event
async def on_message(message):
    # ほかのボットの返信は無視する
    if message.author.bot:
        return

    if "大丈夫？" in message.content:
        rand = random.random()
        if rand < 0.9:
            response = "俺なら大丈夫だぜ"
        else:
            response = "大丈夫なわけねえだろ"
        await message.channel.send(response)

    await bot.process_commands(message)

@bot.command()
async def ざつよう(ctx):
    bot_data["value"] -= 1
    save_data()
    await ctx.send(f"サンキュ！あと{bot_data['value']}本残ってるぞ！")

PLAYER_DATA_FILE = 'player_data.json'

# －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
# ダンジョンの部屋画像（仮のURL）
ROOM_IMAGES = {
    "start": "https://i.imgur.com/Gx4WaWK.png",
    "north": "https://i.imgur.com/8Km9tLL.jpg",
    "east": "https://i.imgur.com/O3ZC3GM.jpg",
    "west": "https://i.imgur.com/4M34hi2.png"
}

# ボタン付きビュー
class DungeonView(discord.ui.View):
    def __init__(self, location="start"):
        super().__init__()
        self.location = location

    @discord.ui.button(label="北へ進む", style=discord.ButtonStyle.primary)
    async def go_north(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=create_dungeon_embed("north"), view=DungeonView("north"))

    @discord.ui.button(label="東へ進む", style=discord.ButtonStyle.success)
    async def go_east(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=create_dungeon_embed("east"), view=DungeonView("east"))

    @discord.ui.button(label="西へ進む", style=discord.ButtonStyle.danger)
    async def go_west(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=create_dungeon_embed("west"), view=DungeonView("west"))

# Embed生成関数
def create_dungeon_embed(location):
    embed = discord.Embed(
        title=f"{location.title()} の部屋",
        description=f"{location} の方角に進みました。",
        color=discord.Color.dark_gold()
    )
    embed.set_image(url=ROOM_IMAGES.get(location, ROOM_IMAGES["start"]))
    return embed

# コマンド実行で開始
@bot.command()
async def dungeon(ctx):
    embed = create_dungeon_embed("start")
    view = DungeonView()
    await ctx.send(embed=embed, view=view)

# ----------------------------------------------------------------------------------------------------------------------------
user_states = {}

# イベントの定義（画像付き）
EVENTS = [
    {
        "type": "enemy",
        "desc": "敵が現れた！HPが10減った。",
        "hp_change": -10,
        "image": "https://i.imgur.com/JS6k5tJ.png"  # 敵画像
    },
    {
        "type": "treasure",
        "desc": "宝箱を見つけた！HPが10回復した。",
        "hp_change": +10,
        "image": "https://i.imgur.com/8Km9tLL.jpg"  # 宝箱画像
    },
    {
        "type": "trap",
        "desc": "罠にかかった！HPが5減った。",
        "hp_change": -5,
        "image": "https://i.imgur.com/O3ZC3GM.jpg"  # 罠画像
    },
    {
        "type": "nothing",
        "desc": "何も起こらなかった…。",
        "hp_change": 0,
        "image": "https://i.imgur.com/4M34hi2.png"  # 空部屋画像
    }
]

# View（進むボタン）
class DungeonEventView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="➡ 進む", style=discord.ButtonStyle.primary)
    async def proceed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("これはあなたのゲームではありません。", ephemeral=True)
            return

        state = user_states[self.user_id]
        state["stage"] += 1
        event = random.choice(EVENTS)
        state["hp"] += event["hp_change"]

        embed = discord.Embed(
            title=f"ステージ {state['stage']}",
            description=event["desc"],
            color=discord.Color.red() if event["hp_change"] < 0 else discord.Color.green()
        )
        embed.set_image(url=event["image"])
        embed.add_field(name="HP", value=str(state["hp"]))

        if state["hp"] <= 0:
            embed.title = "💀 ゲームオーバー！"
            embed.description += "\nHPがなくなりました…"
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            await interaction.response.edit_message(embed=embed, view=DungeonEventView(self.user_id))

# コマンドでゲーム開始
@bot.command()
async def start(ctx):
    user_states[ctx.author.id] = {"hp": 100, "stage": 0}
    embed = discord.Embed(
        title="⚔️ ダンジョンに突入！",
        description="進むボタンでダンジョンを進もう。",
        color=discord.Color.blue()
    )
    embed.set_image(url="https://media.discordapp.net/attachments/846657450115727403/1388050166912778280/1751006740721.png?ex=685f91f4&is=685e4074&hm=eb25e582d5d9b64d7c4ac11918dde4c66bc4b1f65eaeb8900e50e3c205c35bd4&=&format=webp&quality=lossless&width=1054&height=1059")  # 初期部屋画像
    embed.add_field(name="HP", value="100")
    await ctx.send(embed=embed, view=DungeonEventView(ctx.author.id))
#　－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－

# 🔁 実行

bot.run(os.environ['DISCORD_TOKEN'])

