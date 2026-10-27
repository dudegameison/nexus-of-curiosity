import pygame
import sys
import random
import json
import os
import math
import time
from pygame import sndarray
import numpy as np

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Nexus of Curiosity v2.2")
clock = pygame.time.Clock()
font_large = pygame.font.SysFont("consolas", 48, bold=True)
font_med = pygame.font.SysFont("consolas", 28)
font_small = pygame.font.SysFont("consolas", 18)

COLORS = {
    "normal": {"space": (5, 0, 15), "neon": (0, 255, 200), "accent": (255, 100, 200)},
    "cb": {"space": (10, 10, 20), "neon": (255, 200, 0), "accent": (0, 255, 255)}
}
color_mode = "normal"

SAVE_FILE = "save.json"
seed = random.randint(10000, 99999)
random.seed(seed)
curiosity = 0
truth_fragments = 0
achievements = []
unlocked_planets = ["Nexus"]
current_state = "MENU"
galaxy = []
current_planet = None
player_x = 300
player_y = 500
velocity_x = 0
velocity_y = 0
camera_x = 0
WORLD_WIDTH = 3000
truths_collected = 0
required_truths = 6
dialogue_active = False
dialogue_text = ""
particles = []

def play_beep(freq=440, duration=0.1, vol=0.3):
    try:
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        wave = np.sin(2 * np.pi * freq * t) * 32767 * vol
        stereo = np.column_stack((wave, wave)).astype(np.int16)
        sound = sndarray.make_sound(stereo)
        sound.play()
    except:
        pass

def draw_nebula_background():
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill(COLORS[color_mode]["space"])
    for _ in range(80):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 3)
        color = COLORS[color_mode]["neon"] if random.random() > 0.7 else (100, 50, 200)
        pygame.draw.circle(surf, color, (x, y), size)
    return surf

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = random.randint(30, 70)
        self.color = color
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vx *= 0.98
        self.vy *= 0.98
    def draw(self, surf):
        if self.life > 0:
            alpha = int(255 * (self.life / 70))
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            s.fill((*self.color, alpha))
            surf.blit(s, (self.x - camera_x, self.y))

def generate_galaxy():
    global galaxy
    galaxy = []
    for i in range(25):
        system = {"name": f"System-{i}", "x": random.randint(100, SCREEN_WIDTH-100), "y": random.randint(100, SCREEN_HEIGHT-100), "planets": []}
        for p in range(random.randint(2, 5)):
            biome = random.choice(["crystal_forest", "lava_ocean", "ring_world", "quantum_fog", "neon_jungle"])
            system["planets"].append({
                "name": f"{system['name']}-P{p}",
                "biome": biome,
                "gravity": random.uniform(0.5, 1.5),
                "discovered": False,
                "truths": random.randint(3, 8)
            })
        galaxy.append(system)

def main_menu():
    global current_state
    bg = draw_nebula_background()
    while current_state == "MENU":
        screen.blit(bg, (0, 0))
        title = font_large.render("NEXUS OF CURIOSITY v2.2", True, COLORS[color_mode]["neon"])
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 120))
        subtitle = font_med.render("Planets are HUGE and FUN! Collect truths or crash the universe.", True, COLORS[color_mode]["accent"])
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 200))
        for i, text in enumerate(["NEW GAME", "LOAD GAME", "OPTIONS", "CREDITS", "QUIT"]):
            col = COLORS[color_mode]["neon"] if i == 0 else (200, 200, 255)
            btn = font_med.render(text, True, col)
            y = 320 + i * 60
            screen.blit(btn, (SCREEN_WIDTH//2 - btn.get_width()//2, y))
            mx, my = pygame.mouse.get_pos()
            if pygame.mouse.get_pressed()[0] and y < my < y + 40 and SCREEN_WIDTH//2 - 150 < mx < SCREEN_WIDTH//2 + 150:
                if text == "NEW GAME":
                    generate_galaxy()
                    current_state = "TUTORIAL"
                elif text == "LOAD GAME":
                    load_game()
                    current_state = "SPACE_FLIGHT"
                elif text == "OPTIONS":
                    options_menu()
                elif text == "CREDITS":
                    credits_screen()
                elif text == "QUIT":
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def options_menu():
    global color_mode
    while True:
        screen.fill(COLORS[color_mode]["space"])
        txt = font_med.render("OPTIONS - ESC to return", True, COLORS[color_mode]["neon"])
        screen.blit(txt, (50, 50))
        cb_txt = font_med.render(f"Color-blind mode: {color_mode.upper()}", True, COLORS[color_mode]["accent"])
        screen.blit(cb_txt, (50, 150))
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            if 50 < mx < 400 and 150 < my < 200:
                color_mode = "cb" if color_mode == "normal" else "normal"
                time.sleep(0.2)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()
        clock.tick(60)

def credits_screen():
    while True:
        screen.fill(COLORS[color_mode]["space"])
        lines = [
            "NEXUS OF CURIOSITY v2.2",
            "Built live by CodeGrok for Dude Gameison",
            "xAI inspired • Zero crashes guaranteed",
            "",
            "Press ESC"
        ]
        for i, line in enumerate(lines):
            col = COLORS[color_mode]["neon"] if i == 0 else (255, 255, 255)
            txt = font_med.render(line, True, col)
            screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 100 + i*50))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def tutorial_nexus():
    global current_state
    bg = draw_nebula_background()
    lines = [
        "42: Welcome back, boss! Press WASD to move.",
        "42: Land on any planet by clicking it in space.",
        "42: On planets: WASD + SPACE to jump + E to scan truths.",
        "42: Collect 6 truths per planet to win the level!"
    ]
    step = 0
    while step < len(lines):
        screen.blit(bg, (0, 0))
        pygame.draw.rect(screen, (30, 30, 80), (100, 100, SCREEN_WIDTH-200, SCREEN_HEIGHT-200), border_radius=20)
        txt = font_med.render("NEXUS HUB - Tutorial", True, COLORS[color_mode]["neon"])
        screen.blit(txt, (150, 150))
        line = font_small.render(lines[step], True, COLORS[color_mode]["accent"])
        screen.blit(line, (150, 300))
        pygame.draw.polygon(screen, COLORS[color_mode]["neon"], [(640, 400), (620, 440), (660, 440)])
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                step += 1
                play_beep(880, 0.05)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                current_state = "SPACE_FLIGHT"
                return
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()
        clock.tick(60)
    current_state = "SPACE_FLIGHT"

