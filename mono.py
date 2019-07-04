import arcade
import random
import os


SURFACE = {}


class Checker:

    def __init__(self):

        # Core object attributes:
        self.position = None
        self.color = None
        self.queen = False
        
        # Move/attack lists, can be empty:
        self.move_list = []
        self.attack_list = []
        
        self._texture = None
        self._selected = False

    @property
    def _ready(self):
        return True if self._texture is not None else False

    def build(self, init_color: str, init_position: list):
        self.color = init_color
        self.position = init_position
        # texture_name = '{object}{type}_{color}.png'.format(
        #     object='checker',
        #     type='_queen' if self.queen else '',
        #     color=self.color
        # )
        # texture_path = os.path.join(os.path.dirname(__file__), f'images/{texture_name}')
        # self._texture = arcade.load_texture(
        #     file_name=texture_path,
        #     mirrored=False,
        #     flipped=False,
        #     scale=1
        # )

    @property
    def coordinates(self):
        coordinates = Board.convert_board_position_to_coordinates(self.position)
        return coordinates

    @property
    def can_promote(self):
        result = False
        row, column = self.position
        if self.color == 'White' and row == 8 or self.color == 'Black' and row == 1:
            result = True
        return result

    @property
    def can_move(self):
        return True if self.move_list else False

    @property
    def can_attack(self):
        return True if self.attack_list else False

    def select(self):
        self._selected = True
        self._selected_angle = random.choice((random.randint(-22, -12), random.randint(12, 22)))

    def deselect(self):
        self._selected = False
        self._selected_angle = 0

    def display(self):

        # If checker object contains a texture, rendering texture:
        if self._ready:
            arcade.draw_texture_rectangle(
                center_x=0,
                center_y=0,
                width=self.texture.width,
                height=self.texture.height,
                texture=self.texture,
                angle=0 if not self._selected else self._selected_angle,
                alpha=255,
            )
        
        # Otherwise, checker object will use primitive shapes to "construct" a visual representative of itself:
        else:

            # Acquiring color palettes and coordinates:
            coord_x, coord_y = self.coordinates
            color_white_main = [230, 230, 225]
            color_white_alt = [200, 200, 200]
            color_black_main = [135, 75, 60]
            color_black_alt = [80, 20, 15]

            # Rendering outer radius:
            arcade.draw_circle_filled(
                center_x=coord_x + 2,
                center_y=coord_y + 1,
                radius=int(64 * 0.90 / 2),
                color=color_white_alt if self.color == 'White' else 
                      color_black_alt if self.color == 'Black' else 
                      arcade.color.RED_DEVIL,
                num_segments=64
            )
            arcade.draw_circle_filled(
                center_x=coord_x - 2,
                center_y=coord_y - 1,
                radius=int(64 * 0.90 / 2),
                color=color_white_main if self.color == 'White' else 
                      color_black_main if self.color == 'Black' else 
                      arcade.color.RUSTY_RED,
                num_segments=64
            )

            # Rendering inner radius:
            arcade.draw_circle_filled(
                center_x=coord_x - 2,
                center_y=coord_y - 1,
                radius=int(64 * 0.90 * 0.65 / 2),
                color=color_white_alt if self.color == 'White' else 
                      color_black_alt if self.color == 'Black' else 
                      arcade.color.RED_DEVIL,
                num_segments=64
            )
            arcade.draw_circle_filled(
                center_x=coord_x + 2,
                center_y=coord_y + 1,
                radius=int(64 * 0.90 * 0.65 / 2),
                color=color_white_main if self.color == 'White' else 
                      color_black_main if self.color == 'Black' else 
                      arcade.color.RUSTY_RED,
                num_segments=64
            )

            # If checker is queen, rendering a stamp:
            if self.queen:
                arcade.draw_text(
                    text='Q',
                    start_x=coord_x,
                    start_y=coord_y,
                    color=color_white_alt if self.color == 'White' else 
                          color_black_alt if self.color == 'Black' else 
                          arcade.color.RED_DEVIL,
                    font_name='georgia',
                    font_size=12,
                    align='center',
                    bold=False,
                    italic=False,
                    anchor_x='center',
                    anchor_y='center'
                )

    def move(self, board_position: list):

        # Moving self to a new dictionary position in SURFACE, removing itself from old position:
        new_row, new_column = board_position
        old_row, old_column = self.position
        Board.clear_board_position(self.position)
        Board.put_checker_on_board_position(self, board_position)

        # Removing checker objects between new and old positioins:
        positions_between = Board.get_positions_between(self.position, board_position)
        if positions_between:
            for position in positions_between:
                Board.clear_board_position(position)

        # Assigning new position and checking if can promote:
        self.position = board_position
        if self.can_promote:
            self.promote()

    def promote(self):
        if not self.queen:
            self.queen = True
            self.build()

    def look_around(self):
        self.move_list = []
        self.attack_list = []
        for axis_x in (-1, 1):
            attacking = False
            for axis_y in (-1, 1):
                peek_position = self.position
                forward = False
                if axis_y == 1 and self.color == 'White' or axis_y == -1 and self.color == 'Black':
                    forward = True
                while True:
                    peek_position = [peek_position[0] + axis_y, peek_position[1] + axis_x]
                    if Board.assert_board_position_is_valid(peek_position):
                        if Board.assert_board_position_is_empty(peek_position):
                            if attacking:
                                self.move_list.append(peek_position)
                                self.attack_list.append(peek_position)
                                if not self.queen:
                                    break
                            else:
                                if forward:
                                    self.move_list.append(peek_position)
                                    if not self.queen:
                                        break
                                else:
                                    if self.queen:
                                        self.move_list.append(peek_position)
                                    else:
                                        break
                        else:
                            checker_encountered = Board.get_checker_by_position(peek_position)
                            if checker_encountered.color == self.color:
                                break
                            else:
                                if not attacking:
                                    attacking = True
                                else:
                                    break
                    else:
                        break

    def update(self):
        self.look_around()


