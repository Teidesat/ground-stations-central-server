
class StackBuffer:
    def __init__(self, maxsize:int):
        self.maxsize = maxsize
        self.stack = []

    def add(self, data):
        if self.is_full():
            return 'El stack esta lleno'
        self.stack.append(data)

    def get(self):
        if self.is_empty():
            return 'El stack esta vacío'
        return self.stack.pop()
    
    def is_full(self):
        return len(self.stack) == self.maxsize
    
    def is_empty(self):
        return len(self.stack) == 0