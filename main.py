import os
import random
import sqlite3
import sys
import traceback
import math

import pygame

# =========================
# CRASH LOGGER (Android)
# =========================
def _android_private_dir():
    if "ANDROID_ARGUMENT" in os.environ:
        from android.storage import app_storage_path
        return app_storage_path()
    return os.path.dirname(__file__) or "."

def _log_path():
    return os.path.join(_android_private_dir(), "crash.log")

def install_crash_logger():
    def _excepthook(exc_type, exc, tb):
        try:
            with open(_log_path(), "w", encoding="utf-8") as f:
                f.write("".join(traceback.format_exception(exc_type, exc, tb)))
        except Exception:
            pass
        traceback.print_exception(exc_type, exc, tb)
    sys.excepthook = _excepthook

install_crash_logger()

# =========================
# ANDROID HELPERS
# =========================
def get_db_path():
    if "ANDROID_ARGUMENT" in os.environ:
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), "snake_wild_v4.db")
    return "snake_wild_v4.db"

def pedir_permisos():
    try:
        from android.permissions import Permission, request_permissions
        request_permissions([
            Permission.WRITE_EXTERNAL_STORAGE, 
            Permission.READ_EXTERNAL_STORAGE
        ])
    except Exception:
        pass

# =========================
# INIT PYGAME
# =========================
pygame.init()
pedir_permisos()

pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
ANCHO, ALTO = pantalla.get_size()

BLOQUE = 40
reloj = pygame.time.Clock()

# Colores
FONDO_MENU = (20, 25, 30)
ACENTO = (0, 255, 150)
BLANCO = (240, 240, 240)
ROJO = (255, 50, 50)

# Fuentes
fuente_t = pygame.font.SysFont(None, 60, bold=True)
fuente_m = pygame.font.SysFont(None, 32, bold=True)
fuente_p = pygame.font.SysFont(None, 24)

# =========================
# SKINS (4 opciones)
# =========================
SKINS = {
    "Pitón Real": {
        "cabeza": (107, 142, 35), "cuerpo": (85, 107, 47),
        "patron": (139, 69, 19), "fondo": (25, 30, 25), "precio": 0
    },
    "Coral": {
        "cabeza": (20, 20, 20), "cuerpo": (220, 20, 20),
        "patron": (255, 230, 0), "fondo": (35, 20, 20), "precio": 200
    },
    "Mamba Azul": {
        "cabeza": (30, 60, 80), "cuerpo": (50, 80, 110),
        "patron": (100, 150, 200), "fondo": (20, 25, 35), "precio": 500
    },
    "Albina": {
        "cabeza": (255, 240, 230), "cuerpo": (255, 218, 185),
        "patron": (255, 255, 255), "fondo": (40, 35, 30), "precio": 1000
    },
}

# =========================
# DATABASE
# =========================
def db_query(query, params=(), fetch=True, commit=True):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.execute(query, params)
    res = cursor.fetchone() if fetch else None
    if commit:
        conn.commit()
    conn.close()
    return res

def init_db():
    conn = sqlite3.connect(get_db_path())
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY, 
            monedas INTEGER DEFAULT 100, 
            skin_activa TEXT DEFAULT 'Pitón Real'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            usuario_id INTEGER, 
            skin_nombre TEXT, 
            PRIMARY KEY(usuario_id, skin_nombre)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            puntos INTEGER, 
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("INSERT OR IGNORE INTO usuario (id, monedas) VALUES (1, 100)")
    conn.execute("INSERT OR IGNORE INTO inventario (usuario_id, skin_nombre) VALUES (1, 'Pitón Real')")
    conn.commit()
    conn.close()

# =========================
# GAME HELPERS
# =========================
def spawn_comida():
    min_x, max_x = BLOQUE, ANCHO - BLOQUE * 2
    min_y, max_y = BLOQUE * 2, ALTO - BLOQUE * 2
    
    x = round(random.randrange(min_x, max(max_x, min_x+1)) / BLOQUE) * BLOQUE
    y = round(random.randrange(min_y, max(max_y, min_y+1)) / BLOQUE) * BLOQUE
    return x, y

