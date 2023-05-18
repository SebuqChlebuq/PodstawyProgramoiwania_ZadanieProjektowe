import sys

LINE_UP = '\033[2A'
LINE_DOWN = '\033[1B'
LINE_CLEAR = '\033[2K'
CURSOR_INVISIBLE = '\033[?25l'
CURSOR_VISIBLE = '\033[?25h'

cursorVisible = True

def setCursorAt(x, y):
    x = str(x)
    y = str(y)
    LINE_AT = '\033['+x+';'+y+'H'
    print(LINE_AT, end="")
    sys.stdout.flush()
