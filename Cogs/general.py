import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import sys
import os

# 1. 取得目前檔案的絕對路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
# 2. 取得父目錄（也就是專案根目錄）
parent_dir = os.path.dirname(current_dir)
# 3. 把父目錄加入搜尋清單
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# 4. 現在可以用「絕對路徑」的方式匯入隔壁資料夾的檔案
from SQL_Commands import sql_commands
from Data_Models import models
from Graphic_Tools import graphic_tools

#--------------------------------------------------------------------------------------------------

class General(commands.Cog):
    #------ Initialize ------
    def __init__(self, bot:commands.Bot):
        self.bot = bot

        self.db = sqlite3.connect("Bot_DB.db")
        self.db.row_factory = sqlite3.Row #可直接讀取column的名稱
        self.table = "BA_Music"
        self.cursor = self.db.cursor()

    #------------ Slash Commands ------------
    
    @app_commands.command(name="greeting", description="打招呼")
    async def greeting(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"{interaction.user.mention}！Ciallo～(∠・ω< )⌒★")

    #------ Menu ------
    @app_commands.command(name="info", description="Bot功能說明")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="# - Archive Bot : 蔚藍檔案劇情、OST相關資料查詢",
            description="## 可查詢學生大廳、劇情與每首OST之間的關係，以及曲子的資訊",
            color=discord.Color.from_str("#00F1FF"),
            timestamp=interaction.created_at
        )
        embed.add_field(name="目前已上線的功能", value="- 請輸入 `/cmd_list` 進行查詢", inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        embed.set_footer(text="Developed by ItsZir, via Discord.py")

        await interaction.response.send_message(embed=embed)

#setup function for each Cog file
async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))