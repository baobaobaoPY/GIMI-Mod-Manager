from PIL import Image, ImageTk
from tkinter import filedialog
import tkinter as tk
import webbrowser
import subprocess
import sqlite3
import base64
import shutil
import sys
import os
import re
import io
import json
import win32com.client

# 导入主脚本所需副模块
import GIMI_ModInstallation  # 导入GIMI_ModInstallation模块
from Furina_base64_PNG import base64_image_string  # 使用base64模块图像资源硬编码加载程序UI美化
import JianTingYuanShen  # 导入JianTingYuanShen模块

print("""
\x1b[1;97m《《《《《\x1b[0m \x1b[1;4;97;96mGIMI·Mod-Manager.exe 版本:2.0.27.20250318\x1b[0m \x1b[1;97m》》》》》\x1b[0m

\x1b[1;96mGIMI·Mod-Manager\x1b[0m:\x1b[1;97m"\x1b[0m\x1b[4m利用终端+GUI界面按钮交互以获取您所需的功能(最佳运行分辨率\x1b[4;97m1920*1080\x1b[0m\x1b[4m)\x1b[0m\x1b[1;97m"\x1b[0m

\x1b[1;96mGIMI·Mod-Manager\x1b[0m:\x1b[1;97m"\x1b[0m\x1b[4m提示您(在初次运行后请勿删除程序生成的文档以及文件夹,防止程序运行出现严重错误!)\x1b[0m\x1b[1;97m"\x1b[0m

\x1b[1;96mGIMI·Mod-Manager\x1b[0m:\x1b[1;97m"\x1b[0m\x1b[4m在安装大型MOD资源时请您耐心等待程序的安装,此时出现程序无响应现象时属于正常情况,此时请勿关闭程序!\x1b[0m\x1b[1;97m"\x1b[0m
""")

# 定义默认的GameBanana网址
base_url = "https://gamebanana.com/search?_sOrder=popularity&"

txt_file_path = "原神Mods网址管理文档.txt"
mods_install_path = "Mods资源安装&备份夹"
install_folder = "1.资源安装夹"
backup_folder = "2.资源备份夹"
target_mods_folder = "Mod\\GIMI\\Mods"
db_file_path = "GIMI·Mod-Manager_WAY.db"
config_file_path = "Mod\\XXMI Launcher Config.json"

# 获取程序自身所在文件夹路径
def get_self_folder_path():
    return os.path.dirname(os.path.abspath(sys.argv[0]))

# 初始化数据库
def initialize_db():
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS image_paths (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_name TEXT UNIQUE,
        image_path TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_name TEXT UNIQUE,
        setting_value TEXT
    )
    """)
    conn.commit()
    conn.close()

# 更新图片路径
def update_image_path(image_name, new_path):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO image_paths (image_name, image_path)
    VALUES (?, ?)
    """, (image_name, new_path))
    conn.commit()
    conn.close()

def get_image_path_from_db(image_name):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT image_path FROM image_paths WHERE image_name = ?
    """, (image_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

# 保存游戏设置到数据库
def save_game_setting(setting_name, setting_value):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO game_settings (setting_name, setting_value)
    VALUES (?, ?)
    """, (setting_name, setting_value))
    conn.commit()
    conn.close()

