
import os
import random
import time
import threading
import json
from datetime import datetime
from pathlib import Path

# Kivy UI
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window

# Android 文件选择和壁纸设置
try:
    from jnius import autoclass, cast
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False

# 配置常量
SCALE_MODES = {
    "适应": {"desc": "保持比例，完整显示"},
    "拉伸": {"desc": "拉伸变形填满屏幕"},
    "填充": {"desc": "保持比例，裁剪边缘填满"},
    "居中": {"desc": "原尺寸居中"},
}

INTERVAL_OPTIONS = [5, 10, 15]
CACHE_SIZE = 5


class WallpaperService:
    """壁纸切换核心服务"""
    def __init__(self):
        self.config_path = self._get_path("config.json")
        self.history_path = self._get_path("history.json")

        self.config = {
            'folder_path': '',
            'interval': 10,
            'cooldown': 15,
            'scale_mode': '适应',
            'play_mode': '随机播放',
            'running': False
        }
        self.play_history = {}
        self.image_list = []

        self._seq_index = 0
        self._shuffled_list = []
        self._shuffle_index = 0
        self._cache = []
        self._cache_lock = threading.Lock()

        self._running = False
        self._thread = None
        self._stop_event = threading.Event()
        self._current_wallpaper = ""

        self.load_config()
        self.load_history()

    def _get_path(self, filename):
        if IS_ANDROID:
            base = primary_external_storage_path()
            folder = os.path.join(base, "WallpaperChanger")
        else:
            folder = os.path.join(os.path.expanduser("~"), "WallpaperChanger")
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, filename)

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config.update(json.load(f))
            except:
                pass

    def save_config(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass

    def load_history(self):
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    self.play_history = json.load(f)
            except:
                pass

    def save_history(self):
        try:
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(self.play_history, f, ensure_ascii=False, indent=2)
        except:
            pass

    def scan_images(self):
        folder = self.config.get('folder_path', '')
        if not folder or not os.path.exists(folder):
            self.image_list = []
            self._shuffled_list = []
            self._seq_index = 0
            self._shuffle_index = 0
            with self._cache_lock:
                self._cache = []
            return []

        patterns = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
        images = []
        for pattern in patterns:
            images.extend(Path(folder).rglob(pattern))

        new_list = sorted([str(p) for p in set(images)])

        if new_list != self.image_list:
            self.image_list = new_list
            self._seq_index = 0
            self._shuffle_index = 0
            with self._cache_lock:
                self._cache = []
            if self.image_list:
                self._shuffled_list = self.image_list.copy()
                random.shuffle(self._shuffled_list)
            else:
                self._shuffled_list = []

        return self.image_list

    def set_wallpaper(self, image_path):
        if not os.path.exists(image_path):
            return False

        if not IS_ANDROID:
            print(f"[模拟] 设置壁纸: {os.path.basename(image_path)}")
            self._current_wallpaper = image_path
            return True

        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            WallpaperManager = autoclass('android.app.WallpaperManager')
            BitmapFactory = autoclass('android.graphics.BitmapFactory')

            activity = PythonActivity.mActivity
            wm = WallpaperManager.getInstance(activity)
            bitmap = BitmapFactory.decodeFile(image_path)

            if bitmap:
                wm.setBitmap(bitmap)
                self._current_wallpaper = image_path
                return True
        except Exception as e:
            print(f"设置壁纸失败: {e}")

        return False

    def _fill_cache(self):
        with self._cache_lock:
            if not self.image_list:
                return

            play_mode = self.config.get('play_mode', '随机播放')
            needed = CACHE_SIZE - len(self._cache)

            if needed <= 0:
                return

            for _ in range(needed):
                if play_mode == '顺序播放':
                    if self._seq_index >= len(self.image_list):
                        self._seq_index = 0
                    img = self.image_list[self._seq_index]
                    self._seq_index += 1
                    self._cache.append(img)

                elif play_mode == '乱序播放':
                    if not self._shuffled_list:
                        self._shuffled_list = self.image_list.copy()
                        random.shuffle(self._shuffled_list)
                        self._shuffle_index = 0

                    if self._shuffle_index >= len(self._shuffled_list):
                        self._shuffled_list = self.image_list.copy()
                        random.shuffle(self._shuffled_list)
                        self._shuffle_index = 0

                    img = self._shuffled_list[self._shuffle_index]
                    self._shuffle_index += 1
                    self._cache.append(img)

                else:  # 随机播放
                    now = time.time()
                    cooldown = self.config['cooldown'] * 60
                    available = [img for img in self.image_list 
                                 if img not in self.play_history or 
                                 (now - self.play_history.get(img, 0) > cooldown)]

                    if not available:
                        available = self.image_list

                    chosen = random.choice(available)
                    self.play_history[chosen] = now
                    self._cache.append(chosen)

            if play_mode == '随机播放':
                self.save_history()

    def get_next_image(self):
        if not self.image_list:
            self.scan_images()

        if not self.image_list:
            return None

        with self._cache_lock:
            cache_empty = len(self._cache) == 0

        if cache_empty:
            self._fill_cache()

        with self._cache_lock:
            if self._cache:
                return self._cache.pop(0)

        # 备用直接获取
        play_mode = self.config.get('play_mode', '随机播放')
        if play_mode == '顺序播放':
            if self._seq_index >= len(self.image_list):
                self._seq_index = 0
            chosen = self.image_list[self._seq_index]
            self._seq_index += 1
            return chosen
        elif play_mode == '乱序播放':
            if not self._shuffled_list or self._shuffle_index >= len(self._shuffled_list):
                self._shuffled_list = self.image_list.copy()
                random.shuffle(self._shuffled_list)
                self._shuffle_index = 0
            chosen = self._shuffled_list[self._shuffle_index]
            self._shuffle_index += 1
            return chosen
        else:
            now = time.time()
            cooldown = self.config['cooldown'] * 60
            available = [img for img in self.image_list 
                         if img not in self.play_history or 
                         (now - self.play_history.get(img, 0) > cooldown)]
            if not available:
                available = self.image_list
            chosen = random.choice(available)
            self.play_history[chosen] = now
            self.save_history()
            return chosen

    def _run_loop(self):
        last_scan = time.time()
        scan_interval = 7200  # 2小时

        while not self._stop_event.is_set():
            if not self._running:
                break

            try:
                now = time.time()
                if now - last_scan >= scan_interval:
                    old = len(self.image_list)
                    self.scan_images()
                    new = len(self.image_list)
                    if new != old:
                        print(f"自动扫描: 图片 {old} → {new}")
                    last_scan = now

                img = self.get_next_image()
                if img:
                    self.set_wallpaper(img)
                    ts = datetime.now().strftime('%H:%M:%S')
                    play = self.config.get('play_mode', '随机播放')
                    with self._cache_lock:
                        cc = len(self._cache)
                    print(f"[{ts}] [{play}] {os.path.basename(img)} [缓存:{cc}]")

                threading.Thread(target=self._fill_cache, daemon=True).start()

                interval = self.config['interval']
                waited = 0.0
                while waited < interval:
                    if self._stop_event.is_set():
                        break
                    time.sleep(0.5)
                    waited += 0.5

            except Exception as e:
                print(f"切换出错: {e}")
                time.sleep(1)

    def start(self):
        if self._running:
            return True

        self.scan_images()
        if not self.image_list:
            return False

        self._fill_cache()
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self.config['running'] = True
        self.save_config()
        return True

    def stop(self):
        self._running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        self._thread = None
        with self._cache_lock:
            self._cache = []
        self.config['running'] = False
        self.save_config()

    def restart(self):
        was = self._running
        self.stop()
        if was:
            time.sleep(0.2)
            self.start()

    def next_wallpaper(self):
        img = self.get_next_image()
        if img:
            self.set_wallpaper(img)
            return img
        return None


class MainLayout(BoxLayout):
    def __init__(self, service, **kwargs):
        super().__init__(**kwargs)
        self.service = service
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10

        # 标题
        self.add_widget(Label(text='壁纸切换器', font_size='24sp', size_hint_y=None, height=50))

        # 文件夹路径
        self.add_widget(Label(text='图片文件夹路径:', size_hint_y=None, height=30))
        self.folder_input = TextInput(
            text=service.config.get('folder_path', ''),
            multiline=False,
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.folder_input)

        # 浏览按钮（安卓上需要权限）
        btn_browse = Button(text='选择文件夹', size_hint_y=None, height=50)
        btn_browse.bind(on_press=self.browse_folder)
        self.add_widget(btn_browse)

        # 图片总数
        self.total_label = Label(
            text=f'图片总数: {len(service.image_list)} 张',
            color=(0.2, 0.4, 1, 1),
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.total_label)

        # 当前壁纸
        self.current_label = Label(
            text='当前壁纸: 未设置',
            color=(0, 0.6, 0, 1),
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.current_label)

        # 缩放模式
        self.add_widget(Label(text='缩放模式:', size_hint_y=None, height=30))
        self.scale_spinner = Spinner(
            text=service.config.get('scale_mode', '适应'),
            values=['适应', '拉伸', '填充', '居中'],
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.scale_spinner)

        # 播放模式
        self.add_widget(Label(text='播放模式:', size_hint_y=None, height=30))
        self.play_spinner = Spinner(
            text=service.config.get('play_mode', '随机播放'),
            values=['随机播放', '顺序播放', '乱序播放'],
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.play_spinner)

        # 切换时间
        self.add_widget(Label(text='切换时间:', size_hint_y=None, height=30))
        self.interval_spinner = Spinner(
            text=str(service.config.get('interval', 10)) + '秒',
            values=['5秒', '10秒', '15秒'],
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.interval_spinner)

        # 冷却时间
        self.add_widget(Label(text='重复冷却(分钟,仅随机):', size_hint_y=None, height=30))
        self.cooldown_input = TextInput(
            text=str(service.config.get('cooldown', 15)),
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.cooldown_input)

        # 状态
        self.status_label = Label(
            text='状态: 已停止',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.status_label)

        # 按钮行
        btn_row = BoxLayout(size_hint_y=None, height=50, spacing=5)

        btn_start = Button(text='开始')
        btn_start.bind(on_press=self.start_service)
        btn_row.add_widget(btn_start)

        btn_stop = Button(text='停止')
        btn_stop.bind(on_press=self.stop_service)
        btn_row.add_widget(btn_stop)

        btn_next = Button(text='立即切换')
        btn_next.bind(on_press=self.next_wallpaper)
        btn_row.add_widget(btn_next)

        self.add_widget(btn_row)

        # 保存提示
        self.hint_label = Label(text='', color=(0, 0.8, 0, 1), size_hint_y=None, height=30)
        self.add_widget(self.hint_label)

        # 定时刷新当前壁纸显示
        Clock.schedule_interval(self.refresh_ui, 2)

    def browse_folder(self, instance):
        if IS_ANDROID:
            # 请求存储权限
            request_permissions([Permission.READ_EXTERNAL_STORAGE])
            # 在安卓上简单使用固定路径或让用户手动输入
            self.show_popup('提示', '安卓版请手动输入图片文件夹路径，例如:
/sdcard/Pictures/Wallpapers')
        else:
            self.show_popup('提示', '桌面版请手动输入路径')

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

    def apply_config(self):
        self.service.config['folder_path'] = self.folder_input.text.strip()
        self.service.config['scale_mode'] = self.scale_spinner.text
        self.service.config['play_mode'] = self.play_spinner.text
        self.service.config['interval'] = int(self.interval_spinner.text.replace('秒', ''))
        try:
            self.service.config['cooldown'] = int(self.cooldown_input.text)
        except:
            pass
        self.service.save_config()
        self.service.scan_images()
        self.total_label.text = f'图片总数: {len(self.service.image_list)} 张'

    def start_service(self, instance):
        self.apply_config()
        if self.service.start():
            self.status_label.text = '状态: 运行中'
            self.hint_label.text = '已开始切换！'
        else:
            self.hint_label.text = '未找到图片！'
        Clock.schedule_once(lambda dt: setattr(self.hint_label, 'text', ''), 2)

    def stop_service(self, instance):
        self.service.stop()
        self.status_label.text = '状态: 已停止'
        self.hint_label.text = '已停止！'
        Clock.schedule_once(lambda dt: setattr(self.hint_label, 'text', ''), 2)

    def next_wallpaper(self, instance):
        self.apply_config()
        img = self.service.next_wallpaper()
        if img:
            self.current_label.text = f'当前壁纸: {os.path.basename(img)}'
            self.hint_label.text = '已切换！'
        else:
            self.hint_label.text = '未找到图片！'
        Clock.schedule_once(lambda dt: setattr(self.hint_label, 'text', ''), 2)

    def refresh_ui(self, dt):
        if self.service._current_wallpaper:
            self.current_label.text = f'当前壁纸: {os.path.basename(self.service._current_wallpaper)}'
        self.status_label.text = f'状态: {"运行中" if self.service._running else "已停止"}'


class WallpaperApp(App):
    def build(self):
        if IS_ANDROID:
            request_permissions([Permission.READ_EXTERNAL_STORAGE])
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        self.service = WallpaperService()
        return MainLayout(self.service)


if __name__ == '__main__':
    WallpaperApp().run()
