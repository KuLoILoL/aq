import discord
from discord.ext import commands
import os
import random
import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is ready: {bot.user}')

# 🔹 ボタン付きの処理用ビュー
class MyButtonView(discord.ui.View):
    @discord.ui.button(label="挨拶", style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("# ドカーン💥", ephemeral=True)

# 🔹 コマンド関数
async def hello_command(ctx):
    await ctx.send("ハロー")

async def button_command(ctx):
    view = MyButtonView()
    await ctx.send("おはようございます！", view=view)

# 🔹 コマンドマップ
command_map = {
    "hello": hello_command,
    "おはよう": button_command
}

for name, handler in command_map.items():
    bot.command(name=name)(handler)

@bot.event
async def on_message(message):
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

DATA_FILE = "player_data.json"
player_data = {}

def load_data():
    global player_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            player_data = json.load(f)

# ここから戦闘ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(player_data, f, ensure_ascii=False, indent=2)

load_data()

class Character:
    def __init__(self, name, level=1, exp=0, max_hp=100, strength=10, agility=8):
        self.name = name
        self.level = level
        self.exp = exp
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.agility = agility

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "exp": self.exp,
            "max_hp": self.max_hp,
            "strength": self.strength,
            "agility": self.agility
        }

    def gain_exp(self, amount):
        self.exp += amount
        level_up = False
        while self.exp >= self.next_level_exp():
            self.exp -= self.next_level_exp()
            self.level += 1
            self.max_hp += 20
            self.strength += 3
            self.agility += 2
            level_up = True
        return level_up

    def next_level_exp(self):
        return 50 + self.level * 20

    @property
    def attack(self):
        return self.strength + 5

    @property
    def defense(self):
        return int(self.agility / 2) + 3

    def is_alive(self):
        return self.hp > 0

    def attack_target(self, target):
        damage = max(1, self.attack - target.defense)
        target.hp -= damage
        return damage

class BattleView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="攻撃", style=discord.ButtonStyle.danger)
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("これはあなたの戦闘ではありません。", ephemeral=True)
            return

        data = player_data.get(str(self.user_id))
        if not data:
            await interaction.response.send_message("戦闘データが見つかりません。", ephemeral=True)
            return

        player = data["player"]
        enemy = data["enemy"]

        dmg_to_enemy = player.attack_target(enemy)
        dmg_to_player = enemy.attack_target(player)

        if not enemy.is_alive():
            gained_exp = 30 + enemy.level * 10
            level_up = player.gain_exp(gained_exp)
            player.hp = player.max_hp
            save_data()
            del player_data[str(self.user_id)]
            result = f"🎉 勝利！EXPを {gained_exp} 獲得！"
            if level_up:
                result += f"\n⬆️ {player.name} は レベル {player.level} に上がった！"

            await interaction.response.edit_message(content=result, embed=None, view=None)
            return

        if not player.is_alive():
            del player_data[str(self.user_id)]
            await interaction.response.edit_message(content="💀 やられてしまった…", embed=None, view=None)
            return

        embed = discord.Embed(title="⚔️ 戦闘中", color=discord.Color.red())
        embed.add_field(name="あなたのHP", value=f"{player.hp} / {player.max_hp}")
        embed.add_field(name="敵のHP", value=f"{enemy.hp} / {enemy.max_hp}")
        await interaction.response.edit_message(embed=embed, view=self)

@bot.command()
async def たたかい(ctx):
    user_id = str(ctx.author.id)

    if user_id in player_data:
        await ctx.send("すでに戦闘中です！")
        return

    # プレイヤーデータの読み込み or 新規作成
    saved = load_data()
    if user_id in saved:
        p = saved[user_id]
        player = Character(p["name"], p["level"], p["exp"], p["max_hp"], p["strength"], p["agility"])
    else:
        player = Character(ctx.author.display_name)

    # 敵のレベルはプレイヤーのレベル ±1（最低1）
    enemy_level = max(1, random.randint(player.level - 1, player.level + 1))
    enemy = Character("スライム", level=enemy_level, max_hp=80 + 15 * enemy_level,
                      strength=8 + 2 * enemy_level, agility=6 + 2 * enemy_level)

    player.hp = player.max_hp
    enemy.hp = enemy.max_hp

    player_data[user_id] = {
        "player": player,
        "enemy": enemy
    }

    embed = discord.Embed(title="⚔️ 戦闘開始！", description="攻撃ボタンを押してバトル！", color=discord.Color.red())
    embed.add_field(name="あなたのHP", value=f"{player.hp} / {player.max_hp}")
    embed.add_field(name="敵のHP", value=f"{enemy.hp} / {enemy.max_hp}")
    view = BattleView(user_id=int(user_id))
    await ctx.send(embed=embed, view=view)

    # 永続保存
    saved[user_id] = player.to_dict()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(saved, f, ensure_ascii=False, indent=2)

# 実行
bot.run(os.environ['DISCORD_TOKEN'])
