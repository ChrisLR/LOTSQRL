from bearlibterminal import terminal


def draw_help_file():
    terminal.clear()
    lines = []
    try:
        with open("manual.txt", "r") as manual_file:
            lines = manual_file.readlines()

        for i, line in enumerate(lines):
            terminal.printf(1, i, line)
        terminal.refresh()
    except Exception:
        terminal.printf(1, 5, "Could not load manual file! Press any key to continue playing")
        terminal.refresh()
    terminal.read()
