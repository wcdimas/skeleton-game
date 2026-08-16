# Stage 2: System Design & Documentation

This document explains the architecture of the custom Python browser engine we built in `poc2_pyscript/index.html`. 

## 1. The Camera System & Expanded Map
Instead of locking the player to an 800x600 screen, the map is now defined as 2500x2500 pixels.
- **The Camera Engine**: The `Camera` is simply two variables: `camera_x` and `camera_y`.
- **Logic**: Every frame, the engine updates the camera's coordinates to be exactly where the player is, minus half the screen width/height. This keeps the player perfectly centered. 
- **Clamping**: The camera is "clamped" (restricted) so it cannot show areas outside the 2500x2500 map.
- **Rendering Offset**: When drawing anything (enemies, grid, projectiles), we subtract `camera_x` and `camera_y` from their actual positions. If an enemy is at `x=1000`, and the camera is at `x=800`, the enemy is drawn on the canvas at `x=200`.

## 2. Procedural Graphics
To completely eliminate the need for external images and keep file sizes incredibly small, we use Python to interact directly with the HTML5 Canvas 2D Context.
- **`draw_skeleton()`**: Uses geometric shapes (arcs for the skull, lines for ribs) to draw the player.
- **`draw_wizard()`**: Uses polygons (the `moveTo` and `lineTo` functions) to draw cloaks and hats.
- By using `ctx.save()`, `ctx.translate()`, and `ctx.scale(-1, 1)`, we can flip the character based on which way they are facing without needing duplicate drawing code!

## 3. The Health Engine
We created a reusable `HealthSystem` class.
- **Components**: Both the `SkeletonPlayer` and `WizardEnemy` instantiate this class.
- **Invulnerability Frames (i-frames)**: When `take_damage()` is called, it triggers a `0.5s` timer. If the character takes damage again before the timer ends, it is ignored. This prevents a character from taking 60 instances of damage per second when standing inside a projectile!
- **Visual Feedback**: The characters blink (skip drawing on certain frames) while the timer is active.

## 4. Combat & Hitbox Manager
Combat is broken into two entities managed by the main `Engine`:
1. **Hitboxes**: When the player presses `Space`, a temporary invisible box (the sword swing) is spawned in front of them for 0.15 seconds. The engine checks if any wizard overlaps this box. If they do, the wizard's `HealthSystem` takes damage.
2. **Projectiles**: Wizards shoot lightning bolts. These are independent entities that travel along a calculated math vector (using trigonometry and distance formulas) toward where the player was standing. If they overlap the player, the player takes damage.

## 5. Wizard AI State Machine
The enemy wizards don't just walk toward the player blindly. They use a state machine based on their distance to the player:
- **`WANDER`**: If the player is far away (>600px), the wizard picks a random coordinate nearby and slowly walks to it, pausing randomly.
- **`CHASE`**: If the player enters their vision (<600px), they walk toward the player to get in range.
- **`ATTACK`**: If they are within sweet-spot range (<400px), they stop moving, aim, and spawn a lightning projectile toward the player. They wait for a cooldown timer before shooting again.
- **`FLEE`**: If the player charges at them and gets too close (<200px), they walk backwards to maintain a safe distance, preventing the player from easily swinging their sword.
- **Respawn System**: The main loop counts how many wizards are alive. If the count drops below a maximum limit, a hidden timer starts. After a few seconds, a new wizard is mathematically spawned far away from the player's current camera view.