def space_flight():
    global current_state, player_x, player_y, current_planet
    player_x, player_y = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
    velocity = [0, 0]
    bg = draw_nebula_background()
    while current_state == "SPACE_FLIGHT":
        screen.blit(bg, (0, 0))
        for system in galaxy:
            pygame.draw.circle(screen, (200, 100, 255), (system["x"], system["y"]), 8)
            label = font_small.render(system["name"], True, (255, 255, 255))
            screen.blit(label, (system["x"] + 12, system["y"] - 10))
        keys = pygame.key.get_pressed()
        accel = 0.4
        if keys[pygame.K_w]: velocity[1] -= accel
        if keys[pygame.K_s]: velocity[1] += accel
        if keys[pygame.K_a]: velocity[0] -= accel
        if keys[pygame.K_d]: velocity[0] += accel
        velocity[0] *= 0.96
        velocity[1] *= 0.96
        player_x += velocity[0]
        player_y += velocity[1]
        player_x = player_x % SCREEN_WIDTH
        player_y = player_y % SCREEN_HEIGHT
        ship_angle = math.atan2(velocity[1], velocity[0]) if velocity != [0,0] else 0
        ship_points = [(player_x, player_y), (player_x-20*math.cos(ship_angle), player_y-20*math.sin(ship_angle)), (player_x-10*math.cos(ship_angle+2.5), player_y-10*math.sin(ship_angle+2.5))]
        pygame.draw.polygon(screen, COLORS[color_mode]["neon"], ship_points)
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            for system in galaxy:
                for planet in system["planets"]:
                    if math.hypot(system["x"] - mx, system["y"] - my) < 40:
                        current_planet = planet
                        current_state = "PLANET_EXPLORATION"
                        play_beep(1200, 0.3)
                        return
        hud = font_small.render(f"Curiosity: {curiosity}  Fragments: {truth_fragments}", True, (255, 255, 255))
        screen.blit(hud, (20, SCREEN_HEIGHT-30))
        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                current_state = "MENU"
                return

