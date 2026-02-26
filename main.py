#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音直播语音助手 - 独立APP版
使用Kivy构建安卓原生界面
"""

import os
import sys
import json
import random
import threading
import time
from datetime import datetime

# Kivy配置
os.environ['KIVY_AUDIO'] = 'android'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from kivy.core.audio import SoundLoader
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
class AudioManager:
    """音频播放管理器"""
    
    def __init__(self, audio_dir):
        self.audio_dir = audio_dir
        self.current_sound = None
        self.volume = 0.8
        
        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(os.path.join(audio_dir, 'hours'), exist_ok=True)
        os.makedirs(os.path.join(audio_dir, 'minutes'), exist_ok=True)
        
    def play_file(self, filename):
        filepath = os.path.join(self.audio_dir, filename)
        if not os.path.exists(filepath):
            print(f"音频不存在: {filepath}")
            return False
            
        try:
            if self.current_sound:
                self.current_sound.stop()
                
            sound = SoundLoader.load(filepath)
            if sound:
                sound.volume = self.volume
                sound.play()
                self.current_sound = sound
                return True
            return False
        except Exception as e:
            print(f"播放错误: {e}")
            return False
    
    def play_sequence(self, files, delay=0.5):
        def play_thread():
            for f in files:
                if self.play_file(f):
                    time.sleep(delay + (self.current_sound.length if self.current_sound else 0))
        threading.Thread(target=play_thread, daemon=True).start()
    
    def stop(self):
        if self.current_sound:
            self.current_sound.stop()
class LiveAssistantCore:
    """直播助手核心逻辑"""
    
    def __init__(self, audio_dir, settings):
        self.audio = AudioManager(audio_dir)
        self.settings = settings
        self.running = False
        self.next_announce = 0
        self.timer_thread = None
        
    def start(self):
        self.running = True
        initial = random.randint(10, 30)
        self.schedule_next(initial)
        print(f"助手已启动，首次播报{initial}秒后")
        
    def stop(self):
        self.running = False
        self.audio.stop()
        
    def schedule_next(self, delay=None):
        if delay is None:
            min_sec = self.settings.get('min_interval', 120)
            max_sec = self.settings.get('max_interval', 300)
            delay = random.randint(min_sec, max_sec)
        self.next_announce = time.time() + delay
        
        if self.timer_thread and self.timer_thread.is_alive():
            return
            
        def timer_loop():
            while self.running:
                remaining = self.next_announce - time.time()
                if remaining <= 0:
                    self.announce_time()
                    self.schedule_next()
                    break
                time.sleep(1)
        
        self.timer_thread = threading.Thread(target=timer_loop, daemon=True)
        self.timer_thread.start()
    
    def announce_time(self):
        now = datetime.now()
        h, m = now.hour, now.minute
        print(f"播报时间: {h:02d}:{m:02d}")
        
        files = ['prefix.mp3', f'hours/{h}.mp3']
        
        if m == 0:
            files.append('minutes/0.mp3')
        elif m == 15:
            files.append('minutes/15.mp3')
        elif m == 30:
            files.append('minutes/30.mp3')
        elif m == 45:
            files.append('minutes/45.mp3')
        else:
            files.append(f'minutes/{m}.mp3')
        
        files.append('suffix.mp3')
        self.audio.play_sequence(files, delay=0.3)
        return f"{h:02d}:{m:02d}"
    
    def play_welcome(self):
        self.audio.play_file('welcome.mp3')
    
    def manual_announce(self):
        return self.announce_time()
class MainWidget(BoxLayout):
    status_text = StringProperty("准备就绪")
    next_time_text = StringProperty("下次播报: --:--")
    volume_value = NumericProperty(0.8)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.app_dir = self.get_app_dir()
        self.audio_dir = os.path.join(self.app_dir, 'audio')
        self.settings = self.load_settings()
        self.assistant = LiveAssistantCore(self.audio_dir, self.settings)
        self.assistant.audio.volume = self.settings.get('volume', 0.8)
        self.build_ui()
        Clock.schedule_interval(self.update_status, 1)
        
    def get_app_dir(self):
        if platform == 'android':
            from android.storage import primary_external_storage_path
            base = primary_external_storage_path()
            app_dir = os.path.join(base, 'LiveAssistant')
        else:
            app_dir = os.path.expanduser('~/LiveAssistant')
        os.makedirs(app_dir, exist_ok=True)
        return app_dir
    
    def load_settings(self):
        config_file = os.path.join(self.app_dir, 'config.json')
        default = {'min_interval': 120, 'max_interval': 300, 'volume': 0.8}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return {**default, **json.load(f)}
            except:
                pass
        return default
    
    def save_settings(self):
        config_file = os.path.join(self.app_dir, 'config.json')
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
    def build_ui(self):
        title = Label(text='直播语音助手', font_size='24sp', size_hint_y=None, height=50)
        self.add_widget(title)
        
        self.status_label = Label(text=self.status_text, font_size='16sp', size_hint_y=None, height=30, color=(0.3, 0.6, 1, 1))
        self.add_widget(self.status_label)
        
        self.next_time_label = Label(text=self.next_time_text, font_size='14sp', size_hint_y=None, height=25)
        self.add_widget(self.next_time_label)
        
        controls = GridLayout(cols=2, spacing=10, size_hint_y=None, height=150)
        
        self.toggle_btn = Button(text='启动助手', font_size='18sp', background_color=(0.2, 0.8, 0.2, 1))
        self.toggle_btn.bind(on_press=self.toggle_assistant)
        controls.add_widget(self.toggle_btn)
        
        announce_btn = Button(text='立即报时', font_size='18sp', background_color=(0.2, 0.6, 1, 1))
        announce_btn.bind(on_press=self.manual_announce)
        controls.add_widget(announce_btn)
        
        welcome_btn = Button(text='播放欢迎语', font_size='18sp', background_color=(1, 0.6, 0.2, 1))
        welcome_btn.bind(on_press=self.play_welcome)
        controls.add_widget(welcome_btn)
        
        audio_btn = Button(text='音频管理', font_size='18sp', background_color=(0.6, 0.4, 0.8, 1))
        audio_btn.bind(on_press=self.open_audio_manager)
        controls.add_widget(audio_btn)
        
        self.add_widget(controls)
        self.build_settings_ui()
    
    def build_settings_ui(self):
        settings_box = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height=200)
        
        vol_box = BoxLayout(size_hint_y=None, height=40)
        vol_box.add_widget(Label(text='音量:', size_hint_x=None, width=60))
        self.volume_slider = Slider(min=0, max=1, value=self.settings['volume'])
        self.volume_slider.bind(value=self.on_volume_change)
        vol_box.add_widget(self.volume_slider)
        self.vol_label = Label(text=f"{int(self.settings['volume']*100)}%", size_hint_x=None, width=50)
        vol_box.add_widget(self.vol_label)
        settings_box.add_widget(vol_box)
        
        interval_box = GridLayout(cols=2, spacing=5, size_hint_y=None, height=80)
        interval_box.add_widget(Label(text='最小间隔(秒):'))
        self.min_input = TextInput(text=str(self.settings['min_interval']), input_filter='int', multiline=False)
        interval_box.add_widget(self.min_input)
        
        interval_box.add_widget(Label(text='最大间隔(秒):'))
        self.max_input = TextInput(text=str(self.settings['max_interval']), input_filter='int', multiline=False)
        interval_box.add_widget(self.max_input)
        settings_box.add_widget(interval_box)
        
        save_btn = Button(text='保存设置', size_hint_y=None, height=40, background_color=(0.4, 0.8, 0.4, 1))
        save_btn.bind(on_press=self.save_interval_settings)
        settings_box.add_widget(save_btn)
        
        self.add_widget(settings_box)
        
        self.audio_status = Label(text=self.check_audio_status(), font_size='12sp', size_hint_y=None, height=100, markup=True)
        self.add_widget(self.audio_status)
        
        help_btn = Button(text='查看录音指导', size_hint_y=None, height=40, background_color=(0.5, 0.5, 0.5, 1))
        help_btn.bind(on_press=self.show_help)
        self.add_widget(help_btn)
    def check_audio_status(self):
        required = ['welcome.mp3', 'prefix.mp3', 'suffix.mp3']
        hours_exist = sum(1 for h in range(24) if os.path.exists(os.path.join(self.audio_dir, 'hours', f'{h}.mp3')))
        status = []
        for f in required:
            exists = os.path.exists(os.path.join(self.audio_dir, f))
            status.append(f'{"✅" if exists else "❌"} {f}')
        status.append(f'⏰ 时间音频: {hours_exist}/24')
        return '\n'.join(status)
    
    def toggle_assistant(self, instance):
        if not self.assistant.running:
            self.save_interval_settings(None)
            self.assistant.start()
            self.status_text = "运行中 - 自动播报已开启"
            self.toggle_btn.text = '停止助手'
            self.toggle_btn.background_color = (0.8, 0.2, 0.2, 1)
        else:
            self.assistant.stop()
            self.status_text = "已停止"
            self.next_time_text = "下次播报: --:--"
            self.toggle_btn.text = '启动助手'
            self.toggle_btn.background_color = (0.2, 0.8, 0.2, 1)
    
    def manual_announce(self, instance):
        if self.assistant.running:
            time_str = self.assistant.manual_announce()
            self.status_text = f"手动播报: {time_str}"
        else:
            self.status_text = "请先启动助手"
    
    def play_welcome(self, instance):
        self.assistant.play_welcome()
        self.status_text = "播放欢迎语"
    
    def on_volume_change(self, instance, value):
        self.volume_value = value
        self.vol_label.text = f"{int(value*100)}%"
        self.assistant.audio.volume = value
        self.settings['volume'] = value
    
    def save_interval_settings(self, instance):
        try:
            min_val = int(self.min_input.text)
            max_val = int(self.max_input.text)
            if min_val < 10 or max_val > 3600:
                self.status_text = "间隔需在10-3600秒之间"
                return
            if min_val >= max_val:
                self.status_text = "最小间隔必须小于最大间隔"
                return
            self.settings['min_interval'] = min_val
            self.settings['max_interval'] = max_val
            self.save_settings()
            self.status_text = f"设置已保存: {min_val}-{max_val}秒"
        except ValueError:
            self.status_text = "请输入有效数字"
    
    def update_status(self, dt):
        self.status_label.text = self.status_text
        if self.assistant.running and self.assistant.next_announce > 0:
            remaining = int(self.assistant.next_announce - time.time())
            if remaining > 0:
                mins, secs = divmod(remaining, 60)
                self.next_time_text = f"下次播报: {mins:02d}:{secs:02d}"
            else:
                self.next_time_text = "正在播报..."
        else:
            self.next_time_text = "下次播报: --:--"
        if int(time.time()) % 10 == 0:
            self.audio_status.text = self.check_audio_status()
    def open_audio_manager(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text=f'音频存放位置:\n{self.audio_dir}', font_size='12sp', halign='center'))
        
        file_chooser = FileChooserListView(path=self.audio_dir, filters=['*.mp3', '*.wav', '*.m4a'])
        content.add_widget(file_chooser)
        
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        play_btn = Button(text='试听')
        play_btn.bind(on_press=lambda x: self.preview_audio(file_chooser.selection))
        btn_box.add_widget(play_btn)
        
        refresh_btn = Button(text='刷新')
        refresh_btn.bind(on_press=lambda x: setattr(file_chooser, 'path', self.audio_dir))
        btn_box.add_widget(refresh_btn)
        
        close_btn = Button(text='关闭')
        btn_box.add_widget(close_btn)
        
        content.add_widget(btn_box)
        
        popup = Popup(title='音频文件管理', content=content, size_hint=(0.9, 0.9))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def preview_audio(self, selection):
        if selection:
            sound = SoundLoader.load(selection[0])
            if sound:
                sound.volume = self.volume_value
                sound.play()
    
    def show_help(self, instance):
        help_text = """录音文件说明

必需文件：
• welcome.mp3 - 欢迎语
• prefix.mp3 - "现在时间是"
• suffix.mp3 - 结束语

时间音频（hours/目录）：
• 0.mp3 到 23.mp3

分钟音频（minutes/目录）：
• 0.mp3, 15.mp3, 30.mp3, 45.mp3

录音建议：
安静环境，手机录音机，MP3格式"""
        
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=help_text, halign='left', valign='top'))
        btn = Button(text='关闭', size_hint_y=None, height=50)
        content.add_widget(btn)
        popup = Popup(title='录音指导', content=content, size_hint=(0.9, 0.8))
        btn.bind(on_press=popup.dismiss)
        popup.open()

class LiveAssistantApp(App):
    def build(self):
        self.title = '直播语音助手'
        return MainWidget()
    
    def on_pause(self):
        return True

if __name__ == '__main__':
    if platform == 'android':
        request_permissions([
            Permission.INTERNET,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.FOREGROUND_SERVICE
        ])
    LiveAssistantApp().run()

