#!/usr/bin/env python3
import curses
import random
import time
import math
import os

NORSE_NAMES = ["HELLO"]

RUNES = "ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛇᛈᛉᛊᛏᛒᛖᛗᛚᛜᛝᛞᛟ"
GLITCH = "░▒▓█▄▀▌▐─│┌┐└┘├┤┬┴┼╔╗╚╝║═"
KATAKANA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"

ODIN_ASCII = [
    "  ▄██████▄  ████████▄   ▄█  ███▄▄▄▄   ",
    " ███    ███ ███   ▀███ ███  ███▀▀▀██▄  ",
    " ███    ███ ███    ███ ███▌ ███   ███  ",
    " ███    ███ ███    ███ ███▌ ███   ███  ",
    " ███    ███ ███    ███ ███▌ ███   ███  ",
    " ███    ███ ███    ███ ███  ███   ███  ",
    " ███    ███ ███   ▄███ ███  ███   ███  ",
    "  ▀██████▀  ████████▀  █▀    ▀█   █▀  ",
]

SUBTITLE = "O D I N   O D I N   O D I N"


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    for i, color in enumerate([
        curses.COLOR_GREEN, curses.COLOR_GREEN, curses.COLOR_CYAN,
        curses.COLOR_RED, curses.COLOR_YELLOW, curses.COLOR_MAGENTA,
        curses.COLOR_WHITE, curses.COLOR_BLUE,
    ], 1):
        curses.init_pair(i, color, -1)


class NorseRain:
    def __init__(self, height, width):
        self.h = height
        self.w = width
        self.drops = []
        self.max_drops = width // 3

    def spawn(self):
        if len(self.drops) >= self.max_drops or random.random() >= 0.4:
            return
        col = random.randint(0, self.w - 2)
        speed = random.uniform(0.3, 1.0)
        r = random.random()
        if r < 0.3:
            text = random.choice(NORSE_NAMES)
        elif r < 0.6:
            text = "".join(random.choice(RUNES) for _ in range(random.randint(2, 6)))
        else:
            text = "".join(random.choice(KATAKANA) for _ in range(random.randint(3, 8)))
        self.drops.append({
            "col": col, "row": -1, "speed": speed,
            "text": text, "age": 0.0,
            "color": random.choice([1, 2, 3, 6, 8]),
            "bright": random.random() < 0.3,
        })

    def update(self):
        alive = []
        for d in self.drops:
            d["age"] += d["speed"]
            d["row"] = int(d["age"])
            if d["row"] < self.h + 10:
                alive.append(d)
        self.drops = alive

    def draw(self, scr):
        for d in self.drops:
            row, col = d["row"], d["col"]
            text = d["text"]
            color = curses.color_pair(d["color"])
            if d["bright"]:
                color |= curses.A_BOLD
            for i, ch in enumerate(text):
                r = row - len(text) + i + 1
                if 0 <= r < self.h - 1 and 0 <= col < self.w - 1:
                    try:
                        if i == len(text) - 1:
                            scr.addch(r, col, ch, curses.color_pair(7) | curses.A_BOLD)
                        elif i < len(text) - 4:
                            scr.addch(r, col, ch, curses.color_pair(2))
                        else:
                            scr.addch(r, col, ch, color)
                    except curses.error:
                        pass
            for t in range(min(6, row)):
                tr = row - len(text) - t
                if 0 <= tr < self.h - 1 and 0 <= col < self.w - 1:
                    try:
                        scr.addch(tr, col, random.choice(".:·"), curses.color_pair(2))
                    except curses.error:
                        pass


