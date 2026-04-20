#!/usr/bin/env python3
# SnakeWildPro FULL - 4 Skins + Tienda + Records + Pausa
# 100% Android SDL2 - SIN CRASHES

import os
import random
import sqlite3
import sys
import math
import traceback

try:
    import pygame
except:
    sys.exit(1)

# =========================
# ANDROID SAFE STORAGE
# =========================
def storage_path():
    try:
        if "ANDROID_ARGUMENT" in os.environ:
            from android.storage import app_storage_path
            return app_storage_path()
    except:
        pass
    return "./data"

os.makedirs(storage_path(), exist_ok=True)
DB_PATH = os.path.join(storage_path(), "snakewild.db")

# =========================
# DATABASE PRO
# =========================
def db_init():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS player (
                id INTEGER PRIMARY KEY, 
                coins INTEGER DEFAULT 250, 
                skin TEXT DEFAULT 'Pitón', 
                highscore INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS skins (
                player_id INTEGER, 
                skin_name TEXT, 
                price INTEGER,
                owned INTEGER DEFAULT 0,
                PRIMARY KEY(player_id, skin_name)
            )
        """)
        conn.execute("INSERT OR IGNORE INTO player (id, coins) VALUES (1, 250)")
        conn.commit()
        conn.close()
    except:
        pass

def db_get(field):
    try:
        conn = sqlite3.connect(DB_PATH)
        res = conn.execute(f"SELECT {field} FROM player WHERE id=1").fetchone()
        conn.close()
        return res[0] if res else 0
    except:
        return 0

def db_set(field, value):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(f"UPDATE player SET {field}=? WHERE id=1", (value,))
        conn.commit()
        conn.close()
    except:
        pass

def db_buy_skin(skin_name, price):
    try:
        conn = sqlite3.connect(DB_PATH)
        coins = db_get("coins")
        if coins >= price:
            conn.execute("UPDATE player SET coins = coins - ? WHERE id=1", (price,))
            conn.execute("INSERT OR IGNORE INTO skins (player_id, skin_name, price, owned) VALUES (1, ?, ?, 1)", 
                        (skin_name, price))
            conn.commit()
        conn.close()
    except:
        pass

def db_set_skin(skin_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE player SET skin=? WHERE id=1", (skin_name,))
        conn.commit()
        conn.close()
    except:
        pass

def db_highscore(score):
    try:
        conn = sqlite3.connect(DB_PATH)
        current = conn.execute("SELECT highscore FROM player WHERE id=1").fetchone()[0]
        if score > current:
            conn.execute("UPDATE player SET highscore=? WHERE id=1", (score,))
            conn.commit()
        conn.close()
    except:
        pass

# =========================
# SKINS COMPLETAS (4)
# =========================
SKINS = {
    "Pitón": {
        "head": (107,142,35), "body": (85,107,47), "pattern": (139,69,19),
        "bg": (25,30,25), "food": (255,200,100), "price": 0, "owned": True
    },
    "Coral": {
        "head": (220,20,20), "body": (150,20,20), "pattern": (255,230,0),
        "bg": (35,20,20), "food": (255,255,255), "price": 150, "owned": False
    },
    "Mamba": {
        "head": (50,80,110), "body": (30,60,80), "pattern": (100,150,200),
        "bg": (20,25,35), "food": (255,255,0), "price": 350, "owned": False
    },
    "Albina": {
        "head": (255,240,230), "body": (255,218,185), "pattern": (255,255,255),
        "bg": (40,35,30), "food": (200,150,100), "price": 800, "owned": False
    }
}

# =========================
# INIT ANDROID SAFE
# =========================
pygame.init()
info = pygame.display.Info()
W, H = info.current_w, info.current_h
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.NOFRAME)
pygame.display.set_caption("🐍 Snake Wild Pro")

CELL_SIZE = min(W, H) // 28
clock = pygame.time.Clock()
font_big = pygame.font.Font(None, min(64, W//15))
font_med = pygame.font.Font(None, min(42, W//20))
font_small = pygame.font.Font(None, min(32, W//25))

db_init()

# Game state
state = "MENU"
score = 0
coins = 0
highscore = 0
snake = []
direction = [CELL_SIZE, 0]
food = []
paused = False
game_over = False
current_skin = "Pitón"

def reset_game():
    global snake, direction, food, score, game_over, paused
    snake = [[W//2, H//2]]
    direction = [CELL_SIZE, 0]
    food = [random.randrange(CELL_SIZE, W-CELL_SIZE, CELL_SIZE), 
            random.randrange(CELL_SIZE, H-CELL_SIZE, CELL_SIZE)]
    score = 0
    game_over = False
    paused = False

def draw_snake(skin):
    for i, segment in enumerate(snake):
        color = skin["head"] if i == 0 else skin["body"]
        rect = pygame.Rect(segment[0], segment[1], CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, color, rect, border_radius=6)
        if i > 0 and random.random() < 0.3:
            pygame.draw.circle(screen, skin["pattern"], 
                            (segment[0]+CELL_SIZE//3, segment[1]+CELL_SIZE//3), 4)

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# =========================
# MAIN LOOP INFINITO
# =========================
running = True
while running:
    try:
        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos if hasattr(event, 'pos') else (W//2, H//2)
                
                if state == "MENU":
                    # Play button
                    if W//2-150 < mx < W//2+150 and H//2-30 < my < H//2+50:
                        state = "GAME"
                        reset_game()
                
                elif state == "GAME":
                    if game_over:
                        # Restart
                        state = "MENU"
                    elif paused:
                        paused = False
                    else:
                        # Direction (touch safe)
                        if abs(direction[1]) > 0:  # Vertical
                            if mx < W//3: direction = [-CELL_SIZE, 0]
                            else: direction = [CELL_SIZE, 0]
                        else:  # Horizontal
                            if my < H//3: direction = [0, -CELL_SIZE]
                            else: direction = [0, CELL_SIZE]
                
                elif state == "SHOP":
                    # Skin buttons
                    btn_w, btn_h = W//2.2, H//6
                    for i, (name, skin) in enumerate(SKINS.items()):
                        btn_x = 30 + (i%2)*(W//2 + 20)
                        btn_y = 120 + (i//2)*(btn_h + 20)
                        if (btn_x < mx < btn_x+btn_w and btn_y < my < btn_y+btn_h):
                            if skin["price"] == 0 or skin["owned"]:
                                db_set_skin(name)
                                current_skin = name
                                state = "MENU"
                            else:
                                db_buy_skin(name, skin["price"])
                                state = "MENU"
                
                elif state == "SCORES":
                    if W//2-100 < mx < W//2+100 and H-100 < my < H-20:
                        state = "MENU"

        # UPDATE GAME
        if state == "GAME" and not game_over and not paused:
            head = [snake[0][0] + direction[0], snake[0][1] + direction[1]]
            
            # COLLISIONS
            if (head[0] <= 0 or head[0] >= W or head[1] <= 0 or head[1] >= H or 
                head in snake):
                game_over = True
                db_highscore(score)
                db_set("coins", db_get("coins") + score//2)
            else:
                snake.insert(0, head)
                
                # FOOD
                if distance(head, food) < CELL_SIZE*0.8:
                    score += 10
                    food = [random.randrange(CELL_SIZE, W-CELL_SIZE, CELL_SIZE), 
                           random.randrange(CELL_SIZE, H-CELL_SIZE, CELL_SIZE)]
                else:
                    snake.pop()

        # DRAW
        screen.fill(SKINS[current_skin]["bg"])
        
        if state == "MENU":
            coins = db_get("coins")
            highscore = db_get("highscore")
            
            # Title
            title = font_big.render("🐍 SNAKE WILD PRO", True, (0,255,150))
            screen.blit(title, (W//2 - title.get_width()//2, H//5))
            
            # Stats
            stats1 = font_med.render(f"Monedas: ${coins}", True, (255,255,255))
            stats2 = font_med.render(f"Record: {highscore}", True, (255,255,255))
            screen.blit(stats1, (W//2 - stats1.get_width()//2, H//2.5))
            screen.blit(stats2, (W//2 - stats2.get_width()//2, H//2.1))
            
            # Buttons
            play_rect = pygame.Rect(W//2-150, H//2-30, 300, 80)
            pygame.draw.rect(screen, (0,255,150), play_rect, border_radius=15)
            play_txt = font_med.render("🎮 JUGAR", True, (20,25,30))
            screen.blit(play_txt, (W//2-play_txt.get_width()//2, H//2+10))
            
            shop_rect = pygame.Rect(W//2-150, H//2+70, 300, 70)
            pygame.draw.rect(screen, (100,200,150), shop_rect, border_radius=15)
            shop_txt = font_med.render("🛒 SKINS", True, (20,25,30))
            screen.blit(shop_txt, (W//2-shop_txt.get_width()//2, H//2+85))
            
        elif state == "GAME":
            skin = SKINS[current_skin]
            
            # Food
            pygame.draw.circle(screen, skin["food"], 
                             (food[0]+CELL_SIZE//2, food[1]+CELL_SIZE//2), 
                             CELL_SIZE//2.5)
            
            # Snake
            draw_snake(skin)
            
            # UI
            score_txt = font_med.render(f"PUNTOS: {score}", True, (255,255,255))
            skin_txt = font_small.render(f"Skin: {current_skin}", True, (200,200,200))
            screen.blit(score_txt, (20, 20))
            screen.blit(skin_txt, (20, 60))
            
            if paused:
                pause_rect = pygame.Rect(W//2-200, H//2-50, 400, 100)
                pygame.draw.rect(screen, (0,0,0,128), pause_rect, border_radius=20)
                pause_txt = font_big.render("PAUSADO", True, (255,255,255))
                screen.blit(pause_txt, (W//2-pause_txt.get_width()//2, H//2-25))
            
            if game_over:
                go_rect = pygame.Rect(W//2-250, H//2-80, 500, 160)
                pygame.draw.rect(screen, (0,0,0,180), go_rect, border_radius=20)
                go_txt1 = font_med.render("GAME OVER", True, (255,100,100))
                go_txt2 = font_small.render(f"Puntos: {score}", True, (255,255,255))
                go_txt3 = font_small.render("Toca para menú", True, (200,200,200))
                screen.blit(go_txt1, (W//2-go_txt1.get_width()//2, H//2-60))
                screen.blit(go_txt2, (W//2-go_txt2.get_width()//2, H//2-20))
                screen.blit(go_txt3, (W//2-go_txt3.get_width()//2, H//2+20))
        
        elif state == "SHOP":
            title = font_big.render("🛒 SKINS", True, (0,255,150))
            screen.blit(title, (W//2 - title.get_width()//2, 40))
            
            coins = db_get("coins")
            coins_txt = font_med.render(f"${coins}", True, (255,255,255))
            screen.blit(coins_txt, (W//2 - coins_txt.get_width()//2, 90))
            
            btn_w, btn_h = W//2.2, H//6
            for i, (name, skin) in enumerate(SKINS.items()):
                btn_x = 30 + (i%2)*(W//2 + 20)
                btn_y = 140 + (i//2)*(btn_h + 25)
                
                # Button
                owned = skin["price"] == 0
                color = (0,255,150) if owned else (100,100,100)
                pygame.draw.rect(screen, color, (btn_x, btn_y, btn_w, btn_h), 
                               border_radius=15)
                
                # Preview snake
                mini_snake = [[btn_x+30, btn_y+btn_h//2], [btn_x+60, btn_y+btn_h//2]]
                for seg in mini_snake:
                    pygame.draw.rect(screen, skin["head"], 
                                   (seg[0], seg[1], 20, 20))
                
                # Text
                name_txt = font_med.render(name, True, (255,255,255))
                price_txt = font_small.render(f"${skin['price']}", True, (200,200,200))
                screen.blit(name_txt, (btn_x+100, btn_y+20))
                screen.blit(price_txt, (btn_x+100, btn_y+60))
        
        elif state == "SCORES":
            title = font_big.render("🏆 RECORDS", True, (255,215,0))
            screen.blit(title, (W//2 - title.get_width()//2, 50))
            
            highscore = db_get("highscore")
            hs_txt = font_med.render(f"Mejor: {highscore}", True, (255,255,255))
            screen.blit(hs_txt, (W//2 - hs_txt.get_width()//2, 150))
            
            # Back button
            back_rect = pygame.Rect(W//2-120, H-100, 240, 70)
            pygame.draw.rect(screen, (0,255,150), back_rect, border_radius=15)
            back_txt = font_med.render("MENÚ", True, (20,25,30))
            screen.blit(back_txt, (W//2-back_txt.get_width()//2, H-80))
        
        pygame.display.flip()
        clock.tick(14)
        
    except Exception as e:
        # NEVER DIE
        try:
            with open(os.path.join(storage_path(), "log.txt"), "a") as f:
                f.write(f"Error: {e}\n")
        except:
            pass
        state = "MENU"

pygame.quit()
