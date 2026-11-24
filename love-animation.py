import tkinter as tk
import math
import random
import os
import ctypes

# --- Maximum Sharpness on Windows (High-DPI) ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# --- Optional Audio Setup ---
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

# --- Configuration ---
WIDTH, HEIGHT = 680, 680
CX, CY = WIDTH // 2, HEIGHT // 2

BG_COLOR = "#120e1f"
GOLD = "#f0cb86"
GOLD_GLOW = "#5c4727"
DIM_TEXT = "#7e72a6"
BRIGHT_TEXT = "#ffe2a8"
RING_COLOR = "#342a52"

# Audio settings
SONG_FILE = "song.mp3"       # Keep song.mp3 in the same folder as this script
SONG_START_SEC = 0.0         # Change if you want to start mid-song
SONG_DURATION_SEC = 31.0     # Plays for 45 seconds then fades out

# Timing settings (~60 FPS)
REVEAL_INTERVAL = 31     # Slow & smooth reveal
FADE_FRAMES = 55.0

PHRASES = [
    "I love you", "You mean the world to me", "My heart is yours",
    "Forever and always", "You are my home", "I adore you",
    "You complete me", "My favorite person", "I'm yours",
    "You are my sunshine", "Love you endlessly", "My soulmate",
    "You make me whole", "Always on my mind", "You're my everything",
    "I cherish you", "Better together", "My one and only",
    "You steal my breath", "Crazy about you", "My safe place",
    "Love at first sight", "You are magic", "My heart beats for you",
    "Lucky to have you", "You're my peace", "Head over heels",
    "My sweetest dream", "You light up my life", "Endlessly in love",
    "You're my anchor", "Together forever", "My greatest blessing",
    "I'm so into you", "You're my happiness", "Lost in your eyes",
    "My best friend", "Love you to the moon", "You're irreplaceable",
    "My heart chose you", "Every day with you", "You're my lifeline",
    "Purest love", "You're my universe", "Always by your side",
    "My forever love", "You make me smile", "Deeply in love",
    "You're my destiny", "Simply love you"
]

N = len(PHRASES)

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def lerp_color(c1, c2, t):
    t = clamp(t)
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return f"#{int(r1 + (r2 - r1) * t):02x}{int(g1 + (g2 - g1) * t):02x}{int(b1 + (b2 - b1) * t):02x}"

# --- Start Music ---
music_playing = False
music_fading = False
script_dir = os.path.dirname(os.path.abspath(__file__))
audio_path = os.path.join(script_dir, SONG_FILE)

if not HAS_PYGAME:
    print("❌ Audio off: pygame is not installed.")
elif not os.path.exists(audio_path):
    print(f"❌ Audio off: '{SONG_FILE}' not found in folder: {script_dir}")
else:
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play(start=SONG_START_SEC)
        music_playing = True
        print(f"✅ Playing: {SONG_FILE}")
    except Exception as e:
        print(f"❌ Audio error: {e}")

# --- Window Setup ---
root = tk.Tk()
root.title(f"{N} Ways to Say I Love You")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR, highlightthickness=0)
canvas.pack()

INNER_R = 122
OUTER_R = 308

# Twinkling background stars
stars = []
for _ in range(85):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    r = random.uniform(0.6, 1.5)
    speed = random.uniform(0.05, 0.16)
    phase = random.uniform(0, math.tau)
    twinkle_speed = random.uniform(0.02, 0.05)
    item = canvas.create_oval(x - r, y - r, x + r, y + r, fill="#3d335c", outline="")
    stars.append([item, x, y, r, speed, phase, twinkle_speed])

# Solid dark center disc
canvas.create_oval(
    CX - INNER_R, CY - INNER_R, CX + INNER_R, CY + INNER_R,
    fill=BG_COLOR, outline=RING_COLOR, width=1.5
)
canvas.create_oval(
    CX - (INNER_R - 7), CY - (INNER_R - 7), CX + (INNER_R - 7), CY + (INNER_R - 7),
    outline="#221a38", width=1
)

# Layered outer golden arcs (progress bar)
outer_arc_glow = canvas.create_arc(
    CX - OUTER_R, CY - OUTER_R, CX + OUTER_R, CY + OUTER_R,
    start=90, extent=0, style=tk.ARC, outline=GOLD_GLOW, width=5
)
outer_arc = canvas.create_arc(
    CX - OUTER_R, CY - OUTER_R, CX + OUTER_R, CY + OUTER_R,
    start=90, extent=0, style=tk.ARC, outline=GOLD, width=2
)

