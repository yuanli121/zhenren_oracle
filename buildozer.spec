[app]

title = 贞人占卜·免费版
package.name = zhenren_oracle_free
package.domain = com.zhenren
source.dir = .
source.include_exts = py,kv,png,jpg,ttf,db
version = 1.0.0

requirements = python3,kivy==2.3.1

orientation = portrait
fullscreen = 0
window.clearcolor = 0.07,0.05,0.02,1

android.permissions =
android.api = 33
android.minapi = 26
android.ndk = 25b
android.sdk = 34
android.ndk_api = 26
android.arch = arm64-v8a

android.allow_backup = True
android.presplash_color = #120A04
android.splash_color = #120A04

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

[buildozer]

log_level = 2
warn_on_root = 1
