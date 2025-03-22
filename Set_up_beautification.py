# Set_up_beautification.py
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import sqlite3
import win32com.client
import pywintypes
import winsound  # 用于播放错误提示音


# 初始化数据库连接
def init_db():
    conn = sqlite3.connect("GIMI·Mod-Manager_WAY.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_name TEXT UNIQUE,
        setting_value TEXT
    )
    """)
    conn.commit()
    conn.close()


# 获取程序自身所在路径
def get_self_folder_path():
    return os.path.dirname(os.path.abspath(sys.argv[0]))


# 保存设置到数据库
def save_setting(setting_name, setting_value):
    conn = sqlite3.connect("GIMI·Mod-Manager_WAY.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO game_settings (setting_name, setting_value)
    VALUES (?, ?)
    """, (setting_name, setting_value))
    conn.commit()
    conn.close()


# 获取设置从数据库
def get_setting(setting_name):
    conn = sqlite3.connect("GIMI·Mod-Manager_WAY.db")
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


# 获取3DMigoto.dll默认路径
def get_default_3dmigoto_path():
    current_dir = get_self_folder_path()
    default_path = os.path.join(current_dir, "Mod", "GIMI", "nvapi64.dll")
    if os.path.exists(default_path):
        return default_path
    return None


# 获取NVIDIA.dll默认路径
def get_default_nvidia_path():
    default_path = r"C:\Windows\System32\nvapi64.dll"
    if os.path.exists(default_path):
        return default_path
    return None


# 打开文件选择对话框选择nvapi64.dll
def select_nvapi64_file():
    file_path = filedialog.askopenfilename(
        title="选择nvapi64.dll文件",
        filetypes=[("DLL文件", "nvapi64.dll")]
    )
    return file_path

def handle_fix_mods(window):
    # 获取程序自身所在路径
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
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
        print(f"\x1b[92m修复工具正确存在于\x1b[0m:\x1b[4;97m{fix_tool_path}\x1b[0m\x1b[92m路径下\x1b[0m!")
        try:
            # 运行修复工具
            result = subprocess.run([fix_tool_path], check=True, capture_output=True, text=True)
            # 捕获标准输出和错误输出
            print("\x1b[92m修复程序运行成功\x1b[0m")
            if result.stdout:
                print("修复程序输出:")
                print(result.stdout)
            if result.stderr:
                print("修复程序错误输出:")
                print(result.stderr)
            print("\x1b[92m第三方程序的模组修复工作以完成\x1b[0m!")
        except subprocess.CalledProcessError as e:
            print(f"运行修复程序时出错:\x1b[91m{e}\x1b[0m")
            if e.stdout:
                print("修复程序输出:")
                print(e.stdout)
            if e.stderr:
                print("修复程序错误输出:")
                print(e.stderr)
    else:
        print("\x1b[91m修复失败\x1b[0m,未找到相关修复所需程序")

