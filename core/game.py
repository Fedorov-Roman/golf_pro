import pygame
import sys
import math
import random
from enum import Enum
import os

import config
import textures
import core.records as records
from entities.ball import Ball
from ui.widgets import Button
from ui.menu import draw_menu, draw_game_over_background, draw_records_screen
from ui.game_ui import draw_game
from ui.map_ui import draw_map_view
from core.physics import update_physics
from core.hole_generator import generate_hole
from core.particles import ParticleSystem
from core.camera import Camera
from core.zones import ZoneManager
from core.session import Session
from core.bonuses import BonusManager
from core.shot_system import ShotSystem


class GameState(Enum):
    MENU_PLAYERS = 1
    MENU_HOLES = 2
    MENU_FIELD = 3
    MENU_WEATHER = 4
    GAME = 5
    GAME_OVER = 6
    MENU_RECORDS = 7
    MAP = 8


class GolfGame:
    """Оркестратор игры."""

    def __init__(self, screen):
        self.screen = screen
        pygame.display.set_caption("Питон Гольф Про")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 60)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.state = GameState.MENU_PLAYERS
        self.num_players = 2
        self.num_holes = 3
        self.field_type = "forest"
        self.weather = "sunny"

        self.camera = Camera(
            config.WORLD_WIDTH,
            config.WORLD_HEIGHT,
            config.SCREEN_WIDTH,
            config.SCREEN_HEIGHT,
        )
        self.zone_manager = ZoneManager()
        self.shot_system = ShotSystem()
        self.bonus_manager = BonusManager()
        self.session = None

        self.textures = textures.generate_all()

        def load_ball_image(path, target_size=20):
            try:
                raw = pygame.image.load(path).convert_alpha()
            except:
                return None
            rect = raw.get_bounding_rect()
            if rect.width == 0 or rect.height == 0:
                return None
            cropped = raw.subsurface(rect)
            w, h = cropped.get_width(), cropped.get_height()
            scale = target_size / max(w, h)
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))
            return pygame.transform.smoothscale(cropped, (new_w, new_h))

        self.ball_surf = load_ball_image("assets/images/BALLWHITE.png")
        if self.ball_surf is None:
            self.ball_surf = textures.make_ball()

        self.ball_shadow = pygame.Surface((24, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(self.ball_shadow, (0, 0, 0, 100), (2, 2, 20, 8))

        color_files = [
            "BALLRED.png",
            "BALLBLUE.png",
            "BALLWELLOY.png",
            "BALLPERPULE.png",
        ]
        self.ball_surfs_colored = []
        for fname in color_files:
            path = os.path.join("assets", "images", fname)
            img = load_ball_image(path)
            if img is None:
                idx = color_files.index(fname)
                color = (
                    config.PLAYER_COLORS[idx]
                    if idx < len(config.PLAYER_COLORS)
                    else (255, 255, 255)
                )
                img = textures.make_colored_ball(color)
            self.ball_surfs_colored.append(img)

        self.holes_data = []
        self.current_hole = 0
        self.balls = []
        self.ball_moving = False
        self.pending_activation = None
        self.particle_system = ParticleSystem()

        self.menu_buttons = []
        self.gameover_button = None
        self.message = ""
        self.record_message = ""
        self.records_scroll_offset = 0
        self.records_content_height = 0

        self.dragging_camera = False
        self.last_mouse_pos = (0, 0)

    def start_game(self):
        self.session = Session(self.num_players, self.num_holes)
        self.bonus_manager.reset()
        self.holes_data = []
        for i in range(self.num_holes):
            hole = generate_hole(self.field_type, self.weather)
            hole["index"] = i
            self.holes_data.append(hole)
        self.current_hole = 0
        self.reset_hole()
        self.state = GameState.GAME
        self.message = ""
        self.particle_system.init_for_weather(
            self.field_type, self.weather, self.holes_data[0]["wind"]
        )

    def reset_hole(self):
        hole = self.holes_data[self.current_hole]
        self.balls = [Ball(i, hole["start"]) for i in range(self.num_players)]
        self.balls[0].visible = True
        self.session.reset_hole()
        self.ball_moving = False
        self.shot_system.cancel_aim()
        self.shot_system.selecting_angle = False
        self.pending_activation = None
        self.message = ""
        self.zone_manager.load_zones(hole.get("zones", []), hole.get("obstacles", []))
        self.particle_system.init_for_weather(
            self.field_type, self.weather, hole["wind"]
        )
        self.camera.pos = [hole["start"][0], hole["start"][1]]
        self.camera._clamp()

    def shoot(self, direction, power, player_idx, angle_deg):
        ball = self.balls[player_idx]
        if not ball.visible or ball.moving or ball.in_hole:
            return

        # Проверяем модификаторы зоны (rough, bunker)
        power_mult, min_angle = self.zone_manager.get_shot_modifier(ball)
        if min_angle > 0 and angle_deg < min_angle:
            self.message = f"Угол должен быть >= {min_angle}° для удара из бункера!"
            return
        power *= power_mult

        club = config.CLUBS[self.session.player_clubs[player_idx]]
        shot = self.shot_system.calculate_shot(direction, power, club, angle_deg)
        ball.vel[0], ball.vel[1] = shot["vel"]
        ball.vz = shot["vz"]
        ball.z = shot["z"]
        ball.spin_force = list(shot["spin"])
        ball.in_flight = True
        ball.moving = False
        self.session.add_stroke(player_idx, self.current_hole)
        self.ball_moving = True
        self.session.next_player()
        if not self.balls[self.session.active_player].visible:
            self.pending_activation = self.session.active_player
        else:
            self.pending_activation = None

    def update(self, dt):
        if self.state == GameState.GAME:
            msgs = update_physics(
                self.balls,
                self.holes_data[self.current_hole],
                dt,
                self.session.strokes,
                self.session.players_finished,
                zone_manager=self.zone_manager,
            )
            for msg in msgs:
                self.message = msg
                if "завершил лунку" in msg:
                    hole_pos = self.holes_data[self.current_hole]["hole"]
                    self.particle_system.create_hole_splash(hole_pos)
            self.ball_moving = any(
                b.visible and (b.moving or b.in_flight) for b in self.balls
            )
            if self.pending_activation is not None and not self.ball_moving:
                player_idx = self.pending_activation
                if not self.balls[player_idx].visible:
                    hole_start = self.holes_data[self.current_hole]["start"]
                    self.balls[player_idx].pos = list(hole_start)
                    self.balls[player_idx].visible = True
                    self.balls[player_idx].moving = False
                    self.balls[player_idx].vel = [0, 0]
                    self.message = f"Ход игрока {player_idx + 1}"
                self.pending_activation = None
            self.particle_system.update(dt, self.holes_data[self.current_hole]["wind"])

    def draw(self):
        if self.state in (
            GameState.MENU_PLAYERS,
            GameState.MENU_HOLES,
            GameState.MENU_FIELD,
            GameState.MENU_WEATHER,
        ):
            draw_menu(
                self.screen,
                self.state,
                self.menu_buttons,
                self.message,
                self.font_large,
                self.font,
                self.small_font,
            )
        elif self.state == GameState.MENU_RECORDS:
            content_height, corrected_offset = draw_records_screen(
                self.screen,
                self.font_large,
                self.font,
                self.small_font,
                self.menu_buttons,
                self.message,
                self.records_scroll_offset,
            )
            self.records_content_height = content_height
            self.records_scroll_offset = corrected_offset
        elif self.state == GameState.GAME:
            draw_game(self.screen, self)
        elif self.state == GameState.MAP:
            draw_map_view(self.screen, self)
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()

    def draw_game_over(self):
        totals = self.session.totals()
        draw_game_over_background(
            self.screen,
            self.font_large,
            self.font,
            self.small_font,
            totals,
            self.num_players,
        )
        if self.record_message:
            record_surf = self.font.render(self.record_message, True, config.YELLOW)
            record_rect = record_surf.get_rect(
                center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 200)
            )
            bg_rect = record_rect.inflate(40, 20)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, 150))
            self.screen.blit(bg_surf, bg_rect)
            self.screen.blit(record_surf, record_rect)
        if self.gameover_button:
            self.gameover_button.update(pygame.mouse.get_pos())
            self.gameover_button.draw(self.screen, self.font)

    def advance_hole(self):
        self.current_hole += 1
        if self.current_hole >= self.num_holes:
            self.state = GameState.GAME_OVER
            totals = self.session.totals()
            min_strokes = min(totals)
            winner_idx = self.session.winner_index()
            winner_name = f"Игрок {winner_idx+1}"
            if records.is_new_record(
                self.field_type, self.weather, self.num_holes, min_strokes
            ):
                self.record_message = f"НОВЫЙ РЕКОРД! {winner_name}: {min_strokes} ударов ({self.num_holes} лунки)"
                records.update_record(
                    self.field_type,
                    self.weather,
                    self.num_holes,
                    min_strokes,
                    winner_name,
                )
            else:
                current_record = records.get_record(
                    self.field_type, self.weather, self.num_holes
                )
                if current_record:
                    self.record_message = f"Рекорд ({self.num_holes} лунки): {current_record['winner']} — {current_record['strokes']} ударов"
                else:
                    self.record_message = ""
            self.gameover_button = Button(
                (config.SCREEN_WIDTH // 2 - 150, config.SCREEN_HEIGHT - 150, 300, 70),
                "В меню",
                config.GREEN,
                (0, 200, 0),
            )
        else:
            self.reset_hole()

    def setup_menu(self):
        self.menu_buttons.clear()
        if self.state == GameState.MENU_PLAYERS:
            self.message = "Выберите количество игроков"
            for i, n in enumerate([2, 3, 4, 5]):
                colors = [config.GREEN, config.BLUE, (255, 165, 0), (128, 0, 128)]
                hovers = [(0, 200, 0), (0, 0, 200), (255, 140, 0), (148, 0, 211)]
                self.menu_buttons.append(
                    Button(
                        (config.SCREEN_WIDTH // 2 - 200, 200 + i * 80, 400, 70),
                        f"{n} игрока",
                        colors[i],
                        hovers[i],
                    )
                )
            self.menu_buttons.append(
                Button(
                    (config.SCREEN_WIDTH // 2 - 150, 550, 300, 60),
                    "Рекорды",
                    config.BLUE,
                    (100, 100, 255),
                )
            )
            self.menu_buttons.append(
                Button(
                    (config.SCREEN_WIDTH // 2 - 150, 630, 300, 60),
                    "Сбросить рекорды",
                    config.RED,
                    (255, 100, 100),
                )
            )
        elif self.state == GameState.MENU_RECORDS:
            self.message = ""
            self.menu_buttons.append(
                Button(
                    (
                        config.SCREEN_WIDTH // 2 - 100,
                        config.SCREEN_HEIGHT - 70,
                        200,
                        50,
                    ),
                    "Назад",
                    config.GRAY,
                    (180, 180, 180),
                )
            )
            self.records_scroll_offset = 0
        elif self.state == GameState.MENU_HOLES:
            self.message = "Выберите количество лунок"
            for i, h in enumerate([3, 6, 9]):
                self.menu_buttons.append(
                    Button(
                        (config.SCREEN_WIDTH // 2 - 200, 200 + i * 100, 400, 70),
                        f"{h} лунок",
                        config.YELLOW,
                        (255, 200, 0),
                    )
                )
        elif self.state == GameState.MENU_FIELD:
            self.message = "Выберите поле"
            fields = [("forest", "Лес"), ("desert", "Пустыня"), ("snow", "Снег")]
            for i, (key, name) in enumerate(fields):
                color = (
                    config.DARK_GREEN
                    if key == "forest"
                    else config.SAND_COLOR if key == "desert" else config.SNOW_WHITE
                )
                hover = (
                    (0, 150, 0)
                    if key == "forest"
                    else (210, 180, 140) if key == "desert" else (230, 230, 230)
                )
                txt_col = config.WHITE if key == "forest" else config.BLACK
                self.menu_buttons.append(
                    Button(
                        (config.SCREEN_WIDTH // 2 - 200, 200 + i * 100, 400, 70),
                        name,
                        color,
                        hover,
                        txt_col,
                    )
                )
        elif self.state == GameState.MENU_WEATHER:
            self.message = "Выберите погоду"
            w_opts = [
                ("sunny", "Солнечно", config.YELLOW),
                ("rain", "Дождь", config.GRAY),
                ("windy", "Ветрено", config.LIGHT_BLUE),
            ]
            for i, (key, name, col) in enumerate(w_opts):
                hover = (
                    (255, 200, 0)
                    if key == "sunny"
                    else (100, 100, 100) if key == "rain" else (135, 206, 250)
                )
                self.menu_buttons.append(
                    Button(
                        (config.SCREEN_WIDTH // 2 - 200, 200 + i * 100, 400, 70),
                        name,
                        col,
                        hover,
                        config.BLACK,
                    )
                )

    def handle_event(self, event):
        if self.shot_system.selecting_angle:
            if event.type == pygame.MOUSEMOTION:
                ball = self.balls[self.session.active_player]
                world_mouse = self.camera.screen_to_world(event.pos)
                self.shot_system.update_angle(
                    world_mouse[1], ball.pos[1], self.camera.zoom
                )
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.camera.zoom_in()
                else:
                    self.camera.zoom_out()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                result = self.shot_system.confirm_angle()
                if result is not None:
                    direction, power, angle = result
                    self.shoot(direction, power, self.session.active_player, angle)
            return

        if event.type == pygame.MOUSEWHEEL:
            if self.state == GameState.GAME:
                if event.y > 0:
                    self.camera.zoom_in()
                else:
                    self.camera.zoom_out()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.state in (
                    GameState.MENU_PLAYERS,
                    GameState.MENU_HOLES,
                    GameState.MENU_FIELD,
                    GameState.MENU_WEATHER,
                    GameState.MENU_RECORDS,
                ):
                    for btn in self.menu_buttons:
                        if btn.is_clicked(event.pos):
                            self.process_menu_click(btn.text)
                elif self.state == GameState.GAME:
                    if not self.shot_system.is_aiming:
                        ball = self.balls[self.session.active_player]
                        world_mouse = self.camera.screen_to_world(event.pos)
                        if (
                            not self.ball_moving
                            and ball.visible
                            and not ball.in_hole
                            and math.hypot(
                                world_mouse[0] - ball.pos[0],
                                world_mouse[1] - ball.pos[1],
                            )
                            < 40
                        ):
                            self.shot_system.start_aim(ball.pos, world_mouse)
                        else:
                            self.dragging_camera = True
                            self.last_mouse_pos = event.pos
                elif self.state == GameState.GAME_OVER and self.gameover_button:
                    if self.gameover_button.is_clicked(event.pos):
                        self.state = GameState.MENU_PLAYERS
                        self.setup_menu()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.dragging_camera:
                    self.dragging_camera = False
                elif self.state == GameState.GAME and self.shot_system.is_aiming:
                    club = config.CLUBS[self.session.current_club()]
                    result = self.shot_system.finish_aim(club)
                    if result is not None:
                        direction, power = result
                        self.shot_system.start_angle_selection(direction, power)
        elif event.type == pygame.MOUSEMOTION:
            if self.state == GameState.GAME:
                if self.dragging_camera:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.camera.move(dx, dy)
                    self.last_mouse_pos = event.pos
                elif self.shot_system.is_aiming:
                    self.shot_system.accumulate_motion(event.rel)
        elif event.type == pygame.KEYDOWN:
            if self.state == GameState.GAME:
                if event.key == pygame.K_1:
                    self.session.set_club(self.session.active_player, 0)
                elif event.key == pygame.K_2:
                    self.session.set_club(self.session.active_player, 1)
                elif event.key == pygame.K_3:
                    self.session.set_club(self.session.active_player, 2)
                elif event.key == pygame.K_4:
                    self.session.set_club(self.session.active_player, 3)
                elif event.key == pygame.K_5:
                    self.session.set_club(self.session.active_player, 4)
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU_PLAYERS
                    self.setup_menu()
                    self.message = ""
                elif event.key == pygame.K_TAB:
                    self.state = GameState.MAP
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if self.session.hole_finished_for_all() and not self.ball_moving:
                        self.advance_hole()
                        self.message = ""
            elif self.state == GameState.MAP:
                if event.key in (pygame.K_TAB, pygame.K_ESCAPE):
                    self.state = GameState.GAME

    def process_menu_click(self, text):
        if self.state == GameState.MENU_PLAYERS:
            if "2" in text:
                self.num_players = 2
            elif "3" in text:
                self.num_players = 3
            elif "4" in text:
                self.num_players = 4
            elif "5" in text:
                self.num_players = 5
            elif "Рекорды" in text:
                self.state = GameState.MENU_RECORDS
                self.setup_menu()
                return
            elif "Сбросить рекорды" in text:
                records.clear_records()
                self.message = "Рекорды сброшены!"
                self.setup_menu()
                return
            self.state = GameState.MENU_HOLES
            self.setup_menu()
        elif self.state == GameState.MENU_RECORDS:
            if "Назад" in text:
                self.state = GameState.MENU_PLAYERS
                self.setup_menu()
        elif self.state == GameState.MENU_HOLES:
            self.num_holes = int(text.split()[0])
            self.state = GameState.MENU_FIELD
            self.setup_menu()
        elif self.state == GameState.MENU_FIELD:
            if text == "Лес":
                self.field_type = "forest"
            elif text == "Пустыня":
                self.field_type = "desert"
            elif text == "Снег":
                self.field_type = "snow"
            self.state = GameState.MENU_WEATHER
            self.setup_menu()
        elif self.state == GameState.MENU_WEATHER:
            if text == "Солнечно":
                self.weather = "sunny"
            elif text == "Дождь":
                self.weather = "rain"
            elif text == "Ветрено":
                self.weather = "windy"
            self.start_game()

    def run(self):
        self.setup_menu()
        running = True
        while running:
            dt = self.clock.tick(config.FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()
        sys.exit()