# Crisp Center Text Elements
canvas.create_text(
    CX, CY - 46, text=f"{N} WAYS TO SAY\nI LOVE YOU",
    fill=GOLD, font=("Segoe UI", 9, "bold"), justify="center"
)
center_phrase = canvas.create_text(
    CX, CY + 6, text="",
    fill="#f7f0fa", font=("Times New Roman", 15, "italic"), width=200, justify="center"
)
canvas.create_line(CX - 26, CY + 42, CX + 26, CY + 42, fill=GOLD, width=1)
center_counter = canvas.create_text(
    CX, CY + 58, text=f"1 / {N}",
    fill=DIM_TEXT, font=("Segoe UI", 9)
)
hint_text = canvas.create_text(
    CX, CY + 78, text="",
    fill="#9e8ec7", font=("Segoe UI", 8)
)

tick = 0
shown = 0
done_t = None
cur = 0
center_fade = 0.0

def show_center(idx):
    global cur, center_fade
    cur = idx
    center_fade = 0.0
    canvas.itemconfig(center_phrase, text=PHRASES[idx])
    canvas.itemconfig(center_counter, text=f"{idx + 1} / {N}")

def on_spoke_click(idx):
    # Allow user to click any revealed phrase to read it
    if spokes[idx]["born"] is not None:
        show_center(idx)

def on_key(event):
    # Arrow keys to browse phrases after completion
    if done_t is None:
        return
    if event.keysym in ("Right", "Down"):
        show_center((cur + 1) % N)
    elif event.keysym in ("Left", "Up"):
        show_center((cur - 1) % N)

root.bind("<Key>", on_key)

# Spokes setup
spokes = []
for i, text in enumerate(PHRASES):
    deg = (90 - (i * 360.0 / N)) % 360
    rad = math.radians(deg)

    if 90 < deg < 270:
        text_angle = deg - 180
        anchor = "e"
    else:
        text_angle = deg
        anchor = "w"

    item = canvas.create_text(
        CX, CY, text=text, fill=BG_COLOR,
        font=("Segoe UI", 8), angle=text_angle, anchor=anchor
    )

    # Make each phrase clickable
    canvas.tag_bind(item, "<Button-1>", lambda e, idx=i: on_spoke_click(idx))
    canvas.tag_bind(item, "<Enter>", lambda e: canvas.config(cursor="hand2"))
    canvas.tag_bind(item, "<Leave>", lambda e: canvas.config(cursor=""))

    spokes.append({
        "item": item,
        "rad": rad,
        "born": None,
    })

def on_close():
    if music_playing:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

def step():
    global tick, shown, done_t, center_fade, music_fading
    tick += 1

    # 45-second song fadeout
    if music_playing and not music_fading:
        elapsed_sec = tick * 0.016
        if elapsed_sec >= (SONG_DURATION_SEC - 3.0):
            pygame.mixer.music.fadeout(3000)
            music_fading = True

    # Drift & twinkle stars
    for s in stars:
        s[2] -= s[4]
        if s[2] < -5:
            s[2] = HEIGHT + 5
        canvas.coords(s[0], s[1] - s[3], s[2] - s[3], s[1] + s[3], s[2] + s[3])
        twinkle = 0.5 + 0.5 * math.sin(tick * s[6] + s[5])
        star_col = lerp_color("#251e3b", "#8a7eb5", twinkle)
        canvas.itemconfig(s[0], fill=star_col)

    # Reveal spokes slowly one by one, then STOP when complete
    if shown < N and (tick - 1) % REVEAL_INTERVAL == 0:
        spokes[shown]["born"] = tick
        show_center(shown)
        shown += 1
        if shown == N:
            done_t = tick
            canvas.itemconfig(hint_text, text="Click any line to read")

    # Smoothly animate outer golden ring (stops at full circle)
    total_reveal_ticks = N * REVEAL_INTERVAL
    progress = clamp(tick / total_reveal_ticks)
    arc_extent = -359.9 * progress
    canvas.itemconfig(outer_arc_glow, extent=arc_extent)
    canvas.itemconfig(outer_arc, extent=arc_extent)

    # Smooth fade-in for center phrase
    if center_fade < 1.0:
        center_fade = clamp(center_fade + 0.05)
        e_fade = 1 - (1 - center_fade) ** 3
        canvas.itemconfig(center_phrase, fill=lerp_color(BG_COLOR, "#f7f0fa", e_fade))

    # Spokes: slide out and highlight ONLY the selected phrase
    for i, p in enumerate(spokes):
        if p["born"] is None:
            continue
        u = clamp((tick - p["born"]) / FADE_FRAMES)
        e = 1 - (1 - u) ** 3

        r = INNER_R + 12 + (20 * e)
        x = CX + math.cos(p["rad"]) * r
        y = CY - math.sin(p["rad"]) * r
        canvas.coords(p["item"], x, y)

        base_col = lerp_color(BG_COLOR, DIM_TEXT, e)
        final_col = BRIGHT_TEXT if i == cur else base_col
        canvas.itemconfig(p["item"], fill=final_col)

    root.after(16, step)

step()
root.mainloop()