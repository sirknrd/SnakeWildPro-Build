import pygame
import random
import sqlite3
import sys
import os

# --- CONFIGURACIÓN E INTERFAZ ---
pygame.init()
ANCHO, ALTO = 800, 600
BLOQUE = 20
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Snake Pro: Wild Edition Mobile")
reloj = pygame.time.Clock()

# Colores y Estética
FONDO_MENU = (20, 25, 30)
ACENTO = (0, 255, 150)
BLANCO = (240, 240, 240)
fuente_t = pygame.font.SysFont("Arial", 60, bold=True)
fuente_m = pygame.font.SysFont("Arial", 24, bold=True)

# --- DEFINICIÓN DE SKINS ---
SKINS = {
    "Pitón Real": {"cabeza": (107, 142, 35), "cuerpo": (85, 107, 47), "patron": (139, 69, 19), "fondo": (25, 30, 25), "precio": 0},
    "Coral": {"cabeza": (20, 20, 20), "cuerpo": (220, 20, 20), "patron": (255, 230, 0), "fondo": (35, 20, 20), "precio": 200},
    "Mamba Azul": {"cabeza": (30, 60, 80), "cuerpo": (50, 80, 110), "patron": (100, 150, 200), "fondo": (20, 25, 35), "precio": 500},
    "Albina": {"cabeza": (255, 240, 230), "cuerpo": (255, 218, 185), "patron": (255, 255, 255), "fondo": (40, 35, 30), "precio": 1000}
}

# --- SISTEMA DE PARTÍCULAS ---
class Particula:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx, self.vy = random.uniform(-3, 3), random.uniform(-3, 3)
        self.vida = 255
        self.color = color

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 15
        self.vy += 0.1

    def dibujar(self, superficie):
        if self.vida > 0:
            s = pygame.Surface((4, 4))
            s.set_alpha(self.vida)
            s.fill(self.color)
            superficie.blit(s, (int(self.x), int(self.y)))

# --- RUTA DE BASE DE DATOS (Compatible con Android) ---
def get_db_path():
    # En Android, necesitamos escribir en una carpeta con permisos
    if 'PYTHONPATH' in os.environ: # Detecta si es Android
        from android.storage import app_storage_path
        return os.path.join(app_storage_path(), "data_snake.db")
    return "data_snake.db"

