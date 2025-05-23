import os


def progress_bar(value, threshold=20):
    filled = int(threshold * value)
    empty = threshold - filled
    bar = "█" * filled + "-" * empty
    return f"[{bar}] {value:.0%}"


def clear():
    os.system("cls" if os.name == "nt" else "clear")