def phase_void(scr, h, w):
    scr.clear()
    phrases = [
        "GINNUNGAGAP",
        "VON MISES",
        "",
        "   ...listening...",
    ]
    for idx, phrase in enumerate(phrases):
        row = h // 2 - 3 + idx
        col = max(0, w // 2 - len(phrase) // 2)
        if 0 <= row < h - 1:
            for i, ch in enumerate(phrase):
                if col + i < w - 1:
                    scr.addch(row, col + i, ch, curses.color_pair(2))
                    scr.refresh()
                    time.sleep(0.04)
        time.sleep(0.2)
    time.sleep(1.5)
    for _ in range(15):
        for _ in range(60):
            r = random.randint(0, h - 2)
            c = random.randint(0, w - 2)
            scr.addch(r, c, random.choice(GLITCH),
                      curses.color_pair(random.choice([2, 4, 6])))
        scr.refresh()
        time.sleep(0.05)


def phase_rain(scr, h, w, duration=7.0):
    rain = NorseRain(h, w)
    start = time.time()
    scr.clear()
    while time.time() - start < duration:
        scr.erase()
        rain.spawn()
        rain.spawn()
        rain.update()
        rain.draw(scr)
        if random.random() < 0.03:
            name = random.choice(NORSE_NAMES)
            fr = random.randint(0, h - 2)
            fc = random.randint(0, max(1, w - len(name) - 1))
            try:
                scr.addstr(fr, fc, name,
                           curses.color_pair(random.choice([5, 6, 4])) | curses.A_BOLD)
            except curses.error:
                pass
        scr.refresh()
        time.sleep(0.045)


def phase_convergence(scr, h, w):
    rain = NorseRain(h, w)
    for _ in range(200):
        rain.spawn()
        rain.update()

    logo_h = len(ODIN_ASCII)
    logo_w = max(len(l) for l in ODIN_ASCII)
    sr = h // 2 - logo_h // 2 - 2
    sc = w // 2 - logo_w // 2

    all_pos = [(ri, ci, ch) for ri, line in enumerate(ODIN_ASCII)
               for ci, ch in enumerate(line) if ch != ' ']
    random.shuffle(all_pos)

    revealed = set()
    cpf = max(1, len(all_pos) // 40)
    idx = 0

    while idx < len(all_pos):
        scr.erase()
        rain.spawn()
        rain.update()
        rain.draw(scr)
        for _ in range(min(cpf, len(all_pos) - idx)):
            revealed.add(all_pos[idx])
            idx += 1
        for (ri, ci, ch) in revealed:
            r, c = sr + ri, sc + ci
            if 0 <= r < h - 1 and 0 <= c < w - 1:
                try:
                    scr.addch(r, c, ch, curses.color_pair(3) | curses.A_BOLD)
                except curses.error:
                    pass
        if random.random() < 0.3:
            gr = sr + random.randint(0, logo_h - 1)
            gc = sc + random.randint(0, logo_w - 1)
            if 0 <= gr < h - 1 and 0 <= gc < w - 1:
                try:
                    scr.addch(gr, gc, random.choice(GLITCH),
                              curses.color_pair(random.choice([4, 6])) | curses.A_BOLD)
                except curses.error:
                    pass
        scr.refresh()
        time.sleep(0.06)

    sub_row = sr + logo_h + 2
    sub_col = max(0, w // 2 - len(SUBTITLE) // 2)
    for i in range(len(SUBTITLE)):
        scr.erase()
        rain.spawn()
        rain.update()
        rain.draw(scr)
        for (ri, ci, ch) in revealed:
            r, c = sr + ri, sc + ci
            if 0 <= r < h - 1 and 0 <= c < w - 1:
                try:
                    scr.addch(r, c, ch, curses.color_pair(3) | curses.A_BOLD)
                except curses.error:
                    pass
        if 0 <= sub_row < h - 1:
            try:
                scr.addstr(sub_row, sub_col, SUBTITLE[:i + 1],
                           curses.color_pair(5) | curses.A_BOLD)
            except curses.error:
                pass
        scr.refresh()
        time.sleep(0.04)

    scr.refresh()
    time.sleep(2.0)



def phase_final(scr, h, w):
    rain = NorseRain(h, w)
    rain.max_drops = w // 2
    logo_h = len(ODIN_ASCII)
    logo_w = max(len(l) for l in ODIN_ASCII)
    sr = h // 2 - logo_h // 2 - 1
    sc = w // 2 - logo_w // 2
    scr.nodelay(True)
    scr.timeout(45)
    exit_msg = "[ press any key to exit the simulation ]"
    exit_col = max(0, w // 2 - len(exit_msg) // 2)
    pulse = 0.0

    while True:
        scr.erase()
        rain.spawn()
        rain.spawn()
        rain.spawn()
        rain.update()
        rain.draw(scr)
        pulse += 0.15
        bright = (1 + math.sin(pulse)) / 2
        lc = curses.color_pair(3) | (curses.A_BOLD if bright > 0.5 else 0)
        for ri, line in enumerate(ODIN_ASCII):
            for ci, ch in enumerate(line):
                if ch != ' ':
                    r, c = sr + ri, sc + ci
                    if 0 <= r < h - 1 and 0 <= c < w - 1:
                        try:
                            scr.addch(r, c, ch, lc)
                        except curses.error:
                            pass
        sub_row = sr + logo_h + 1
        sub_col = max(0, w // 2 - len(SUBTITLE) // 2)
        if 0 <= sub_row < h - 1:
            try:
                scr.addstr(sub_row, sub_col, SUBTITLE,
                           curses.color_pair(5) | curses.A_BOLD)
            except curses.error:
                pass
        if int(pulse * 2) % 3 != 0:
            try:
                scr.addstr(h - 1, exit_col, exit_msg, curses.color_pair(2))
            except curses.error:
                pass
        if random.random() < 0.05:
            name = random.choice(NORSE_NAMES)
            try:
                scr.addstr(0, 0, f" {name} ",
                           curses.color_pair(random.choice([4, 5, 6])) | curses.A_BOLD)
            except curses.error:
                pass
        scr.refresh()
        if scr.getch() != -1:
            break

    scr.nodelay(False)
    scr.erase()
    farewell = [
        "",
        "  ─── GOD MORGEN ───",
        "",
    ]
    for i, line in enumerate(farewell):
        row = h // 2 - len(farewell) // 2 + i
        col = max(0, w // 2 - len(line) // 2)
        if 0 <= row < h - 1:
            try:
                c = curses.color_pair(3) if i in (1, 3, 4, 5, 6) else curses.color_pair(2)
                scr.addstr(row, col, line, c)
            except curses.error:
                pass
    scr.refresh()
    time.sleep(3)


def main(scr):
    curses.curs_set(0)
    init_colors()
    scr.clear()
    scr.scrollok(True)
    h, w = scr.getmaxyx()
    if h < 20 or w < 60:
        scr.addstr(0, 0, "Terminal too small. Need 60x20+.", curses.color_pair(4))
        scr.refresh()
        time.sleep(3)
        return
    phase_void(scr, h, w)
    phase_rain(scr, h, w, duration=7.0)
    phase_convergence(scr, h, w)
    phase_final(scr, h, w)


if __name__ == "__main__":
    os.environ.setdefault("ESCDELAY", "25")
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n  GOD MORGEN.\n")
