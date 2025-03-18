import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import py7zr
import rarfile
import lzma
import tarfile
import sys
import send2trash
import winsound  # 用于添加提示音

# 通用安装逻辑
def install_mod(mod_zip_path, target_folder, backup_folder_path, filename):
    # 检查备份文件夹中是否存在同名压缩包
    backup_zip_path = os.path.join(backup_folder_path, filename)
    if os.path.exists(backup_zip_path):
        winsound.Beep(200, 255)  # 添加提示音
        result = messagebox.askyesno("安装提示", f"安装此“{filename}”Mod时在资源备份夹中出现同名压缩包请求指示\n1.点击“是”将移动同名压缩包至回收站以保持继续安装\n2.点击“否”以结束此Mod的相关安装")
        if not result:
            return False
        else:
            try:
                send2trash.send2trash(backup_zip_path)
                print(f"已将同名压缩包“{filename}”移动至回收站")
            except Exception as e:
                print(f"\x1b[91m移动同名压缩包“{filename}”至回收站时出错\x1b[0m,\x1b[91m错误为\x1b[0m:“{e}”")
                return False

    # 检查目标文件夹是否存在同名文件夹
    if os.path.exists(target_folder):
        winsound.Beep(200, 255)  # 添加提示音
        result = messagebox.askyesno("安装提示", f"安装此“{filename}”Mod时在安装路径下存在同名文件夹请求指示\n1.点击“是”将移动同名文件夹至回收站以保持继续安装\n2.点击“否”以结束此Mod的相关安装")
        if not result:
            return False
        else:
            try:
                send2trash.send2trash(target_folder)
                print(f"已将同名文件夹“{os.path.basename(target_folder)}”移动至回收站")
            except Exception as e:
                print(f"\x1b[91m移动同名文件夹“{os.path.basename(target_folder)}”至回收站时出错\x1b[0m,\x1b[91m错误为\x1b[0m:“{e}”")
                return False

    # 解压文件
    try:
        if mod_zip_path.endswith('.zip'):
            with zipfile.ZipFile(mod_zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_folder)
        elif mod_zip_path.endswith('.7z'):
            with py7zr.SevenZipFile(mod_zip_path, 'r') as z:
                z.extractall(target_folder)
        elif mod_zip_path.endswith('.rar'):
            # 使用 rarfile 模块解压 RAR 文件
            with rarfile.RarFile(mod_zip_path, 'r') as rf:
                rf.extractall(target_folder)
        elif mod_zip_path.endswith('.arj') or mod_zip_path.endswith('.lzh'):
            with lzma.open(mod_zip_path, 'rb') as f:
                data = f.read()
            with open(os.path.join(target_folder, filename[:-4]), 'wb') as f:
                f.write(data)
        elif mod_zip_path.endswith(('.tar', '.tar.gz', '.tar.bz2')):
            with tarfile.open(mod_zip_path, 'r:*') as tar_ref:
                tar_ref.extractall(target_folder)
        return True
    except Exception as e:
        print(f"\x1b[91m解压\x1b[0m“{filename}”\x1b[91m时出错\x1b[0m,\x1b[91m错误为\x1b[0m:“{e}”")
        return False

