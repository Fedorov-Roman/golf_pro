import random
import math
import heapq
import config
import textures
from entities.zone import Zone


def _is_position_free(pos, radius, obstacles, min_gap=15):
    for obs in obstacles:
        r_sum = radius + obs["radius"]
        d = math.hypot(pos[0] - obs["pos"][0], pos[1] - obs["pos"][1])
        if d < r_sum - min_gap:
            return False
    return True


def _generate_position(
    radius,
    obstacles,
    avoid_start_hole=False,
    start=None,
    hole_pos=None,
    max_attempts=500,
):
    for _ in range(max_attempts):
        x = random.randint(150, config.WORLD_WIDTH - 150)
        y = random.randint(150, config.WORLD_HEIGHT - 150)
        pos = (x, y)
        if not _is_position_free(pos, radius, obstacles):
            continue
        if avoid_start_hole and (start is not None) and (hole_pos is not None):
            if math.hypot(x - start[0], y - start[1]) < radius + 80:
                continue
            if math.hypot(x - hole_pos[0], y - hole_pos[1]) < radius + 80:
                continue
        return pos
    return (
        random.randint(150, config.WORLD_WIDTH - 150),
        random.randint(150, config.WORLD_HEIGHT - 150),
    )


def _generate_obstacles(field_type, preset, start, hole_pos, obstacles_list):
    def too_close_to_start_hole(pos, r):
        if math.hypot(pos[0] - start[0], pos[1] - start[1]) < r + 80:
            return True
        if math.hypot(pos[0] - hole_pos[0], pos[1] - hole_pos[1]) < r + 80:
            return True
        return False

    if field_type == "desert":
        for _ in range(random.randint(5, 8)):
            r = random.randint(25, 40)
            pos = _generate_position(
                r, obstacles_list, avoid_start_hole=True, start=start, hole_pos=hole_pos
            )
            if pos is None:
                continue
            obstacles_list.append(
                {
                    "type": "bush",
                    "pos": pos,
                    "radius": r,
                    "image": textures.make_bush(r),
                }
            )
        for _ in range(random.randint(5, 8)):
            r = random.randint(15, 25)
            pos = _generate_position(
                r, obstacles_list, avoid_start_hole=True, start=start, hole_pos=hole_pos
            )
            if pos is None:
                continue
            obstacles_list.append(
                {
                    "type": "rock",
                    "pos": pos,
                    "radius": r,
                    "image": textures.make_rock(r),
                }
            )
    elif field_type == "snow":
        for _ in range(random.randint(6, 10)):
            r = random.randint(35, 55)
            pos = _generate_position(
                r, obstacles_list, avoid_start_hole=True, start=start, hole_pos=hole_pos
            )
            if pos is None:
                continue
            obstacles_list.append(
                {
                    "type": "ice_block",
                    "pos": pos,
                    "radius": r,
                    "image": textures.make_ice_block(r),
                }
            )
        for _ in range(random.randint(2, 4)):
            r = random.randint(55, 100)
            pos = _generate_position(
                r, obstacles_list, avoid_start_hole=True, start=start, hole_pos=hole_pos
            )
            if pos is None:
                continue
            obstacles_list.append(
                {
                    "type": "ice",
                    "pos": pos,
                    "radius": r,
                    "image": textures.make_ice_surface(r),
                }
            )
    else:  # forest
        for _ in range(random.randint(7, 12)):
            r = random.randint(30, 50)
            pos = _generate_position(
                r, obstacles_list, avoid_start_hole=True, start=start, hole_pos=hole_pos
            )
            if pos is None:
                continue
            obstacles_list.append(
                {
                    "type": "tree",
                    "pos": pos,
                    "radius": r,
                    "image": textures.make_tree(r, preset["tree"]),
                }
            )

    sand_count = (
        random.randint(3, 6) if field_type != "desert" else random.randint(4, 7)
    )
    for _ in range(sand_count):
        r = random.randint(45, 75)
        pos = _generate_position(
            r, obstacles_list, avoid_start_hole=True, start=start, hole_pos=hole_pos
        )
        if pos is None:
            continue
        obstacles_list.append(
            {
                "type": "sand",
                "pos": pos,
                "radius": r,
                "image": textures.make_bunker(r, preset["sand"]),
            }
        )

    if field_type != "snow":
        for _ in range(random.randint(1, 3)):
            r = random.randint(55, 100)
            pos = _generate_position(
                r, obstacles_list, avoid_start_hole=True, start=start, hole_pos=hole_pos
            )
            if pos is None:
                continue
            water_surf, blobs_rel = textures.make_water_smooth(r, preset["water"])
            blobs_world = [
                (pos[0] + bx, pos[1] + by, br + config.WATER_OUTLINE)
                for bx, by, br in blobs_rel
            ]
            obstacles_list.append(
                {
                    "type": "water",
                    "pos": pos,
                    "radius": r,
                    "image": water_surf,
                    "blobs": blobs_world,
                }
            )


