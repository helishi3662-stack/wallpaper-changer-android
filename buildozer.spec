[app]
title = 壁纸切换器
package.name = wallpaperchanger
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,pyjnius,android
orientation = portrait
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,SET_WALLPAPER,INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0