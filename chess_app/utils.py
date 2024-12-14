# chess_app/utils.py

import chess.engine
import chess.pgn

class AIPlayer:
    def __init__(self, engine_path, depth=2):
        self.engine_path = engine_path
        self.depth = depth
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)

    def set_depth(self, depth):
        self.depth = depth

    def get_best_move(self, board):
        try:
            result = self.engine.play(board, chess.engine.Limit(depth=self.depth))
            return result.move
        except Exception as e:
            print(f"Error getting best move: {e}")
            return None

    def get_evaluation(self, board):
        """
        Returns the current evaluation of the board in centipawns.
        """
        try:
            info = self.engine.analyse(board, chess.engine.Limit(depth=1))
            score = info["score"].white()
            if score.is_mate():
                # Assign a high value for mate in X
                mate_score = 100000 if score.mate() > 0 else -100000
                return mate_score
            else:
                return score.score()
        except Exception as e:
            print(f"Error getting evaluation: {e}")
            return 0  # Neutral evaluation in case of error

    def close(self):
        self.engine.quit()

class GameAnalyzer:
    def __init__(self, engine_path, depth=3):
        self.engine_path = engine_path
        self.depth = depth
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
    
    def analyze_game(self, board):
        """
        Analyzes the game by iterating through all moves and collecting evaluations.
        Returns a list of tuples: (move, evaluation)
        """
        analysis = []
        temp_board = chess.Board()
        for move in board.move_stack:
            temp_board.push(move)
            try:
                info = self.engine.analyse(temp_board, chess.engine.Limit(depth=self.depth))
                score = info["score"].white()
                if score.is_mate():
                    eval_score = 100000 if score.mate() > 0 else -100000
                else:
                    eval_score = score.score()
                analysis.append((move, eval_score))
            except Exception as e:
                print(f"Error analyzing move {move}: {e}")
                analysis.append((move, 0))  # Neutral evaluation in case of error
        return analysis
    
    def close(self):
        self.engine.quit()

class SaveLoad:
    @staticmethod
    def save_game(board, filename):
        """
        Saves the current game to a PGN file.
        """
        game = chess.pgn.Game.from_board(board)
        with open(filename, 'w') as f:
            f.write(str(game))
    
    @staticmethod
    def load_game(filename):
        """
        Loads a game from a PGN file and returns a chess.Board object.
        """
        with open(filename, 'r') as f:
            game = chess.pgn.read_game(f)
        if game is None:
            raise ValueError("No game found in the PGN file.")
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
        return board

class SoundEffects:
    def __init__(self):
        import pygame
        pygame.mixer.init()
        try:
            self.move_sound = pygame.mixer.Sound("assets/sounds/move.mp3")
            self.capture_sound = pygame.mixer.Sound("assets/sounds/capture.mp3")
        except pygame.error as e:
            print(f"Error loading sound files: {e}")
            self.move_sound = None
            self.capture_sound = None
    
    def play_move(self):
        if self.move_sound:
            self.move_sound.play()
    
    def play_capture(self):
        if self.capture_sound:
            self.capture_sound.play()

class Theme:
    def __init__(self, app):
        self.app = app
        self.current_theme = "light"
    
    def apply_light_theme(self):
        self.app.root.configure(bg="#F5F5F7")
        self.app.side_panel_frame.configure(bg="#FFFFFF")
        # Update other widgets' backgrounds and foregrounds as needed
    
    def apply_dark_theme(self):
        self.app.root.configure(bg="#2E2E2E")
        self.app.side_panel_frame.configure(bg="#3C3F41")
        # Update other widgets' backgrounds and foregrounds as needed
    
    def toggle_theme(self):
        if self.current_theme == "light":
            self.apply_dark_theme()
            self.current_theme = "dark"
        else:
            self.apply_light_theme()
            self.current_theme = "light"

class Timer:
    @staticmethod
    def format_time(white_time, black_time):
        white_minutes = white_time // 60
        white_seconds = white_time % 60
        black_minutes = black_time // 60
        black_seconds = black_time % 60
        return f"White: {white_minutes:02}:{white_seconds:02} - Black: {black_minutes:02}:{black_seconds:02}"