from enum import Enum

INFO = 'info'
SOCKET = 'socket'


class Logger():
    def __init__(self, levels: list):
        self.levels = set(levels)

    def log(self, level, message):
        if level in self.levels:
            print(f"[{level}]   {message}")