import curses
import random
import urllib.request
import urllib.error

import requests

STATUS_OFFICIAL = "official"
STATUS_VERIFIED = "verified"
STATUS_UNVERIFIED = "unverified"
STATUS_OFFLINE = "offline"

def fetch_remote_status(url, build_id):
    try:
        res = requests.get(url, timeout=2)
        data = res.json()
        builds = data.get("builds", {})
        status = builds.get(build_id, STATUS_UNVERIFIED)
        return status, data.get("message", ""), data
    except Exception:
        return STATUS_OFFLINE, "Keine Verbindung zur Lizenzprüfung", None

def draw_badge(win, status, sh, sw):
    if status == STATUS_OFFICIAL:
        text = "[ Offizielle Version ]"
    elif status == STATUS_VERIFIED:
        text = "[ Verifizierte Buildkopie ]"
    elif status == STATUS_UNVERIFIED:
        text = "[ Unverifizierte Buildkopie ]"
    else:
        text = "[ Offline – keine Prüfung ]"

    y = sh - 1
    x = max(0, sw - len(text) - 1)
    try:
        win.addstr(y, x, text)
    except curses.error:
        pass




# Score

score = 0

# Fenster vorbereiten
s = curses.initscr()
curses.curs_set(0) # Kein Cursor
sh, sw = s.getmaxyx()
w = curses.newwin(sh, sw, 0, 0) # Neues Fenster

# Hier einmal den Status abfragen
VERIFY_URL = "https://raw.githubusercontent.com/CodeProjects21/verify/refs/heads/main/verify_snake.json"
BUILD_ID = "v1.0.0"


status, server_msg, _ = fetch_remote_status(VERIFY_URL, BUILD_ID)

# Start Animation
intro_lines = [
    "┌─[🐍 Snake Game]──────────────────────────────┐",
    "│ Geschrieben von Benjamin · Sommer 2025       │",
    "│ Linux-Terminal required. Fun guaranteed.     │",
    "└──────────────────────────────────────────────┘"
]

start_y = sh//2 - len(intro_lines)//2
start_x = sw//2 - len(intro_lines[0])//2

for i, line in enumerate(intro_lines):
    w.addstr(start_y + i, start_x, line)
    w.refresh()
    curses.napms(400) # 400ms Pause pro Zeile

w.addstr(start_y + len(intro_lines) + 1, start_x, "Zum Starten beliebige Taste drücken...")
w.refresh()
w.getch()
w.clear()
w.refresh()


# Grundeinstellungen

w.keypad(1) # Pfeiltasten aktivieren
w.timeout(100)  # Snake-Geschwindigkeit (in ms)



# Snake Start Pos. und Nahrung
snk_x = sw//4 # Pos
snk_y = sh//2 # Pos
snake = [
    [snk_y, snk_x],
    [snk_y, snk_x-1],
    [snk_y, snk_x-2]
]
food = [sh//2, sw//2] # Nahrung
w.addch(food[0], food[1], curses.ACS_PI)


w.refresh()


# Startbewegung
key = curses.KEY_RIGHT

while True:
    next_key = w.getch()
    key = key if next_key == -1 else next_key

    if next_key == ord('p'):
        w.addstr(sh//2, sw//2 - 5, "PAUSE")
        w.refresh()
        while True:
            key2 = w.getch()
            if key2 != -1:  # weiter mit 'p'
                next_key = -1     # Letzten Key "verwerfen"
                break


    # Neu Pos. vom Kopf
    head = [snake[0][0], snake[0][1]]

    if key == curses.KEY_DOWN:
        head[0] += 1
    if key == curses.KEY_UP:
        head[0] -= 1
    if key == curses.KEY_LEFT:
        head[1] -= 1
    if key == curses.KEY_RIGHT:
        head[1] += 1

    draw_badge(w, status, sh, sw)

    # Gameover Bedingungen
    if head in snake or head[0] in [0,sh] or head[1] in [0, sw]:
        w.clear()
        msg = f"GAME OVER! Score: {score}"
        w.refresh()
        curses.napms(2000)
        curses.endwin()
        quit()

    snake.insert(0, head)

    # Futter essen or nicht
    if head == food:
        score += 1
        food = None
        while food is None:
            nf = [
                random.randint(1, sh-2),
                random.randint(1, sw-2)
            ]
            food = nf if nf not in snake else None
        w.addch(food[0], food[1], curses.ACS_PI)
    else:
        tail = snake.pop()
        w.addch(tail[0], tail[1], ' ')


    # Snake zeichnen
    w.addch(snake[0][0], snake[0][1], '#')
    draw_badge(w, status, sh, sw)
    w.border(0)

    # Score anzeigen (z.B. oben links):
    w.addstr(0, 2, f'Score: {score}')

    w.addch(snake[0][0], snake[0][1], '@')
    for y, x in snake[1:]:
        w.addch(y, x, 'o')
