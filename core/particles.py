import random
import math
import pygame
import config

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def init_for_weather(self, field_type, weather, wind):
        self.particles.clear()
        if weather == "windy":
            count = 80
            for _ in range(count):
                x = random.randint(0, config.WORLD_WIDTH)
                y = random.randint(0, config.WORLD_HEIGHT)
                if field_type == "forest":
                    col = (random.randint(100,180), random.randint(50,100), 20, random.randint(100,200))
                    ptype = "leaf"
                elif field_type == "desert":
                    col = (194,178,128, random.randint(100,200))
                    ptype = "sand_grain"
                elif field_type == "snow":
                    col = (255,255,255, random.randint(150,255))
                    ptype = "snowflake"
                else:
                    col, ptype = (200,200,200,200), "leaf"
                vel = [random.uniform(-40,40), random.uniform(-40,40)]
                self.particles.append({"pos":[x,y], "vel":vel, "type":ptype,
                                       "color":col, "size":random.randint(2,5), "life":None})
        elif weather == "rain":
            count = 200
            wind_x, wind_y = wind
            for _ in range(count):
                x = random.randint(0, config.WORLD_WIDTH)
                y = random.randint(0, config.WORLD_HEIGHT)
                vel_x = wind_x*0.1 + random.uniform(-30,30)
                vel_y = 300 + random.uniform(0,200) + wind_y*0.1
                self.particles.append({"pos":[x,y], "vel":[vel_x,vel_y], "type":"rain",
                                       "color":(173,216,230,180), "size":random.randint(6,12), "life":None})

    def create_splash(self, pos):
        for _ in range(10):
            self.particles.append({"pos":list(pos), "vel":[random.uniform(-100,100), random.uniform(-100,50)],
                                   "type":"water_splash", "color":(135,206,250,200),
                                   "size":random.randint(3,6), "life":0.5})

    def create_hole_splash(self, pos):
        """Цветные искры при попадании в лунку."""
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 100)
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle) - 50
            col = random.choice([
                (255, 215, 0), (255, 100, 0), (255, 255, 0), (255, 50, 50)
            ])
            self.particles.append({"pos": list(pos), "vel": [vx, vy], "type": "spark",
                                   "color": col + (255,), "size": random.randint(2, 5), "life": 0.6})

    def update(self, dt, wind):
        for p in self.particles[:]:
            if p.get("life"):
                p["life"] -= dt
                if p["life"] <= 0:
                    self.particles.remove(p)
                    continue
            if p["type"] != "rain":
                p["vel"][0] += wind[0]*dt*0.3
                p["vel"][1] += wind[1]*dt*0.3
                p["vel"][0] *= 0.99
                p["vel"][1] *= 0.99
            p["pos"][0] += p["vel"][0]*dt
            p["pos"][1] += p["vel"][1]*dt
            if p["type"] == "rain":
                if p["pos"][1] > config.WORLD_HEIGHT+50:
                    p["pos"][1] = -50
                    p["pos"][0] = random.randint(0, config.WORLD_WIDTH)
            else:
                if p["pos"][0] < -20: p["pos"][0] = config.WORLD_WIDTH+20
                elif p["pos"][0] > config.WORLD_WIDTH+20: p["pos"][0] = -20
                if p["pos"][1] < -20: p["pos"][1] = config.WORLD_HEIGHT+20
                elif p["pos"][1] > config.WORLD_HEIGHT+20: p["pos"][1] = -20

    def draw(self, surf, camera=None):
        for p in self.particles:
            if p["type"] == "rain":
                length = p["size"]
                rain_surf = pygame.Surface((2, length), pygame.SRCALPHA)
                for i in range(int(length)):
                    alpha = int(180*(1 - i/length))
                    rain_surf.fill((173,216,230, alpha), (0,i,2,1))
                if camera:
                    sx, sy = camera.world_to_screen(p["pos"])
                else:
                    sx, sy = p["pos"]
                surf.blit(rain_surf, (int(sx), int(sy)-length))
            elif p["type"] == "spark":
                life = p.get("life", 0.6)
                alpha = int(255 * (life/0.6))
                col = p["color"][:3] + (alpha,)
                size = int(p["size"] * (camera.zoom if camera else 1.0))
                if size < 1: size = 1
                s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(s, col, (size, size), size)
                if camera:
                    sx, sy = camera.world_to_screen(p["pos"])
                else:
                    sx, sy = p["pos"]
                surf.blit(s, (int(sx - size), int(sy - size)))
            else:
                col = p["color"]
                size = int(p["size"] * (camera.zoom if camera else 1.0))
                if size < 1: size = 1
                if len(col)==4:
                    s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    pygame.draw.circle(s, col, (size, size), size)
                    if camera:
                        sx, sy = camera.world_to_screen(p["pos"])
                    else:
                        sx, sy = p["pos"]
                    surf.blit(s, (int(sx - size), int(sy - size)))
                else:
                    if camera:
                        sx, sy = camera.world_to_screen(p["pos"])
                    else:
                        sx, sy = p["pos"]
                    pygame.draw.circle(surf, col, (int(sx), int(sy)), size)