def init_db():
    path = get_db_path()
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE IF NOT EXISTS usuario (id INTEGER PRIMARY KEY, monedas INTEGER DEFAULT 100, skin_activa TEXT DEFAULT 'Pitón Real')")
    conn.execute("CREATE TABLE IF NOT EXISTS inventario (usuario_id INTEGER, skin_nombre TEXT, PRIMARY KEY(usuario_id, skin_nombre))")
    conn.execute("CREATE TABLE IF NOT EXISTS records (puntos INTEGER, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.execute("INSERT OR IGNORE INTO usuario (id, monedas) VALUES (1, 100)")
    conn.execute("INSERT OR IGNORE INTO inventario (usuario_id, skin_nombre) VALUES (1, 'Pitón Real')")
    conn.commit()
    conn.close()

def db_query(query, params=(), fetch=True):
    path = get_db_path()
    conn = sqlite3.connect(path)
    cursor = conn.execute(query, params)
    res = cursor.fetchone() if fetch else None
    conn.commit()
    conn.close()
    return res

# --- COMPONENTES ---
def boton(texto, y, color_base=(45, 50, 65)):
    rect = pygame.Rect(ANCHO//2 - 150, y, 300, 50)
    cursor = pygame.mouse.get_pos()
    color = (70, 75, 90) if rect.collidepoint(cursor) else color_base
    pygame.draw.rect(pantalla, color, rect, border_radius=15)
    pygame.draw.rect(pantalla, ACENTO, rect, 2, border_radius=15)
    txt = fuente_m.render(texto, True, BLANCO)
    pantalla.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
    return rect

def dibujar_serpiente(cuerpo, skin_name):
    s = SKINS[skin_name]
    for i, p in enumerate(cuerpo):
        es_cabeza = (i == len(cuerpo) - 1)
        rect = pygame.Rect(p[0], p[1], BLOQUE - 1, BLOQUE - 1)
        if es_cabeza:
            pygame.draw.rect(pantalla, s["cabeza"], rect, border_radius=10)
            pygame.draw.circle(pantalla, (255, 255, 255), (p[0]+6, p[1]+6), 3)
            pygame.draw.circle(pantalla, (255, 255, 255), (p[0]+14, p[1]+6), 3)
        else:
            color = s["patron"] if i % 3 == 0 else s["cuerpo"]
            pygame.draw.rect(pantalla, color, rect, border_radius=5)

# --- ESTADOS ---
def ver_records():
    while True:
        pantalla.fill(FONDO_MENU)
        pantalla.blit(fuente_t.render("TOP SCORES", True, ACENTO), (ANCHO//2-170, 50))
        conn = sqlite3.connect(get_db_path())
        mejores = conn.execute("SELECT puntos, fecha FROM records ORDER BY puntos DESC LIMIT 5").fetchall()
        conn.close()
        y = 180
        for i, r in enumerate(mejores):
            txt = f"#{i+1} - {r[0]} PTS ({r[1][:10]})"
            pantalla.blit(fuente_m.render(txt, True, BLANCO), (250, y))
            y += 50
        btn_v = boton("VOLVER", 480, (40, 40, 40))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "SALIR"
            if e.type == pygame.MOUSEBUTTONDOWN and btn_v.collidepoint(e.pos): return "MENU"

def tienda():
    while True:
        res_u = db_query("SELECT monedas, skin_activa FROM usuario WHERE id=1")
        monedas, activa = res_u
        conn = sqlite3.connect(get_db_path())
        compradas = [f[0] for f in conn.execute("SELECT skin_nombre FROM inventario WHERE usuario_id=1").fetchall()]
        conn.close()
        pantalla.fill(FONDO_MENU)
        pantalla.blit(fuente_t.render("WILD STORE", True, ACENTO), (ANCHO//2-180, 40))
        y, btns = 140, {}
        for nombre, info in SKINS.items():
            if nombre == activa: txt, col = "[ EQUIPADA ]", (0, 150, 100)
            elif nombre in compradas: txt, col = f"USAR {nombre}", (45, 65, 90)
            else: txt, col = f"{nombre} (${info['precio']})", (60, 45, 45)
            btns[nombre] = boton(txt, y, color_base=col)
            y += 65
        btn_v = boton("VOLVER", 480, (80, 40, 40))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "SALIR"
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btn_v.collidepoint(e.pos): return "MENU"
                for n, b in btns.items():
                    if b.collidepoint(e.pos):
                        if n in compradas: db_query("UPDATE usuario SET skin_activa=? WHERE id=1", (n,), False)
                        elif monedas >= SKINS[n]["precio"]:
                            db_query("UPDATE usuario SET monedas=monedas-?, skin_activa=? WHERE id=1", (SKINS[n]["precio"], n), False)
                            db_query("INSERT INTO inventario VALUES (1, ?)", (n,), False)

def juego():
    res = db_query("SELECT monedas, skin_activa FROM usuario WHERE id=1")
    monedas, skin_name = res
    skin = SKINS[skin_name]
    x, y, dx, dy = ANCHO//2, ALTO//2, BLOQUE, 0
    cuerpo, largo, puntos = [[x, y]], 4, 0
    cx = round(random.randrange(20, ANCHO-20)/BLOQUE)*BLOQUE
    cy = round(random.randrange(80, ALTO-20)/BLOQUE)*BLOQUE
    particulas, bloqueo_dir = [], False

    while True:
        pantalla.fill(skin["fondo"])
        
        # --- CONTROL HÍBRIDO (TECLADO + TOUCH) ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "SALIR"
            
            # Control por teclado
            if e.type == pygame.KEYDOWN and not bloqueo_dir:
                if e.key == pygame.K_UP and dy == 0: dx, dy, bloqueo_dir = 0, -BLOQUE, True
                elif e.key == pygame.K_DOWN and dy == 0: dx, dy, bloqueo_dir = 0, BLOQUE, True
                elif e.key == pygame.K_LEFT and dx == 0: dx, dy, bloqueo_dir = -BLOQUE, 0, True
                elif e.key == pygame.K_RIGHT and dx == 0: dx, dy, bloqueo_dir = BLOQUE, 0, True
            
            # Control por toque (Touch)
            if e.type == pygame.MOUSEBUTTONDOWN and not bloqueo_dir:
                mx, my = e.pos
                # Dividimos la pantalla en zonas para girar
                if my < ALTO // 4: # Arriba
                    if dy == 0: dx, dy, bloqueo_dir = 0, -BLOQUE, True
                elif my > (ALTO // 4) * 3: # Abajo
                    if dy == 0: dx, dy, bloqueo_dir = 0, BLOQUE, True
                elif mx < ANCHO // 2: # Izquierda
                    if dx == 0: dx, dy, bloqueo_dir = -BLOQUE, 0, True
                else: # Derecha
                    if dx == 0: dx, dy, bloqueo_dir = BLOQUE, 0, True

        x, y = x + dx, y + dy
        if x<0 or x>=ANCHO or y<0 or y>=ALTO or [x,y] in cuerpo[:-1]: break
        cuerpo.append([x,y])
        if len(cuerpo) > largo: del cuerpo[0]

        if x == cx and y == cy:
            puntos += 10; largo += 1
            for _ in range(15): particulas.append(Particula(cx+10, cy+10, (50, 255, 50)))
            cx = round(random.randrange(20, ANCHO-20)/BLOQUE)*BLOQUE
            cy = round(random.randrange(80, ALTO-20)/BLOQUE)*BLOQUE

        pygame.draw.circle(pantalla, (255, 50, 50), (cx+10, cy+10), 10)
        for p in particulas[:]:
            p.actualizar(); p.dibujar(pantalla)
            if p.vida <= 0: particulas.remove(p)

        dibujar_serpiente(cuerpo, skin_name)
        pantalla.blit(fuente_m.render(f"PUNTOS: {puntos}", True, BLANCO), (20, 20))
        pygame.display.flip()
        reloj.tick(12 + (puntos // 50))
        bloqueo_dir = False

    if puntos > 0: db_query("INSERT INTO records (puntos) VALUES (?)", (puntos,), False)
    db_query("UPDATE usuario SET monedas = monedas + ? WHERE id=1", (puntos,), False)
    return "MENU"

def menu():
    while True:
        res = db_query("SELECT monedas, skin_activa FROM usuario WHERE id=1")
        monedas = res[0]
        pantalla.fill(FONDO_MENU)
        pantalla.blit(fuente_t.render("SNAKE WILD", True, ACENTO), (ANCHO//2-180, 80))
        pantalla.blit(fuente_m.render(f"MONEDAS: {monedas}", True, (200, 200, 200)), (ANCHO//2-80, 180))
        b_j, b_t, b_r, b_s = boton("JUGAR", 250), boton("TIENDA", 320), boton("RECORDS", 390), boton("SALIR", 460)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "SALIR"
            if e.type == pygame.MOUSEBUTTONDOWN:
                if b_j.collidepoint(e.pos): return "JUEGO"
                if b_t.collidepoint(e.pos): return "TIENDA"
                if b_r.collidepoint(e.pos): return "RECORDS"
                if b_s.collidepoint(e.pos): return "SALIR"

# --- BUCLE PRINCIPAL ---
init_db()
estado = "MENU"
while estado != "SALIR":
    if estado == "MENU": estado = menu()
    elif estado == "TIENDA": estado = tienda()
    elif estado == "JUEGO": estado = juego()
    elif estado == "RECORDS": estado = ver_records()
pygame.quit()