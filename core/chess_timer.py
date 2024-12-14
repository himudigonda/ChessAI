class ChessTimer:
    def __init__(self, initial_time=600):
        self.white_time = initial_time
        self.black_time = initial_time
        self.active_color = True  # True for white, False for black
        self.running = False

    def switch_timer(self):
        self.active_color = not self.active_color
        self.running = True

    def update(self, elapsed_time):
        if self.running:
            if self.active_color:
                self.white_time -= elapsed_time
            else:
                self.black_time -= elapsed_time
