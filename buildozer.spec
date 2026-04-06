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
requirements = python3,kivy==2.3.0

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (int) Target Android API (Actualizado para 2026)
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Las arquitecturas necesarias para celulares modernos (64 bits) y antiguos (32 bits)
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
