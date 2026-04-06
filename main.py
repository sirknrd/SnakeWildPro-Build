import pygame
import random
import sqlite3
import os

# --- COMPATIBILIDAD ANDROID (CRÍTICO) ---
def get_db_path():
    # En Android, escribimos en la carpeta de datos privados de la app
    try:
        from android.storage import app_storage_path
        base_path = app_storage_path()
    except ImportError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, "data_snake_v2.db")

# --- CONFIGURACIÓN ---
pygame.init()
# Para móviles, es mejor detectar la resolución real o usar una fija escalable
ANCHO, ALTO = 800, 600 
pantalla = pygame.display.set_mode((ANCHO, ALTO))
reloj = pygame.time.Clock()

# Colores
FONDO_MENU = (20, 25, 30)
ACENTO = (0, 255, 150)
BLANCO = (240, 240, 240)

# Fuentes (Usamos SysFont para evitar errores si no encuentra el archivo .ttf)
fuente_t = pygame.font.SysFont("sans-serif", 60, bold=True)
fuente_m = pygame.font.SysFont("sans-serif", 24, bold=True)

# --- SKINS ---
SKINS = {
    "Pitón Real": {"cabeza": (107, 142, 35), "cuerpo": (85, 107, 47), "patron": (139, 69, 19), "fondo": (25, 30, 25), "precio": 0},
    "Coral": {"cabeza": (20, 20, 20), "cuerpo": (220, 20, 20), "patron": (255, 230, 0), "fondo": (35, 20, 20), "precio": 200},
    "Mamba Azul": {"cabeza": (30, 60, 80), "cuerpo": (50, 80, 110), "patron": (100, 150, 200), "fondo": (20, 25, 35), "precio": 500},
    "Albina": {"cabeza": (255, 240, 230), "cuerpo": (255, 218, 185), "patron": (255, 255, 255), "fondo": (40, 35, 30), "precio": 1000}
}

BLOQUE = 20

# --- DB MANAGER ---
def db_query(query, params=(), fetch=True, commit=True):
    path = get_db_path()
    conn = sqlite3.connect(path)
    cursor = conn.execute(query, params)
    res = cursor.fetchone() if fetch else None
    if commit: conn.commit()
    conn.close()
    return res

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

# --- CLASES ---
class Particula:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx, self.vy = random.uniform(-3, 3), random.uniform(-3, 3)
        self.vida = 255
        self.color = color
    def actualizar(self):
        self.x += self.vx; self.y += self.vy; self.vida -= 15
    def dibujar(self, superficie):
        if self.vida > 0:
            s = pygame.Surface((4, 4))
            s.set_alpha(self.vida); s.fill(self.color)
            superficie.blit(s, (int(self.x), int(self.y)))

# --- MOTOR DE JUEGO ---
def dibujar_serpiente(cuerpo, skin_name):
    s = SKINS[skin_name]
    for i, p in enumerate(cuerpo):
        rect = pygame.Rect(p[0], p[1], BLOQUE - 1, BLOQUE - 1)
        color = s["cabeza"] if i == len(cuerpo)-1 else (s["patron"] if i % 3 == 0 else s["cuerpo"])
        pygame.draw.rect(pantalla, color, rect, border_radius=5)

def juego():
    res = db_query("SELECT monedas, skin_activa FROM usuario WHERE id=1")
    monedas_init, skin_name = res
    skin = SKINS[skin_name]
    x, y, dx, dy = ANCHO//2, ALTO//2, BLOQUE, 0
    cuerpo, largo, puntos = [[x, y]], 4, 0
    cx = round(random.randrange(20, ANCHO-20)/BLOQUE)*BLOQUE
    cy = round(random.randrange(80, ALTO-20)/BLOQUE)*BLOQUE
    particulas = []

    while True:
        pantalla.fill(skin["fondo"])
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "SALIR"
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                if my < ALTO//3 and dy == 0: dx, dy = 0, -BLOQUE
                elif my > (ALTO//3)*2 and dy == 0: dx, dy = 0, BLOQUE
                elif mx < ANCHO//2 and dx == 0: dx, dy = -BLOQUE, 0
                elif mx >= ANCHO//2 and dx == 0: dx, dy = BLOQUE, 0

        x += dx; y += dy
        if x<0 or x>=ANCHO or y<0 or y>=ALTO or [x,y] in cuerpo[:-1]: break
        cuerpo.append([x,y])
        if len(cuerpo) > largo: del cuerpo[0]

        if x == cx and y == cy:
            puntos += 10; largo += 1
            for _ in range(10): particulas.append(Particula(cx, cy, ACENTO))
            cx = round(random.randrange(20, ANCHO-20)/BLOQUE)*BLOQUE
            cy = round(random.randrange(80, ALTO-20)/BLOQUE)*BLOQUE

        pygame.draw.circle(pantalla, (255, 50, 50), (cx+10, cy+10), 10)
        for p in particulas[:]:
            p.actualizar(); p.dibujar(pantalla)
            if p.vida <= 0: particulas.remove(p)

        dibujar_serpiente(cuerpo, skin_name)
        pygame.display.flip()
        reloj.tick(12)

    db_query("UPDATE usuario SET monedas = monedas + ? WHERE id=1", (puntos,), False)
    db_query("INSERT INTO records (puntos) VALUES (?)", (puntos,), False)
    return "MENU"

def menu():
    while True:
        res = db_query("SELECT monedas FROM usuario WHERE id=1")
        pantalla.fill(FONDO_MENU)
        txt = fuente_t.render("SNAKE WILD", True, ACENTO)
        pantalla.blit(txt, (ANCHO//2 - txt.get_width()//2, 100))
        
        # Botón simplificado para touch
        rect_jugar = pygame.Rect(ANCHO//2-100, 300, 200, 60)
        pygame.draw.rect(pantalla, ACENTO, rect_jugar, border_radius=10)
        btn_txt = fuente_m.render("TAP TO PLAY", True, FONDO_MENU)
        pantalla.blit(btn_txt, (rect_jugar.centerx-btn_txt.get_width()//2, rect_jugar.centery-10))
        
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "SALIR"
            if e.type == pygame.MOUSEBUTTONDOWN:
                if rect_jugar.collidepoint(e.pos): return "JUEGO"

# --- EJECUCIÓN ---
if __name__ == "__main__":
    init_db()
    estado = "MENU"
    while estado != "SALIR":
        if estado == "MENU": estado = menu()
        elif estado == "JUEGO": estado = juego()
    pygame.quit()
