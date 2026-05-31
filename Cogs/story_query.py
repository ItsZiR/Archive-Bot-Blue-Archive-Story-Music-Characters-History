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

class Story_Query(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

        self.db = sqlite3.connect("Bot_DB.db")
        self.db.row_factory = sqlite3.Row #可直接讀取column的名稱
        self.table = "BA_Story_Overall"
        self.cursor = self.db.cursor()

    class StoryPageView(graphic_tools.PageView):
        def __init__(self, pages, topic):
            super().__init__(pages)
            self.pages = pages #表示分頁方式
            self.current = 0 #目前頁碼
            self.prev.disabled = True
            self.next.disabled = len(pages) <= 1
            self.topic = topic
        
        def make_embed(self):
            embed = discord.Embed(
                title=f"蔚藍檔案{self.topic}清單",
                description=f"第 {self.current+1} / {len(self.pages)} 頁",
                color=discord.Color.from_str("#00F1FF")
            )
            for data in self.pages[self.current]:
                title = f"No. {data['Number']}, "
                fmt = ""
                match data['Type']:
                    case "Main":
                        title += "主線劇情 "
                        part:str = data['Part']
                        if data['Part'] == None: part = ""

                        if data['Main_Story_Part'] == 2:
                            title += "(主線第二部) "

                        if data['Story_Title'] == "序幕":
                            title += data['Story_Title']
                        elif str(data['Volume']).endswith('.'):
                            title += f'''{data['Volume']} {data['Chapter']}\n\t{data['Story_Title']}: {data['Story_Subtitle']} {part}'''
                        else:
                            title += f'''Vol. {data['Volume']}-{data['Chapter']}\n\t{data['Story_Title']}: {data['Story_Subtitle']} {part}'''
                        
                        fmt = f"話數: {data['Episodes']}, 實裝日期: {data['Released_day']}"

                    case "Club":
                        title += f"社團劇情: {data['Story_Title']}"
                        fmt = f"話數: {data['Episodes']}, 實裝日期: {data['Released_day']}"
                    
                    case "Event":
                        title += f"活動劇情: {data['Story_Title']}"
                        if data['Story_Subtitle']: title += f" {data['Story_Subtitle']}"
                        fmt = f"話數: {data['Episodes']}, 實裝日期: {data['Released_day']}"
                    
                    case "Mini":
                        title += f"迷你劇情: {data['Story_Title']}"
                        fmt = f"話數: {data['Episodes']}, 實裝日期: {data['Released_day']}"

                embed.add_field(
                    name=title,
                    value=fmt,
                    inline=False
                )
                embed.set_footer(text="Developed by ItsZir, via Discord.py")

            return embed

    @app_commands.command(name="story_list", description="劇情大全")
    async def story_list(self, interaction: discord.Interaction):
        self.cursor.execute(sql_commands.story_list_overall_sql(self.table))
        story_list = self.cursor.fetchall()

        per_page = 8 # 切頁
        pages = []
        for i in range(0, len(story_list), per_page):
            pages.append(story_list[i:i+per_page])
        
        if not pages:
            await interaction.response.send_message("沒有資料")
            return
        
        view = self.StoryPageView(pages, topic="全劇情")
        await interaction.response.send_message(embed=view.make_embed(), view=view)

    @app_commands.command(name="story_list_category", description="特定種類劇情的清單")
    async def story_list_category(self, interaction: discord.Interaction, story_type: str):
        self.cursor.execute(sql_commands.story_list_category_sql(self.table, story_type))
        story_list = self.cursor.fetchall()
        
        per_page = 8 #切頁
        pages = []
        for i in range(0, len(story_list), per_page):
            pages.append(story_list[i:i+per_page])
        
        if not pages:
            await interaction.response.send_message("沒有資料")
            return
        
        mapping = {
            "Main": "主線劇情",
            "Event": "活動劇情",
            "Club": "社團劇情",
            "Mini": "迷你劇情"
        }
        view = self.StoryPageView(pages, topic= mapping[story_type])

        await interaction.response.send_message(embed=view.make_embed(), view=view)

    @story_list_category.autocomplete("story_type")
    async def story_list_category_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str #user目前輸入值
    ) -> list[app_commands.Choice[str]]:
        mapping = {
            "Main": "主線劇情",
            "Event": "活動劇情",
            "Club": "社團劇情",
            "Mini": "迷你劇情"
        }
        choice = [
            app_commands.Choice(name=zh, value=en)
            for en, zh in mapping.items()
        ]

        return choice[:25]

#setup function for each Cog file
async def setup(bot: commands.Bot):
    await bot.add_cog(Story_Query(bot))