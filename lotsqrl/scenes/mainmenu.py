import sys

from bearlibterminal import terminal


def main_screen_loop():
    terminal.clear()
    terminal.printf(20, 11, "  / _ \\")
    terminal.printf(20, 12, "\_\(_)/_/")
    terminal.printf(20, 13, " _//o\\\\_")
    terminal.printf(20, 14, "  /   \\")

    terminal.printf(30, 8, "Lair of the Spider Queen")
    terminal.printf(30, 16, "Goblins are infiltrating your lair.")
    terminal.printf(30, 17, "Punish them, feast on their corpses.")
    terminal.printf(30, 18, "Grow your army from their remains.")
    terminal.printf(30, 25, "Press any key to Start")
    terminal.refresh()
    e = terminal.read()
    if e == terminal.TK_CLOSE:
        sys.exit()
    terminal.clear()
