[app]
title = 直播语音助手
package.name = liveassistant
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,wav,mp3
version = 1.0.0
requirements = python3,kivy==2.2.1,androidstorage,pyjnius,requests,schedule
orientation = portrait
fullscreen = 0
android.presplash_color = #FFFFFF
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,FOREGROUND_SERVICE,WAKE_LOCK,RECORD_AUDIO

# Android 配置
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True

# 构建工具配置
android.build_tools = 33.0.0

# 关键修复：移除有问题的 Gradle 依赖配置
# android.gradle_dependencies 这行会导致构建失败，已删除

# 关键添加：禁用 p4a 的 setup.py 处理（避免冲突）
p4a.setup_py = False

# 关键添加：确保使用正确的 bootstrap
p4a.bootstrap = sdl2

# 资源文件配置
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
[buildozer]
log_level = 2
warn_on_root = 1
