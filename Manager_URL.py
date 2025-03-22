import os
import sys
import configparser
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import webbrowser
import sqlite3
import shutil

class ModManager:
    def __init__(self, root):
        self.root = root
        self.root.title("GIMI·Mod-Manager")
        self.root.geometry("1250x600")

        # 设置路径
        self.base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.mods_path = os.path.join(self.base_path, "Mod", "GIMI", "Mods")
        self.db_path = os.path.join(self.base_path, "GIMI·Mod-Manager_WAY.db")

        # 初始化数据库
        self.initialize_db()

        # 创建UI组件
        self.create_ui()

        # 加载模组信息
        self.load_mods()

    def initialize_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            path TEXT,
            size TEXT,
            description TEXT,
            image_path TEXT
        )
        ''')
        conn.commit()
        conn.close()

    def create_ui(self):
        # 创建左侧模组列表
        self.mod_list_frame = Frame(self.root, width=200, bg="#f0f0f0")
        self.mod_list_frame.pack(side=LEFT, fill=Y)

        # 创建右侧模组详情
        self.mod_detail_frame = Frame(self.root)
        self.mod_detail_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # 创建模组列表标题
        Label(self.mod_list_frame, text="模组列表", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=10)

        # 创建模组列表
        self.mod_listbox = Listbox(self.mod_list_frame, width=30, height=25, font=("Arial", 10))
        self.mod_listbox.pack(padx=10, pady=10, fill=Y)
        self.mod_listbox.bind('<<ListboxSelect>>', self.show_mod_detail)

        # 创建模组详情标题
        Label(self.mod_detail_frame, text="模组详情", font=("Arial", 12, "bold")).pack(anchor=W, padx=10, pady=10)

        # 创建模组详情内容
        self.detail_frame = Frame(self.mod_detail_frame)
        self.detail_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # 创建模组图片展示区域
        self.image_frame = Frame(self.detail_frame, width=300, height=300, bg="#e0e0e0")
        self.image_frame.pack(side=LEFT, padx=10, pady=10)
        self.image_label = Label(self.image_frame, text="模组图片展示区域", width=30, height=15, bg="#e0e0e0")
        self.image_label.pack(fill=BOTH, expand=True)

        # 创建模组信息区域
        self.info_frame = Frame(self.detail_frame)
        self.info_frame.pack(side=RIGHT, fill=Y, padx=10, pady=10)

        # 创建模组名称标签
        self.name_label = Label(self.info_frame, text="模组名称:", font=("Arial", 10, "bold"))
        self.name_label.pack(anchor=W, pady=5)
        self.name_value = Label(self.info_frame, text="")
        self.name_value.pack(anchor=W)

        # 创建模组大小标签
        self.size_label = Label(self.info_frame, text="占用大小:", font=("Arial", 10, "bold"))
        self.size_label.pack(anchor=W, pady=5)
        self.size_value = Label(self.info_frame, text="")
        self.size_value.pack(anchor=W)

        # 创建模组路径标签
        self.path_label = Label(self.info_frame, text="安装路径:", font=("Arial", 10, "bold"))
        self.path_label.pack(anchor=W, pady=5)
        self.path_value = Label(self.info_frame, text="", wraplength=300)
        self.path_value.pack(anchor=W)

        # 创建模组描述标签
        self.desc_label = Label(self.info_frame, text="模组描述:", font=("Arial", 10, "bold"))
        self.desc_label.pack(anchor=W, pady=5)
        self.desc_value = Label(self.info_frame, text="", wraplength=300)
        self.desc_value.pack(anchor=W)

        # 创建操作按钮区域
        self.button_frame = Frame(self.mod_detail_frame)
        self.button_frame.pack(fill=X, padx=10, pady=10)

        # 创建管理按钮
        self.manage_button = Button(self.button_frame, text="管理模组", width=10, command=self.manage_mod)
        self.manage_button.pack(side=LEFT, padx=5)

        # 创建打开文件夹按钮
        self.open_folder_button = Button(self.button_frame, text="打开文件夹", width=10, command=self.open_mod_folder)
        self.open_folder_button.pack(side=LEFT, padx=5)

        # 创建跳转按钮
        self.jump_button = Button(self.button_frame, text="跳转网址", width=10, command=self.jump_to_url)
        self.jump_button.pack(side=LEFT, padx=5)

        # 创建输入框
        self.url_entry = Entry(self.button_frame, width=30)
        self.url_entry.pack(side=LEFT, padx=5, fill=X, expand=True)

    def load_mods(self):
        if not os.path.exists(self.mods_path):
            os.makedirs(self.mods_path)
            return

        # 清空现有列表
        self.mod_listbox.delete(0, END)

        # 遍历Mods文件夹下的所有子文件夹
        mod_folders = [f for f in os.listdir(self.mods_path) if os.path.isdir(os.path.join(self.mods_path, f))]

        for folder in mod_folders:
            mod_path = os.path.join(self.mods_path, folder)
            ini_files = [f for f in os.listdir(mod_path) if f.endswith(".ini")]

            for ini_file in ini_files:
                ini_path = os.path.join(mod_path, ini_file)
                self.parse_ini_file(ini_path)

    def parse_ini_file(self, ini_path):
        config = configparser.ConfigParser()
        config.read(ini_path)

        mod_name = os.path.basename(ini_path).replace(".ini", "")
        mod_folder = os.path.dirname(ini_path)
        mod_description = ""
        mod_image_path = None

        # 尝试从ini文件中读取描述信息
        if "Info" in config.sections() and "Description" in config["Info"]:
            mod_description = config["Info"]["Description"]

        # 尝试查找模组图片
        if "Files" in config.sections() and "PreviewImage" in config["Files"]:
            image_file = config["Files"]["PreviewImage"]
            image_path = os.path.join(mod_folder, image_file)
            if os.path.exists(image_path):
                mod_image_path = image_path

        # 如果没有找到图片，尝试自动查找
        if not mod_image_path:
            image_extensions = [".png", ".jpg", ".jpeg", ".dds"]
            for root, dirs, files in os.walk(mod_folder):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in image_extensions):
                        mod_image_path = os.path.join(root, file)
                        break
                if mod_image_path:
                    break

        # 计算模组大小
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(mod_folder):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)

        # 格式化大小
        size_str = self.format_size(total_size)

        # 存储到数据库
        self.save_mod_to_db(mod_name, mod_folder, size_str, mod_description, mod_image_path)

        # 添加到列表框
        self.mod_listbox.insert(END, mod_name)

    def save_mod_to_db(self, name, path, size, description, image_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO mods (name, path, size, description, image_path)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, path, size, description, image_path))
        conn.commit()
        conn.close()

    def show_mod_detail(self, event):
        # 清空当前详情
        self.name_value.config(text="")
        self.size_value.config(text="")
        self.path_value.config(text="")
        self.desc_value.config(text="")
        self.image_label.config(image='', text="模组图片展示区域")

        # 获取选中的模组
        selection = self.mod_listbox.curselection()
        if not selection:
            return

        mod_name = self.mod_listbox.get(selection[0])

        # 从数据库中获取模组信息
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM mods WHERE name = ?
        ''', (mod_name,))
        mod_info = cursor.fetchone()
        conn.close()

        if mod_info:
            mod_name, mod_path, mod_size, mod_desc, mod_image_path = mod_info[1], mod_info[2], mod_info[3], mod_info[4], mod_info[5]

            # 设置模组名称
            self.name_value.config(text=mod_name)

            # 设置模组大小
            self.size_value.config(text=mod_size)

            # 设置模组路径
            self.path_value.config(text=mod_path)

            # 设置模组描述
            self.desc_value.config(text=mod_desc)

            # 加载模组图片
            if mod_image_path and os.path.exists(mod_image_path):
                try:
                    img = Image.open(mod_image_path)
                    img.thumbnail((200, 200))
                    imgtk = ImageTk.PhotoImage(img)
                    self.image_label.config(image=imgtk)
                    self.image_label.image = imgtk
                except:
                    pass

    def manage_mod(self):
        selection = self.mod_listbox.curselection()
        if not selection:
            return

        mod_name = self.mod_listbox.get(selection[0])
        print(f"管理模组: {mod_name}")

    def open_mod_folder(self):
        selection = self.mod_listbox.curselection()
        if not selection:
            return

        mod_name = self.mod_listbox.get(selection[0])
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT path FROM mods WHERE name = ?
        ''', (mod_name,))
        mod_path = cursor.fetchone()[0]
        conn.close()

        if mod_path and os.path.exists(mod_path):
            os.startfile(mod_path)

    def jump_to_url(self):
        url = self.url_entry.get()
        if url:
            webbrowser.open(url)

    def format_size(self, size_bytes):
        if size_bytes >= 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
        elif size_bytes >= 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes} B"

if __name__ == "__main__":
    root = Tk()
    app = ModManager(root)
    root.mainloop()