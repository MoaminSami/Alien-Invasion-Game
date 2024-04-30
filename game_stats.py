class GameStats:
    """Track statistics for Alien Invasion."""

    def __init__(self, ai_game):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()
        # Initialize the number of aliens killed to 0
        self.game_active = True
        self.aliens_killed = 0
        self.level = 1  # Initialize the level to 1
        
    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        # self.game_active = True

    def increment_aliens_killed(self):
        """Increment the number of aliens killed."""
        self.aliens_killed += 1

    def increment_level(self):
        """Increment the level."""
        self.level += 1