class Board:

    TILE_SIDE_LEN = 64
    TILE_COUNT_ROW = 8
    TILE_COUNT_COLUMN = 8
    TILE_COLOR_LIGHT = [255, 210, 155]
    TILE_COLOR_DARK = [25, 20, 20]

    MARGIN_OUTER_LEN = 14
    MARGIN_INNER_LEN = 2
    MARGIN_LEN = 16
    MARGIN_OUTER_COLOR = TILE_COLOR_DARK
    MARGIN_INNER_COLOR = TILE_COLOR_LIGHT
    MARGIN_INDEX_LETTERS = 'ABCDEFGH'
    MARGIN_INDEX_NUMBERS = '12345678'

    BOARD_SIDE_LEN = MARGIN_LEN * 2 + TILE_SIDE_LEN * TILE_COUNT_COLUMN
    BOARD_POSITION_X = int(BOARD_SIDE_LEN / 2)
    BOARD_POSITION_Y = int(BOARD_SIDE_LEN / 2)

    def __init__(self):
        self._texture = None

    @property
    def _ready(self):
        return True if self._texture is not None else False
    
    def build(self):

        # Setting up SURFACE map:
        for row in range(1, self.TILE_COUNT_ROW + 1):
            if row not in SURFACE.keys():
                SURFACE[row] = {}
            for column in range(1, self.TILE_COUNT_COLUMN + 1):
                if column not in SURFACE[row].keys():
                    SURFACE[row][column] = None
        
        # Setting texture:
        # texture_name = 'board_surface.png'
        # texture_path = os.path.join(os.path.dirname(__file__), f'images/{texture_name}')
        # self._texture = arcade.load_texture(
        #     file_name=texture_path,
        #     mirrored=False,
        #     flipped=False,
        #     scale=1
        # )

        # Getting ready for first use:
        self.surface_fill()
        self.active_player = 'White'
        self.active_checker = None
        self.update()

    @staticmethod
    def surface_fill():
        for row in SURFACE:
            for column in SURFACE[row]:
                board_position = [row, column]
                if Board.assert_board_position_can_spawn(board_position):
                    checker_color = 'White' if row in (1, 2, 3) else 'Black'
                    checker_object = Checker()
                    checker_object.build(init_color=checker_color, init_position=board_position)
                    Board.put_checker_on_board_position(checker_object, board_position)

    @staticmethod
    def surface_clear():
        for row in SURFACE:
            for column in SURFACE[row]:
                SURFACE[row][column] = None

    @classmethod
    def surface_reset(cls):
        cls.surface_clear()
        cls.surface_fill()
        cls.update()

    @staticmethod
    def convert_board_position_to_coordinates(board_position: list):
        row, column = board_position
        coord_x = int((Board.MARGIN_LEN + Board.TILE_SIDE_LEN / 2) + (column - 1) * Board.TILE_SIDE_LEN)
        coord_y = int((Board.MARGIN_LEN + Board.TILE_SIDE_LEN / 2) + (row - 1) * Board.TILE_SIDE_LEN)
        coordinates = [coord_x, coord_y]
        return coordinates
    
    @staticmethod
    def convert_coordinates_to_board_position(coordinates: list):
        coord_x, coord_y = coordinates
        row = (coord_y - Board.MARGIN_LEN) // Board.TILE_SIDE_LEN + 1
        column = (coord_x - Board.MARGIN_LEN) // Board.TILE_SIDE_LEN + 1
        board_position = [row, column]
        return board_position

    @staticmethod
    def assert_board_position_is_occupied(board_position: list):
        occupied = True
        if Board.assert_board_position_is_valid(board_position):
            row, column = board_position
            checker = SURFACE[row][column]
            if checker is None:
                occupied = False
        return occupied

    @staticmethod
    def assert_board_position_is_empty(board_position: list):
        empty = True
        if Board.assert_board_position_is_valid(board_position):
            row, column = board_position
            checker = SURFACE[row][column]
            if checker is not None:
                empty = False
        return empty
    
    @staticmethod
    def assert_board_position_is_valid(board_position: list):
        result = False
        row, column = board_position
        if row in range(1, Board.TILE_COUNT_ROW + 1) and column in range(1, Board.TILE_COUNT_COLUMN + 1):
            result = True
        return result

    @staticmethod
    def assert_board_position_can_be_used(board_position: list):
        if Board.assert_board_position_is_valid(board_position):
            row, column = board_position
            can_be_used = False 
            if row % 2 == 0 and column % 2 != 0 or row % 2 != 0 and column % 2 == 0:
                can_be_used = True
            return can_be_used

    @staticmethod
    def assert_board_position_can_spawn(board_position: list):
        if Board.assert_board_position_can_be_used(board_position):
            row, column = board_position
            can_spawn = False
            if row in (1, 2, 3, 6, 7, 8):
                can_spawn = True
            return can_spawn

    @staticmethod
    def get_checker_by_position(board_position: list):
        if Board.assert_board_position_is_valid(board_position):
            row, column = board_position
            checker = SURFACE[row][column]
            return checker

    @staticmethod
    def get_checker_by_coordinates(coordinates: list):
        board_position = Board.convert_coordinates_to_board_position(coordinates)
        checker = Board.get_checker_by_position(board_position)
        return checker

    @staticmethod
    def get_positions_between(board_position_start: list, board_position_end: list):
        difference = board_position_start[0] - board_position_end[0]
        positions_between = []
        if difference > 1:
            row_axis = 1 if board_position_end[0] > board_position_start[0] else -1
            column_axis = 1 if board_position_end[1] > board_position_start[1] else -1
            peek_position = board_position_start
            while peek_position != board_position_end:
                peek_position = [peek_position[0] + row_axis, peek_position[1] + column_axis]
                if Board.assert_board_position_is_valid(peek_position):
                    positions_between.append(peek_position)
                else:
                    break
        return positions_between
    
    @staticmethod
    def clear_board_position(board_position: list):
        row, column = board_position
        SURFACE[row][column] = None
    
    @staticmethod
    def put_checker_on_board_position(checker_object, board_position: list):
        row, column = board_position
        SURFACE[row][column] = checker_object

    def display(self):

        # If checker object contains a texture, rendering texture:
        if self._ready:
            arcade.draw_texture_rectangle(
                center_x=self.BOARD_POSITION_X,
                center_y=self.BOARD_POSITION_Y,
                width=self._texture.width,
                height=self._texture.height,
                texture=self._texture,
                angle=0,
                alpha=255
            )
        
        # Otherwise, board object will use primitive shapes to "construct" a visual representative of itself:
        else:

            # Other margin:
            arcade.draw_rectangle_filled(
                center_x=self.BOARD_POSITION_X,
                center_y=self.BOARD_POSITION_Y,
                width=self.BOARD_SIDE_LEN,
                height=self.BOARD_SIDE_LEN,
                color=self.MARGIN_OUTER_COLOR,
            )

            # Inner margin:
            arcade.draw_rectangle_filled(
                center_x=self.BOARD_POSITION_X,
                center_y=self.BOARD_POSITION_Y,
                width=self.BOARD_SIDE_LEN - self.MARGIN_OUTER_LEN * 2,
                height=self.BOARD_SIDE_LEN - self.MARGIN_OUTER_LEN * 2,
                color=self.MARGIN_INNER_COLOR,
            )

            # Tiles:
            tile_color = self.TILE_COLOR_LIGHT
            tile_coord_x = int(self.MARGIN_LEN + self.TILE_SIDE_LEN / 2)
            tile_coord_y = int(self.MARGIN_LEN + self.TILE_SIDE_LEN / 2)
            for row in range(self.TILE_COUNT_ROW):
                for column in range(self.TILE_COUNT_COLUMN):
                    if tile_color == self.TILE_COLOR_DARK:
                        arcade.draw_rectangle_filled(
                            center_x=tile_coord_x,
                            center_y=tile_coord_y,
                            width=self.TILE_SIDE_LEN,
                            height=self.TILE_SIDE_LEN,
                            color=tile_color,
                        )
                    tile_coord_x += self.TILE_SIDE_LEN
                    tile_color = self.TILE_COLOR_DARK if tile_color == self.TILE_COLOR_LIGHT else self.TILE_COLOR_LIGHT
                tile_color = self.TILE_COLOR_DARK if tile_color == self.TILE_COLOR_LIGHT else self.TILE_COLOR_LIGHT
                tile_coord_x = int(self.MARGIN_LEN + self.TILE_SIDE_LEN / 2)
                tile_coord_y += self.TILE_SIDE_LEN
            
            # Letter index:
            pass

            # Number index:
            pass


    def display_objects(self):
        for row in SURFACE:
            for column in SURFACE[row]:
                board_position = [row, column]
                if self.assert_board_position_is_occupied(board_position):
                    checker = self.get_checker_by_position(board_position)
                    checker.display()
    
    def update(self):
        for row in SURFACE:
            for column in SURFACE[row]:
                if SURFACE[row][column] is not None:
                    checker = SURFACE[row][column]
                    checker.update()


