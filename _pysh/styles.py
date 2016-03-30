import sys


def define_style(code):
    if sys.stdout.isatty():
        return "\033[{}m".format(code)
    return ""


STYLES = {
    "PLAIN": define_style(0),
    "RED": define_style(31),
    "GREEN": define_style(32),
    "YELLOW": define_style(33),
    "CYAN": define_style(36),
}
