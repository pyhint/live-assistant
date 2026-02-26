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
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.arch = arm64-v8a
android.allow_backup = True
p4a.local_recipes = 
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
orientation = portrait
[buildozer]
log_level = 2
warn_on_root = 1
