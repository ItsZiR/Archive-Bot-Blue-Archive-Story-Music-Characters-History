import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import sys, os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from SQL_Commands import sql_commands
from Data_Models import models
from Graphic_Tools import graphic_tools

#--------------------------------------------------------------------------------------------------

class Student_Query(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

        self.db = sqlite3.connect("Bot_DB.db")
        self.db.row_factory = sqlite3.Row #可直接讀取column的名稱
        self.table = "BA_Students"
        self.cursor = self.db.cursor()
    
    @app_commands.command(name="stu_count", description="目前實裝的學生數量")
    #@app_commands.describe()
    async def stu_count(self, interaction: discord.Interaction):
        self.cursor.execute(sql_commands.stu_count_sql(self.table))
        stu_counts = self.cursor.fetchone()[0]
        self.cursor.execute(sql_commands.stu_unique_count_sql(self.table))
        stu_unique_counts = self.cursor.fetchone()[0]

        embed = discord.Embed(
            title="目前已實裝學生學生統計(以日服為基準):",
            color=discord.Color.from_str("#00F1FF"),
            timestamp=interaction.created_at
        )

        embed.add_field(name="所有學生數量", value=stu_counts, inline=False)
        embed.add_field(name="所有不重複學生數量(但包括黑子)", value=stu_unique_counts, inline=False)
        embed.set_footer(text="Developed by ItsZir, via Discord.py")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stu_school_loli_rate", description="統計各校的蘿莉佔比(限定身高152含以下的)")
    #@app_commands.describe("不考慮聯動角色")
    async def stu_school_loli_rate(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.cursor.execute(sql_commands.stu_school_estimate_sql(self.table))
        result = self.cursor.fetchall()

        school_list = []
        loli_rate = []

        for data in result:
            school_list.append(data['School'])
            loli_rate.append(round(data['height_U152'] / data['total_students'] * 100, 2))

        image_buf = graphic_tools.create_bar_img(school_list, loli_rate, '各校蘿莉佔比')

        file = discord.File(image_buf, filename="chart.png")
        embed = discord.Embed(
            title="📊 各校蘿莉比例分析 (身高小於或等於152)",
            color=discord.Color.from_str("#00F1FF")
        )
        embed.set_image(url="attachment://chart.png")

        await interaction.followup.send(embed=embed, file=file)

#setup function for each Cog file
async def setup(bot: commands.Bot):
    await bot.add_cog(Student_Query(bot))
