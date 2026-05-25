class BonusManager:
    """Заглушка системы бонусов."""

    def __init__(self):
        self.enabled = False

    def reset(self):
        pass

    def check_bonus(self, session, field, weather, holes):
        return False

    def use_bonus(self, session, player_idx):
        return False
