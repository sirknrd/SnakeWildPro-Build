[app]
title = Snake Wild Pro
package.name = snakewildpro
package.domain = org.conrad
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.4

# REQUERIMIENTOS CRÍTICOS: Cython es el traductor, android es para permisos
requirements = python3==3.10.12,pygame==2.5.2,cython,sqlite3,android

orientation = portrait
fullscreen = 1

# Ajustes para celulares modernos (2026)
android.api = 34
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.copy_libs = 1

# PERMISOS: Sin esto, la app se cierra al intentar crear la DB
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# MOTOR DE JUEGO
p4a.bootstrap = sdl2
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
