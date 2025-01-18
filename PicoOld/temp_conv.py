class channel_cal:
    def __init__(self, c0, c1):
        self.c0 = c0
        self.c1 = c1
    
    def convert(self, x):
        temp = self.c0 * x + self.c1
        return temp
        
    