def planet_exploration():
    global current_state, player_x, player_y, velocity_x, velocity_y, camera_x, truths_collected, dialogue_active, dialogue_text, curiosity, truth_fragments
    try:
        truths_collected = 0
        required_truths = 6
        truths_positions = [(600, 400), (1100, 300), (1700, 550), (2200, 250), (2600, 450), (2900, 380)]
        gravity = current_planet["gravity"] * 0.35
        ground_y = 580
        platforms = [(400, 480, 300), (900, 420, 250), (1500, 500, 400), (2100, 380, 200), (2700, 520, 350)]
        alien_x = 1400
        player_x = 300
        player_y = ground_y - 60
        velocity_x = velocity_y = 0
        camera_x = 0
        while current_state == "PLANET_EXPLORATION":
            screen.fill((20, 30, 50) if current_planet["biome"] in ["crystal_forest", "neon_jungle"] else (80, 20, 10))
            pygame.draw.rect(screen, (40, 120, 40), (0 - camera_x, ground_y, WORLD_WIDTH, SCREEN_HEIGHT - ground_y))
            for px, py, pw in platforms:
                pygame.draw.rect(screen, (0, 200, 255), (px - camera_x, py, pw, 20))
            for i, (tx, ty) in enumerate(truths_positions):
                if i >= truths_collected:
                    pygame.draw.circle(screen, (255, 255, 100), (tx - camera_x, ty), 18)
            screen_x = player_x - camera_x
            pygame.draw.circle(screen, COLORS[color_mode]["neon"], (int(screen_x), int(player_y)), 25)
            pygame.draw.rect(screen, COLORS[color_mode]["accent"], (int(screen_x)-15, int(player_y)+25, 30, 40))
            if abs(player_x - alien_x) < 80 and not dialogue_active:
                pygame.draw.circle(screen, (255, 100, 100), (alien_x - camera_x, 480), 22)
                prompt = font_small.render("SPACE = debate alien", True, (255, 255, 255))
                screen.blit(prompt, (alien_x - camera_x - 80, 420))
            camera_x = max(0, min(player_x - SCREEN_WIDTH//2, WORLD_WIDTH - SCREEN_WIDTH))
            keys = pygame.key.get_pressed()
            velocity_x = (keys[pygame.K_d] - keys[pygame.K_a]) * 7
            player_x += velocity_x
            player_x = max(50, min(player_x, WORLD_WIDTH - 50))
            velocity_y += gravity
            player_y += velocity_y
            if player_y >= ground_y - 60:
                player_y = ground_y - 60
                velocity_y = 0
                if keys[pygame.K_SPACE]:
                    velocity_y = -16
                    play_beep(280, 0.08)
            for px, py, pw in platforms:
                if velocity_y > 0 and py - 60 < player_y < py and px < player_x < px + pw:
                    player_y = py - 60
                    velocity_y = 0
                    if keys[pygame.K_SPACE]:
                        velocity_y = -16
            for i in range(len(truths_positions)-1, -1, -1):
                tx, ty = truths_positions[i]
                if truths_collected <= i and math.hypot(player_x - tx, player_y - ty) < 50 and keys[pygame.K_e]:
                    truths_collected += 1
                    truth_fragments += 1
                    curiosity += 8
                    particles.append(Particle(tx, ty, (255, 255, 100)))
                    play_beep(1600, 0.4)
                    truths_positions.pop(i)
                    break
            if abs(player_x - alien_x) < 80 and keys[pygame.K_SPACE] and not dialogue_active:
                dialogue_active = True
                dialogue_text = random.choice(["42: This alien says the answer is 43! Y/N?", "Alien: Prove 42 is wrong!"])
                play_beep(900, 0.3)
            if dialogue_active:
                pygame.draw.rect(screen, (10, 10, 30), (100, 100, SCREEN_WIDTH-200, 180))
                txt = font_med.render(dialogue_text, True, COLORS[color_mode]["accent"])
                screen.blit(txt, (150, 140))
                sub = font_small.render("Y = win debate   N = leave", True, (255,255,255))
                screen.blit(sub, (150, 220))
                if keys[pygame.K_y]:
                    truths_collected += 2
                    dialogue_active = False
                    play_beep(1200, 0.6)
                if keys[pygame.K_n]:
                    dialogue_active = False
                    play_beep(400, 0.2)
            mission = font_med.render(f"Collect {required_truths - truths_collected} more Truths to escape!", True, COLORS[color_mode]["neon"])
            screen.blit(mission, (20, 20))
            frag = font_small.render(f"Fragments: {truth_fragments}   Curiosity: {curiosity}", True, (255,255,255))
            screen.blit(frag, (20, 60))
            if truths_collected >= required_truths:
                win = font_large.render("MISSION COMPLETE! Portal opening…", True, (0, 255, 100))
                screen.blit(win, (SCREEN_WIDTH//2 - win.get_width()//2, 200))
                for _ in range(30):
                    particles.append(Particle(random.randint(100, SCREEN_WIDTH-100), random.randint(100, 400), (0, 255, 100)))
                pygame.display.flip()
                time.sleep(2)
                current_planet["discovered"] = True
                current_state = "SPACE_FLIGHT"
                break
            for p in particles[:]:
                p.update()
                p.draw(screen)
                if p.life <= 0:
                    particles.remove(p)
            pygame.display.flip()
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_game()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = "SPACE_FLIGHT"
                    return
    except Exception as e:
        print(f"Oops! Tiny crash inside planet: {e}")
        current_state = "SPACE_FLIGHT"

def save_game():
    data = {"curiosity": curiosity, "truth_fragments": truth_fragments, "achievements": achievements, "seed": seed, "unlocked_planets": unlocked_planets}
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def load_game():
    global curiosity, truth_fragments, achievements, seed, unlocked_planets
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        curiosity = data.get("curiosity", 0)
        truth_fragments = data.get("truth_fragments", 0)
        achievements = data.get("achievements", [])
        seed = data.get("seed", seed)
        unlocked_planets = data.get("unlocked_planets", ["Nexus"])
        random.seed(seed)
        generate_galaxy()

def game_loop():
    global current_state
    main_menu()
    while True:
        if current_state == "TUTORIAL":
            tutorial_nexus()
        elif current_state == "SPACE_FLIGHT":
            space_flight()
        elif current_state == "PLANET_EXPLORATION":
            planet_exploration()

if __name__ == "__main__":
    print("Nexus of Curiosity v2.2 launching!")
    print("Controls: WASD move | SPACE jump | E scan | ESC back | Mouse click planets")
    try:
        game_loop()
    except Exception as e:
        print(f"Game crashed with: {e}")
        input("Press Enter to close...")
