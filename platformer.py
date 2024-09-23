import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 60
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 50
POWER_UP_SIZE = 30
BULLET_WIDTH = 5
BULLET_HEIGHT = 5
BULLET_SPEED = 10
PLAYER_SPEED = 5
PLAYER_HEALTH = 100
MAX_ENEMIES = 5  # Maximum number of enemies on screen
POWER_UP_SPAWN_TIME = 300  # Time in frames to wait before spawning a power-up

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wave-Based Shooting Game")

# Player class
class Player:
    def __init__(self):
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill((0, 128, 255))
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT // 2 - PLAYER_HEIGHT // 2  # Center vertically
        self.health = PLAYER_HEALTH
        self.invincible = False
        self.invincible_timer = 0

    def draw(self, surface):
        if self.invincible:
            # Flash rainbow colors
            color = (255, 0, 0) if (self.invincible_timer // 5) % 2 == 0 else (0, 0, 255)
            self.image.fill(color)
        else:
            self.image.fill((0, 128, 255))
        surface.blit(self.image, self.rect)
        # Draw health bar
        health_ratio = self.health / PLAYER_HEALTH
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 10, PLAYER_WIDTH, 5))  # Red background
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 10, PLAYER_WIDTH * health_ratio, 5))  # Green health bar

    def move(self, direction):
        if direction == 'up' and self.rect.top > 0:
            self.rect.y -= PLAYER_SPEED
        elif direction == 'down' and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += PLAYER_SPEED

    def update(self):
        if self.invincible:
            self.invincible_timer += 1
            if self.invincible_timer >= 15 * FPS:  # 15 seconds
                self.invincible = False

# Enemy class
class Enemy:
    def __init__(self, existing_enemies):
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = self.get_non_overlapping_position(existing_enemies)
        self.health = 1  # Normal enemies have 1 health

    def get_non_overlapping_position(self, existing_enemies):
        while True:
            y_position = random.randint(0, SCREEN_HEIGHT - ENEMY_HEIGHT - 10)
            # Check for overlap with existing enemies
            overlap = False
            for enemy in existing_enemies:
                if abs(y_position - enemy.rect.y) < ENEMY_HEIGHT:  # If close, overlap occurs
                    overlap = True
                    break
            if not overlap:
                return y_position

    def update(self):
        self.rect.x -= 2  # Move the enemy left

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# SpecialEnemy class
class SpecialEnemy(Enemy):
    def __init__(self, existing_enemies):
        super().__init__(existing_enemies)
        self.image.fill((0, 255, 0))  # Different colour for special enemy
        self.health = 3  # Special enemies have 3 health

    def draw(self, surface):
        super().draw(surface)
        # Draw health bar
        health_ratio = self.health / 3  # Normalize health for display
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 10, ENEMY_WIDTH, 5))  # Red background
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 10, ENEMY_WIDTH * health_ratio, 5))  # Green health bar

# Bullet class
class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BULLET_WIDTH, BULLET_HEIGHT)
        self.velocity = (BULLET_SPEED, 0)  # Move horizontally to the right

    def update(self):
        self.rect.x += self.velocity[0]

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect)

