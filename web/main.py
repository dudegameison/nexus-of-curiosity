import pygame
import sys
import random
import json
import os
import math
import asyncio

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Nexus of Curiosity - Browser")
clock = pygame.time.Clock()
font_large = pygame.font.SysFont("consolas", 48, bold=True)
font_med = pygame.font.SysFont("consolas", 28)
font_small = pygame.font.SysFont("consolas", 18)

COLORS = {
    "normal": {"space": (5, 0, 15), "neon": (0, 255, 200), "accent": (255, 100, 200)}
}
color_mode = "normal"

current_state = "MENU"
galaxy = []
current_planet = None
player_x = 300
player_y = 500
camera_x = 0
WORLD_WIDTH = 3000
truths_collected = 0
required_truths = 6
curiosity = 0
truth_fragments = 0
particles = []

def play_beep(*args, **kwargs):
    pass  # stub for browser

def draw_nebula_background():
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill(COLORS[color_mode]["space"])
    for _ in range(60):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        pygame.draw.circle(surf, COLORS[color_mode]["neon"], (x, y), random.randint(1, 3))
    return surf

def generate_galaxy():
    global galaxy
    galaxy = []
    for i in range(15):
        system = {"name": f"Sys-{i}", "x": random.randint(100, SCREEN_WIDTH-100), "y": random.randint(100, SCREEN_HEIGHT-100), "planets": []}
        for p in range(random.randint(1, 3)):
            system["planets"].append({
                "name": f"P{p}",
                "biome": random.choice(["crystal", "lava", "neon"]),
                "gravity": random.uniform(0.6, 1.2)
            })
        galaxy.append(system)

async def main_menu():
    global current_state
    bg = draw_nebula_background()
    while current_state == "MENU":
        screen.blit(bg, (0, 0))
        title = font_large.render("NEXUS OF CURIOSITY", True, COLORS[color_mode]["neon"])
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 140))
        sub = font_med.render("Click NEW GAME to start", True, COLORS[color_mode]["accent"])
        screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 220))
        btn = font_med.render("NEW GAME", True, COLORS[color_mode]["neon"])
        screen.blit(btn, (SCREEN_WIDTH//2 - btn.get_width()//2, 360))
        mx, my = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and 360 < my < 400 and SCREEN_WIDTH//2-120 < mx < SCREEN_WIDTH//2+120:
            generate_galaxy()
            current_state = "SPACE"
            return
        pygame.display.flip()
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

async def space_flight():
    global current_state, player_x, player_y, current_planet
    player_x, player_y = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
    vel = [0, 0]
    bg = draw_nebula_background()
    while current_state == "SPACE":
        screen.blit(bg, (0, 0))
        for sys_ in galaxy:
            pygame.draw.circle(screen, (180, 80, 255), (sys_["x"], sys_["y"]), 7)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: vel[1] -= 0.5
        if keys[pygame.K_s]: vel[1] += 0.5
        if keys[pygame.K_a]: vel[0] -= 0.5
        if keys[pygame.K_d]: vel[0] += 0.5
        vel[0] *= 0.95
        vel[1] *= 0.95
        player_x = (player_x + vel[0]) % SCREEN_WIDTH
        player_y = (player_y + vel[1]) % SCREEN_HEIGHT
        pygame.draw.polygon(screen, COLORS[color_mode]["neon"], [(player_x, player_y-12), (player_x-10, player_y+10), (player_x+10, player_y+10)])
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            for sys_ in galaxy:
                if math.hypot(sys_["x"]-mx, sys_["y"]-my) < 40 and sys_["planets"]:
                    current_planet = sys_["planets"][0]
                    current_state = "PLANET"
                    return
        pygame.display.flip()
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

async def planet_exploration():
    global current_state, player_x, player_y, camera_x, truths_collected, curiosity, truth_fragments
    truths_collected = 0
    truths_pos = [(500, 400), (1100, 300), (1700, 500), (2300, 350), (2800, 450)]
    player_x = 250
    player_y = 500
    vel_y = 0
    gravity = 0.4
    ground = 560
    while current_state == "PLANET":
        screen.fill((15, 25, 40))
        pygame.draw.rect(screen, (50, 130, 50), (0-camera_x, ground, WORLD_WIDTH, 200))
        for tx, ty in truths_pos:
            if truths_collected < len(truths_pos):
                pygame.draw.circle(screen, (255, 255, 120), (tx - camera_x, ty), 16)
        screen_x = player_x - camera_x
        pygame.draw.circle(screen, COLORS[color_mode]["neon"], (int(screen_x), int(player_y)), 22)
        camera_x = max(0, min(player_x - SCREEN_WIDTH//2, WORLD_WIDTH - SCREEN_WIDTH))
        keys = pygame.key.get_pressed()
        player_x += (keys[pygame.K_d] - keys[pygame.K_a]) * 6
        player_x = max(40, min(player_x, WORLD_WIDTH-40))
        vel_y += gravity
        player_y += vel_y
        if player_y > ground - 50:
            player_y = ground - 50
            vel_y = 0
            if keys[pygame.K_SPACE]:
                vel_y = -14
        # collect
        for i, (tx, ty) in enumerate(truths_pos):
            if i >= truths_collected and math.hypot(player_x-tx, player_y-ty) < 40 and keys[pygame.K_e]:
                truths_collected += 1
                truth_fragments += 1
                curiosity += 5
                break
        hud = font_med.render(f"Truths: {truths_collected}/{len(truths_pos)}  Fragments: {truth_fragments}", True, (255,255,255))
        screen.blit(hud, (20, 20))
        if truths_collected >= len(truths_pos):
            win = font_large.render("PLANET CLEARED!", True, (0, 255, 100))
            screen.blit(win, (SCREEN_WIDTH//2 - win.get_width()//2, 180))
            pygame.display.flip()
            await asyncio.sleep(1.5)
            current_state = "SPACE"
            return
        pygame.display.flip()
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                current_state = "SPACE"
                return

async def game_loop():
    global current_state
    await main_menu()
    while True:
        if current_state == "SPACE":
            await space_flight()
        elif current_state == "PLANET":
            await planet_exploration()
        else:
            await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(game_loop())