class UI:
    def __init__(self):
        self.mode = 0
        self.prev = self.mode

    def switch(self, mode_id: int):
        self.prev = self.mode
        self.mode = mode_id

    def display(self):

        # Ignored, if game is active:
        if self.mode == 0:
            pass

        # Otherwise, overlay is rendered with UI menu elements:
        else:

            # Rendering white overlay:
            overlay_filename = os.path.join(os.path.dirname(__file__), 'images/white_overlay.png')
            overlay_texture = arcade.load_texture(
                file_name=overlay_filename,
                mirrored=False,
                flipped=False,
                scale=1
            )
            arcade.draw_texture_rectangle(
                center_x=Board.BOARD_POSITION_X,
                center_y=Board.BOARD_POSITION_Y,
                width=overlay_texture.width,
                height=overlay_texture.height,
                texture=overlay_texture,
                angle=0,
                alpha=225,
            )

            # Render logo:
            logo_lower_coord_x = Board.BOARD_POSITION_X
            logo_lower_coord_y = Board.BOARD_POSITION_Y + Board.BOARD_POSITION_Y / 2
            logo_upper_coord_x = Board.BOARD_POSITION_X
            logo_upper_coord_y = logo_lower_coord_y - 32
            arcade.draw_text(
                text='Zen Marathon',
                start_x=logo_upper_coord_x,
                start_y=logo_upper_coord_y,
                color=Board.TILE_COLOR_DARK,
                font_size=16,
                font_name='georgia',
                anchor_x='center',
                anchor_y='center'
            )
            arcade.draw_text(
                text='Checkers King',
                start_x=logo_lower_coord_x,
                start_y=logo_lower_coord_y,
                color=Board.TILE_COLOR_DARK,
                font_size=42,
                font_name='georgia',
                anchor_x='center',
                anchor_y='center'
            )

            # Render menu name:
            pass

            # Render instructions:
            instructions = str('Press SPACE to start new game...' if self.mode == 1 else 
                               'Game paused...' if self.mode == 2 else   
                               'Defeat. Press SPACE to continue...' if self.mode == 3 else 
                               'Victory! Press SPACE to continue' if self.mode == 4 else
                               'Draw. Press SPACE to continue' if self.mode == 5 else
                               'Something went wrong!')
            arcade.draw_text(
                text=instructions,
                start_x=Board.BOARD_POSITION_X,
                start_y=Board.BOARD_POSITION_Y,
                color=Board.TILE_COLOR_DARK,
                font_size=16,
                font_name='georgia',
                anchor_x='center',
                anchor_y='center'
            )



