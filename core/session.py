class Session:
    """Все данные партии (очки, очередь, клюшки)."""

    def __init__(self, num_players, num_holes):
        self.num_players = num_players
        self.num_holes = num_holes
        self.strokes = [[0] * num_holes for _ in range(num_players)]
        self.penalties = [[0] * num_holes for _ in range(num_players)]
        self.bonuses = [[0] * num_holes for _ in range(num_players)]
        self.players_finished = [False] * num_players
        self.player_clubs = [0] * num_players
        self.active_player = 0

    def add_stroke(self, player_idx, hole_idx):
        self.strokes[player_idx][hole_idx] += 1

    def add_penalty(self, player_idx, hole_idx):
        self.penalties[player_idx][hole_idx] += 1
        self.strokes[player_idx][hole_idx] += 1

    def next_player(self):
        self.active_player = (self.active_player + 1) % self.num_players
        attempts = 0
        while self.players_finished[self.active_player] and attempts < self.num_players:
            self.active_player = (self.active_player + 1) % self.num_players
            attempts += 1

    def reset_hole(self):
        self.players_finished = [False] * self.num_players
        self.active_player = 0

    def hole_finished_for_all(self):
        return all(self.players_finished)

    def set_club(self, player_idx, club_idx):
        if 0 <= club_idx < 5:
            self.player_clubs[player_idx] = club_idx

    def current_club(self):
        return self.player_clubs[self.active_player]

    def totals(self):
        return [sum(self.strokes[p]) for p in range(self.num_players)]

    def winner_index(self):
        t = self.totals()
        return t.index(min(t))
