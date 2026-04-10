[app]
title = Snake Wild Pro
package.name = snakewildpro
package.domain = org.conrad
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.4

# Recomendado para p4a/SDL2:
# - sqlite3 ya viene con Python
# - no declares "android" como requirement
requirements = python3==3.10.12,pygame==2.1.3,cython

orientation = portrait
fullscreen = 1

android.api = 34
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.copy_libs = 1

# En Android 14, WRITE/READ_EXTERNAL_STORAGE no aplica como antes.
# Tu DB va en app_storage_path() (privado), así que no requiere permisos.
android.permissions = INTERNET

p4a.bootstrap = sdl2
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
