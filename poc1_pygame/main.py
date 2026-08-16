import asyncio
import pygame

pygame.init()

# Setup screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skeleton Game - POC 1")

# Load skeleton sprite
# Scaling it down to 64x64 for the game
try:
    sprite_image = pygame.image.load("../assets/skeleton.jpg").convert()
    sprite_image = pygame.transform.scale(sprite_image, (64, 64))
except Exception as e:
    # Fallback to drawing a red square if image is missing
    print("Warning: Could not load sprite image. Using fallback.", e)
    sprite_image = pygame.Surface((64, 64))
    sprite_image.fill((255, 0, 0))

class Skeleton:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 64, 64)
        self.speed = 300 # pixels per second

    def update(self, dt, keys, obstacles):
        # Calculate movement
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT]:
            dx -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            dx += self.speed * dt
        if keys[pygame.K_UP]:
            dy -= self.speed * dt
        if keys[pygame.K_DOWN]:
            dy += self.speed * dt
        
        # Apply movement and check collisions on X axis
        self.rect.x += dx
        for obs in obstacles:
            if self.rect.colliderect(obs):
                if dx > 0: # moving right
                    self.rect.right = obs.left
                elif dx < 0: # moving left
                    self.rect.left = obs.right

        # Apply movement and check collisions on Y axis
        self.rect.y += dy
        for obs in obstacles:
            if self.rect.colliderect(obs):
                if dy > 0: # moving down
                    self.rect.bottom = obs.top
                elif dy < 0: # moving up
                    self.rect.top = obs.bottom

    def draw(self, surface):
        surface.blit(sprite_image, self.rect)

# Define some static obstacles for collision testing
obstacles = [
    pygame.Rect(200, 200, 100, 100),
    pygame.Rect(500, 300, 50, 200),
    pygame.Rect(300, 450, 200, 50)
]

# Create player in the center of the screen
player = Skeleton(WIDTH // 2, HEIGHT // 2)

async def main():
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # dt is time since last frame in seconds
        # tick(60) limits the loop to 60 FPS
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Get currently pressed keys
        keys = pygame.key.get_pressed()
        
        # Update game logic
        player.update(dt, keys, obstacles)
        
        # Render background
        screen.fill((50, 50, 50)) # dark gray background
        
        # Draw obstacles
        for obs in obstacles:
            pygame.draw.rect(screen, (100, 100, 100), obs)
            pygame.draw.rect(screen, (200, 200, 200), obs, 2) # border
            
        # Draw player
        player.draw(screen)
        
        pygame.display.flip()
        
        # This is REQUIRED for pygbag / WebAssembly to hand control back to the browser
        await asyncio.sleep(0)

# Run the game loop asynchronously
if __name__ == "__main__":
    asyncio.run(main())
