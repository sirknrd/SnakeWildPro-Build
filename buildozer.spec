[app]

# (str) Title of your application
title = Snake Wild Pro

# (str) Package name
package.name = snakewildpro

# (str) Package domain (needed for android/ios packaging)
package.domain = org.conrad

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 0.1

# (list) Application requirements
# NOTA: Usamos pygame y sqlite3 porque tu código es Pygame puro.
requirements = python3==3.10.12,pygame==2.5.2,sqlite3,android

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (int) Target Android API (Actualizado a nivel 34 para 2026)
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) El "traductor" para Pygame (DEBE SER sdl2)
p4a.bootstrap = sdl2

# (str) Las arquitecturas necesarias para que no se cierre (64 y 32 bits)
android.archs = arm64-v8a, armeabi-v7a

# (bool) allow backup support
android.allow_backup = True

# (str) python-for-android branch to use
p4a.branch = master

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