class Gameshell(arcade.Window):

    def __init__(self):

        # Core components:
        self.board = Board()
        self.board.build()
        self.ui = UI()
        self.ui.switch(1)

        super().__init__(
            width=self.board.BOARD_SIDE_LEN,
            height=self.board.BOARD_SIDE_LEN,
            title='ZenCheckersMarathon',
            fullscreen=False,
            resizable=False,
            antialiasing=False,
            update_rate=1/60
        )

        self.active_player = 'White'
        self.active_checker = None

        self.show_checker_moves = False
        self.show_checker_attacks = False
        self.show_all_movable_checkers = False
        self.show_all_attacking_checkers = False

        self.game_running = False
        self.game_paused = False

    def setup(self):
        arcade.set_background_color(color=arcade.color.RUBY_RED)
    
    def initialize(self):
        arcade.run()

    def switch_mode(self, mode: int):
        # 0 = Active game
        # 1 = Main menu
        # 2 = Pause menu
        # 3 = Win menu
        # 4 = Lose menu
        # 5 = Draw menu
        self.ui.switch(mode)
    
    def switch_active_player(self):
        self.active_player = 'Black' if self.active_player == 'White' else 'White'
        if self.active_checker is not None:
            self.active_checker = None

        # LOSE, if active player not AI, else WIN:
        if self.player_has_no_checkers():
            self.game_running = False
            self.game_paused = False
            self.switch_mode(3 if self.active_player == 'White' else 4)
        
        # Else, check if player can move:
        else:

            # Continue normally:
            if self.player_can_move():
                pass    

            # DRAW conditions:
            else:
                self.game_running = False
                self.game_paused = False
                self.switch_mode(5)

    def player_can_move(self):
        can_move = False
        player_checkers = []
        for row in SURFACE:
            for column in SURFACE[row]:
                board_position = [row, column]
                if self.board.assert_board_position_is_occupied(board_position):
                    checker = self.board.get_checker_by_position(board_position)
                    if checker.color == self.active_player:
                        player_checkers.append(checker)
        if player_checkers:
            for checker in player_checkers:
                if checker.can_move:
                    can_move = True
                    break
        return can_move
    
    def player_must_attack(self):
        must_attack = False
        player_checkers = []
        for row in SURFACE:
            for column in SURFACE[row]:
                board_position = [row, column]
                if self.board.assert_board_position_is_occupied(board_position):
                    checker = self.board.get_checker_by_position(board_position)
                    if checker.color == self.active_player:
                        player_checkers.append(checker)
        if player_checkers:
            for checker in player_checkers:
                if checker.can_attack:
                    must_attack = True
                    break
        return must_attack
    
    def player_has_no_checkers(self):
        no_checkers = True
        for row in SURFACE:
            for column in SURFACE[row]:
                board_position = [row, column]
                if self.board.assert_board_position_is_occupied(board_position):
                    checker = self.board.get_checker_by_position(board_position)
                    if checker.color == self.active_player:
                        no_checkers = False
                        break
        return no_checkers

    def on_draw(self):

        color_green = [135, 220, 55]
        color_red = [220, 55, 55]

        def highlight_active_checker():
            if self.active_checker is not None:
                if self.active_checker.color == self.active_player:
                    coord_x, coord_y = self.active_checker.coordinates
                    arcade.draw_rectangle_filled(
                            center_x=coord_x,
                            center_y=coord_y,
                            width=int(Board.TILE_SIDE_LEN * 0.85),
                            height=int(Board.TILE_SIDE_LEN * 0.85),
                            color=color_green,
                            tilt_angle=0
                        )
        
        def show_checker_moves():
            if self.active_checker is not None:
                for move_position in self.active_checker.move_list:
                    coordinates = Board.convert_board_position_to_coordinates(move_position)
                    coord_x, coord_y = coordinates
                    arcade.draw_rectangle_outline(
                        center_x=coord_x,
                        center_y=coord_y,
                        width=int(Board.TILE_SIDE_LEN * 0.85),
                        height=int(Board.TILE_SIDE_LEN * 0.85),
                        color=color_green,
                        border_width=2,
                        tilt_angle=0
                    )
        
        def show_checker_attacks():
            if self.active_checker is not None:
                for attack_position in self.active_checker.attack_list:
                    coordinates = self.board.convert_board_position_to_coordinates(attack_position)
                    coord_x, coord_y = coordinates
                    arcade.draw_rectangle_outline(
                        center_x=coord_x,
                        center_y=coord_y,
                        width=int(Board.TILE_SIDE_LEN * 0.85),
                        height=int(Board.TILE_SIDE_LEN * 0.85),
                        color=color_red,
                        border_width=2,
                        tilt_angle=0
                    )
        
        def show_all_movable_checkers():
            checkers_available = []
            for row in SURFACE:
                for column in SURFACE[row]:
                    board_position = [row, column]
                    if self.board.assert_board_position_is_occupied(board_position):
                        checker = self.board.get_checker_by_position(board_position)
                        if checker.color == self.active_player:
                            checkers_available.append(checker)
            for checker in checkers_available:
                if checker.can_move:
                    coord_x, coord_y = checker.coordinates
                    arcade.draw_rectangle_filled(
                        center_x=coord_x,
                        center_y=coord_y,
                        width=int(Board.TILE_SIDE_LEN * 0.85),
                        height=int(Board.TILE_SIDE_LEN * 0.85),
                        color=color_green,
                        tilt_angle=0
                    )
        
        def show_all_attacking_checkers():
            checkers_available = []
            for row in SURFACE:
                for column in SURFACE[row]:
                    board_position = [row, column]
                    if self.board.assert_board_position_is_occupied(board_position):
                        checker = self.board.get_checker_by_position(board_position)
                        if checker.color == self.active_player:
                            checkers_available.append(checker)
            for checker in checkers_available:
                if checker.can_attack:
                    coord_x, coord_y = checker.coordinates
                    arcade.draw_rectangle_filled(
                        center_x=coord_x,
                        center_y=coord_y,
                        width=int(Board.TILE_SIDE_LEN * 0.85),
                        height=int(Board.TILE_SIDE_LEN * 0.85),
                        color=color_red,
                        tilt_angle=0
                    )

        def handle_highlights():
            highlight_active_checker()

            if self.show_all_movable_checkers:
                self.show_checker_moves = False
                self.show_checker_attacks = False
                show_all_movable_checkers()
            if self.show_all_attacking_checkers:
                self.show_checker_moves = False
                self.show_checker_attacks = False
                show_all_attacking_checkers()

            if self.show_checker_moves:
                self.show_all_movable_checkers = False
                self.show_all_attacking_checkers = False
                show_checker_moves()
            if self.show_checker_attacks:
                self.show_all_movable_checkers = False
                self.show_all_attacking_checkers = False
                show_checker_attacks()
            
        # Initializing arcade library render cycle:
        arcade.start_render()

        # Render board surface, highlights and checker objects:
        self.board.display()
        handle_highlights()
        self.board.display_objects()
        self.ui.display()

    def on_key_press(self, key_pressed, modifiers):
        
        if self.ui.mode == 0:
            if key_pressed == arcade.key.H:
                if self.active_checker is not None:
                    self.active_checker.deselect()
                    self.active_checker = None
                self.show_checker_moves = False
                self.show_checker_attacks = False
                self.show_all_movable_checkers = True
                self.show_all_attacking_checkers = True
            elif key_pressed == arcade.key.ESCAPE:
                self.switch_mode(2)
                self.game_paused = True
        else:
            if self.ui.mode == 1:
                if key_pressed == arcade.key.ESCAPE:
                    quit()
                elif key_pressed == arcade.key.SPACE:
                    self.switch_mode(0)
                    self.game_running = True
                    self.game_paused = False
            elif self.ui.mode == 2:
                if key_pressed == arcade.key.ESCAPE:
                    self.switch_mode(0)
                    self.game_paused = False
                elif key_pressed == arcade.key.Q:
                    self.switch_mode(5)
                    self.game_running = False
                    self.game_paused = False
            elif self.ui.mode in (3, 4, 5):
                if key_pressed == arcade.key.SPACE:
                    self.switch_mode(1)

    def on_key_release(self, key_released, modifiers):
        
        if self.ui.mode == 0:
            if key_released == arcade.key.H:
                if self.active_checker is not None:
                    self.active_checker.deselect()
                    self.active_checker = None
                self.show_checker_moves = False
                self.show_checker_attacks = False
                self.show_all_movable_checkers = False
                self.show_all_attacking_checkers = False
        else:
            pass

    def on_mouse_press(self, x, y, button, modifiers):

        def clear_highlights():
            self.show_checker_moves = False
            self.show_checker_attacks = False
            self.show_all_movable_checkers = False
            self.show_all_attacking_checkers = False

        def show_checker_highlights():
            if self.active_checker is not None:
                if self.active_checker.can_move:
                    self.show_checker_moves = True
                    if self.active_checker.can_attack:
                        self.show_checker_moves = False
                        self.show_checker_attacks = True
        
        def force_highlights():
            self.show_checker_moves = False
            self.show_checker_attacks = False
            self.show_all_movable_checkers = True
            self.show_all_attacking_checkers = True
        
        def select_checker(checker):
            if self.active_checker is None:
                clear_highlights()
                self.active_checker = checker
                checker.select()
                checker.look_around()
        
        def deselect_checker():
            if self.active_checker is not None:
                self.active_checker.deselect()
                self.active_checker = None
        
        def move_checker(board_position):
            if self.active_checker.can_attack:
                self.active_checker.move(click_position)
                self.board.update()
                if not self.active_checker.can_attack:
                    deselect_checker()
                    clear_highlights()
                    self.switch_active_player()
            else:
                self.active_checker.move(click_position)
                self.board.update()
                deselect_checker()
                clear_highlights()
                self.switch_active_player()

        click_coordinates = [x, y]
        click_position = self.board.convert_coordinates_to_board_position(click_coordinates)
        click_checker = None
        if self.board.assert_board_position_is_occupied(click_position):
            click_checker = self.board.get_checker_by_position(click_position)
        
        if self.active_checker is None:
            if click_checker is None:
                clear_highlights()
            else:
                select_checker(click_checker)
                if click_checker.color == self.active_player:
                    show_checker_highlights()
        else:
            if click_checker is None:
                if click_position in self.active_checker.move_list:
                    if self.player_must_attack():
                        if self.active_checker.can_attack:
                            if click_position in self.active_checker.attack_list:
                                move_checker(click_position)
                            else:
                                deselect_checker()
                                force_highlights()
                        else:
                            deselect_checker()
                            force_highlights()
                    else:
                        move_checker(click_position)
                else:
                    deselect_checker()
                    clear_highlights()
            else:
                if click_checker == self.active_checker:
                    deselect_checker()
                    clear_highlights()
                else:
                    deselect_checker()
                    select_checker(click_checker)
                    if click_checker.color == self.active_player:
                        show_checker_highlights()

    def update(self, delta_time):
        pass

sh = Gameshell()
sh.setup()
sh.initialize()