# 打开修复窗口
def open_repair_window(window):
    repair_window = tk.Toplevel(window)
    repair_window.title("修复Mod或设置程序")
    repair_window.geometry("500x255")
    repair_window.resizable(False, False)

    # 设置3DMigoto.dll路径
    tk.Label(repair_window, text="设置3DMigoto.dll路径:").pack(anchor=tk.W, padx=10, pady=5)

    default_3dmigoto_path = get_default_3dmigoto_path()
    saved_3dmigoto_path = get_setting("3dmigoto_path")

    path_frame_3dmigoto = tk.Frame(repair_window)
    path_frame_3dmigoto.pack(fill=tk.X, padx=10, pady=5)

    if saved_3dmigoto_path:
        path_var_3dmigoto = tk.StringVar(value=saved_3dmigoto_path)
    elif default_3dmigoto_path:
        path_var_3dmigoto = tk.StringVar(value=default_3dmigoto_path)
    else:
        path_var_3dmigoto = tk.StringVar(value="路径丢失,您未按正确方式安装,或需手动配置路径!")

    path_entry_3dmigoto = tk.Entry(path_frame_3dmigoto, textvariable=path_var_3dmigoto,
                                   state='readonly' if not default_3dmigoto_path else 'normal')
    path_entry_3dmigoto.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def update_3dmigoto_path():
        new_path = select_nvapi64_file()
        if new_path:
            save_setting("3dmigoto_path", new_path)
            path_var_3dmigoto.set(new_path)

    btn_modify_3dmigoto = tk.Button(path_frame_3dmigoto, text="修改", command=update_3dmigoto_path)
    btn_modify_3dmigoto.pack(side=tk.RIGHT, padx=5)

    # 设置NVIDIA.dll路径
    tk.Label(repair_window, text="设置NVIDIA.dll路径:").pack(anchor=tk.W, padx=10, pady=5)

    default_nvidia_path = get_default_nvidia_path()
    saved_nvidia_path = get_setting("nvidia_path")

    path_frame_nvidia = tk.Frame(repair_window)
    path_frame_nvidia.pack(fill=tk.X, padx=10, pady=5)

    if saved_nvidia_path:
        path_var_nvidia = tk.StringVar(value=saved_nvidia_path)
    elif default_nvidia_path:
        path_var_nvidia = tk.StringVar(value=default_nvidia_path)
    else:
        path_var_nvidia = tk.StringVar(value="未找到默认路径")

    path_entry_nvidia = tk.Entry(path_frame_nvidia, textvariable=path_var_nvidia,
                                 state='readonly' if not default_nvidia_path else 'normal')
    path_entry_nvidia.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def update_nvidia_path():
        new_path = select_nvapi64_file()
        if new_path:
            save_setting("nvidia_path", new_path)
            path_var_nvidia.set(new_path)

    btn_modify_nvidia = tk.Button(path_frame_nvidia, text="修改", command=update_nvidia_path)
    btn_modify_nvidia.pack(side=tk.RIGHT, padx=5)

    # 按钮框
    btn_frame = tk.Frame(repair_window)
    btn_frame.pack(pady=10)

    # 修复Mod按钮
    def repair_mods():
        handle_fix_mods(window)

    repair_mods_btn = tk.Button(btn_frame, text="修复模组资源", command=repair_mods, width=12, height=1)
    repair_mods_btn.pack(side=tk.LEFT, padx=5)

    # 防报错功能
    def toggle_error_prevention(btn):
        conn = sqlite3.connect("GIMI·Mod-Manager_WAY.db")
        cursor = conn.cursor()
        cursor.execute("SELECT setting_value FROM game_settings WHERE setting_name = 'error_prevention'")
        result = cursor.fetchone()
        if result and result[0] == "on":
            cursor.execute("UPDATE game_settings SET setting_value = 'off' WHERE setting_name = 'error_prevention'")
            print("\x1b[91m防报错功能现处于关闭状态\x1b[0m")
            btn.config(text="开启防报错")
        else:
            cursor.execute(
                "INSERT OR REPLACE INTO game_settings (setting_name, setting_value) VALUES ('error_prevention', 'on')")
            print("\x1b[92m防报错功能现处于开启状态\x1b[0m")
            btn.config(text="关闭防报错")
        conn.commit()
        conn.close()

    # 获取防报错功能状态
    conn = sqlite3.connect("GIMI·Mod-Manager_WAY.db")
    cursor = conn.cursor()
    cursor.execute("SELECT setting_value FROM game_settings WHERE setting_name = 'error_prevention'")
    result = cursor.fetchone()
    conn.close()
    if result and result[0] == "on":
        btn_text = "关闭防报错"
    else:
        btn_text = "开启防报错"

    error_prevention_btn = tk.Button(btn_frame, text=btn_text,
                                     command=lambda: toggle_error_prevention(error_prevention_btn), width=12, height=1)
    error_prevention_btn.pack(side=tk.LEFT, padx=5)

    # 更换背景美化按钮
    def change_background():
        current_background = get_setting("background")
        if current_background == "Furina":
            save_setting("background", "Citlali")
            print("\x1b[4;97m背景美化已切换为\x1b[0m > \x1b[95m茜特拉莉\x1b[0m")
        else:
            save_setting("background", "Furina")
            print("\x1b[4;97m背景美化已切换为\x1b[0m > \x1b[94m芙宁娜\x1b[0m")
        # 播放错误提示音
        try:
            # 尝试播放 Windows 错误提示音
            winsound.MessageBeep(winsound.MB_ICONHAND)
        except:
            # 如果上述方法失败，使用备用频率和时长
            winsound.Beep(750, 300)
        # 显示提示框
        response = messagebox.showinfo("提示", "成功切换背景美化方案 // 以重启程序才可生效!", parent=repair_window)
        if response == "ok":
            repair_window.destroy()
        else:
            repair_window.destroy()

    background_btn = tk.Button(btn_frame, text="更换背景美化", command=change_background, width=12, height=1)
    background_btn.pack(side=tk.LEFT, padx=5)

    # 退出界面按钮
    cancel_btn = tk.Button(repair_window, text="关闭界面", command=repair_window.destroy, width=10, height=1)
    cancel_btn.pack(pady=10)

    repair_window.grab_set()


# 初始化数据库
init_db()