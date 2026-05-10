import discord
import matplotlib.pyplot as plt
import numpy as np
import io

plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] # 設定微軟正黑體
plt.rcParams['axes.unicode_minus'] = False

def create_bar_img(schools, heights):
    # 建立畫布
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 繪製水平長條圖 (y軸是學校, x軸是寬度即身高)
    bars = ax.barh(schools, heights, color='skyblue', align='center')
    
    # 設定標籤與標題
    ax.set_xlabel('比例(%)')
    ax.set_title('各校蘿莉佔比')
    
    # 反轉 y 軸讓第一筆資料在最上面
    ax.invert_yaxis() 
    
    # 在長條圖末端顯示數值
    ax.bar_label(bars, fmt="%.2f", padding=3)
    
    # 自動調整佈局避免標籤被切到
    plt.tight_layout()

    # 存入 BytesIO
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf

class PageView(discord.ui.View):
    def __init__(self, pages, timeout=None):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current = 0
        self.prev.disabled = True
        self.next.disabled = len(pages) <= 1

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current > 0:
            self.current -= 1
        self.prev.disabled = self.current == 0
        self.next.disabled = False
        await interaction.response.edit_message(embed=self.make_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current < len(self.pages) - 1:
            self.current += 1
        self.next.disabled = self.current == len(self.pages) - 1
        self.prev.disabled = False
        await interaction.response.edit_message(embed=self.make_embed(), view=self)