# 获取游戏设置从数据库
def get_game_setting(setting_name):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT setting_value FROM game_settings WHERE setting_name = ?
    """, (setting_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def load_background_image(window, width=1292, height=646):
    try:
        # 从64进制字符串加载图片
        image_data = base64.b64decode(base64_image_string)
        img = Image.open(io.BytesIO(image_data))
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"""\x1b[91m加载背景图片时出错\x1b[0m,错误为:“{e}”\n\x1b[92m请重新安装程序或更新程序至最新版本\x1b[0m,\x1b[92m按此操作后情况仍未解决请立即联系开发者并提交此错误\x1b[0m!
""")
        return None

def set_background_image(window, image):
    if image:
        background_label = tk.Label(window, image=image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        return background_label
    return None

def handle_url_view(window):
    url = base_url + "_sSearchString=Genshin+Impact&_idGameRow=8552"
    print(f"原神Mods蕉网网址为:\n{url}")


def handle_update_urls(window):
    if os.path.exists(txt_file_path):
        with open(txt_file_path, "r", encoding="utf-8") as file:
            content = file.read()
            print("\n")
            print(content)
    else:
        print("\x1b[91m文件意外丢失·请重新运行程序\x1b[0m!")


def handle_lazy_search(window):
    input_window = tk.Toplevel(window)
    input_window.title("输入")
    input_window.geometry("225x125")
    input_window.resizable(False, False)

    input_window.grab_set()

    label = tk.Label(input_window, text="输入角色名或角色编号:")
    label.pack(pady=10)

    entry = tk.Entry(input_window, width=30)
    entry.pack(pady=5)
    entry.focus_set()  # 输入框自动获得焦点

    def confirm_input():
        # 获取用户输入的角色名或角色编号
        search_term = entry.get().strip()
        # 调用翻译函数，将用户输入的角色名或角色编号翻译为英文
        translated_details = translate_to_english_with_color(search_term)
        input_window.destroy()  # 关闭输入窗口
        if translated_details:
            role_name, translated_name, url, quality = translated_details
            print(f"""此角色或编号“{role_name}”的翻译结果为:“{translated_name}”可能的相关香蕉网Mods搜索网址为:\n{url}
""")
        else:
            print(f"""此角色或编号“\x1b[91m{search_term}\x1b[0m”的英文翻译不存在!
""")

    confirm_button = tk.Button(input_window, text="确认", command=confirm_input)
    confirm_button.pack(side=tk.LEFT, padx=10, pady=10)

    cancel_button = tk.Button(input_window, text="取消", command=input_window.destroy)
    cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)

    # 按下回车键触发确认操作
    input_window.bind('<Return>', lambda event: confirm_input())

def translate_to_english_with_color(text):
    # 定义角色名翻译映射
    translation_map = {
        # name=中翻英 country=国家 element=元素属性 body_type=体型 gender=性别 weapon=武器类型 quality=品质
        # 国家:{ 蒙德,璃月,稻妻,须弥,枫丹,纳塔,至冬,提瓦特,深渊,未知 }
        # 元素属性:{ 火元素,水元素,风元素,雷元素,草元素,冰元素,岩元素,全元素,未知 }
        # 体型:{ 成男,成女,少年,少女,萝莉,未知 }
        # 性别:{ 男,女,未知 }
        # 武器类型:{ 单手剑,双手剑,弓,长柄,法器,未知 }
        # 品质:{ 五星金品,四星紫品,未知 }
        "安柏": {"name": "Amber", "country": "蒙德", "element": "火元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "四星紫品", "numbering": "00001"},
        "安博": {"name": "Amber", "country": "蒙德", "element": "火元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "四星紫品", "numbering": "00001"},
        "安伯": {"name": "Amber", "country": "蒙德", "element": "火元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "四星紫品", "numbering": "00001"},
        "安泊": {"name": "Amber", "country": "蒙德", "element": "火元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "四星紫品", "numbering": "00001"},

        "凯亚": {"name": "Kaeya", "country": "蒙德", "element": "冰元素", "body_type": "成男", "gender": "男",
                 "weapon": "单手剑", "quality": "四星紫品", "numbering": "00002"},
        "凯雅": {"name": "Kaeya", "country": "蒙德", "element": "冰元素", "body_type": "成男", "gender": "男",
                 "weapon": "单手剑", "quality": "四星紫品", "numbering": "00002"},
        "铠亚": {"name": "Kaeya", "country": "蒙德", "element": "冰元素", "body_type": "成男", "gender": "男",
                 "weapon": "单手剑", "quality": "四星紫品", "numbering": "00002"},
        "铠雅": {"name": "Kaeya", "country": "蒙德", "element": "冰元素", "body_type": "成男", "gender": "男",
                 "weapon": "单手剑", "quality": "四星紫品", "numbering": "00002"},

        "丽莎": {"name": "Lisa", "country": "蒙德", "element": "雷元素", "body_type": "成女", "gender": "女",
                 "weapon": "法器", "quality": "四星紫品", "numbering": "00003"},
        "丽沙": {"name": "Lisa", "country": "蒙德", "element": "雷元素", "body_type": "成女", "gender": "女",
                 "weapon": "法器", "quality": "四星紫品", "numbering": "00003"},
        "莉莎": {"name": "Lisa", "country": "蒙德", "element": "雷元素", "body_type": "成女", "gender": "女",
                 "weapon": "法器", "quality": "四星紫品", "numbering": "00003"},
        "莉沙": {"name": "Lisa", "country": "蒙德", "element": "雷元素", "body_type": "成女", "gender": "女",
                 "weapon": "法器", "quality": "四星紫品", "numbering": "00003"},

        "芭芭拉": {"name": "Barbara", "country": "蒙德", "element": "水元素", "body_type": "少女", "gender": "女",
                   "weapon": "法器", "quality": "四星紫品", "numbering": "00004"},
        "芭芭啦": {"name": "Barbara", "country": "蒙德", "element": "水元素", "body_type": "少女", "gender": "女",
                   "weapon": "法器", "quality": "四星紫品", "numbering": "00004"},
        "巴巴拉": {"name": "Barbara", "country": "蒙德", "element": "水元素", "body_type": "少女", "gender": "女",
                   "weapon": "法器", "quality": "四星紫品", "numbering": "00004"},
        "巴巴啦": {"name": "Barbara", "country": "蒙德", "element": "水元素", "body_type": "少女", "gender": "女",
                   "weapon": "法器", "quality": "四星紫品", "numbering": "00004"},

        "雷泽": {"name": "Razur", "country": "蒙德", "element": "雷元素", "body_type": "少年", "gender": "男",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00005"},
        "狼崽": {"name": "Razur", "country": "蒙德", "element": "雷元素", "body_type": "少年", "gender": "男",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00005"},
        "小狼崽": {"name": "Razur", "country": "蒙德", "element": "雷元素", "body_type": "少年", "gender": "男",
                   "weapon": "双手剑", "quality": "四星紫品", "numbering": "00005"},
        "蒙德狼崽": {"name": "Razur", "country": "蒙德", "element": "雷元素", "body_type": "少年", "gender": "男",
                     "weapon": "双手剑", "quality": "四星紫品", "numbering": "00005"},
        "蒙德小狼崽": {"name": "Razur", "country": "蒙德", "element": "雷元素", "body_type": "少年", "gender": "男",
                       "weapon": "双手剑", "quality": "四星紫品", "numbering": "00005"},

        "香菱": {"name": "Xiangling", "country": "璃月", "element": "火元素", "body_type": "少女", "gender": "女",
                 "weapon": "长柄", "quality": "四星紫品", "numbering": "00006"},
        "锅巴": {"name": "Xiangling", "country": "璃月", "element": "火元素", "body_type": "少女", "gender": "女",
                 "weapon": "长柄", "quality": "四星紫品", "numbering": "00006"},

        "北斗": {"name": "Beidou", "country": "璃月", "element": "雷元素", "body_type": "成女", "gender": "女",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00007"},

        "行秋": {"name": "Xingqiu", "country": "璃月", "element": "水元素", "body_type": "少年", "gender": "男",
                 "weapon": "单手剑", "quality": "四星紫品", "numbering": "00008"},

        "凝光": {"name": "Ningguang", "country": "璃月", "element": "岩元素", "body_type": "成女", "gender": "女",
                 "weapon": "法器", "quality": "四星紫品", "numbering": "00009"},

        "菲谢尔": {"name": "Fischl", "country": "蒙德", "element": "雷元素", "body_type": "少女", "gender": "女",
                   "weapon": "弓", "quality": "四星紫品", "numbering": "00010"},
        "小艾咪": {"name": "Fischl", "country": "蒙德", "element": "雷元素", "body_type": "少女", "gender": "女",
                   "weapon": "弓", "quality": "四星紫品", "numbering": "00010"},
        "奥兹": {"name": "Fischl", "country": "蒙德", "element": "雷元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "四星紫品", "numbering": "00010"},
        "皇女": {"name": "Fischl", "country": "蒙德", "element": "雷元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "四星紫品", "numbering": "00010"},

        "班尼特": {"name": "Bennett", "country": "蒙德", "element": "火元素", "body_type": "少年", "gender": "男",
                   "weapon": "单手剑", "quality": "四星紫品", "numbering": "00011"},
        "倒霉蛋": {"name": "Bennett", "country": "蒙德", "element": "火元素", "body_type": "少年", "gender": "男",
                   "weapon": "单手剑", "quality": "四星紫品", "numbering": "00011"},
        "冒险倒霉家": {"name": "Bennett", "country": "蒙德", "element": "火元素", "body_type": "少年", "gender": "男",
                       "weapon": "单手剑", "quality": "四星紫品", "numbering": "00011"},
        "蒙德倒霉蛋": {"name": "Bennett", "country": "蒙德", "element": "火元素", "body_type": "少年", "gender": "男",
                       "weapon": "单手剑", "quality": "四星紫品", "numbering": "00011"},

        "诺艾尔": {"name": "Noelle", "country": "蒙德", "element": "岩元素", "body_type": "少女", "gender": "女",
                   "weapon": "双手剑", "quality": "四星紫品", "numbering": "00012"},
        "女仆": {"name": "Noelle", "country": "蒙德", "element": "岩元素", "body_type": "少女", "gender": "女",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00012"},

        "重云": {"name": "chongyun", "country": "璃月", "element": "冰元素", "body_type": "少年", "gender": "男",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00013"},
        "纯阳之体": {"name": "chongyun", "country": "璃月", "element": "冰元素", "body_type": "少年", "gender": "男",
                     "weapon": "双手剑", "quality": "四星紫品", "numbering": "00013"},
        "璃月纯阳": {"name": "chongyun", "country": "璃月", "element": "冰元素", "body_type": "少年", "gender": "男",
                     "weapon": "双手剑", "quality": "四星紫品", "numbering": "00013"},

        "砂糖": {"name": "Sucrose", "country": "蒙德", "element": "风元素", "body_type": "少女", "gender": "女",
                 "weapon": "法器", "quality": "四星紫品", "numbering": "00014"},
        "小万叶": {"name": "Sucrose", "country": "蒙德", "element": "风元素", "body_type": "少女", "gender": "女",
                   "weapon": "法器", "quality": "四星紫品", "numbering": "00014"},

        "琴": {"name": "Jean", "country": "蒙德", "element": "风元素", "body_type": "成女", "gender": "女",
               "weapon": "单手剑", "quality": "五星金品", "numbering": "00015"},
        "琴团长": {"name": "Jean", "country": "蒙德", "element": "风元素", "body_type": "成女", "gender": "女",
                   "weapon": "单手剑", "quality": "五星金品", "numbering": "00015"},

        "迪卢克": {"name": "Diluc", "country": "蒙德", "element": "火元素", "body_type": "成男", "gender": "男",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00016"},
        "暗夜英雄": {"name": "Diluc", "country": "蒙德", "element": "火元素", "body_type": "成男", "gender": "男",
                     "weapon": "双手剑", "quality": "五星金品", "numbering": "00016"},
        "迪姥爷": {"name": "Diluc", "country": "蒙德", "element": "火元素", "body_type": "成男", "gender": "男",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00016"},
        "卢姥爷": {"name": "Diluc", "country": "蒙德", "element": "火元素", "body_type": "成男", "gender": "男",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00016"},

        "七七": {"name": "Qiqi", "country": "璃月", "element": "冰元素", "body_type": "萝莉", "gender": "女",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00017"},
        "璃月僵尸": {"name": "Qiqi", "country": "璃月", "element": "冰元素", "body_type": "萝莉", "gender": "女",
                     "weapon": "单手剑", "quality": "五星金品", "numbering": "00017"},

        "莫娜": {"name": "Mona", "country": "蒙德", "element": "水元素", "body_type": "少女", "gender": "女",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00018"},
        "阿斯托洛吉斯·莫娜·梅基斯图斯": {"name": "Mona", "country": "蒙德", "element": "水元素", "body_type": "少女",
                                         "gender": "女", "weapon": "法器", "quality": "五星金品", "numbering": "00018"},
        "阿斯托洛吉斯莫娜梅基斯图斯": {"name": "Mona", "country": "蒙德", "element": "水元素", "body_type": "少女",
                                       "gender": "女", "weapon": "法器", "quality": "五星金品", "numbering": "00018"},

        "刻晴": {"name": "Keqing", "country": "璃月", "element": "雷元素", "body_type": "少女", "gender": "女",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00019"},
        "璃月飞雷神": {"name": "Keqing", "country": "璃月", "element": "雷元素", "body_type": "少女", "gender": "女",
                       "weapon": "单手剑", "quality": "五星金品", "numbering": "00019"},

        "温迪": {"name": "Venti", "country": "蒙德", "element": "风元素", "body_type": "少年", "gender": "男",
                 "weapon": "弓", "quality": "五星金品", "numbering": "00020"},
        "风神": {"name": "Venti", "country": "蒙德", "element": "风元素", "body_type": "少年", "gender": "男",
                 "weapon": "弓", "quality": "五星金品", "numbering": "00020"},
        "蒙德酒鬼": {"name": "Venti", "country": "蒙德", "element": "风元素", "body_type": "少年", "gender": "男",
                     "weapon": "弓", "quality": "五星金品", "numbering": "00020"},
        "卖唱的": {"name": "Venti", "country": "蒙德", "element": "风元素", "body_type": "少年", "gender": "男",
                   "weapon": "弓", "quality": "五星金品", "numbering": "00020"},
        "吟游诗人": {"name": "Venti", "country": "蒙德", "element": "风元素", "body_type": "少年", "gender": "男",
                     "weapon": "弓", "quality": "五星金品", "numbering": "00020"},
        "巴巴托斯": {"name": "Venti", "country": "蒙德", "element": "风元素", "body_type": "少年", "gender": "男",
                     "weapon": "弓", "quality": "五星金品", "numbering": "00020"},

        "可莉": {"name": "Klee", "country": "蒙德", "element": "火元素", "body_type": "萝莉", "gender": "女",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00021"},
        "可利": {"name": "Klee", "country": "蒙德", "element": "火元素", "body_type": "萝莉", "gender": "女",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00021"},

        "迪奥娜": {"name": "Diona", "country": "蒙德", "element": "冰元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "弓", "quality": "四星紫品", "numbering": "00022"},

        "达达利亚": {"name": "Tartaglia", "country": "璃月", "element": "水元素", "body_type": "成男", "gender": "男",
                     "weapon": "弓", "quality": "五星金品", "numbering": "00023"},
        "公子": {"name": "Tartaglia", "country": "璃月", "element": "水元素", "body_type": "成男", "gender": "男",
                 "weapon": "弓", "quality": "五星金品", "numbering": "00023"},

        "辛焱": {"name": "Xinyan", "country": "璃月", "element": "火元素", "body_type": "少女", "gender": "女",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00024"},

        "钟离": {"name": "Zhongli", "country": "璃月", "element": "岩元素", "body_type": "成男", "gender": "男",
                 "weapon": "长柄", "quality": "五星金品", "numbering": "00025"},
        "钟老爷子": {"name": "Zhongli", "country": "璃月", "element": "岩元素", "body_type": "成男", "gender": "男",
                     "weapon": "长柄", "quality": "五星金品", "numbering": "00025"},
        "老爷子": {"name": "Zhongli", "country": "璃月", "element": "岩元素", "body_type": "成男", "gender": "男",
                   "weapon": "长柄", "quality": "五星金品", "numbering": "00025"},
        "岩王爷": {"name": "Zhongli", "country": "璃月", "element": "岩元素", "body_type": "成男", "gender": "男",
                   "weapon": "长柄", "quality": "五星金品", "numbering": "00025"},
        "岩神": {"name": "Zhongli", "country": "璃月", "element": "岩元素", "body_type": "成男", "gender": "男",
                 "weapon": "长柄", "quality": "五星金品", "numbering": "00025"},
        "摩拉克斯": {"name": "Zhongli", "country": "璃月", "element": "岩元素", "body_type": "成男", "gender": "男",
                     "weapon": "长柄", "quality": "五星金品", "numbering": "00025"},

        "阿贝多": {"name": "Albedo", "country": "蒙德", "element": "岩元素", "body_type": "少年", "gender": "男",
                   "weapon": "单手剑", "quality": "五星金品", "numbering": "00026"},

        "甘雨": {"name": "Ganyu", "country": "璃月", "element": "冰元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "五星金品", "numbering": "00027"},
        "王小美": {"name": "Ganyu", "country": "璃月", "element": "冰元素", "body_type": "少女", "gender": "女",
                   "weapon": "弓", "quality": "五星金品", "numbering": "00027"},
        "椰羊": {"name": "Ganyu", "country": "璃月", "element": "冰元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "五星金品", "numbering": "00027"},

        "魈": {"name": "Xiao", "country": "璃月", "element": "风元素", "body_type": "少年", "gender": "男",
               "weapon": "长柄", "quality": "五星金品", "numbering": "00028"},

        "胡桃": {"name": "Hu+Tao", "country": "璃月", "element": "火元素", "body_type": "少女", "gender": "女",
                 "weapon": "长柄", "quality": "五星金品", "numbering": "00029"},
        "胡堂主": {"name": "Hu+Tao", "country": "璃月", "element": "火元素", "body_type": "少女", "gender": "女",
                   "weapon": "长柄", "quality": "五星金品", "numbering": "00029"},

        "罗莎莉亚": {"name": "Rosaria", "country": "蒙德", "element": "冰元素", "body_type": "少女", "gender": "女",
                     "weapon": "长柄", "quality": "四星紫品", "numbering": "00030"},
        "罗沙利亚": {"name": "Rosaria", "country": "蒙德", "element": "冰元素", "body_type": "少女", "gender": "女",
                     "weapon": "长柄", "quality": "四星紫品", "numbering": "00030"},

        "烟绯": {"name": "Yanfei", "country": "璃月", "element": "火元素", "body_type": "少女", "gender": "女",
                 "weapon": "法器", "quality": "四星紫品", "numbering": "00031"},

        "优菈": {"name": "Eula", "country": "蒙德", "element": "冰元素", "body_type": "成女", "gender": "女",
                 "weapon": "双手剑", "quality": "五星金品", "numbering": "00032"},
        "优拉": {"name": "Eula", "country": "蒙德", "element": "冰元素", "body_type": "成女", "gender": "女",
                 "weapon": "双手剑", "quality": "五星金品", "numbering": "00032"},

        "艾洛伊": {"name": "Aloy", "country": "未知", "element": "冰元素", "body_type": "少女", "gender": "女",
                   "weapon": "弓", "quality": "未知", "numbering": "00033"},
        "埃洛伊": {"name": "Aloy", "country": "未知", "element": "冰元素", "body_type": "少女", "gender": "女",
                   "weapon": "弓", "quality": "未知", "numbering": "00033"},
        "埃落伊": {"name": "Aloy", "country": "未知", "element": "冰元素", "body_type": "少女", "gender": "女",
                   "weapon": "弓", "quality": "未知", "numbering": "00033"},
        "艾落伊": {"name": "Aloy", "country": "未知", "element": "冰元素", "body_type": "少女", "gender": "女",
                   "weapon": "弓", "quality": "未知", "numbering": "00033"},

        "枫原万叶": {"name": "Kaedehara+Kazuha", "country": "稻妻", "element": "风元素", "body_type": "少年",
                     "gender": "男", "weapon": "单手剑", "quality": "五星金品", "numbering": "00034"},
        "万叶": {"name": "Kaedehara+Kazuha", "country": "稻妻", "element": "风元素", "body_type": "少年",
                 "gender": "男", "weapon": "单手剑", "quality": "五星金品", "numbering": "00034"},

        "神里绫华": {"name": "Kamisato+Ayaka", "country": "稻妻", "element": "冰元素", "body_type": "少女",
                     "gender": "女", "weapon": "单手剑", "quality": "五星金品", "numbering": "00035"},
        "神里凌华": {"name": "Kamisato+Ayaka", "country": "稻妻", "element": "冰元素", "body_type": "少女",
                     "gender": "女", "weapon": "单手剑", "quality": "五星金品", "numbering": "00035"},
        "绫华": {"name": "Kamisato+Ayaka", "country": "稻妻", "element": "冰元素", "body_type": "少女", "gender": "女",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00035"},
        "凌华": {"name": "Kamisato+Ayaka", "country": "稻妻", "element": "冰元素", "body_type": "少女", "gender": "女",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00035"},

        "早柚": {"name": "Sayu", "country": "稻妻", "element": "风元素", "body_type": "萝莉", "gender": "女",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00036"},
        "旱抽": {"name": "Sayu", "country": "稻妻", "element": "风元素", "body_type": "萝莉", "gender": "女",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00036"},

        "宵宫": {"name": "Yoimiya", "country": "稻妻", "element": "火元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "五星金品", "numbering": "00037"},

        "九条裟罗": {"name": "Kujou+Sara", "country": "稻妻", "element": "雷元素", "body_type": "少女", "gender": "女",
                     "weapon": "弓", "quality": "四星紫品", "numbering": "00038"},
        "九条": {"name": "Kujou+Sara", "country": "稻妻", "element": "雷元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "四星紫品", "numbering": "00038"},
        "天狗": {"name": "Kujou+Sara", "country": "稻妻", "element": "雷元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "四星紫品", "numbering": "00038"},

        "雷电将军": {"name": "Raiden+Shogun", "country": "稻妻", "element": "雷元素", "body_type": "成女",
                     "gender": "女", "weapon": "长柄", "quality": "五星金品", "numbering": "00039"},
        "影": {"name": "Raiden+Shogun", "country": "稻妻", "element": "雷元素", "body_type": "成女", "gender": "女",
               "weapon": "长柄", "quality": "五星金品", "numbering": "00039"},
        "雷神": {"name": "Raiden+Shogun", "country": "稻妻", "element": "雷元素", "body_type": "成女", "gender": "女",
                 "weapon": "长柄", "quality": "五星金品", "numbering": "00039"},
        "巴尔泽布": {"name": "Raiden+Shogun", "country": "稻妻", "element": "雷元素", "body_type": "成女",
                     "gender": "女", "weapon": "长柄", "quality": "五星金品", "numbering": "00039"},
        "将军大人": {"name": "Raiden+Shogun", "country": "稻妻", "element": "雷元素", "body_type": "成女",
                     "gender": "女", "weapon": "长柄", "quality": "五星金品", "numbering": "00039"},
        "将军": {"name": "Raiden+Shogun", "country": "稻妻", "element": "雷元素", "body_type": "成女", "gender": "女",
                 "weapon": "长柄", "quality": "五星金品", "numbering": "00039"},
        "雷电影": {"name": "Raiden+Shogun", "country": "稻妻", "element": "雷元素", "body_type": "成女", "gender": "女",
                   "weapon": "长柄", "quality": "五星金品", "numbering": "00039"},

        "珊瑚宫心海": {"name": "Sangonomiya+Kokomi", "country": "稻妻", "element": "水元素", "body_type": "少女",
                       "gender": "女", "weapon": "法器", "quality": "五星金品", "numbering": "00040"},
        "心海": {"name": "Sangonomiya+Kokomi", "country": "稻妻", "element": "水元素", "body_type": "少女",
                 "gender": "女", "weapon": "法器", "quality": "五星金品", "numbering": "00041"},

        "托马": {"name": "Thoma", "country": "稻妻", "element": "火元素", "body_type": "少年", "gender": "男",
                 "weapon": "长柄", "quality": "四星紫品", "numbering": "00042"},

        "五郎": {"name": "Gorou", "country": "稻妻", "element": "岩元素", "body_type": "少年", "gender": "男",
                 "weapon": "弓", "quality": "四星紫品", "numbering": "00043"},

        "荒泷一斗": {"name": "Aratak+Itto", "country": "稻妻", "element": "岩元素", "body_type": "成男", "gender": "男",
                     "weapon": "双手剑", "quality": "五星金品", "numbering": "00044"},
        "一斗": {"name": "Aratak+Itto", "country": "稻妻", "element": "岩元素", "body_type": "成男", "gender": "男",
                 "weapon": "双手剑", "quality": "五星金品", "numbering": "00044"},

        "云堇": {"name": "Yun+Jin", "country": "璃月", "element": "岩元素", "body_type": "少女", "gender": "女",
                 "weapon": "长柄", "quality": "四星紫品", "numbering": "00045"},

        "申鹤": {"name": "Shenhe", "country": "璃月", "element": "冰元素", "body_type": "成女", "gender": "女",
                 "weapon": "长柄", "quality": "五星金品", "numbering": "00046"},

        "八重神子": {"name": "Yae+Miko", "country": "稻妻", "element": "雷元素", "body_type": "成女", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00047"},
        "八重": {"name": "Yae+Miko", "country": "稻妻", "element": "雷元素", "body_type": "成女", "gender": "女",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00047"},
        "神子": {"name": "Yae+Miko", "country": "稻妻", "element": "雷元素", "body_type": "成女", "gender": "女",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00047"},
        "八只虫子": {"name": "Yae+Miko", "country": "稻妻", "element": "雷元素", "body_type": "成女", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00047"},

        "神里绫人": {"name": "Kamisato+Ayato", "country": "稻妻", "element": "水元素", "body_type": "成男",
                     "gender": "男", "weapon": "单手剑", "quality": "五星金品", "numbering": "00048"},
        "神里凌人": {"name": "Kamisato+Ayato", "country": "稻妻", "element": "水元素", "body_type": "成男",
                     "gender": "男", "weapon": "单手剑", "quality": "五星金品", "numbering": "00048"},
        "绫人": {"name": "Kamisato+Ayato", "country": "稻妻", "element": "水元素", "body_type": "成男", "gender": "男",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00048"},
        "凌人": {"name": "Kamisato+Ayato", "country": "稻妻", "element": "水元素", "body_type": "成男", "gender": "男",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00048"},

        "夜兰": {"name": "Yelan", "country": "璃月", "element": "水元素", "body_type": "成女", "gender": "女",
                 "weapon": "弓", "quality": "五星金品", "numbering": "00049"},

        "久岐忍": {"name": "Kuki+Shinobu", "country": "稻妻", "element": "雷元素", "body_type": "少女", "gender": "女",
                   "weapon": "单手剑", "quality": "四星紫品", "numbering": "00050"},

        "鹿野院平藏": {"name": "Shikanoin+Heizou", "country": "稻妻", "element": "风元素", "body_type": "少年",
                       "gender": "男", "weapon": "法器", "quality": "四星紫品", "numbering": "00051"},
        "小鹿": {"name": "Shikanoin+Heizou", "country": "稻妻", "element": "风元素", "body_type": "少年",
                 "gender": "男", "weapon": "法器", "quality": "四星紫品", "numbering": "00051"},

        "柯莱": {"name": "Collei", "country": "须弥", "element": "草元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "四星紫品", "numbering": "00052"},

        "提纳里": {"name": "Tighnari", "country": "须弥", "element": "草元素", "body_type": "少年", "gender": "男",
                   "weapon": "弓", "quality": "五星金品", "numbering": "00053"},

        "多莉": {"name": "Dori", "country": "须弥", "element": "雷元素", "body_type": "萝莉", "gender": "女",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00054"},
        "多利": {"name": "Dori", "country": "须弥", "element": "雷元素", "body_type": "萝莉", "gender": "女",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00054"},
        "多立": {"name": "Dori", "country": "须弥", "element": "雷元素", "body_type": "萝莉", "gender": "女",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00054"},

        "坎蒂丝": {"name": "Candace", "country": "须弥", "element": "水元素", "body_type": "少女", "gender": "女",
                   "weapon": "长柄", "quality": "四星紫品", "numbering": "00055"},
        "坎迪丝": {"name": "Candace", "country": "须弥", "element": "水元素", "body_type": "少女", "gender": "女",
                   "weapon": "长柄", "quality": "四星紫品", "numbering": "00055"},
        "坎蒂斯": {"name": "Candace", "country": "须弥", "element": "水元素", "body_type": "少女", "gender": "女",
                   "weapon": "长柄", "quality": "四星紫品", "numbering": "00055"},
        "坎迪斯": {"name": "Candace", "country": "须弥", "element": "水元素", "body_type": "少女", "gender": "女",
                   "weapon": "长柄", "quality": "四星紫品", "numbering": "00055"},

        "赛诺": {"name": "Cyno", "country": "须弥", "element": "雷元素", "body_type": "少年", "gender": "男",
                 "weapon": "长柄", "quality": "五星金品", "numbering": "00056"},
        "大风机关": {"name": "Cyno", "country": "须弥", "element": "雷元素", "body_type": "少年", "gender": "男",
                     "weapon": "长柄", "quality": "五星金品", "numbering": "00056"},
        "冷笑话大王": {"name": "Cyno", "country": "须弥", "element": "雷元素", "body_type": "少年", "gender": "男",
                       "weapon": "长柄", "quality": "五星金品", "numbering": "00056"},

        "妮露": {"name": "Nilou", "country": "须弥", "element": "水元素", "body_type": "少女", "gender": "女",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00057"},
        "妮怒": {"name": "Nilou", "country": "须弥", "element": "水元素", "body_type": "少女", "gender": "女",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00057"},

        "纳西妲": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00058"},
        "草神": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉", "gender": "女",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00058"},
        "小草神": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00058"},
        "小慈树王": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00058"},
        "羽毛球": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00058"},
        "大慈树王": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00058"},
        "拉希达": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00058"},
        "拉稀达": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00058"},
        "纳西达": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00058"},
        "布耶尔": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00058"},
        "小吉祥草王": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉", "gender": "女",
                       "weapon": "法器", "quality": "五星金品", "numbering": "00058"},
        "吉祥草王": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00058"},
        "摩诃善法大吉祥智慧主": {"name": "Nahida", "country": "须弥", "element": "草元素", "body_type": "萝莉",
                                 "gender": "女", "weapon": "法器", "quality": "五星金品", "numbering": "00058"},

        "莱依拉": {"name": "Layla", "country": "须弥", "element": "冰元素", "body_type": "少女", "gender": "女",
                   "weapon": "单手剑", "quality": "四星紫品", "numbering": "00059"},
        "来依拉": {"name": "Layla", "country": "须弥", "element": "冰元素", "body_type": "少女", "gender": "女",
                   "weapon": "单手剑", "quality": "四星紫品", "numbering": "00059"},
        "莱依菈": {"name": "Layla", "country": "须弥", "element": "冰元素", "body_type": "少女", "gender": "女",
                   "weapon": "单手剑", "quality": "四星紫品", "numbering": "00059"},
        "来依菈": {"name": "Layla", "country": "须弥", "element": "冰元素", "body_type": "少女", "gender": "女",
                   "weapon": "单手剑", "quality": "四星紫品", "numbering": "00059"},

        "珐露珊": {"name": "Faruzan", "country": "须弥", "element": "风元素", "body_type": "少女", "gender": "女",
                   "weapon": "弓", "quality": "四星紫品", "numbering": "00060"},
        "珐露姗": {"name": "Faruzan", "country": "须弥", "element": "风元素", "body_type": "少女", "gender": "女",
                   "weapon": "弓", "quality": "四星紫品", "numbering": "00060"},
        "前辈": {"name": "Faruzan", "country": "须弥", "element": "风元素", "body_type": "少女", "gender": "女",
                 "weapon": "弓", "quality": "四星紫品", "numbering": "00060"},

        "流浪者": {"name": "Wanderer", "country": "须弥", "element": "风元素", "body_type": "少年", "gender": "男",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00061"},
        "散兵": {"name": "Wanderer", "country": "须弥", "element": "风元素", "body_type": "少年", "gender": "男",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00061"},
        "伞兵": {"name": "Wanderer", "country": "须弥", "element": "风元素", "body_type": "少年", "gender": "男",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00061"},
        "三度背叛": {"name": "Wanderer", "country": "须弥", "element": "风元素", "body_type": "少年", "gender": "男",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00061"},
        "流浪汉": {"name": "Wanderer", "country": "须弥", "element": "风元素", "body_type": "少年", "gender": "男",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00061"},

        "瑶瑶": {"name": "Yaoyao", "country": "璃月", "element": "草元素", "body_type": "萝莉", "gender": "女",
                 "weapon": "长柄", "quality": "四星紫品", "numbering": "00062"},

        "艾尔海森": {"name": "Alhaitham", "country": "须弥", "element": "草元素", "body_type": "成男", "gender": "男",
                     "weapon": "单手剑", "quality": "五星金品", "numbering": "00063"},
        "海森": {"name": "Alhaitham", "country": "须弥", "element": "草元素", "body_type": "成男", "gender": "男",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00063"},

        "迪希雅": {"name": "Dehya", "country": "须弥", "element": "火元素", "body_type": "成女", "gender": "女",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00064"},

        "米卡": {"name": "Mika", "country": "蒙德", "element": "冰元素", "body_type": "少年", "gender": "男",
                 "weapon": "长柄", "quality": "四星紫品", "numbering": "00065"},

        "卡维": {"name": "Kaveh", "country": "须弥", "element": "草元素", "body_type": "成男", "gender": "男",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00066"},

        "白术": {"name": "Baizhu", "country": "璃月", "element": "草元素", "body_type": "成男", "gender": "男",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00067"},

        "绮良良": {"name": "Kirara", "country": "稻妻", "element": "草元素", "body_type": "少女", "gender": "女",
                   "weapon": "单手剑", "quality": "四星紫品", "numbering": "00068"},

        "琳妮特": {"name": "Lynette", "country": "枫丹", "element": "风元素", "body_type": "少女", "gender": "女",
                   "weapon": "单手剑", "quality": "四星紫品", "numbering": "00069"},

        "林尼": {"name": "Lyney", "country": "枫丹", "element": "火元素", "body_type": "少年", "gender": "男",
                 "weapon": "弓", "quality": "五星金品", "numbering": "00070"},

        "菲米尼": {"name": "Freminet", "country": "枫丹", "element": "冰元素", "body_type": "少年", "gender": "男",
                   "weapon": "双手剑", "quality": "四星紫品", "numbering": "00071"},

        "那维莱特": {"name": "Neuvillette", "country": "枫丹", "element": "水元素", "body_type": "成男", "gender": "男",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00072"},
        "水龙王": {"name": "Neuvillette", "country": "枫丹", "element": "水元素", "body_type": "成男", "gender": "男",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00072"},
        "龙王": {"name": "Neuvillette", "country": "枫丹", "element": "水元素", "body_type": "成男", "gender": "男",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00072"},
        "水龙": {"name": "Neuvillette", "country": "枫丹", "element": "水元素", "body_type": "成男", "gender": "男",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00072"},

        "莱欧斯利": {"name": "Wriothesley", "country": "枫丹", "element": "冰元素", "body_type": "成男", "gender": "男",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00073"},
        "典狱长": {"name": "Wriothesley", "country": "枫丹", "element": "冰元素", "body_type": "成男", "gender": "男",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00073"},

        "夏洛蒂": {"name": "Charlotte", "country": "枫丹", "element": "冰元素", "body_type": "少女", "gender": "女",
                   "weapon": "法器", "quality": "四星紫品", "numbering": "00074"},

        "芙宁娜": {"name": "Furina", "country": "枫丹", "element": "水元素", "body_type": "少女", "gender": "女",
                   "weapon": "单手剑", "quality": "五星金品", "numbering": "00075"},
        "水神": {"name": "Furina", "country": "枫丹", "element": "水元素", "body_type": "少女", "gender": "女",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00075"},
        "芙芙": {"name": "Furina", "country": "枫丹", "element": "水元素", "body_type": "少女", "gender": "女",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00075"},
        "小芙芙": {"name": "Furina", "country": "枫丹", "element": "水元素", "body_type": "少女", "gender": "女",
                   "weapon": "单手剑", "quality": "五星金品", "numbering": "00075"},
        "芙卡洛斯": {"name": "Furina", "country": "枫丹", "element": "水元素", "body_type": "少女", "gender": "女",
                     "weapon": "单手剑", "quality": "五星金品", "numbering": "00075"},

        "娜维娅": {"name": "Navia", "country": "枫丹", "element": "岩元素", "body_type": "成女", "gender": "女",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00076"},
        "那维娅": {"name": "Navia", "country": "枫丹", "element": "岩元素", "body_type": "成女", "gender": "女",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00076"},
        "娜维亚": {"name": "Navia", "country": "枫丹", "element": "岩元素", "body_type": "成女", "gender": "女",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00076"},
        "那维亚": {"name": "Navia", "country": "枫丹", "element": "岩元素", "body_type": "成女", "gender": "女",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00076"},
        "纳维娅": {"name": "Navia", "country": "枫丹", "element": "岩元素", "body_type": "成女", "gender": "女",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00076"},
        "纳维亚": {"name": "Navia", "country": "枫丹", "element": "岩元素", "body_type": "成女", "gender": "女",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00076"},

        "夏洛蕾": {"name": "Chevreuse", "country": "枫丹", "element": "火元素", "body_type": "少女", "gender": "女",
                   "weapon": "长柄", "quality": "四星紫品", "numbering": "00077"},

        "嘉明": {"name": "Gaming", "country": "璃月", "element": "火元素", "body_type": "少年", "gender": "男",
                 "weapon": "双手剑", "quality": "四星紫品", "numbering": "00078"},

        "闲云": {"name": "Xianyun", "country": "璃月", "element": "风元素", "body_type": "成女", "gender": "女",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00079"},
        "那个女人": {"name": "Xianyun", "country": "璃月", "element": "风元素", "body_type": "成女", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00079"},

        "千织": {"name": "Chiori", "country": "枫丹", "element": "岩元素", "body_type": "少女", "gender": "女",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00080"},
        "千只": {"name": "Chiori", "country": "枫丹", "element": "岩元素", "body_type": "少女", "gender": "女",
                 "weapon": "单手剑", "quality": "五星金品", "numbering": "00080"},

        "阿蕾奇诺": {"name": "Arlecchino", "country": "枫丹", "element": "火元素", "body_type": "成女", "gender": "女",
                     "weapon": "长柄", "quality": "五星金品", "numbering": "00081"},
        "仆人": {"name": "Arlecchino", "country": "枫丹", "element": "火元素", "body_type": "成女", "gender": "女",
                 "weapon": "长柄", "quality": "五星金品", "numbering": "00081"},
        "佩露薇莉": {"name": "Arlecchino", "country": "枫丹", "element": "火元素", "body_type": "成女", "gender": "女",
                     "weapon": "长柄", "quality": "五星金品", "numbering": "00081"},
        "佩佩": {"name": "Arlecchino", "country": "枫丹", "element": "火元素", "body_type": "成女", "gender": "女",
                 "weapon": "长柄", "quality": "五星金品", "numbering": "00081"},

        "赛索斯": {"name": "Sethos", "country": "须弥", "element": "雷元素", "body_type": "少年", "gender": "男",
                   "weapon": "弓", "quality": "四星紫品", "numbering": "00082"},

        "克洛琳德": {"name": "Clorinde", "country": "枫丹", "element": "雷元素", "body_type": "成女", "gender": "女",
                     "weapon": "单手剑", "quality": "五星金品", "numbering": "00083"},

        "希格雯": {"name": "Sigewinne", "country": "枫丹", "element": "水元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "弓", "quality": "五星金品", "numbering": "00084"},
        "美露莘": {"name": "Sigewinne", "country": "枫丹", "element": "水元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "弓", "quality": "五星金品", "numbering": "00084"},

        "艾梅莉埃": {"name": "Emilie", "country": "枫丹", "element": "草元素", "body_type": "成女", "gender": "女",
                     "weapon": "长柄", "quality": "五星金品", "numbering": "00085"},
        "艾梅利埃": {"name": "Emilie", "country": "枫丹", "element": "草元素", "body_type": "成女", "gender": "女",
                     "weapon": "长柄", "quality": "五星金品", "numbering": "00085"},

        "卡齐娜": {"name": "Kachina", "country": "纳塔", "element": "岩元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "长柄", "quality": "四星紫品", "numbering": "00086"},
        "卡齐那": {"name": "Kachina", "country": "纳塔", "element": "岩元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "长柄", "quality": "四星紫品", "numbering": "00086"},

        "玛拉妮": {"name": "Mualani", "country": "纳塔", "element": "水元素", "body_type": "少女", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00087"},
        "马拉妮": {"name": "Mualani", "country": "纳塔", "element": "水元素", "body_type": "少女", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00087"},

        "基尼齐": {"name": "kinich", "country": "纳塔", "element": "草元素", "body_type": "少年", "gender": "男",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00088"},

        "希诺宁": {"name": "Xilonen", "country": "纳塔", "element": "岩元素", "body_type": "成女", "gender": "女",
                   "weapon": "单手剑", "quality": "五星金品", "numbering": "00089"},

        "欧洛伦": {"name": "Ororon", "country": "纳塔", "element": "雷元素", "body_type": "成男", "gender": "男",
                   "weapon": "弓", "quality": "五星金品", "numbering": "00090"},
        "孙子": {"name": "Ororon", "country": "纳塔", "element": "雷元素", "body_type": "成男", "gender": "男",
                 "weapon": "弓", "quality": "五星金品", "numbering": "00090"},
        "好大孙": {"name": "Ororon", "country": "纳塔", "element": "雷元素", "body_type": "成男", "gender": "男",
                   "weapon": "弓", "quality": "五星金品", "numbering": "00090"},

        "恰斯卡": {"name": "Chasca", "country": "纳塔", "element": "风元素", "body_type": "成女", "gender": "女",
                   "weapon": "弓", "quality": "五星金品", "numbering": "00091"},

        "玛薇卡": {"name": "Mavuika", "country": "纳塔", "element": "火元素", "body_type": "成女", "gender": "女",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00092"},
        "火神": {"name": "Mavuika", "country": "纳塔", "element": "火元素", "body_type": "成女", "gender": "女",
                 "weapon": "双手剑", "quality": "五星金品", "numbering": "00092"},
        "码微卡": {"name": "Mavuika", "country": "纳塔", "element": "火元素", "body_type": "成女", "gender": "女",
                   "weapon": "双手剑", "quality": "五星金品", "numbering": "00092"},

        "西特拉利": {"name": "Citlali", "country": "纳塔", "element": "冰元素", "body_type": "少女", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00093"},
        "茜特拉莉": {"name": "Citlali", "country": "纳塔", "element": "冰元素", "body_type": "少女", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00093"},
        "茜特菈莉": {"name": "Citlali", "country": "纳塔", "element": "冰元素", "body_type": "少女", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00093"},
        "西特菈莉": {"name": "Citlali", "country": "纳塔", "element": "冰元素", "body_type": "少女", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00093"},
        "西特拉莉": {"name": "Citlali", "country": "纳塔", "element": "冰元素", "body_type": "少女", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00093"},
        "茜特拉丽": {"name": "Citlali", "country": "纳塔", "element": "冰元素", "body_type": "少女", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00093"},
        "西特菈丽": {"name": "Citlali", "country": "纳塔", "element": "冰元素", "body_type": "少女", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00093"},
        "西特拉丽": {"name": "Citlali", "country": "纳塔", "element": "冰元素", "body_type": "少女", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00093"},
        "茜特菈丽": {"name": "Citlali", "country": "纳塔", "element": "冰元素", "body_type": "少女", "gender": "女",
                     "weapon": "法器", "quality": "五星金品", "numbering": "00093"},
        "奶奶": {"name": "Citlali", "country": "纳塔", "element": "冰元素", "body_type": "少女", "gender": "女",
                 "weapon": "法器", "quality": "五星金品", "numbering": "00093"},

        "蓝砚": {"name": "Lan+Yan", "country": "璃月", "element": "风元素", "body_type": "少女", "gender": "女",
                 "weapon": "法器", "quality": "四星紫品", "numbering": "00094"},
        "蓝颜": {"name": "Lan+Yan", "country": "璃月", "element": "风元素", "body_type": "少女", "gender": "女",
                 "weapon": "法器", "quality": "四星紫品", "numbering": "00094"},
        "蓝燕": {"name": "Lan+Yan", "country": "璃月", "element": "风元素", "body_type": "少女", "gender": "女",
                 "weapon": "法器", "quality": "四星紫品", "numbering": "00094"},
        "蓝艳": {"name": "Lan+Yan", "country": "璃月", "element": "风元素", "body_type": "少女", "gender": "女",
                 "weapon": "法器", "quality": "四星紫品", "numbering": "00094"},

        "梦见月瑞希": {"name": "Yumemizuki+Mizuki", "country": "稻妻", "element": "风元素", "body_type": "少女",
                       "gender": "女", "weapon": "法器", "quality": "五星金品", "numbering": "00095"},
        "梦见月": {"name": "Yumemizuki+Mizuki", "country": "稻妻", "element": "风元素", "body_type": "少女",
                   "gender": "女", "weapon": "法器", "quality": "五星金品", "numbering": "00095"},
        "稻妻魅魔": {"name": "Yumemizuki+Mizuki", "country": "稻妻", "element": "风元素", "body_type": "少女",
                     "gender": "女", "weapon": "法器", "quality": "五星金品", "numbering": "00095"},
        "食梦嬷": {"name": "Yumemizuki+Mizuki", "country": "稻妻", "element": "风元素", "body_type": "少女",
                   "gender": "女", "weapon": "法器", "quality": "五星金品", "numbering": "00095"},
        "月瑞希": {"name": "Yumemizuki+Mizuki", "country": "稻妻", "element": "风元素", "body_type": "少女",
                   "gender": "女", "weapon": "法器", "quality": "五星金品", "numbering": "00095"},
        "食梦貘": {"name": "Yumemizuki+Mizuki", "country": "稻妻", "element": "风元素", "body_type": "少女",
                   "gender": "女", "weapon": "法器", "quality": "五星金品", "numbering": "00095"},

        "瓦雷莎": {"name": "Varesa", "country": "纳塔", "element": "雷元素", "body_type": "少女", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00096"},
        "瓦蕾莎": {"name": "Varesa", "country": "纳塔", "element": "雷元素", "body_type": "少女", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00096"},
        "瓦蕾沙": {"name": "Varesa", "country": "纳塔", "element": "雷元素", "body_type": "少女", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00096"},
        "瓦雷沙": {"name": "Varesa", "country": "纳塔", "element": "雷元素", "body_type": "少女", "gender": "女",
                   "weapon": "法器", "quality": "五星金品", "numbering": "00096"},

        "伊安珊": {"name": "Iansan", "country": "纳塔", "element": "雷元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "长柄", "quality": "四星紫品", "numbering": "00097"},
        "伊安删": {"name": "Iansan", "country": "纳塔", "element": "雷元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "长柄", "quality": "四星紫品", "numbering": "00097"},
        "伊安姗": {"name": "Iansan", "country": "纳塔", "element": "雷元素", "body_type": "萝莉", "gender": "女",
                   "weapon": "长柄", "quality": "四星紫品", "numbering": "00097"},

        "丝柯克": {"name": "Skirk", "country": "深渊", "element": "冰元素", "body_type": "成女", "gender": "女",
                   "weapon": "单手剑", "quality": "五星金品", "numbering": "00098"},
        "丝科克": {"name": "Skirk", "country": "深渊", "element": "冰元素", "body_type": "成女", "gender": "女",
                   "weapon": "单手剑", "quality": "五星金品", "numbering": "00098"},
        "斯柯克": {"name": "Skirk", "country": "深渊", "element": "冰元素", "body_type": "成女", "gender": "女",
                   "weapon": "单手剑", "quality": "五星金品", "numbering": "00098"},
        "斯科克": {"name": "Skirk", "country": "深渊", "element": "冰元素", "body_type": "成女", "gender": "女",
                   "weapon": "单手剑", "quality": "五星金品", "numbering": "00098"},

        "空": {"name": "Aether", "country": "未知", "element": "全元素", "body_type": "少年", "gender": "男",
               "weapon": "单手剑", "quality": "五星金品", "numbering": "99999"},
        "莹": {"name": "Lumine", "country": "未知", "element": "全元素", "body_type": "少女", "gender": "女",
               "weapon": "单手剑", "quality": "五星金品", "numbering": "99998"},
        "派蒙": {"name": "Paimon", "country": "提瓦特", "element": "未知", "body_type": "未知", "gender": "女",
                 "weapon": "未知", "quality": "未知", "numbering": "99997"},
    }

    # 定义品质颜色映射
    quality_colors = {
        "四星紫品": "\x1b[38;5;135m",  # 紫色
        "五星金品": "\x1b[93m",  # 金色
        "未知": "\x1b[91m",  # 红色
    }

    # 角色编号映射
    numbering_map = {}
    for key, data in translation_map.items():
        if "name" in data and "numbering" in data and "quality" in data:
            if data["numbering"] not in numbering_map:
                numbering_map[data["numbering"]] = {
                    "name": data["name"],
                    "quality": data["quality"]
                }

    # 如果输入的是编号
    if text in numbering_map:
        data = numbering_map[text]
        quality = data["quality"]
        translated_name = data["name"]
        color_code = quality_colors.get(quality, "\x1b[0m")
        # 构建角色名和翻译名时带上颜色
        formatted_role_name = f"{color_code}{text}\x1b[0m"
        formatted_translated_name = f"{color_code}{translated_name}\x1b[0m"
        url = base_url + f"_sSearchString={translated_name}"
        return (formatted_role_name, formatted_translated_name, url, quality)
    # 如果输入的是中文名
    elif text in translation_map:
        data = translation_map[text]
        quality = data["quality"]
        translated_name = data["name"]
        color_code = quality_colors.get(quality, "\x1b[0m")
        formatted_role_name = f"{color_code}{text}\x1b[0m"
        formatted_translated_name = f"{color_code}{translated_name}\x1b[0m"
        url = base_url + f"_sSearchString={translated_name}"
        return (formatted_role_name, formatted_translated_name, url, quality)
    else:
        return None


def create_menus(window):
    # 创建独立按钮
    btn_option1 = tk.Button(window, text="修复Mods以及启动值项", command=lambda: open_repair_window(window))
    btn_option1.place(x=20, y=24, width=150, height=30)

    btn_option2 = tk.Button(window, text="查看我的Mods网址信息", command=lambda: handle_update_urls(window))
    btn_option2.place(x=20, y=64, width=150, height=30)

    btn_option3 = tk.Button(window, text="懒人翻译&快速生成网址", command=lambda: handle_lazy_search(window))
    btn_option3.place(x=20, y=104, width=150, height=30)

    btn_game_settings = tk.Button(window, text="启动游戏以及相关设置", command=lambda: open_game_settings(window))
    btn_game_settings.place(x=20, y=144, width=150, height=30)

    btn_install_mods = tk.Button(window, text="一键安装我的Mods资源",
                                 command=lambda: GIMI_ModInstallation.handle_install_mods(window))
    btn_install_mods.place(x=20, y=184, width=150, height=30)

    btn_custom_install = tk.Button(window, text="自定义Mods资源的安装",
                                   command=lambda: GIMI_ModInstallation.handle_custom_install(window))
    btn_custom_install.place(x=20, y=224, width=150, height=30)

    btn_exit = tk.Button(window, text="退出程序", command=lambda: handle_exit(window))
    btn_exit.place(x=20, y=264, width=150, height=30)

def handle_exit(window):
    confirm_window = tk.Toplevel(window)
    confirm_window.title("")
    confirm_window.geometry("175x90")
    confirm_window.resizable(False, False)

    label = tk.Label(confirm_window, text="请确认是否退出！")
    label.pack(pady=10)

    btn_frame = tk.Frame(confirm_window)
    btn_frame.pack()

    btn_yes = tk.Button(btn_frame, text="确认", command=lambda: exit_program(window, confirm_window))
    btn_yes.pack(side=tk.LEFT, padx=10)

    btn_no = tk.Button(btn_frame, text="取消", command=confirm_window.destroy)
    btn_no.pack(side=tk.RIGHT, padx=10)

    confirm_window.grab_set()


def exit_program(window, confirm_window):
    confirm_window.destroy()
    window.destroy()


def handle_fix_mods(window):
    # 获取程序自身所在路径
    current_dir = get_self_folder_path()
    # 构建修复工具的路径
    fix_tool_path = os.path.join(current_dir, "54FixReleaseVersion.exe")

    # 检查修复工具是否存在
    if not os.path.exists(fix_tool_path):
        # 尝试在 Mod 文件夹下查找
        mod_dir = os.path.join(current_dir, "Mod")
        if os.path.exists(mod_dir):
            fix_tool_path = os.path.join(mod_dir, "54FixReleaseVersion.exe")
        else:
            fix_tool_path = None

    # 如果找到修复工具
    if fix_tool_path and os.path.exists(fix_tool_path):
        try:
            subprocess.run([fix_tool_path], check=True)
            print("")
            print("\x1b[1;96mGIMI·Mod-Manager\x1b[0m:\x1b[4;94m54FixReleaseVersion.exe\x1b[0m的文件修复任务运行已结束")
            print("")
        except subprocess.CalledProcessError as e:
            print(f"运行修复程序时出错:“\x1b[91m{e}\x1b[0m”")
    else:
        print("\x1b[91m修复失败\x1b[0m,相关修复组件或程序已丢失")


def main():
    initialize_db()

    window = tk.Tk()
    window.title('GIMI·Mod-Manager 版本:2.0.27.20250318')
    window.geometry("190x320")

    background_image = load_background_image(window)
    set_background_image(window, background_image)

    if not os.path.exists(txt_file_path):
        with open(txt_file_path, "w", encoding="utf-8") as file:
            default_content = """在生成的文档中添加你的Mods网址以方便长期管理这些↓:
(角色透明材质依赖)更新&下载网址：https://gamebanana.com/mods/485763

(3Dmigoto·GIMI)更新&下载网址：https://gamebanana.com/tools/10093

(模组损坏修复)更新&下载网址：https://gamebanana.com/tools/16084

(UID隐藏)更新&下载网址：https://gamebanana.com/mods/431307

① "Mondstadt"✉

② "Liyue"✉✉

③ "Inazuma"✉✉✉

④ "Sumeru"✉✉✉✉

⑤ "Fontaine"✉✉✉✉✉

⑥ "Natalan"✉✉✉✉✉✉

⑦ "Snezhnaya"✉✉✉✉✉✉✉
"""
            file.write(default_content)
        print(f"1.程序所需({txt_file_path})不存在,程序已默认生成所需文档!")
        print(f"""2.你可以直接编辑({txt_file_path})这个文档以及“添加/修改”你心仪的Mods网址!
""")
    if not os.path.exists(mods_install_path):
        os.makedirs(mods_install_path)
        os.makedirs(os.path.join(mods_install_path, install_folder))
        os.makedirs(os.path.join(mods_install_path, backup_folder))
        print(
            f"1.程序所需资源安装文件夹({mods_install_path})以及子文件({install_folder})+({backup_folder})不存在,程序已默认生成所需文件夹以及子文件夹!")
        print(f"""2.在使用“一键安装我的Mods资源”功能时↓:
请务必将您下载的Mods资源压缩包下载至或移动至({mods_install_path})的子文件夹({install_folder})下,以保证程序以正常的安装流程为您安装Mods资源
""")

    create_menus(window)
    window.mainloop()

# 从XXMI Launcher Config.json文件中读取原神安装路径
def get_genshin_path_from_config():
    try:
        config_path = os.path.join(get_self_folder_path(), "Mod", "XXMI Launcher Config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as file:
                config_data = json.load(file)
                game_folder = config_data["Importers"]["GIMI"]["Importer"]["game_folder"]
                if game_folder:
                    # 将路径中的斜杠替换为反斜杠，并添加YuanShen.exe
                    game_folder = game_folder.replace("/", "\\") + "\\YuanShen.exe"
                    return game_folder
        return None
    except Exception as e:
        print(f"从配置文件读取原神安装路径时出错:“\x1b[91m{e}\x1b[0m”")
        return None

def find_xxmi_launcher():
    try:
        current_dir = get_self_folder_path()
        xxmi_path = os.path.join(current_dir, "Mod", "Resources", "Bin", "XXMI Launcher.exe")
        if os.path.exists(xxmi_path):
            return xxmi_path
        return None
    except Exception as e:
        print(f"查找XXMI Launcher.exe时出错:“\x1b[91m{e}\x1b[0m”")
        return None

# 检查权限并提升
def check_and_elevate_privileges(program_path):
    try:
        subprocess.Popen([program_path], shell=True)
        return True
    except Exception as e:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        response = tk.messagebox.askquestion("权限提升请求",f'启动{os.path.basename(program_path)}程序时出现权限问题,请求权限提升\n1.点击"是"将提升本次操作权限\n2.点击"否"将取消本次运行操作!')
        if response == "yes":
            try:
                subprocess.Popen(["runas", "/user:Administrator", program_path], shell=True)
                return True
            except Exception as e:
                print(f"权限提升失败:“\x1b[91m{e}\x1b[0m”")
                return False
        else:
            print("用户已禁止权限提升请求")
            return False

def open_game_settings(window):
    settings_window = tk.Toplevel(window)
    settings_window.title("启动游戏或路径设置")
    settings_window.geometry("600x220")
    settings_window.resizable(False, False)

    # 获取原神安装路径
    genshin_path = get_game_setting("genshin_path")
    if not genshin_path:
        genshin_path = get_genshin_path_from_config()

    # 原神程序路径输入框
    genshin_path_frame = tk.Frame(settings_window)
    genshin_path_frame.pack(pady=10)

    genshin_path_label = tk.Label(genshin_path_frame, text="请选择原神程序路径:")
    genshin_path_label.pack(side=tk.LEFT)

    genshin_path_var = tk.StringVar()
    if genshin_path:
        genshin_path_var.set(genshin_path)
    else:
        print("\x1b[91m未设置路径或未安装原神\x1b[0m,\x1b[91m请您手动定位到YuanShen.exe的路径\x1b[0m!")
    genshin_path_entry = tk.Entry(genshin_path_frame, textvariable=genshin_path_var, width=50)
    genshin_path_entry.pack(side=tk.LEFT, padx=5)

    def browse_genshin_path():
        path = filedialog.askopenfilename(title="请定位原神程序路径:", filetypes=[("可执行文件", "YuanShen.exe")])
        if path:
            genshin_path_var.set(path)
            save_game_setting("genshin_path", path)
            # 更新配置文件中的game_folder路径
            config_path = os.path.join(get_self_folder_path(), "Mod", "XXMI Launcher Config.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as file:
                    config_data = json.load(file)
                config_data["Importers"]["GIMI"]["Importer"]["game_folder"] = path.replace("\\", "/")  # 保存时使用正斜杠
                with open(config_path, "w", encoding="utf-8") as file:
                    json.dump(config_data, file, indent=4)

    genshin_browse_btn = tk.Button(genshin_path_frame, text="定位路径", command=browse_genshin_path, width=8, height=1)
    genshin_browse_btn.pack(side=tk.LEFT, padx=5)

    # 模组加载器路径输入框
    mod_loader_frame = tk.Frame(settings_window)
    mod_loader_frame.pack(pady=10)

    mod_loader_label = tk.Label(mod_loader_frame, text="原神模组加载器路径:")
    mod_loader_label.pack(side=tk.LEFT)

    mod_loader_var = tk.StringVar()
    mod_loader_path = get_game_setting("mod_loader_path")
    if not mod_loader_path:
        mod_loader_path = find_xxmi_launcher()
        if mod_loader_path:
            save_game_setting("mod_loader_path", mod_loader_path)
    if mod_loader_path:
        mod_loader_var.set(mod_loader_path)
    else:
        mod_loader_var.set("未找到模组加载器XXMI,请手动定位")
    mod_loader_entry = tk.Entry(mod_loader_frame, textvariable=mod_loader_var, width=50)
    mod_loader_entry.pack(side=tk.LEFT, padx=5)

    def browse_mod_loader_path():
        xxmi_path = find_xxmi_launcher()
        if xxmi_path:
            mod_loader_var.set(xxmi_path)
            save_game_setting("mod_loader_path", xxmi_path)
        else:
            path = filedialog.askopenfilename(title="选择原神模组加载器", filetypes=[("可执行文件", "XXMI Launcher.exe")])
            if path:
                mod_loader_var.set(path)
                save_game_setting("mod_loader_path", path)

    mod_loader_browse_btn = tk.Button(mod_loader_frame, text="定位路径", command=browse_mod_loader_path, width=8, height=1)
    mod_loader_browse_btn.pack(side=tk.LEFT, padx=5)

    # Mods资源存放目录
    mods_folder_frame = tk.Frame(settings_window)
    mods_folder_frame.pack(pady=10)

    mods_folder_label = tk.Label(mods_folder_frame, text="Mods资源存放目录:")
    mods_folder_label.pack(side=tk.LEFT)

    mods_folder_var = tk.StringVar()
    mods_folder = os.path.join(get_self_folder_path(), "Mod", "GIMI", "Mods")
    mods_folder_var.set(mods_folder)
    mods_folder_entry = tk.Entry(mods_folder_frame, textvariable=mods_folder_var, width=50)
    mods_folder_entry.pack(side=tk.LEFT, padx=5)

    def open_mods_folder():
        mods_path = mods_folder_var.get()
        if os.path.exists(mods_path):
            os.startfile(mods_path)
        else:
            print("\x1b[91m模组加载器相关文件夹不存在或已丢失\x1b[0m,\x1b[91m请先运行\x1b[94mXXMI\x1b[91m程序修复相关文件\x1b[0m!")

    mods_folder_btn = tk.Button(mods_folder_frame, text="打开目录", command=open_mods_folder, width=8, height=1)
    mods_folder_btn.pack(side=tk.LEFT, padx=5)

    # 按钮框
    btn_frame = tk.Frame(settings_window)
    btn_frame.pack(pady=10)

    def close_settings():
        settings_window.destroy()

    close_btn = tk.Button(btn_frame, text="关闭界面", command=close_settings, width=10, height=1)
    close_btn.pack(side=tk.LEFT, padx=10)

    def start_game():
        mod_loader_path = mod_loader_var.get()

        if not mod_loader_path or mod_loader_path == "未找到模组加载器XXMI,请手动定位":
            print("\x1b[91m出现错误配置\x1b[94mXXMI\x1b[0m,\x1b[91m请检查模组加载器的安装路径是否处于本程序同一目录下\x1b[0m!")
            return

        # 检查是否开启防报错功能
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT setting_value FROM game_settings WHERE setting_name = 'error_prevention'")
        result = cursor.fetchone()
        conn.close()
        if result and result[0] == "on":
            # 如果开启防报错功能，则运行 JianTingYuanShen 模块
            genshin_path = genshin_path_var.get()
            JianTingYuanShen.run_jian_ting_yuan_shen(genshin_path)

        if check_and_elevate_privileges(mod_loader_path):
            print("\x1b[94mXXMI\x1b[0m\x1b[92m预加载成功\x1b[0m")
            # 启动模组加载器后关闭设置界面
            settings_window.destroy()
        else:
            print("\x1b[94mXXMI\x1b[0m\x1b[91m加载出错\x1b[0m")

    start_btn = tk.Button(btn_frame, text="启动XXMI", command=start_game, width=10, height=1)
    start_btn.pack(side=tk.RIGHT, padx=10)

    settings_window.grab_set()

# 新增功能：修复Mods以及启动值项
def open_repair_window(window):
    repair_window = tk.Toplevel(window)
    repair_window.title("选择功能")
    repair_window.geometry("350x125")
    repair_window.resizable(False, False)

    label = tk.Label(repair_window, text="请选择您所需的修复项:")
    label.pack(pady=20)

    def close_repair_window():
        repair_window.destroy()

    def repair_mods():
        close_repair_window()
        handle_fix_mods(window)

    # 获取防报错功能状态
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute("SELECT setting_value FROM game_settings WHERE setting_name = 'error_prevention'")
    result = cursor.fetchone()
    conn.close()
    if result and result[0] == "on":
        btn_text = "关闭防报错"
    else:
        btn_text = "开启防报错"

    btn_frame = tk.Frame(repair_window)
    btn_frame.pack(pady=10)

    repair_mods_btn = tk.Button(btn_frame, text="修复模组资源", command=lambda: repair_mods(), width=12, height=1)
    repair_mods_btn.pack(side=tk.LEFT, padx=10)

    error_prevention_btn = tk.Button(btn_frame, text=btn_text, command=lambda: toggle_error_prevention(window, error_prevention_btn), width=12, height=1)
    error_prevention_btn.pack(side=tk.LEFT, padx=10)

    cancel_btn = tk.Button(btn_frame, text="退出界面", command=close_repair_window, width=10, height=1)
    cancel_btn.pack(side=tk.LEFT, padx=20)

    repair_window.grab_set()

# 切换防报错功能状态
def toggle_error_prevention(window, btn):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute("SELECT setting_value FROM game_settings WHERE setting_name = 'error_prevention'")
    result = cursor.fetchone()
    if result and result[0] == "on":
        # 关闭防报错功能
        cursor.execute("UPDATE game_settings SET setting_value = 'off' WHERE setting_name = 'error_prevention'")
        print("防报错功能现处于关闭状态")
        btn.config(text="开启防报错")
    else:
        # 开启防报错功能
        cursor.execute("INSERT OR REPLACE INTO game_settings (setting_name, setting_value) VALUES ('error_prevention', 'on')")
        print("防报错功能现处于开启状态")
        btn.config(text="关闭防报错")
    conn.commit()
    conn.close()

# 创建快捷方式函数
def create_shortcut_with_args(executable_path, arguments):
    """
    在目标程序所在目录中创建快捷方式并设置目标路径和参数
    :param executable_path: 目标程序的完整路径
    :param arguments: 传递给程序的命令行参数
    """
    # 确保目标路径存在
    if not os.path.exists(executable_path):
        raise FileNotFoundError(f"目标程序路径不存在:{executable_path}")
    # 获取目标程序所在目录
    executable_dir = os.path.dirname(executable_path)
    # 快捷方式保存路径
    shortcut_path = os.path.join(executable_dir, "YuanShen - 快捷方式.lnk")
    # 创建Shell对象
    shell = win32com.client.Dispatch("WScript.Shell")
    # 创建快捷方式
    shortcut = shell.CreateShortcut(shortcut_path)
    # 设置快捷方式的目标路径
    shortcut.Targetpath = executable_path
    # 设置命令行参数
    shortcut.Arguments = arguments

    # 保存快捷方式
    try:
        shortcut.Save()
        print("")
        print(f"1.已创建新修改目标值的快捷方式至\x1b[94m>\x1b[4;97m{shortcut_path}\x1b[0m\n2.\x1b[94mXXMI\x1b[0m启动项值也已成功修改为:\x1b[4;97muse_moblie_platform -iscloud 1 -platform_type CLOUD_THIRD_PARTY_PC\x1b[0m")
    except pywintypes.com_error as e:
        print(f"保存快捷方式时发生错误:“\x1b[91m{e}\x1b[0m”")

if __name__ == "__main__":
    main()