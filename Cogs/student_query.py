import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import sys, os
from datetime import datetime

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
    
    class StudentPageView(graphic_tools.PageView):
        def __init__(self, pages, topic):
            super().__init__(pages)
            self.pages = pages #表示分頁方式
            self.current = 0 #目前頁碼
            self.prev.disabled = True
            self.next.disabled = len(pages) <= 1
            self.topic = topic

        def make_embed(self):
            embed = discord.Embed(
                title = self.topic,
                description=f"第 {self.current+1} / {len(self.pages)} 頁",
                color=discord.Color.from_str("#00F1FF")
            )
            for data in self.pages[self.current]:
                date_diff = datetime.today() - datetime.strptime(data["Released_day"], '%Y-%m-%d')
                title = f"{data["Personal_Name"]} - {date_diff.days}天"
                fmt = data["Released_day"]

                embed.add_field(
                    name=title,
                    value=fmt,
                    inline=True
                )

            embed.set_footer(text="Developed by ItsZir, via Discord.py")
            return embed

    def get_student_model(self, sql_result) -> models.Student:
        student = models.Student(
            id = sql_result['id'],
            path_name = sql_result['PathName'],
            name = sql_result['Name'],
            family_name = sql_result['Family_Name'],
            personal_Name = sql_result['Personal_Name'],
            age = sql_result['Age'],
            grade = sql_result['Grade'],
            school = sql_result['School'],
            club = sql_result['Club'],
            height = sql_result['Height'],
            birthday = sql_result['Birthday'],
            hobbies = sql_result['Hobbies'],
            profile = sql_result['Profile'],
            rarity = sql_result['Rarity'],
            voice_actress = sql_result['Voice_Actress'],
            illustrator = sql_result['Illustrator'],
            designer = sql_result['Designer'],

            isDefault = sql_result['isDefault'],
            size = sql_result['Size'],
            memorial_lobby_track = sql_result['Memorial_Lobby_Track'],
            released_day = sql_result['Released_day'],
            type = sql_result['Type'],
            unique_item = sql_result['Unique_Item'],
        )

        return student

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

    @app_commands.command(name="stu_default_list", description="目前沒有新衣裝的學生列表")
    async def stu_default_list(self, interaction: discord.Interaction):
        self.cursor.execute(sql_commands.get_sql_cmd('stu_default_list.sql'))
        stu_list = self.cursor.fetchall()

        per_page = 15 # 切頁
        pages = []
        for i in range(0, len(stu_list), per_page):
            pages.append(stu_list[i:i+per_page])
        
        if not pages:
            await interaction.response.send_message("沒有資料")
            return
        
        view = self.StudentPageView(pages, topic=f"目前尚無新衣裝的學生: {len(stu_list)}位")
        await interaction.response.send_message(embed=view.make_embed(), view=view)

#setup function for each Cog file
async def setup(bot: commands.Bot):
    await bot.add_cog(Student_Query(bot))
