import os
import sqlite3
import shutil
import time
import threading
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def get_base_path():
    if getattr(sys, 'frozen', False):
        # 打包后的程序
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))

class DLLHandler(FileSystemEventHandler):
    def __init__(self, genshin_path):
        self.genshin_path = genshin_path
        # 动态获取模块所在路径，并构建模组目录路径
        base_path = get_base_path()
        self.mod_gimi_dir = os.path.join(base_path, "Mod", "GIMI")
        self.dll_path = os.path.join(self.mod_gimi_dir, "nvapi64.dll")
        self.source_dll = r"C:\Windows\System32\nvapi64.dll"
        self.is_triggered = False

    def on_modified(self, event):
        if event.is_directory:
            return
        if not self.is_triggered:
            try:
                if os.path.exists(self.dll_path):
                    os.remove(self.dll_path)
                    print(f"\x1b[4;94m防15-4001程序\x1b[0m:已删除:{self.dll_path}")
                else:
                    print(f"\x1b[4;94m防15-4001程序\x1b[0m:目标文件不存在:{self.dll_path}")
                if os.path.exists(self.source_dll):
                    shutil.copy2(self.source_dll, self.mod_gimi_dir)
                    print(f"\x1b[4;94m防15-4001程序\x1b[0m:已将{self.source_dll}复制到:{self.mod_gimi_dir}")
                else:
                    print(f"\x1b[4;94m防15-4001程序\x1b[0m:源文件不存在:{self.source_dll}")
                self.is_triggered = True
            except Exception as e:
                print(f"\x1b[4;94m防15-4001程序\x1b[0m:操作\x1b[97mdll\x1b[0m文件时出错:\x1b[91m{e}\x1b[0m")


def start_monitor(genshin_path):
    event_handler = DLLHandler(genshin_path)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(genshin_path), recursive=False)
    observer.start()
    print('\x1b[4;94m防15-4001程序\x1b[0m:等待"YuanShen.exe"的启动············')
    try:
        while True:
            time.sleep(1)
            if event_handler.is_triggered:
                time.sleep(60)
                print(
                    "\x1b[4;94m防15-4001程序\x1b[0m:六十秒等待游戏的启动工作已完成,\x1b[4;94m防15-4001程序\x1b[0m已默认结束进程")
                observer.stop()
                break
    except KeyboardInterrupt:
        observer.stop()
    except Exception as e:
        print(f"\x1b[4;94m防15-4001程序\x1b[0m:监听过程中发生错误:\x1b[91m{e}\x1b[0m")
    finally:
        observer.join()


def run_jian_ting_yuan_shen(genshin_path):
    # 动态获取模块所在路径
    base_path = get_base_path()

    # 获取主脚本的数据库路径
    db_path = os.path.join(base_path, "GIMI·Mod-Manager_WAY.db")

    # 从数据库中获取原神程序路径
    # 这里传递的 genshin_path 参数可以用于覆盖数据库中的路径，或者作为备用
    if genshin_path:
        print("\x1b[4;94m防15-4001程序\x1b[0m:\x1b[92m防报错模块已启用\x1b[0m,\x1b[92m开始工作以及配置相关设置\x1b[0m")
        print(f"\x1b[4;94m防15-4001程序\x1b[0m:使用已有数据库中的原神程序路径{genshin_path}")
    else:
        genshin_path = get_genshin_path_from_db(db_path)
        if not genshin_path:
            print("\x1b[4;94m防15-4001程序\x1b[0m:未找到原神程序路径,请确保数据库中已正确设置")
            return

    # 确保模组目录存在
    mod_gimi_dir = os.path.join(base_path, "Mod", "GIMI")
    if not os.path.exists(mod_gimi_dir):
        try:
            os.makedirs(mod_gimi_dir)
            print(f"\x1b[4;94m防15-4001程序\x1b[0m:已创建模组目录:{mod_gimi_dir}")
        except Exception as e:
            print(f"\x1b[4;94m防15-4001程序\x1b[0m:创建模组目录时出错:\x1b[91m{e}\x1b[0m")
            return

    # 删除模组目录中的 nvapi64.dll 文件
    dll_path = os.path.join(mod_gimi_dir, "nvapi64.dll")
    if os.path.exists(dll_path):
        try:
            os.remove(dll_path)
            print(f"\x1b[4;94m防15-4001程序\x1b[0m:已删除:{dll_path}")
        except Exception as e:
            print(f"\x1b[4;94m防15-4001程序\x1b[0m:删除\x1b[97mdll\x1b[0m文件时出错:\x1b[91m{e}\x1b[0m")
    else:
        print(f"\x1b[4;94m防15-4001程序\x1b[0m:目标\x1b[97mdll\x1b[0m文件不存在:{dll_path}")

    # 启动监听线程
    thread = threading.Thread(target=start_monitor, args=(genshin_path,))
    thread.daemon = True
    thread.start()


def get_genshin_path_from_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT setting_value FROM game_settings WHERE setting_name = 'genshin_path'")
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        print(f"\x1b[4;94m防15-4001程序\x1b[0m:从数据库读取原神路径时出错:\x1b[91m{e}\x1b[0m")
        return None