# 一键安装Mods资源
def handle_install_mods(window):
    target_mods_folder = "Mod\\GIMI\\Mods"
    mods_install_path = "Mods资源安装&备份夹"
    install_folder = "1.资源安装夹"
    backup_folder = "2.资源备份夹"

    if not os.path.exists(target_mods_folder):
        print("模组运行程序相关的“\x1b[91mMod\x1b[0m>\x1b[91mGIMI\x1b[0m>\x1b[91mMods\x1b[0m”文件夹不存在本程序同一文件夹下!\n\x1b[91m请检查MOD运行程序\x1b[0m(\x1b[94mXXMI\x1b[0m或\x1b[94m3DMigoto\x1b[0m)\x1b[91m对应存放的文件夹是否处于本程序同一目录下\x1b[0m,\x1b[91m此错误会导致Mods资源无法正常安装\x1b[0m!")
        return

    if not os.path.exists(mods_install_path):
        os.makedirs(mods_install_path)
    if not os.path.exists(os.path.join(mods_install_path, install_folder)):
        os.makedirs(os.path.join(mods_install_path, install_folder))
    if not os.path.exists(os.path.join(mods_install_path, backup_folder)):
        os.makedirs(os.path.join(mods_install_path, backup_folder))

    # 获取当前程序路径
    current_path = os.getcwd()

    # 解压并安装Mods
    install_path = os.path.join(mods_install_path, install_folder)
    backup_path = os.path.join(mods_install_path, backup_folder)
    target_path = os.path.join(current_path, target_mods_folder)

    # 检查是否有压缩包
    if not any(filename.endswith(('.zip', '.7z', '.rar', '.arj', '.lzh', '.tar', '.tar.gz', '.tar.bz2')) for filename in os.listdir(install_path)):
        print(f"此文件夹“{install_folder}”中暂无Mods资源相关的压缩包,请您先获取相关压缩包资源后在来尝试安装吧!")
        return
    # 遍历安装文件夹中的压缩包
    for filename in os.listdir(install_path):
        if filename.endswith(('.zip', '.7z', '.rar', '.arj', '.lzh', '.tar', '.tar.gz', '.tar.bz2')):
            file_path = os.path.join(install_path, filename)
            mod_folder_name = os.path.splitext(filename)[0]  # 使用压缩包名称作为文件夹名称
            mod_folder_path = os.path.join(target_path, mod_folder_name)

            print("————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————")
            print(f"预备解压“{filename}”压缩包并安装至Mods文件夹中············\n开始一键安装Mod后请勿在此时关闭程序,以防止不完整的“{filename}”资源占用您的设备磁盘空间!")

            # 检查并安装
            if install_mod(file_path, mod_folder_path, backup_path, filename):
                # 移动到备份文件夹
                shutil.move(file_path, backup_path)
                print(f"\x1b[1;97;92m成功解压并安装\x1b[0m:“{filename}”\n————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————")
            else:
                print(f"\x1b[91m已取消安装“{filename}”\x1b[0m\n————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————")

