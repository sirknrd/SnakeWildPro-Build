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
# Solo lo esencial para que no de errores de compilación
requirements = python3,kivy

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) The Android arch to build for
android.arch = armeabi-v7a

# (str) python-for-android branch to use
p4a.branch = master

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