def _cell_to_world(gx, gy):
    return (
        gx * config.A_STAR_CELL_SIZE + config.A_STAR_CELL_SIZE // 2,
        gy * config.A_STAR_CELL_SIZE + config.A_STAR_CELL_SIZE // 2,
    )


def _is_cell_passable(gx, gy, obstacles):
    wx, wy = _cell_to_world(gx, gy)
    half_width = config.FAIRWAY_WIDTH // 2
    margin = config.FAIRWAY_MARGIN
    for obs in obstacles:
        if obs["type"] == "water":
            for bx, by, br in obs["blobs"]:
                if math.hypot(wx - bx, wy - by) < br + half_width + margin:
                    return False
        elif obs["type"] in ("ice", "sand", "tree", "bush", "rock", "ice_block"):
            r = obs["radius"]
            if (
                math.hypot(wx - obs["pos"][0], wy - obs["pos"][1])
                < r + half_width + margin
            ):
                return False
    return True


def _build_fairway_path(start, hole_pos, obstacles):
    cell_size = config.A_STAR_CELL_SIZE
    start_grid = (int(start[0] // cell_size), int(start[1] // cell_size))
    hole_grid = (int(hole_pos[0] // cell_size), int(hole_pos[1] // cell_size))
    max_gx = config.WORLD_WIDTH // cell_size
    max_gy = config.WORLD_HEIGHT // cell_size

    open_set = []
    heapq.heappush(open_set, (0, start_grid))
    came_from = {}
    g_score = {start_grid: 0}
    f_score = {
        start_grid: math.hypot(
            hole_grid[0] - start_grid[0], hole_grid[1] - start_grid[1]
        )
    }

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == hole_grid:
            path = []
            while current in came_from:
                path.append(_cell_to_world(current[0], current[1]))
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path
        for dx, dy in [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]:
            neighbor = (current[0] + dx, current[1] + dy)
            if not (0 <= neighbor[0] <= max_gx and 0 <= neighbor[1] <= max_gy):
                continue
            if not _is_cell_passable(neighbor[0], neighbor[1], obstacles):
                continue
            tentative_g = g_score[current] + (1.414 if dx * dy != 0 else 1.0)
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + math.hypot(
                    hole_grid[0] - neighbor[0], hole_grid[1] - neighbor[1]
                )
                f_score[neighbor] = f
                heapq.heappush(open_set, (f, neighbor))
    return None


def _smooth_path(path, obstacles):
    if len(path) < 3:
        return path
    half_width = config.FAIRWAY_WIDTH // 2
    margin = config.FAIRWAY_MARGIN
    required = half_width + margin

    def is_safe(p):
        for obs in obstacles:
            if obs["type"] == "water":
                for bx, by, br in obs["blobs"]:
                    if math.hypot(p[0] - bx, p[1] - by) < br + required:
                        return False
            elif obs["type"] in ("ice", "sand", "tree", "bush", "rock", "ice_block"):
                r = obs["radius"]
                if (
                    math.hypot(p[0] - obs["pos"][0], p[1] - obs["pos"][1])
                    < r + required
                ):
                    return False
        return True

    for _ in range(config.FAIRWAY_SMOOTH_PASSES):
        new_path = [path[0]]
        for i in range(1, len(path) - 1):
            prev, curr, nxt = path[i - 1], path[i], path[i + 1]
            avg_x = (prev[0] + curr[0] + nxt[0]) / 3
            avg_y = (prev[1] + curr[1] + nxt[1]) / 3
            candidate = (avg_x, avg_y)
            if is_safe(candidate):
                new_path.append(candidate)
            else:
                new_path.append(curr)
        new_path.append(path[-1])
        path = new_path
    return path


def _catmull_rom(p0, p1, p2, p3, t):
    t2 = t * t
    t3 = t2 * t
    x = 0.5 * (
        (2 * p1[0])
        + (-p0[0] + p2[0]) * t
        + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
        + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
    )
    y = 0.5 * (
        (2 * p1[1])
        + (-p0[1] + p2[1]) * t
        + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
        + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
    )
    return (x, y)


def _interpolate_path(path):
    if len(path) < 2:
        return path
    pts = [path[0]] + path + [path[-1]]
    dense = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        steps = max(1, int(dist / config.FAIRWAY_SMOOTH_STEP))
        for s in range(steps):
            t = s / steps
            dense.append(_catmull_rom(p0, p1, p2, p3, t))
    dense.append(path[-1])
    return dense


def _generate_rough_zones(zones, obstacles, fairway_segments, start, hole_pos, preset):
    """Генерирует пятна высокой травы (rough), избегая всех существующих объектов."""
    rough_zones = []
    attempts = 0
    max_attempts = config.ROUGH_COUNT * 20
    while len(rough_zones) < config.ROUGH_COUNT and attempts < max_attempts:
        attempts += 1
        r = random.randint(config.ROUGH_MIN_RADIUS, config.ROUGH_MAX_RADIUS)
        x = random.randint(r + 50, config.WORLD_WIDTH - r - 50)
        y = random.randint(r + 50, config.WORLD_HEIGHT - r - 50)
        pos = (x, y)

        if math.hypot(x - start[0], y - start[1]) < r + 100:
            continue
        if math.hypot(x - hole_pos[0], y - hole_pos[1]) < r + 100:
            continue

        overlaps = False
        for zone in zones + rough_zones:
            dist = math.hypot(x - zone.pos[0], y - zone.pos[1])
            if dist < r + zone.radius + config.ZONE_MARGIN:
                overlaps = True
                break
        if overlaps:
            continue

        if fairway_segments:
            min_dist = float("inf")
            for p1, p2 in fairway_segments:
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                if dx == 0 and dy == 0:
                    dist = math.hypot(x - p1[0], y - p1[1])
                else:
                    t = ((x - p1[0]) * dx + (y - p1[1]) * dy) / (dx * dx + dy * dy)
                    t = max(0.0, min(1.0, t))
                    proj_x = p1[0] + t * dx
                    proj_y = p1[1] + t * dy
                    dist = math.hypot(x - proj_x, y - proj_y)
                if dist < min_dist:
                    min_dist = dist
            if min_dist < r + config.FAIRWAY_WIDTH / 2 + config.FAIRWAY_MARGIN:
                continue

        obs_overlap = False
        for obs in obstacles:
            if obs["type"] == "water":
                for bx, by, br in obs["blobs"]:
                    if math.hypot(x - bx, y - by) < r + br + config.ZONE_MARGIN:
                        obs_overlap = True
                        break
                if obs_overlap:
                    break
            else:
                if (
                    math.hypot(x - obs["pos"][0], y - obs["pos"][1])
                    < r + obs["radius"] + config.ZONE_MARGIN
                ):
                    obs_overlap = True
                    break
        if obs_overlap:
            continue

        # Цвет rough: чуть светлее, чем раньше
        if preset["bg"] == config.FIELD_PRESETS["forest"]["bg"]:
            color = (40, 120, 40)  # светло-зелёный для травы
        elif preset["bg"] == config.FIELD_PRESETS["desert"]["bg"]:
            color = (210, 190, 140)  # светло-песочный
        else:  # snow
            color = (220, 220, 220)  # светло-серый

        rough_img = textures.make_rough_texture(r, color)
        rough_zones.append(
            Zone("rough", pos, radius=r, shape="circle", params={"image": rough_img})
        )

    return rough_zones


def generate_hole(field_type, weather_type):
    preset = config.FIELD_PRESETS[field_type]
    obstacles = []

    start = (
        random.randint(100, config.WORLD_WIDTH // 3),
        random.randint(100, config.WORLD_HEIGHT - 100),
    )
    hole_pos = (
        random.randint(2 * config.WORLD_WIDTH // 3, config.WORLD_WIDTH - 100),
        random.randint(100, config.WORLD_HEIGHT - 100),
    )

    _generate_obstacles(field_type, preset, start, hole_pos, obstacles)

    raw_path = _build_fairway_path(start, hole_pos, obstacles)
    if raw_path is None:
        for _ in range(5):
            if obstacles:
                del obstacles[random.randint(0, len(obstacles) - 1)]
            raw_path = _build_fairway_path(start, hole_pos, obstacles)
            if raw_path is not None:
                break
        if raw_path is None:
            raw_path = [start, hole_pos]

    smoothed = _smooth_path(raw_path, obstacles)
    fairway_points = _interpolate_path(smoothed)
    fairway_segments = [
        (fairway_points[i], fairway_points[i + 1])
        for i in range(len(fairway_points) - 1)
    ]

    w_params = config.WEATHER_PARAMS[weather_type]
    wind_range = w_params["wind_range"]
    wind = (0.0, 0.0)
    if wind_range[1] > 0:
        a = random.uniform(0, 2 * math.pi)
        s = random.uniform(*wind_range)
        wind = (math.cos(a) * s, math.sin(a) * s)

    # --- Генерация зон Tee и Green ---
    zones = []
    bg_color = preset["bg"]
    if field_type == "snow":
        fairway_color = (
            min(255, bg_color[0] + 10),
            min(255, bg_color[1] + 10),
            min(255, bg_color[2] + 10),
        )
    else:
        fairway_color = (
            max(0, bg_color[0] - 10),
            max(0, bg_color[1] - 10),
            max(0, bg_color[2] - 10),
        )
    tee_radius = config.TEE_RADIUS
    tee_img = textures.make_tee_texture(tee_radius, fairway_color)
    zones.append(
        Zone("tee", start, radius=tee_radius, shape="circle", params={"image": tee_img})
    )
    green_radius = config.GREEN_RADIUS
    green_fill = (
        min(255, fairway_color[0] + 20),
        min(255, fairway_color[1] + 20),
        min(255, fairway_color[2] + 20),
    )
    green_img = textures.make_green_texture(green_radius, green_fill, fairway_color)
    zones.append(
        Zone(
            "green",
            hole_pos,
            radius=green_radius,
            shape="circle",
            params={"image": green_img},
        )
    )

    # --- Очистка препятствий, попавших на Tee или Green ---
    margin = config.ZONE_MARGIN
    obstacles[:] = [
        obs for obs in obstacles if not _is_obs_overlapping_zone(obs, zones, margin)
    ]

    # --- Генерация rough-зон ---
    rough_zones = _generate_rough_zones(
        zones, obstacles, fairway_segments, start, hole_pos, preset
    )
    zones.extend(rough_zones)

    return {
        "start": start,
        "hole": hole_pos,
        "obstacles": obstacles,
        "wind": wind,
        "rain_mult": w_params["rain_mult"],
        "field_type": field_type,
        "preset": preset,
        "fairway_points": fairway_points,
        "fairway_segments": fairway_segments,
        "zones": zones,
    }


def _is_obs_overlapping_zone(obs, zones, margin):
    """Проверяет, пересекается ли препятствие с какой-либо зоной (tee, green и т.д.)."""
    for zone in zones:
        # Для воды проверяем каждый blob
        if obs["type"] == "water":
            for bx, by, br in obs["blobs"]:
                dist = math.hypot(bx - zone.pos[0], by - zone.pos[1])
                if dist < br + zone.radius + margin:
                    return True
        else:
            r = obs["radius"]
            dist = math.hypot(obs["pos"][0] - zone.pos[0], obs["pos"][1] - zone.pos[1])
            if dist < r + zone.radius + margin:
                return True
    return False
