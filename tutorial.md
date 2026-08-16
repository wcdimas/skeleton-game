# Making a Python Browser Game: A Beginner's Guide

Welcome! If you're reading this, you want to learn how we built a simple browser-based game using Python. We created two "Proofs of Concept" (POCs). This guide will focus on explaining the **PyScript POC** (`poc2_pyscript/index.html`) since it builds a small game engine entirely from scratch directly in the browser!

## 1. Where We Started
To make a game run in the browser using Python, we used a tool called **PyScript**. PyScript allows us to write Python code inside a regular HTML website.

A game is essentially an infinite loop that runs incredibly fast (usually 60 times a second). In every cycle of this loop, the game does two main things:
1. **Update**: It checks if you pressed any keys, moves the characters, and checks if they hit any walls (collisions).
2. **Draw**: It clears the screen and redraws everything in their new positions.

This is called the **Game Loop**. Let's break down the code line by line!

## 2. Setting up the Website (HTML & CSS)
The first part of our file (`index.html`) is standard HTML. 
```html
<!DOCTYPE html>
<html lang="en">
...
```
- `<link rel="stylesheet" ...>` and `<script ... src="...core.js">`: This is where the magic happens. These two lines load PyScript into our website, giving the browser the ability to understand Python.
- `<style> ... </style>`: This is CSS. It just makes our website look pretty by centering the game, adding a dark background, and giving our game canvas a border.
- `<canvas id="gameCanvas" width="800" height="600"></canvas>`: The `canvas` is like a blank painting canvas. It's an 800x600 pixel rectangle where our Python code will draw the game.

## 3. The Python Engine
Inside the `<script type="py">` tag, we start writing Python!