# PowerUp class
class PowerUp:
    def __init__(self):
        self.image = pygame.Surface((POWER_UP_SIZE, POWER_UP_SIZE))
        self.image.fill((255, 255, 0))  # Yellow star
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(0, SCREEN_HEIGHT - POWER_UP_SIZE - 10)

    def update(self):
        self.rect.x -= 2  # Move the power-up left

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Main execution block
if __name__ == "__main__":
    player = Player()
    enemies = []
    bullets = []
    power_ups = []
    score = 0
    clock = pygame.time.Clock()
    enemy_spawn_timer = 0
    power_up_timer = 0
    wave_number = 1
    enemies_per_wave = 3
    enemies_remaining = enemies_per_wave
    wave_complete = False
    special_enemy_spawned = False
    invincibility_spawned = 0  # To track how many times the invincibility has been spawned

    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Fire bullet when spacebar is pressed
                    bullets.append(Bullet(player.rect.x + PLAYER_WIDTH, player.rect.y + PLAYER_HEIGHT // 2))

        # Movement controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player.move('up')
        if keys[pygame.K_s]:
            player.move('down')

        # Spawn enemies if wave is not complete
        if not wave_complete:
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= 30 and len(enemies) < min(enemies_per_wave, MAX_ENEMIES):  # Spawn rate
                if not special_enemy_spawned and wave_number % 5 == 0 and random.random() < 0.5:
                    enemies.append(SpecialEnemy(enemies))
                    special_enemy_spawned = True
                else:
                    enemies.append(Enemy(enemies))
                enemy_spawn_timer = 0

        # Spawn power-ups
        if invincibility_spawned < wave_number // 4:  # Allow to spawn only once every 4 rounds
            power_up_timer += 1
            if power_up_timer >= POWER_UP_SPAWN_TIME and random.random() < 0.1:  # 10% chance to spawn
                power_ups.append(PowerUp())
                invincibility_spawned += 1  # Track how many times the power-up has spawned
                power_up_timer = 0

        # Update game objects
        for enemy in enemies:
            enemy.update()
        for bullet in bullets:
            bullet.update()
        for power_up in power_ups:
            power_up.update()

        # Check for collisions between bullets and enemies
        for bullet in bullets[:]:  # Use a copy of the list to avoid modifying while iterating
            for enemy in enemies[:]:  # Use a copy of the list to avoid modifying while iterating
                if bullet.rect.colliderect(enemy.rect):
                    bullets.remove(bullet)
                    if isinstance(enemy, SpecialEnemy):
                        enemy.health -= 1  # Decrease health for special enemy
                        if enemy.health <= 0:
                            enemies.remove(enemy)  # Remove special enemy when killed
                            score += 5  # 5 points for special enemy
                            enemies_remaining -= 1
                    else:
                        enemies.remove(enemy)  # Remove normal enemy when hit
                        score += 1
                        enemies_remaining -= 1
                    break

        # Check for collisions with power-ups
        for power_up in power_ups[:]:
            if power_up.rect.colliderect(player.rect):
                player.invincible = True
                player.invincible_timer = 0
                power_ups.remove(power_up)  # Remove the power-up when collected

        # Check if all enemies are defeated
        if enemies_remaining <= 0 and not wave_complete:
            wave_complete = True

        # Check for enemies passing the player
        for enemy in enemies[:]:
            if enemy.rect.x < 0:  # If enemy goes off the screen
                if not player.invincible:
                    player.health -= 10  # Lose health when an enemy reaches the player
                enemies.remove(enemy)

        # Handle wave completion
        if wave_complete:
            wave_complete_text = pygame.font.Font(None, 55).render(f"Wave {wave_number} complete! Press any key to continue.", True, WHITE)
            screen.blit(wave_complete_text, (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        waiting = False
                        wave_number += 1
                        enemies_per_wave += 1  # Increase enemies per wave
                        enemies_remaining = enemies_per_wave
                        enemies.clear()  # Clear existing enemies
                        special_enemy_spawned = False
                        wave_complete = False

        # Clear the screen
        screen.fill((135, 206, 235))  # Light blue background

        # Draw game objects
        player.update()
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for power_up in power_ups:
            power_up.draw(screen)

        # Draw invincibility timer bar if active
        if player.invincible:
            invincibility_remaining = 15 - (player.invincible_timer // FPS)  # Remaining time in seconds
            timer_width = 400 * (invincibility_remaining / 15)
            pygame.draw.rect(screen, (0, 255, 0), (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 30, timer_width, 20))  # Green bar

        # Display score
        score_surface = pygame.font.SysFont(None, 36).render(f"Score: {score}", True, WHITE)
        screen.blit(score_surface, (10, 10))

        # Display game over
        if player.health <= 0:
            game_over_surface = pygame.font.SysFont(None, 55).render("Game Over", True, WHITE)
            screen.blit(game_over_surface, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        waiting = False
                        player.health = PLAYER_HEALTH  # Reset health
                        score = 0
                        wave_number = 1
                        enemies_per_wave = 3
                        enemies_remaining = enemies_per_wave
                        enemies.clear()  # Clear existing enemies
                        invincibility_spawned = 0  # Reset power-up spawn tracker

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)