def calcular_direccion(mx, my, dx, dy):
    """Evita giros de 180° - Solo permite perpendicular"""
    if abs(dx) > 0:  # Moviendo horizontal
        if my < ALTO // 2:
            return 0, -BLOQUE  # Arriba
        else:
            return 0, BLOQUE   # Abajo
    else:  # Moviendo vertical
        if mx < ANCHO // 2:
            return -BLOQUE, 0  # Izquierda
        else:
            return BLOQUE, 0   # Derecha

def dibujar_serpiente(pantalla, cuerpo, skin):
    for i, (px, py) in enumerate(cuerpo):
        color = skin["cabeza"] if i == len(cuerpo) - 1 else skin["cuerpo"]
        pygame.draw.rect(pantalla, color, 
                        (px+1, py+1, BLOQUE-2, BLOQUE-2), border_radius=8)

def pausa():
    """Pantalla de pausa"""
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "SALIR"
            if e.type == pygame.MOUSEBUTTONDOWN:
                return "CONTINUAR"

# =========================
# HIGH SCORE SCREEN
# =========================
def pantalla_records(puntos_reciente):
    while True:
        pantalla.fill(FONDO_MENU)
        
        # Título
        titulo = fuente_t.render("HIGH SCORES", True, ACENTO)
        pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 50))
        
        # Top 5
        records = db_query("SELECT puntos FROM records ORDER BY puntos DESC LIMIT 5")
        for i, (puntos) in enumerate(records or []):
            txt = fuente_m.render(f"{i+1}. {puntos}", True, BLANCO)
            pantalla.blit(txt, (ANCHO//2 - 100, 150 + i*50))
        
        # Puntos reciente
        txt_rec = fuente_p.render(f"Tu puntaje: {puntos_reciente}", True, ACENTO)
        pantalla.blit(txt_rec, (ANCHO//2 - txt_rec.get_width()//2, ALTO-200))
        
        # Botón menú
        rect_menu = pygame.Rect(ANCHO//2-120, ALTO-100, 240, 60)
        pygame.draw.rect(pantalla, ACENTO, rect_menu, border_radius=12)
        btn_txt = fuente_m.render("MENÚ", True, FONDO_MENU)
        pantalla.blit(btn_txt, (rect_menu.centerx-btn_txt.get_width()//2, 
                               rect_menu.centery-btn_txt.get_height()//2))
        
        pygame.display.flip()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "SALIR"
            if e.type == pygame.MOUSEBUTTONDOWN:
                if rect_menu.collidepoint(e.pos):
                    return "MENU"

# =========================
# SKINS SHOP
# =========================
def tienda_skins(monedas):
    skins_disponibles = list(SKINS.keys())
    skin_activa = db_query("SELECT skin_activa FROM usuario WHERE id=1")[0]
    while True:
        pantalla.fill(FONDO_MENU)
        
        # Título
        titulo = fuente_t.render("SKINS", True, ACENTO)
        pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, 30))
        
        monedas_txt = fuente_m.render(f"Monedas: {monedas}", True, BLANCO)
        pantalla.blit(monedas_txt, (20, 60))
        
        # Skins grid
        for i, skin_name in enumerate(skins_disponibles):
            x, y = 50 + (i%2)*350, 120 + (i//2)*200
            skin = SKINS[skin_name]
            
            # Preview serpiente pequeña
            preview_cuerpo = [[x+20, y+60], [x+50, y+60], [x+80, y+60]]
            dibujar_serpiente(pantalla, preview_cuerpo, skin)
            
            # Nombre y precio
            pygame.draw.rect(pantalla, skin["cabeza"], 
                           (x, y, 300, 80), border_radius=10, width=3)
            nombre_txt = fuente_m.render(skin_name, True, BLANCO)
            pantalla.blit(nombre_txt, (x+10, y+10))
            
            if skin["precio"] == 0:
                precio_txt = fuente_m.render("GRATIS ✓", True, ACENTO)
            elif skin_name in [row[0] for row in db_query("SELECT skin_nombre FROM inventario WHERE usuario_id=1") or []]:
                precio_txt = fuente_m.render("COMPRADO ✓", True, ACENTO)
            else:
                precio_txt = fuente_m.render(f"{skin['precio']}", True, BLANCO)
            pantalla.blit(precio_txt, (x+10, y+45))
            
            # Activa
            if skin_name == skin_activa:
                pygame.draw.circle(pantalla, ACENTO, (x+280, y+40), 15)
        
        # Botón atrás
        rect_atras = pygame.Rect(ANCHO-150, ALTO-80, 120, 50)
        pygame.draw.rect(pantalla, ACENTO, rect_atras, border_radius=10)
        atras_txt = fuente_m.render("ATRÁS", True, FONDO_MENU)
        pantalla.blit(atras_txt, (rect_atras.centerx-atras_txt.get_width()//2, 
                                 rect_atras.centery-atras_txt.get_height()//2))
        
        pygame.display.flip()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "SALIR"
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                if rect_atras.collidepoint(mx, my):
                    return "MENU"
                # Comprar/equipar skin
                for i, skin_name in enumerate(skins_disponibles):
                    rx, ry = 50 + (i%2)*350, 120 + (i//2)*200
                    if (rx <= mx <= rx+300 and ry <= my <= ry+80):
                        skin = SKINS[skin_name]
                        if skin["precio"] == 0 or skin_name in [row[0] for row in db_query("SELECT skin_nombre FROM inventario WHERE usuario_id=1") or []]:
                            # Equipar
                            db_query("UPDATE usuario SET skin_activa = ? WHERE id=1", (skin_name,))
                            return "MENU"
                        elif monedas >= skin["precio"]:
                            # Comprar
                            db_query("UPDATE usuario SET monedas = monedas - ? WHERE id=1", (skin["precio"],))
                            db_query("INSERT INTO inventario (usuario_id, skin_nombre) VALUES (1, ?)", (skin_name,))
                            return "TIENDA"

# =========================
# JUEGO PRINCIPAL
# =========================
def juego():
    monedas_db, skin_name = db_query("SELECT monedas, skin_activa FROM usuario WHERE id=1")
    skin = SKINS.get(skin_name, SKINS["Pitón Real"])
    
    # Reset serpiente
    x, y, dx, dy = ANCHO//2, ALTO//2, BLOQUE, 0
    cuerpo, largo, puntos = [[x, y]], 3, 0
    cx, cy = spawn_comida()
    velocidad = 10
    pausado = False
    
    while True:
        pantalla.fill(skin["fondo"])
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "SALIR"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_p:
                pausado = not pausado
            if e.type == pygame.MOUSEBUTTONDOWN and not pausado:
                mx, my = e.pos
                dx, dy = calcular_direccion(mx, my, dx, dy)
        
        if pausado:
            pausa()
            continue
        
        # Movimiento
        x += dx
        y += dy
        
        # COLISIONES MEJORADAS
        if (x < 0 or x >= ANCHO or y < 0 or y >= ALTO or 
            any(abs(x-px)<BLOQUE//2 and abs(y-py)<BLOQUE//2 for px,py in cuerpo[:-1])):
            break
        
        # Actualizar cuerpo
        cuerpo.append([x, y])
        if len(cuerpo) > largo:
            del cuerpo[0]
        
        # Comida
        if abs(x - cx) < BLOQUE and abs(y - cy) < BLOQUE:
            puntos += 10
            largo += 1
            cx, cy = spawn_comida()
        
        # VELOCIDAD DINÁMICA
        velocidad = max(8, 10 + (largo - 3) // 3)
        
        # DIBUJAR
        pygame.draw.circle(pantalla, ROJO, (cx + BLOQUE//2, cy + BLOQUE//2), BLOQUE//2)
        dibujar_serpiente(pantalla, cuerpo, skin)
        
        # UI
        puntos_txt = fuente_m.render(f"PUNTOS: {puntos}", True, BLANCO)
        pantalla.blit(puntos_txt, (20, 20))
        
        pygame.display.flip()
        reloj.tick(velocidad)
    
    # Guardar
    db_query("UPDATE usuario SET monedas = monedas + ? WHERE id=1", (puntos,))
    db_query("INSERT INTO records (puntos) VALUES (?)", (puntos,))
    return "RECORDS", puntos

# =========================
# MENÚ PRINCIPAL
# =========================
def menu():
    while True:
        res = db_query("SELECT monedas, skin_activa FROM usuario WHERE id=1")
        monedas, skin_activa = res if res else (0, "Pitón Real")
        skin = SKINS.get(skin_activa, SKINS["Pitón Real"])
        
        pantalla.fill(FONDO_MENU)
        
        # Título
        titulo = fuente_t.render("SNAKE WILD PRO", True, ACENTO)
        pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, ALTO//5))
        
        # Stats
        stats_txt = fuente_m.render(f"Monedas: {monedas} | Skin: {skin_activa}", True, BLANCO)
        pantalla.blit(stats_txt, (ANCHO//2 - stats_txt.get_width()//2, ALTO//5 + 80))
        
        # Botones
        btn_jugar = pygame.Rect(ANCHO//2-160, ALTO//2-20, 320, 70)
        pygame.draw.rect(pantalla, ACENTO, btn_jugar, border_radius=15)
        jugar_txt = fuente_m.render("🎮 JUGAR", True, FONDO_MENU)
        pantalla.blit(jugar_txt, (btn_jugar.centerx-jugar_txt.get_width()//2, 
                                 btn_jugar.centery-jugar_txt.get_height()//2))
        
        btn_tienda = pygame.Rect(ANCHO//2-160, ALTO//2+70, 320, 70)
        pygame.draw.rect(pantalla, (100, 200, 150), btn_tienda, border_radius=15)
        tienda_txt = fuente_m.render("🛒 TIENDA", True, FONDO_MENU)
        pantalla.blit(tienda_txt, (btn_tienda.centerx-tienda_txt.get_width()//2, 
                                  btn_tienda.centery-tienda_txt.get_height()//2))
        
        btn_records = pygame.Rect(ANCHO//2-160, ALTO//2+160, 320, 70)
        pygame.draw.rect(pantalla, (150, 100, 200), btn_records, border_radius=15)
        records_txt = fuente_m.render("🏆 RECORDS", True, FONDO_MENU)
        pantalla.blit(records_txt, (btn_records.centerx-records_txt.get_width()//2, 
                                   btn_records.centery-records_txt.get_height()//2))
        
        pygame.display.flip()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "SALIR"
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_jugar.collidepoint(e.pos):
                    return "JUEGO"
                elif btn_tienda.collidepoint(e.pos):
                    return "TIENDA"
                elif btn_records.collidepoint(e.pos):
                    return "RECORDS_MENU"

# =========================
# MAIN LOOP
# =========================
if __name__ == "__main__":
    try:
        init_db()
        estado = "MENU"
        puntos_reciente = 0
        
        while estado != "SALIR":
            if estado == "MENU":
                estado = menu()
            elif estado == "JUEGO":
                resultado = juego()
                if isinstance(resultado, tuple):
                    estado, puntos_reciente = resultado
                else:
                    estado = resultado
            elif estado == "TIENDA":
                res = db_query("SELECT monedas FROM usuario WHERE id=1")
                monedas = res[0] if res else 0
                estado = tienda_skins(monedas)
            elif estado == "RECORDS":
                estado = pantalla_records(puntos_reciente)
            elif estado == "RECORDS_MENU":
                estado = pantalla_records(0)
                
    finally:
        pygame.quit()
        sys.exit()