### Importing Tools
```python
import asyncio
from js import document, window, Image, console
from pyodide.ffi import create_proxy
```
- `import asyncio`: Games need to pause for a tiny fraction of a second between frames (so the game doesn't run at lightspeed). `asyncio` lets us do that.
- `from js import ...`: Since Python is running in the browser, it needs a way to talk to the browser's JavaScript. We import `document` (the website), `window` (the browser window), and `Image` to load our sprite.

### Setting up the Canvas
```python
canvas = document.getElementById("gameCanvas")
ctx = canvas.getContext("2d")
WIDTH = canvas.width
HEIGHT = canvas.height
```
- We find our `<canvas>` by its ID (`gameCanvas`).
- We get the `2d` context (`ctx`), which is basically the "paintbrush" we use to draw rectangles, images, and lines.

### Loading the Sprite Image
```python
sprite_loaded = False
sprite_image = Image.new()
sprite_image.src = "../assets/skeleton.jpg"

def on_image_load(event):
    global sprite_loaded
    sprite_loaded = True
    document.getElementById("loading").innerText = "Game Running! Use Arrow Keys to move."
    
sprite_image.onload = on_image_load
```
- We create a new image and tell it where the skeleton file is located.
- Loading an image takes a little bit of time, so we create a function `on_image_load` that runs *only* when the image finishes loading. Once it's ready, we set `sprite_loaded` to `True`.

### Tracking Keyboard Input
```python
keys = { "ArrowLeft": False, "ArrowRight": False, "ArrowUp": False, "ArrowDown": False }

def keydown(event):
    if event.code in keys:
        keys[event.code] = True
        event.preventDefault() 

def keyup(event):
    if event.code in keys:
        keys[event.code] = False
        event.preventDefault()
```
- We create a dictionary `keys` to remember which arrow keys are currently being pressed.
- `keydown` triggers when you press a key down (setting it to `True`). `keyup` triggers when you let go (setting it to `False`).
- `event.preventDefault()` stops the web browser from scrolling down the page when you press the down arrow.

### Collision Detection (Math!)
```python
def rect_intersect(r1, r2):
    return not (r2["x"] >= r1["x"] + r1["w"] or 
                r2["x"] + r2["w"] <= r1["x"] or 
                r2["y"] >= r1["y"] + r1["h"] or 
                r2["y"] + r2["h"] <= r1["y"])
```
- This function checks if two rectangles (`r1` and `r2`) are overlapping. It's called **AABB** (Axis-Aligned Bounding Box) collision. It checks if rectangle 2 is entirely to the right, left, bottom, or top of rectangle 1. If it's *not* any of those, they must be colliding!

### The Skeleton Character
```python
class Skeleton:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 64
        self.h = 64
        self.speed = 300 # pixels per second
```
- A `class` is a blueprint for our character. `__init__` sets up the starting values: his X and Y coordinates (position), his width (`w`) and height (`h`), and his movement speed.

```python
    def update(self, dt, obstacles):
        dx = 0
        dy = 0
        if keys["ArrowLeft"]: dx -= self.speed * dt
        if keys["ArrowRight"]: dx += self.speed * dt
        # ... same for Up and Down ...
```
- `update` calculates how much the skeleton should move (`dx` and `dy`). 
- We multiply speed by `dt` (Delta Time - the time passed since the last frame). This ensures the skeleton moves at the same speed regardless of whether your computer runs the game at 30 FPS or 60 FPS.

```python
        # Apply X movement and resolve collisions
        self.x += dx
        rect = self.get_rect()
        for obs in obstacles:
            if rect_intersect(rect, obs):
                if dx > 0: # moving right
                    self.x = obs["x"] - self.w
                elif dx < 0: # moving left
                    self.x = obs["x"] + obs["w"]
```
- We move the skeleton on the X axis (left/right).
- Then, we loop through all `obstacles`. If the skeleton hits an obstacle while moving right, we push him back so his right side touches the obstacle's left side. This stops him from walking through walls! We repeat this exact logic for the Y axis (up/down).

```python
    def draw(self, ctx):
        if sprite_loaded:
            ctx.drawImage(sprite_image, self.x, self.y, self.w, self.h)
        else:
            ctx.fillStyle = "red"
            ctx.fillRect(self.x, self.y, self.w, self.h)
```
- If the image finished loading, we draw the skeleton sprite. If it's still loading, we just draw a red box as a placeholder.

### Creating the Game World
```python
obstacles = [
    {"x": 200, "y": 200, "w": 100, "h": 100},
    {"x": 500, "y": 300, "w": 50, "h": 200},
    {"x": 300, "y": 450, "w": 200, "h": 50}
]
player = Skeleton(WIDTH / 2, HEIGHT / 2)
```
- We define three walls (obstacles) with their X, Y, Width, and Height.
- We create our `player` exactly in the middle of the screen.

### The Game Loop
```python
async def main():
    last_time = window.performance.now()
    
    while True:
        # Calculate delta time (dt) in seconds
        current_time = window.performance.now()
        dt = (current_time - last_time) / 1000.0
        last_time = current_time
```
- We track the exact time right now, subtract the time of the previous frame, and convert it to seconds. That is our `dt`!

```python
        # Update game state
        player.update(dt, obstacles)
```
- We tell the player to move based on our keys and check for collisions.

```python
        # Clear screen
        ctx.fillStyle = "#323232"
        ctx.fillRect(0, 0, WIDTH, HEIGHT)
```
- We paint the whole screen a dark gray color to erase the old frame. If we didn't do this, the skeleton would leave a "trail" behind him everywhere he walked.

```python
        # Draw obstacles
        for obs in obstacles:
            ctx.fillStyle = "#646464"
            ctx.fillRect(obs["x"], obs["y"], obs["w"], obs["h"])

        # Draw player
        player.draw(ctx)
```
- We draw the obstacles, and then we draw the player on top.

```python
        # Yield to the browser (effectively a ~60 FPS sleep)
        await asyncio.sleep(1/60)
```
- Finally, we tell Python to pause for 1/60th of a second. This limits our game to 60 Frames Per Second (FPS) and stops our computer from overheating by running the loop millions of times a second.

```python
# Start the asynchronous game loop
asyncio.ensure_future(main())
```
- This kicks off the `main` loop we just built, and the game begins!
