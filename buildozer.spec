[app]
# NOMBRE EN PLAY STORE
title = Snake Wild Pro

# ID ÚNICO PAQUETE (NO CAMBIES)
package.name = snakewildpro
package.domain = org.conrad

# ARCHIVOS A INCLUIR
source.dir = .
source.include_exts = py,ini,db

# VERSIONES EXACTAS (ESTABLES)
version = 2.0
requirements = python3==3.10.12,pygame==2.5.2,cython

# PANTALLA
orientation = portrait
fullscreen = 1
window.no_border = 1

# ANDROID TARGETS
android.api = 34
android.minapi = 21
android.targetapi = 34
android.archs = arm64-v8a, armeabi-v7a

# SDL2 PYGAME
p4a.bootstrap = sdl2
p4a.branch = master
android.copy_libs = 1
android.enable_androidx = 1

# PERMISOS MÍNIMOS (DB privada)
android.permissions = INTERNET

# ICONOS (opcional)
# icon.filename = icon.png
# presplash.filename = splash.png
# android.presplash_color = #000000

# OPTIMIZACIONES
android.gradle_dependencies = 
android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

[buildozer]
log_level = 2
warn_on_root = 1
