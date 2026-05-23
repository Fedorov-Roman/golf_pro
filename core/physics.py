import math
import config


def update_physics(balls, hole_data, dt, strokes, players_finished, zone_manager=None):
    messages = []
    wind = hole_data["wind"]
    rain_mult = hole_data["rain_mult"]
    obstacles = hole_data["obstacles"]
    hole_pos = hole_data["hole"]
    hole_index = hole_data["index"]
    fairway_segments = hole_data.get("fairway_segments", [])
    field_type = hole_data.get("field_type", "forest")

    for i, ball in enumerate(balls):
        if not ball.visible or ball.in_hole:
            continue

        # Сохраняем позицию перед движением (для будущего респавна)
        ball.last_pos = list(ball.pos)

        # -------- фаза полёта --------
        if ball.in_flight:
            ball.vz -= config.GRAVITY * dt
            ball.z += ball.vz * dt

            if math.hypot(ball.vel[0], ball.vel[1]) > config.WIND_THRESHOLD:
                ball.vel[0] += wind[0] * dt * 0.4
                ball.vel[1] += wind[1] * dt * 0.4

            ball.pos[0] += ball.vel[0] * dt
            ball.pos[1] += ball.vel[1] * dt

            if ball.z <= 0.0:
                ball.land()
                ball.vel[0] *= 0.95
                ball.vel[1] *= 0.95

            # Границы в воздухе – отскок
            margin = config.MARGIN
            if ball.pos[0] < margin:
                ball.pos[0] = margin
                ball.vel[0] *= -0.5
            elif ball.pos[0] > config.SCREEN_WIDTH - margin:
                ball.pos[0] = config.SCREEN_WIDTH - margin
                ball.vel[0] *= -0.5
            if ball.pos[1] < margin:
                ball.pos[1] = margin
                ball.vel[1] *= -0.5
            elif ball.pos[1] > config.SCREEN_HEIGHT - margin:
                ball.pos[1] = config.SCREEN_HEIGHT - margin
                ball.vel[1] *= -0.5
            continue

        # ------- фаза качения -------
        is_on_fairway = False
        if fairway_segments:
            is_on_fairway = _is_on_fairway(
                ball.pos, fairway_segments, config.FAIRWAY_WIDTH
            )

        if is_on_fairway:
            friction = config.FAIRWAY_FRICTION * rain_mult
        else:
            friction = config.BASE_FRICTION * rain_mult

        # Препятствия
        for obs in obstacles:
            dx = ball.pos[0] - obs["pos"][0]
            dy = ball.pos[1] - obs["pos"][1]
            dist = math.hypot(dx, dy)

            if obs["type"] in ("tree", "bush", "rock", "ice_block"):
                if dist < obs["radius"] + config.BALL_RADIUS:
                    nx = dx / (dist + 0.001)
                    ny = dy / (dist + 0.001)
                    ball.pos[0] = obs["pos"][0] + nx * (
                        obs["radius"] + config.BALL_RADIUS
                    )
                    ball.pos[1] = obs["pos"][1] + ny * (
                        obs["radius"] + config.BALL_RADIUS
                    )
                    vn = ball.vel[0] * nx + ball.vel[1] * ny
                    ball.vel[0] -= 1.9 * vn * nx
                    ball.vel[1] -= 1.9 * vn * ny
                    ball.vel[0] *= 0.5
                    ball.vel[1] *= 0.5
                    ball.moving = True

            elif obs["type"] == "water":
                in_water = False
                for bx, by, br in obs["blobs"]:
                    if (
                        math.hypot(ball.pos[0] - bx, ball.pos[1] - by)
                        < br + config.BALL_RADIUS
                    ):
                        in_water = True
                        break
                if in_water:
                    strokes[i][hole_index] += 1
                    dx = ball.pos[0] - obs["pos"][0]
                    dy = ball.pos[1] - obs["pos"][1]
                    dist_center = math.hypot(dx, dy)
                    nx = dx / (dist_center + 0.001)
                    ny = dy / (dist_center + 0.001)
                    step = 5.0
                    safe = False
                    new_x, new_y = ball.pos[0], ball.pos[1]
                    for _ in range(100):
                        in_any = False
                        for bx, by, br in obs["blobs"]:
                            if (
                                math.hypot(new_x - bx, new_y - by)
                                < br + config.BALL_RADIUS
                            ):
                                in_any = True
                                break
                        if not in_any:
                            other_collision = False
                            for other in obstacles:
                                if other is obs:
                                    continue
                                if (
                                    math.hypot(
                                        new_x - other["pos"][0], new_y - other["pos"][1]
                                    )
                                    < other["radius"] + config.BALL_RADIUS + 5
                                ):
                                    other_collision = True
                                    break
                            if not other_collision:
                                safe = True
                                break
                        new_x += nx * step
                        new_y += ny * step
                    if not safe:
                        max_dist = max(br for (_, _, br) in obs["blobs"]) + 20
                        new_x = obs["pos"][0] + nx * max_dist
                        new_y = obs["pos"][1] + ny * max_dist
                    ball.pos = [new_x, new_y]
                    ball.stop()
                    messages.append(f"Игрок {i+1}: Вода! +1 штраф")
                    break

            elif obs["type"] == "sand":
                if dist < obs["radius"]:
                    friction = (
                        config.BASE_FRICTION * config.SAND_FRICTION_MULT * rain_mult
                    )

            elif obs["type"] == "ice":
                if dist < obs["radius"]:
                    friction = (
                        config.BASE_FRICTION * config.ICE_FRICTION_MULT * rain_mult
                    )

        # Применение физики зон (заглушка)
        if zone_manager is not None:
            zone_manager.apply_physics(ball, dt, field_type)

        if ball.moving:
            speed = math.hypot(ball.vel[0], ball.vel[1])
            if speed < config.STOP_THRESHOLD:
                ball.stop()
            else:
                friction_force = friction * dt
                if friction_force > speed:
                    ball.stop()
                else:
                    ball.vel[0] -= (ball.vel[0] / speed) * friction_force
                    ball.vel[1] -= (ball.vel[1] / speed) * friction_force

                if speed > config.WIND_THRESHOLD:
                    ball.vel[0] += wind[0] * dt * 0.4
                    ball.vel[1] += wind[1] * dt * 0.4

                ball.pos[0] += ball.vel[0] * dt
                ball.pos[1] += ball.vel[1] * dt

                if ball.pos[0] < config.MARGIN:
                    ball.pos[0] = config.MARGIN
                    ball.vel[0] *= -0.5
                elif ball.pos[0] > config.SCREEN_WIDTH - config.MARGIN:
                    ball.pos[0] = config.SCREEN_WIDTH - config.MARGIN
                    ball.vel[0] *= -0.5
                if ball.pos[1] < config.MARGIN:
                    ball.pos[1] = config.MARGIN
                    ball.vel[1] *= -0.5
                elif ball.pos[1] > config.SCREEN_HEIGHT - config.MARGIN:
                    ball.pos[1] = config.SCREEN_HEIGHT - config.MARGIN
                    ball.vel[1] *= -0.5

        # Проверка лунки (только на земле)
        if not ball.in_hole and ball.visible and not ball.in_flight:
            dist_to_hole = math.hypot(
                ball.pos[0] - hole_pos[0], ball.pos[1] - hole_pos[1]
            )
            if dist_to_hole < 12:
                speed = math.hypot(ball.vel[0], ball.vel[1])
                if speed <= config.MAX_HOLE_SPEED:
                    ball.in_hole = True
                    ball.stop()
                    players_finished[i] = True
                    messages.append(f"Игрок {i+1} завершил лунку!")
                else:
                    if not hasattr(ball, "fast_warned") or not ball.fast_warned:
                        messages.append(f"Игрок {i+1}: слишком быстро!")
                        ball.fast_warned = True

    # Столкновения мячей
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            b1, b2 = balls[i], balls[j]
            if not b1.visible or not b2.visible or b1.in_hole or b2.in_hole:
                continue
            if b1.in_flight or b2.in_flight:
                continue
            dx = b2.pos[0] - b1.pos[0]
            dy = b2.pos[1] - b1.pos[1]
            dist = math.hypot(dx, dy)
            min_dist = 2 * config.BALL_RADIUS
            if dist < min_dist and dist > 0.01:
                nx = dx / dist
                ny = dy / dist
                overlap = min_dist - dist
                fix = overlap / 2.0 + 1.0
                b1.pos[0] -= nx * fix
                b1.pos[1] -= ny * fix
                b2.pos[0] += nx * fix
                b2.pos[1] += ny * fix
                dvx = b1.vel[0] - b2.vel[0]
                dvy = b1.vel[1] - b2.vel[1]
                dv_n = dvx * nx + dvy * ny
                if dv_n > 0:
                    b1.vel[0] -= dv_n * nx
                    b1.vel[1] -= dv_n * ny
                    b2.vel[0] += dv_n * nx
                    b2.vel[1] += dv_n * ny
                    b1.moving = True
                    b2.moving = True

    return messages


def _is_on_fairway(pos, fairway_segments, width):
    min_dist = float("inf")
    for p1, p2 in fairway_segments:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        if dx == 0 and dy == 0:
            dist = math.hypot(pos[0] - p1[0], pos[1] - p1[1])
        else:
            t = ((pos[0] - p1[0]) * dx + (pos[1] - p1[1]) * dy) / (dx * dx + dy * dy)
            t = max(0.0, min(1.0, t))
            proj_x = p1[0] + t * dx
            proj_y = p1[1] + t * dy
            dist = math.hypot(pos[0] - proj_x, pos[1] - proj_y)
        min_dist = min(min_dist, dist)
    return min_dist <= width / 2
