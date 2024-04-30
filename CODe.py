import sys
from time import sleep
import pygame
from ship import Ship
from bullet import Bullet
from settings import Settings
from game_stats import GameStats
import pygame.font
import random
from alien import Alien
import pygame.mixer


class AlienInvasion:
    """Overall class to manage game assets and behavior"""

    def __init__(self):
        """Initializing the game, and create game resources"""
        pygame.init()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Moamins Alien Invasion")


        self.stats = GameStats(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        self.bullet_sound = pygame.mixer.Sound('bulletaudio.wav')

    def run_game(self):
        """Start the main loop for the game"""
        self._show_welcome_screen()
        while True:
            self._check_events()

            # Check if the game is active
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_screen()
            else:
                self._rps_game()


    def _show_welcome_screen(self):
        """Display welcome message and rules."""
        font = pygame.font.SysFont(None, 36)
        welcome_text = "Welcome to Alien Invasion!"
        rule_text = "Press 'Space' to shoot. Use 'Left' and 'Right' arrow keys to move. Press 'Q' to quit."
        morerules_text = "The Higher the level, the Harder it gets."
        rps_text = "Once you run out of lives, you will play a rock, paper, scissors game. If you win, you get a life. If you lose, YOU'RE OUT!!!"
        goodluck_text = "You can see aliens killed, ships remaining, and level on top of the screen."
        start_text = "Press 'S' to start the game. GOODLUCK!"

        text_welcome = font.render(welcome_text, True, (255, 255, 255))
        text_rule = font.render(rule_text, True, (255, 255, 255))
        text_morerules = font.render(morerules_text, True, (255, 255, 255))
        text_rps = font.render(rps_text, True, (255, 255, 255))
        text_goodluck = font.render(goodluck_text, True, (255, 255, 255))
        text_start = font.render(start_text, True, (255, 255, 255))

        welcome_rect = text_welcome.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 - 100))
        rule_rect = text_rule.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 - 50))
        morerules_rect = text_morerules.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2))
        rps_rect = text_rps.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 50))
        goodluck_rect = text_goodluck.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 100))
        start_rect = text_start.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 150))

        self.screen.fill((0, 0, 0))
        self.screen.blit(text_welcome, welcome_rect)
        self.screen.blit(text_rule, rule_rect)
        self.screen.blit(text_morerules, morerules_rect)
        self.screen.blit(text_rps, rps_rect)
        self.screen.blit(text_goodluck, goodluck_rect)
        self.screen.blit(text_start, start_rect)

        pygame.display.flip()


        # Wait for user input to start the game
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        waiting = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

        

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        """Respond to key presses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False


    def _fire_bullet(self):
        """Fire a bullet if the limit is not reached yet."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
            self.bullet_sound.play()


    def _update_bullets(self):
        """Update the position of bullets and get rid of old bullets."""
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()


    def _level_up(self):
        """Increase the game difficulty."""
        self.settings.increase_difficulty()  # Adjust settings to increase difficulty
        self._create_fleet()  # Create a new fleet of aliens
        self.ship.center_ship()  # Center the ship
        self.bullets.empty()  # Clear existing bullets
        self.stats.increment_level()  # Increment the level without resetting stats

  
    def _check_bullet_alien_collisions(self):
    # Respond to bullet-alien collisions
    # Check for any bullets that have hit aliens. If so, get rid of the
    # bullet and alien
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
    # Increment the number of aliens killed for each alien destroyed
        for aliens in collisions.values():
            self.stats.increment_aliens_killed()
        

    # Check to see if the aliens group is empty and if so, create a new fleet
        if not self.aliens:
        # Destroy any existing bullets and create a new fleet
            self.bullets.empty()
            self._create_fleet()
            self._level_up()



    def _update_aliens(self):

        #update the position of all aliens in fleet
        # check if fleet at edge then update position of aliens

        self._check_fleet_edges()
        
        self.aliens.update()

        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            print("OH NO!! THE ALIENS HAVE DAMAGED YOUR SHIP")
            #checks to see if ship has been hit
            self._ship_hit()
            # Looks for aliens hitting bottom of screen 
        self._check_aliens_bottom()


    def _create_fleet(self):
        aliens = Alien(self)
        alien_width, alien_height = aliens.rect.size
        available_space_x = self.settings.screen_width - (2*alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        for row_number in range(number_rows):
            for alien_number in range (number_aliens_x):
                self._create_alien(alien_number,row_number)


    def _show_ship_hit_message(self):
        """Render and display a message when the ship is hit."""
        font = pygame.font.SysFont(None, 48)  # You can adjust the font and size here
        text = font.render("Your ship has been hit!", True, (255, 0, 0))  # Red color
        text_rect = text.get_rect()
        text_rect.center = self.screen.get_rect().center
        self.screen.blit(text, text_rect)



    def _create_alien(self,alien_number,row_number):
            aliens = Alien(self)
            alien_width,alien_height = aliens.rect.size
            alien_width = aliens.rect.width
            aliens.x = alien_width + 2 * alien_width * alien_number

            aliens.rect.x = aliens.x
            aliens.rect.y = alien_height + 2 * aliens.rect.height * row_number
            self.aliens.add(aliens)



    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break



    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1



    def _ship_hit(self):
        #ship getting hit by an alien
        if self.stats.ships_left >0:
            #checks the number of ships left
            self.stats.ships_left -=1 
            #get rid of any bullets and aliens that are left
            self.aliens.empty()
            self.bullets.empty()
            #create new fleet and center ship
            self._create_fleet()
            self.ship.center_ship()
            self._show_ship_hit_message()
            sleep(1.0)
        else:
            self.stats.game_active = False


   

    def _show_level(self):
        """Render and display the current level on the screen."""
        font = pygame.font.SysFont(None, 36)
        level_str = (f"Level: {self.settings.level}")
        level_text = font.render(level_str, True, (191, 64, 191))
        level_rect = level_text.get_rect()
        level_rect.centerx = self.screen.get_rect().centerx  # Center the text horizontally
        level_rect.top = 10 
        self.screen.blit(level_text, level_rect)




    def _show_ship_hit_message(self):
            """Render and display a message when the ship is hit."""
            font = pygame.font.SysFont(None, 40)
            text = font.render("SHIP DOWN! SHIP DOWN!", True, (255,10 ,0 ))  # Red color
            text_rect = text.get_rect()
            text_rect.center = self.screen.get_rect().center
            self.screen.blit(text, text_rect)
            
            pygame.display.flip()


    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # same as if ship got hit
                 self._ship_hit()
                 break



    def _show_ship_count(self):
        """Render and display the number of ships remaining."""
        font = pygame.font.SysFont(None, 36)
        ship_count_str = f" SHIPS REMAINING: {self.stats.ships_left}"
        ship_count_text = font.render(ship_count_str, True, (136,8 ,8 ))
        ship_count_rect = ship_count_text.get_rect()
        ship_count_rect.topright = (self.settings.screen_width - 10, 10)
        self.screen.blit(ship_count_text, ship_count_rect)





    def _show_alien_count(self):
        """Render and display the number of aliens killed."""
        font = pygame.font.SysFont(None, 36)
        alien_count_str = f"Aliens Killed: {self.stats.aliens_killed}"
        alien_count_text = font.render(alien_count_str, True, (0,10, 255))
        alien_count_rect = alien_count_text.get_rect()
        alien_count_rect.topleft = (10,10)
        self.screen.blit(alien_count_text, alien_count_rect)







    



    def _update_screen(self):
        """Update images on the screen and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        # if self.stats._ship_hit:
        #     self._show_ship_hit_message()
        self._show_alien_count()
        
        self._show_ship_count()
        self._show_ship_hit_message
        self._show_level()
        pygame.display.flip()




    def _rps_game(self):
        """Rock-paper-scissors game to determine if player gets an extra life."""
        # Display RPS options on the screen
        font = pygame.font.SysFont(None, 48)
        
        # Display "Rock, Paper, Scissors!" message
        text = font.render("Rock, Paper, Scissors!", True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = self.screen.get_rect().center
        self.screen.fill(self.settings.bg_color)
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        sleep(2.0)

        # Display "Enter your choice:" message
        text = font.render("Enter your choice: (r)ock, (p)aper, (s)cissors", True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = self.screen.get_rect().center
        self.screen.fill(self.settings.bg_color)
        self.screen.blit(text, text_rect)
        pygame.display.flip()

        # Player choice
        player_choice = None
        while player_choice not in ['r', 'p', 's']:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        player_choice = 'r'
                    elif event.key == pygame.K_p:
                        player_choice = 'p'
                    elif event.key == pygame.K_s:
                        player_choice = 's'
                    elif event.key == pygame.K_q:
                        sys.exit()  # Exit the game if 'q' is pressed

        # AI choice
        ai_choice = random.choice(['r', 'p', 's'])
        sleep(1.0)

        # Display AI's choice
        text = font.render(f"Computer chose {ai_choice} 1 MORE LIFE", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = self.screen.get_rect().center
        self.screen.fill(self.settings.bg_color)
        self.screen.blit(text, text_rect)
        pygame.display.flip()

        # Determine winner
        if (player_choice == 'r' and ai_choice == 's') or \
        (player_choice == 'p' and ai_choice == 'r') or \
        (player_choice == 's' and ai_choice == 'p'):
            # Display "You win an extra LIFE!" message
            text = font.render("You win an extra LIFE!", True, (0, 255, 0))  # Green color
            text_rect = text.get_rect()
            text_rect.center = self.screen.get_rect().center
            self.screen.fill(self.settings.bg_color)
            self.screen.blit(text, text_rect)

            # Increment ships remaining
            self.stats.ships_left += 1

            # Display ships remaining and aliens killed
            self._show_ship_count()
            self._show_alien_count()

            # Continue shooting aliens by setting game_active to True
            self.stats.game_active = True

        else:
            # Display "You lose!" message
            text = font.render("You lose..BYE!", True, (255, 0, 0))  # Red
            text_rect = text.get_rect()
            text_rect.center = self.screen.get_rect().center
            self.screen.fill(self.settings.bg_color)
            self.screen.blit(text, text_rect)
            pygame.display.flip()

            # Check if the player has run out of lives
            if self.stats.ships_left <= 0:
                sys.exit()  # Game exits if player loses

        # Pause before continuing
        sleep(2.0)

        # Update screen to reflect extra life or game over
        self._update_screen()



if __name__ == '__main__':
    # Make a game instance and run the game
    ai = AlienInvasion()
    ai.run_game()