# 自定义Mods资源安装
def handle_custom_install(window):
    custom_install_window = tk.Toplevel(window)
    custom_install_window.title("自定义Mods资源安装配置")
    custom_install_window.geometry("600x200")
    custom_install_window.resizable(False, False)

    # 强制聚焦，锁定主窗口
    custom_install_window.grab_set()

    # 输入框和按钮
    mod_zip_path_var = tk.StringVar()
    mod_install_path_var = tk.StringVar()
    mod_folder_name_var = tk.StringVar()

    def select_mod_zip_path():
        file_path = filedialog.askopenfilename(
            filetypes=[("压缩包文件", "*.zip;*.7z;*.rar;*.arj;*.lzh;*.tar;*.tar.gz;*.tar.bz2")])
        mod_zip_path_var.set(file_path)

    def select_mod_install_path():
        folder_path = filedialog.askdirectory()
        mod_install_path_var.set(folder_path)

    tk.Label(custom_install_window, text="解压Mod资源的路径:").place(x=20, y=20)
    tk.Entry(custom_install_window, textvariable=mod_zip_path_var, width=50).place(x=160, y=20)
    tk.Button(custom_install_window, text="添加", command=select_mod_zip_path).place(x=520, y=20, width=32, height=20)

    tk.Label(custom_install_window, text="安装Mod资源的路径:").place(x=20, y=60)
    tk.Entry(custom_install_window, textvariable=mod_install_path_var, width=50).place(x=160, y=60)
    tk.Button(custom_install_window, text="添加", command=select_mod_install_path).place(x=520, y=60, width=32,
                                                                                         height=20)

    tk.Label(custom_install_window, text="安装所存储的文件夹名:").place(x=20, y=100)
    tk.Entry(custom_install_window, textvariable=mod_folder_name_var, width=50).place(x=160, y=100)

    def custom_install():
        mod_zip_path = mod_zip_path_var.get()
        mod_install_path = mod_install_path_var.get()
        mod_folder_name = mod_folder_name_var.get()

        if not mod_zip_path or not mod_install_path:
            print("\x1b[91m请填写完整的路径信息\x1b[0m!")
            return

        # 确定目标文件夹名称
        if mod_folder_name:
            target_folder_name = mod_folder_name
        else:
            target_folder_name = os.path.splitext(os.path.basename(mod_zip_path))[0]

        # 构建目标文件夹路径
        target_folder = os.path.join(mod_install_path, target_folder_name)

        # 检查并安装
        backup_folder_path = os.path.join("Mods资源安装&备份夹", "2.资源备份夹")
        os.makedirs(backup_folder_path, exist_ok=True)

        # 检查备份文件夹中是否存在同名压缩包
        backup_zip_path = os.path.join(backup_folder_path, os.path.basename(mod_zip_path))
        if os.path.exists(backup_zip_path):
            winsound.Beep(200, 255)  # 添加提示音
            result = messagebox.askyesno("安装提示", f"安装此“{os.path.basename(mod_zip_path)}”Mod时在资源备份夹中出现同名压缩包请求指示\n1.点击“是”将移动同名压缩包至回收站以保持继续安装\n2.点击“否”以结束此Mod的相关安装")
            if not result:
                print(f"\x1b[91m已取消安装“{mod_zip_path}”\x1b[0m")
                custom_install_window.destroy()
                return
            else:
                try:
                    send2trash.send2trash(backup_zip_path)
                    print(f"已将同名压缩包“{os.path.basename(mod_zip_path)}”移动至回收站")
                except Exception as e:
                    print(f"\x1b[91m移动同名压缩包“{os.path.basename(mod_zip_path)}”至回收站时出错\x1b[0m,\x1b[91m错误为\x1b[0m:“{e}”")
                    custom_install_window.destroy()
                    return

        # 检查目标文件夹是否存在同名文件夹
        if os.path.exists(target_folder):
            winsound.Beep(200, 255)  # 添加提示音
            result = messagebox.askyesno("安装提示", f"安装此“{os.path.basename(mod_zip_path)}”Mod时在安装路径下存在同名文件夹请求指示\n1.点击“是”将移动同名文件夹至回收站以保持继续安装\n2.点击“否”以结束此Mod的相关安装")
            if not result:
                print(f"\x1b[91m已取消安装“{mod_zip_path}”\x1b[0m")
                custom_install_window.destroy()
                return
            else:
                try:
                    send2trash.send2trash(target_folder)
                    print(f"已将同名文件夹“{target_folder_name}”移动至回收站")
                except Exception as e:
                    print(f"\x1b[91m移动同名文件夹“{target_folder_name}”至回收站时出错\x1b[0m,\x1b[91m错误为\x1b[0m:“{e}”")
                    custom_install_window.destroy()
                    return

        # 解压文件
        try:
            if mod_zip_path.endswith('.zip'):
                with zipfile.ZipFile(mod_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(target_folder)
            elif mod_zip_path.endswith('.7z'):
                with py7zr.SevenZipFile(mod_zip_path, 'r') as z:
                    z.extractall(target_folder)
            elif mod_zip_path.endswith('.rar'):
                # 使用 rarfile 模块解压 RAR 文件
                with rarfile.RarFile(mod_zip_path, 'r') as rf:
                    rf.extractall(target_folder)
            elif mod_zip_path.endswith('.arj') or mod_zip_path.endswith('.lzh'):
                with lzma.open(mod_zip_path, 'rb') as f:
                    data = f.read()
                with open(os.path.join(target_folder, os.path.basename(mod_zip_path)[:-4]), 'wb') as f:
                    f.write(data)
            elif mod_zip_path.endswith(('.tar', '.tar.gz', '.tar.bz2')):
                with tarfile.open(mod_zip_path, 'r:*') as tar_ref:
                    tar_ref.extractall(target_folder)
            print(f"————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————\n\x1b[1;97;92m成功解压并安装\x1b[0m:“{mod_zip_path}”\n————————————————————————————————————————————————————————————————————————————————————————————————————————————————————————")
        except Exception as e:
            print(f"\x1b[91m解压\x1b[0m“{mod_zip_path}”\x1b[91m时出错\x1b[0m,\x1b[91m错误为\x1b[0m:“{e}”")
            custom_install_window.destroy()
            return

        try:
            shutil.move(mod_zip_path, backup_folder_path)
        except Exception as e:
            print(f"\x1b[91m移动压缩包“{mod_zip_path}”至备份文件夹时出错\x1b[0m,\x1b[91m错误为\x1b[0m:“{e}”")

        custom_install_window.destroy()

    tk.Button(custom_install_window, text="取消", command=custom_install_window.destroy).place(x=200, y=140, width=100, height=30)
    tk.Button(custom_install_window, text="确认开始", command=custom_install).place(x=310, y=140, width=100, height=30)