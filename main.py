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
    load_user_states()
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

# user_states管理（追加分）
USER_PATH = "user_states.json"
user_states = {}

def save_user_states():
    with open(USER_PATH, "w", encoding="utf-8") as f:
        json.dump(user_states, f, ensure_ascii=False, indent=2)

def load_user_states():
    global user_states
    if os.path.exists(USER_PATH):
        with open(USER_PATH, "r", encoding="utf-8") as f:
            user_states.update(json.load(f))

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

async def takuti_command(ctx):
    embed = discord.Embed(title="💥🔫")
    embed.set_image(url="")
    await ctx.send(embed=embed)
# ✅ コマンド登録

command_map = {
"hello": hello_command,
"おはよう": button_command,
"おやすみ": oyasumi_command,
"石破茂暗殺": ishiba_command,
"たくっち死亡": takuti_command
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
import discord
from discord.ext import commands
import random
import json
import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# --- データ保存パスと初期化 ---
DATA_PATH = "user_data.json"
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r") as f:
        user_states = json.load(f)
else:
    user_states = {}

def save_user_states():
    with open(DATA_PATH, "w") as f:
        json.dump(user_states, f, indent=2)

# --- イベント・宝箱定義（拡張） ---
EVENTS = [
    {"type": "monster", "desc": "モンスターに遭遇した！HP -10", "hp_change": -10, "image": "https://i.imgur.com/yX1ZC2B.png"},
    {"type": "treasure", "desc": "宝箱を見つけた！", "image": "https://i.imgur.com/Nz0x65L.png"},
]

TREASURES = [
    {"name": "回復ポーション", "desc": "回復ポーションを手に入れた！", "item": "回復ポーション"},
    {"name": "謎の巻物", "desc": "よく分からない巻物だ…", "item": "謎の巻物"},
    {"name": "癒しの果実", "desc": "その場でHPが5回復！", "hp_change": 5}
]

# --- アイテム使用コマンド（いつでも使用可能） ---
@bot.command()
async def つかう(ctx, item_name: str):
    user_id = ctx.author.id
    state = user_states.get(str(user_id))
    if not state:
        await ctx.send("ゲームを開始してください（!アビス）")
        return

    if item_name not in state.get("items", []):
        await ctx.send(f"{item_name} を持っていません。")
        return

    if item_name == "回復ポーション":
        state["items"].remove(item_name)
        state["hp"] += 20
        save_user_states()
        await ctx.send(f"🧪 {item_name} を使用し、HPが20回復しました。 現在のHP: {state['hp']}")
    else:
        await ctx.send(f"{item_name} は今は使用できません。")

# --- 宝箱イベントビュー ---
class TreasureChoiceView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.treasure = random.choice(TREASURES)

    @discord.ui.button(label="開ける", style=discord.ButtonStyle.success)
    async def open_box(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("あなたのイベントではありません。", ephemeral=True)
            return

        state = user_states[str(self.user_id)]

        if "item" in self.treasure:
            state["items"].append(self.treasure["item"])
        if "hp_change" in self.treasure:
            state["hp"] += self.treasure["hp_change"]

        save_user_states()

        embed = discord.Embed(
            title=f"{self.treasure['name']} を見つけた！",
            description=self.treasure.get("desc", "アイテムを手に入れた！ ボス戦で使えるよ。"),
            color=discord.Color.green()
        )
        embed.set_image(url="https://i.imgur.com/8Km9tLL.jpg")
        embed.add_field(name="HP", value=str(state["hp"]))
        embed.add_field(name="所持アイテム", value=", ".join(state["items"]) if state["items"] else "なし")

        await interaction.response.edit_message(embed=embed, view=DungeonEventView(self.user_id))
# --- ボス戦ビュー ---
class BossBattleView(discord.ui.View):
    def __init__(self, user_id, boss_hp=50):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.boss_hp = boss_hp

    @discord.ui.button(label="⚔ 戦う", style=discord.ButtonStyle.danger)
    async def fight(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("あなたの戦闘ではありません。", ephemeral=True)
            return

        state = user_states[self.user_id]
        damage = random.randint(5, 15)
        self.boss_hp -= damage
        boss_attack = random.randint(5, 10)
        state["hp"] -= boss_attack

        embed = discord.Embed(title="🧠 ボスバトル！", color=discord.Color.dark_red())
        embed.add_field(name="あなたのHP", value=str(state["hp"]))
        embed.add_field(name="ボスのHP", value=str(max(0, self.boss_hp)))
        embed.description = f"あなたはボスに {damage} ダメージを与えた！\nボスから {boss_attack} ダメージを受けた！"

        if state["hp"] <= 0:
            embed.title = "💀 ゲームオーバー！"
            await interaction.response.edit_message(embed=embed, view=None)
            save_user_states()
            return
        elif self.boss_hp <= 0:
            embed.title = "🎉 ボスを倒した！"
            await interaction.response.edit_message(embed=embed, view=DungeonEventView(self.user_id))
            save_user_states()
            return

        await interaction.response.edit_message(embed=embed, view=self)

# --- ダンジョン探索ビュー ---
class DungeonEventView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="➡ 進む", style=discord.ButtonStyle.primary)
    async def proceed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("これはあなたのゲームではありません。", ephemeral=True)
            return

        state = user_states[str(self.user_id)]

        event = random.choice(EVENTS)
        if event["type"] == "monster" and "謎の巻物" in state.get("items", []):
            state["items"].remove("謎の巻物")
            embed = discord.Embed(title=f"ステージ {state['stage']+1}", description="謎の巻物が光り、敵を回避した！", color=discord.Color.teal())
            embed.set_image(url="https://i.imgur.com/4M34hi2.png")
            state["stage"] += 1
            state["max_stage"] = max(state["max_stage"], state["stage"])
            save_user_states()
            await interaction.response.edit_message(embed=embed, view=DungeonEventView(self.user_id))
            return

        state["stage"] += 1
        state["max_stage"] = max(state["max_stage"], state["stage"])
        save_user_states()

        if state["stage"] % 10 == 0:
            embed = discord.Embed(title="👹 ボス出現！", description="強大なボスが前に立ちはだかる！", color=discord.Color.red())
            embed.set_image(url="https://i.imgur.com/6YQO6mT.jpg")
            await interaction.response.edit_message(embed=embed, view=BossBattleView(self.user_id))
            return

        embed = discord.Embed(title=f"ステージ {state['stage']}", description=event["desc"], color=discord.Color.gold())
        embed.set_image(url=event["image"])

        if event["type"] == "treasure":
            await interaction.response.edit_message(embed=embed, view=TreasureChoiceView(self.user_id))
        else:
            state["hp"] += event["hp_change"]
            embed.add_field(name="HP", value=str(state["hp"]))

            if state["hp"] <= 0:
                embed.title = "💀 ゲームオーバー！"
                embed.description += "\nHPがなくなりました…"
                save_user_states()
                await interaction.response.edit_message(embed=embed, view=None)
            else:
                await interaction.response.edit_message(embed=embed, view=DungeonEventView(self.user_id))

    @discord.ui.button(label="🧪 回復ポーションを使う", style=discord.ButtonStyle.success)
    async def use_potion(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("これはあなたのゲームではありません。", ephemeral=True)
            return

        state = user_states[str(self.user_id)]

        if "回復ポーション" not in state.get("items", []):
            await interaction.response.send_message("回復ポーションを持っていません。", ephemeral=True)
            return

        state["items"].remove("回復ポーション")
        state["hp"] += 20
        save_user_states()

        embed = discord.Embed(title="🧪 回復ポーション使用", description="HPが20回復した！", color=discord.Color.green())
        embed.add_field(name="HP", value=str(state["hp"]))
        embed.add_field(name="所持アイテム", value=", ".join(state["items"]) if state["items"] else "なし")
        await interaction.response.edit_message(embed=embed, view=self)

# --- ゲーム開始コマンド ---
@bot.command()
async def アビス(ctx):
    user_id = str(ctx.author.id)
    user_states[user_id] = {
        "name": ctx.author.display_name,
        "hp": 100,
        "stage": 0,
        "max_stage": 0,
        "items": []
    }
    save_user_states()

    embed = discord.Embed(title="憧れは止められねえんだ🐰", description="進むボタンでアビスを進もう。", color=discord.Color.blue())
    embed.set_image(url="https://media.discordapp.net/attachments/846657450115727403/1388050166912778280/1751006740721.png")
    embed.add_field(name="HP", value="100")
    await ctx.send(embed=embed, view=DungeonEventView(ctx.author.id))

# --- ランキングコマンド ---
@bot.command()
async def きろく(ctx):
    if not user_states:
        await ctx.send("まだ前人未踏です。")
        return

    sorted_users = sorted(user_states.items(), key=lambda x: x[1]["max_stage"], reverse=True)
    description = ""
    for i, (user_id, state) in enumerate(sorted_users[:5], start=1):
        description += f"{i}. **{state['name']}** - アビス第{state['max_stage']}層\n"

    embed = discord.Embed(
        title="🏆 アビスランキング（トップ5）",
        description=description,
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

#　－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－

# 🔁 実行

bot.run(os.environ['DISCORD_TOKEN'])

