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

# Android 配置 - 修复后的关键部分
android.api = 33
android.minapi = 21
android.ndk = 25b
# 删除 android.sdk（已弃用）
# 关键修复：arch -> archs（复数形式）
android.archs = arm64-v8a
android.allow_backup = True

# 关键添加：指定 Gradle 版本，避免自动下载失败
android.gradle_dependencies = com.android.tools.build:gradle:7.4.2

# 关键添加：指定构建工具版本
android.build_tools = 33.0.0

p4a.local_recipes = 
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png

[buildozer]
log_level = 2
warn_on_root = 1
