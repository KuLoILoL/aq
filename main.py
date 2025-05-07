
import discord
from discord.ext import commands
from discord import app_commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# 🔹 ボタン付きの処理用ビュー
class MyButtonView(discord.ui.View):
    @discord.ui.button(label="挨拶", style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("# ドカーン💥", ephemeral=True)

# 🔹 コマンドごとの処理を関数で用意しておく
async def hello_command(ctx):
    await ctx.send("ハロー")

async def button_command(ctx):
    view = MyButtonView()
    await ctx.send("おはようございます！", view=view)

# 🔹 コマンド名 → 関数 の辞書（ループで登録）
command_map = {
    "hello": hello_command,
    "ping": ping_command,
    "おはよう": button_command
}

# 🔁 登録ループ（方法②スタイル）
for name, handler in command_map.items():
    bot.command(name=name)(handler)



# プレイヤーステータスを保存（ユーザーごと）
player_data = {}

class BattleView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="攻撃", style=discord.ButtonStyle.danger)
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("他人の戦闘には参加できません。", ephemeral=True)
            return

        data = player_data.get(self.user_id)
        if not data:
            await interaction.response.send_message("戦闘データが見つかりません。", ephemeral=True)
            return

        # 攻撃処理
        damage_to_enemy = 10
        damage_to_player = random.randint(5, 15)

        data["enemy_hp"] -= damage_to_enemy
        data["player_hp"] -= damage_to_player

        if data["enemy_hp"] <= 0:
            await interaction.response.edit_message(
                content=f"🎉 {interaction.user.display_name} の勝利！",
                embed=None,
                view=None
            )
            player_data.pop(self.user_id, None)
            return

        if data["player_hp"] <= 0:
            await interaction.response.edit_message(
                content=f"💀 {interaction.user.display_name} はやられてしまった…",
                embed=None,
                view=None
            )
            player_data.pop(self.user_id, None)
            return

        # HPを更新して表示
        embed = discord.Embed(title="⚔️ 戦闘中", color=discord.Color.red())
        embed.add_field(name="あなたのHP", value=f"{data['player_hp']} / 100")
        embed.add_field(name="敵のHP", value=f"{data['enemy_hp']} / 50")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1303151128178982973/1369549449927327805/1696009395055.png?ex=681c43d1&is=681af251&hm=855076894a828f92336890ae6b1d25972e60cf8d58ddfcba9058d41f762e6273&format=webp&quality=lossless&width=610&height=709")

        await interaction.response.edit_message(embed=embed, view=self)

@bot.command()
async def たたかい(ctx):
    user_id = ctx.author.id

    if user_id in player_data:
        await ctx.send("すでに戦闘中です！")
        return

    # 初期化
    player_data[user_id] = {
        "player_hp": 100,
        "enemy_hp": 50
    }

    embed = discord.Embed(title="⚔️ 戦闘開始！", description="攻撃ボタンで戦おう！", color=discord.Color.red())
    embed.add_field(name="あなたのHP", value="100 / 100")
    embed.add_field(name="敵のHP", value="50 / 50")
    embed.set_image(url="attachment://enemy.png")  # 同じファイル名で添付

    view = BattleView(user_id)
    file = discord.File("enemy.png", filename="enemy.png")

    await ctx.send(file=file, embed=embed, view=view)

bot.run(os.environ["DISCORD_TOKEN"])

