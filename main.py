import os
import random
import sqlite3
import sys
import traceback

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
    # En Android guardamos en la carpeta privada de la app
    if "ANDROID_ARGUMENT" in os.environ:
        from android.storage import app_storage_path

        return os.path.join(app_storage_path(), "snake_wild_v4.db")
    return "snake_wild_v4.db"


def pedir_permisos():
    # En Android 14 estos permisos de storage ya no “arreglan” SQLite,
    # pero no rompen si están declarados en buildozer.spec.
    try:
        from android.permissions import Permission, request_permissions

        request_permissions(
            [Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE]
        )
    except Exception:
        pass


# =========================
# INIT PYGAME (ANDROID SAFE)
# =========================
pygame.init()
pedir_permisos()

# En Android (SDL2) es más seguro crear ventana con (0,0) y luego leer tamaño real
pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
ANCHO, ALTO = pantalla.get_size()

BLOQUE = 40
reloj = pygame.time.Clock()

# Estética
FONDO_MENU = (20, 25, 30)
ACENTO = (0, 255, 150)
BLANCO = (240, 240, 240)

# Fuentes más compatibles en Android
fuente_t = pygame.font.SysFont(None, 60, bold=True)
fuente_m = pygame.font.SysFont(None, 30, bold=True)

# --- SKINS ---
SKINS = {
    "Pitón Real": {
        "cabeza": (107, 142, 35),
        "cuerpo": (85, 107, 47),
        "patron": (139, 69, 19),
        "fondo": (25, 30, 25),
        "precio": 0,
    },
    "Coral": {
        "cabeza": (20, 20, 20),
        "cuerpo": (220, 20, 20),
        "patron": (255, 230, 0),
        "fondo": (35, 20, 20),
        "precio": 200,
    },
    "Mamba Azul": {
        "cabeza": (30, 60, 80),
        "cuerpo": (50, 80, 110),
        "patron": (100, 150, 200),
        "fondo": (20, 25, 35),
        "precio": 500,
    },
    "Albina": {
        "cabeza": (255, 240, 230),
        "cuerpo": (255, 218, 185),
        "patron": (255, 255, 255),
        "fondo": (40, 35, 30),
        "precio": 1000,
    },
}


# =========================
# DB
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
    conn.execute(
        "CREATE TABLE IF NOT EXISTS usuario (id INTEGER PRIMARY KEY, monedas INTEGER DEFAULT 100, skin_activa TEXT DEFAULT 'Pitón Real')"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS inventario (usuario_id INTEGER, skin_nombre TEXT, PRIMARY KEY(usuario_id, skin_nombre))"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS records (puntos INTEGER, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.execute("INSERT OR IGNORE INTO usuario (id, monedas) VALUES (1, 100)")
    conn.execute(
        "INSERT OR IGNORE INTO inventario (usuario_id, skin_nombre) VALUES (1, 'Pitón Real')"
    )
    conn.commit()
    conn.close()


# =========================
# GAME HELPERS
# =========================
def spawn_comida():
    # Márgenes para evitar spawns pegados a bordes (y randrange inválido en pantallas raras)
    min_x = BLOQUE
    max_x = ANCHO - BLOQUE * 2
    min_y = BLOQUE * 2
    max_y = ALTO - BLOQUE * 2

    if max_x <= min_x:
        x = BLOQUE
    else:
        x = round(random.randrange(min_x, max_x) / BLOQUE) * BLOQUE

    if max_y <= min_y:
        y = BLOQUE * 2
    else:
        y = round(random.randrange(min_y, max_y) / BLOQUE) * BLOQUE

    return x, y


# =========================
# GAME
# =========================
def juego():
    monedas_db, skin_name = db_query("SELECT monedas, skin_activa FROM usuario WHERE id=1")
    skin = SKINS.get(skin_name, SKINS["Pitón Real"])

    x, y, dx, dy = ANCHO // 2, ALTO // 2, BLOQUE, 0
    cuerpo, largo, puntos = [[x, y]], 3, 0
    cx, cy = spawn_comida()

    while True:
        pantalla.fill(skin["fondo"])

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "SALIR"
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                if my < ALTO // 4 and dy == 0:
                    dx, dy = 0, -BLOQUE  # Arriba
                elif my > (ALTO * 3) // 4 and dy == 0:
                    dx, dy = 0, BLOQUE  # Abajo
                elif mx < ANCHO // 2 and dx == 0:
                    dx, dy = -BLOQUE, 0  # Izquierda
                elif mx >= ANCHO // 2 and dx == 0:
                    dx, dy = BLOQUE, 0  # Derecha

        x += dx
        y += dy

        if x < 0 or x >= ANCHO or y < 0 or y >= ALTO or [x, y] in cuerpo[:-1]:
            break

        cuerpo.append([x, y])
        if len(cuerpo) > largo:
            del cuerpo[0]

        if abs(x - cx) < BLOQUE and abs(y - cy) < BLOQUE:
            puntos += 10
            largo += 1
            cx, cy = spawn_comida()

        pygame.draw.circle(
            pantalla,
            (255, 50, 50),
            (cx + BLOQUE // 2, cy + BLOQUE // 2),
            BLOQUE // 2,
        )

        for i, p in enumerate(cuerpo):
            color = skin["cabeza"] if i == len(cuerpo) - 1 else skin["cuerpo"]
            pygame.draw.rect(
                pantalla,
                color,
                (p[0], p[1], BLOQUE - 2, BLOQUE - 2),
                border_radius=8,
            )

        pygame.display.flip()
        reloj.tick(10)

    db_query("UPDATE usuario SET monedas = monedas + ? WHERE id=1", (puntos,))
    db_query("INSERT INTO records (puntos) VALUES (?)", (puntos,))
    return "MENU"


def menu():
    while True:
        res = db_query("SELECT monedas FROM usuario WHERE id=1")
        monedas = res[0] if res else 0

        pantalla.fill(FONDO_MENU)

        titulo = fuente_t.render("SNAKE WILD", True, ACENTO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, ALTO // 4))

        txt_m = fuente_m.render(f"MONEDAS: {monedas}", True, BLANCO)
        pantalla.blit(txt_m, (ANCHO // 2 - txt_m.get_width() // 2, ALTO // 4 + 100))

        rect_btn = pygame.Rect(ANCHO // 2 - 150, ALTO // 2, 300, 80)
        pygame.draw.rect(pantalla, ACENTO, rect_btn, border_radius=15)
        btn_t = fuente_m.render("TAP TO PLAY", True, FONDO_MENU)
        pantalla.blit(
            btn_t,
            (
                rect_btn.centerx - btn_t.get_width() // 2,
                rect_btn.centery - btn_t.get_height() // 2,
            ),
        )

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "SALIR"
            if e.type == pygame.MOUSEBUTTONDOWN:
                if rect_btn.collidepoint(e.pos):
                    return "JUEGO"


# =========================
# MAIN LOOP
# =========================
if __name__ == "__main__":
    try:
        init_db()
        estado = "MENU"
        while estado != "SALIR":
            if estado == "MENU":
                estado = menu()
            elif estado == "JUEGO":
                estado = juego()
    finally:
        pygame.quit()
