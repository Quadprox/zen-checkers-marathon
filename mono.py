import arcade
import random
import os


SURFACE = {}
SURFACE_SET = False


class Board:

    # Board tile surface settings:
    TILE_SIDE_LEN = 64
    TILE_COLOR_LIGHT = [255, 210, 155]
    TILE_COLOR_DARK = [25, 20, 20]
    TILE_COUNT_PER_ROW = 8
    TILE_COUNT_PER_COLUMN = 8

    # Board surface margin surface settings:
    MARGIN_OUTER_LEN = 14
    MARGIN_INNER_LEN = 2
    MARGIN_LEN = MARGIN_OUTER_LEN + MARGIN_INNER_LEN
    MARGIN_OUTER_COLOR = TILE_COLOR_DARK
    MARGIN_INNER_COLOR = TILE_COLOR_LIGHT

    # Board surface general settings:
    BOARD_SIDE_LEN = int(MARGIN_LEN * 2 + TILE_SIDE_LEN * TILE_COUNT_PER_COLUMN)
    BOARD_POSITION_X = int(BOARD_SIDE_LEN / 2)
    BOARD_POSITION_Y = int(BOARD_SIDE_LEN / 2)
    BOARD_BOUNDARY_LEFT = MARGIN_LEN
    BOARD_BOUNDARY_RIGHT = BOARD_SIDE_LEN - MARGIN_LEN
    BOARD_BOUNDARY_BOTTOM = MARGIN_LEN
    BOARD_BOUNDARY_TOP = BOARD_SIDE_LEN - MARGIN_LEN
    BOARD_INDEX_LETTERS = 'ABCDEFGH'
    BOARD_INDEX_NUMBERS = '12345678'

    def __init__(self):
        self._texture = None

    @property
    def ready(self):
        return True if SURFACE_SET else False

    @staticmethod
    def convert_board_position_coordinates(conv_position: list):
        if Board.assert_board_position_is_valid(conv_position):
            row, column = conv_position
            coord_x = int(Board.MARGIN_LEN + Board.TILE_SIDE_LEN / 2 + (column - 1) * Board.TILE_SIDE_LEN)
            coord_y = int(Board.MARGIN_LEN + Board.TILE_SIDE_LEN / 2 + (row - 1) * Board.TILE_SIDE_LEN)
            coordinates = [coord_x, coord_y]
            return coordinates
    
    @staticmethod
    def convert_coordinates_to_board_position(conv_coordinates: list):
        if Board.assert_coordinates_are_valid(conv_coordinates):
            coord_x, coord_y = conv_coordinates
            row = int((coord_y - Board.MARGIN_LEN) // Board.TILE_SIDE_LEN + 1)
            column = int((coord_x - Board.MARGIN_LEN) // Board.TILE_SIDE_LEN + 1)
            board_position = [row, column]
            return board_position

    @staticmethod
    def convert_board_position_to_alphanumeric_index(conv_position: list):
        if Board.assert_board_position_is_valid(conv_position):
            row, column = conv_position
            letter = Board.BOARD_INDEX_LETTERS[column - 1]
            number = Board.BOARD_INDEX_NUMBERS[row - 1]
            alphanumeric_index = f'{letter}{number}'
            return alphanumeric_index

    @staticmethod
    def assert_coordinates_in_board_boundaries(check_coordinates: list):
        assertion_result = False
        if Board.assert_coordinates_are_valid(check_coordinates):
            coord_x, coord_y = check_coordinates
            boundary_x = range(Board.BOARD_BOUNDARY_LEFT, Board.BOARD_BOUNDARY_RIGHT)
            boundary_y = range(Board.BOARD_BOUNDARY_BOTTOM, Board.BOARD_BOUNDARY_TOP)
            if coord_x in boundary_x and coord_y in boundary_y:
                assertion_result = True
        return assertion_result

    @staticmethod
    def assert_coordinates_are_valid(check_coordinates: list):
        assertion_result = False
        if isinstance(check_coordinates, list):
            coord_x, coord_y = check_coordinates
            if isinstance(coord_x, int) and isinstance(coord_y, int):
                if coord_x >= 0 and coord_y >= 0:
                    assertion_result = True
                else:
                    raise ValueError(f'Coordinates can only be positive integers! Input: {check_coordinates}')
            else:
                raise ValueError(f'Coordinates can only be integer type! Input: {type(coord_x), type(coord_y)}')
        else:
            raise ValueError(f'Coordinates can only be parsed in list type! Input: {type(check_coordinates)}')
        return assertion_result

    @staticmethod
    def assert_board_position_is_valid(check_position: list):
        assertion_result = False
        if isinstance(check_position, list):
            row, column = check_position
            if isinstance(row, int) and isinstance(column, int):
                row_range = range(1, 8 + 1)
                column_range = range(1, 8 + 1)
                if row in row_range and column in column_range:
                    assertion_result = True
        return assertion_result

    @staticmethod
    def assert_board_position_can_be_used(check_position: list):
        assertion_result = False
        if Board.assert_board_position_is_valid(check_position):
            row, column = check_position
            if row % 2 == 0 and column % 2 != 0 or row % 2 != 0 and column % 2 == 0:
                assertion_result = True
        return assertion_result

    @staticmethod
    def assert_board_position_can_spawn_checker(check_position: list):
        assertion_result = False
        if Board.assert_board_position_can_be_used(check_position):
            row, column = check_position
            if row in (1, 2, 3, 6, 7, 8):
                assertion_result = True
        return assertion_result

    @staticmethod
    def assert_board_position_is_empty(check_position: list):
        assertion_result = False
        if SURFACE_SET and Board.assert_board_position_is_valid(check_position):
            row, column = check_position
            checker_object = SURFACE[row][column]
            if checker_object is None:
                assertion_result = True
        return assertion_result

    @staticmethod
    def assert_board_position_is_occupied(check_position: list):
        assertion_result = False
        if not Board.assert_board_position_is_empty(check_position):
            assertion_result = True
        return assertion_result

    @staticmethod
    def get_checker_by_board_position(board_position: list):
        if SURFACE_SET and Board.assert_board_position_is_occupied(board_position):
            row, column = board_position
            checker = SURFACE[row][column]
            return checker

    @staticmethod
    def get_checker_by_coordinates(board_coordinates: list):
        board_position = Board.convert_coordinates_to_board_position(board_coordinates)
        checker = Board.get_checker_by_board_position(board_position)
        return checker

    @staticmethod
    def get_board_positions_between(board_position_start: list, board_position_end: list):
        position_difference = abs(board_position_end[0] - board_position_start[0])
        position_list = []
        if position_difference > 1:
            axis_x = 1 if board_position_end[1] > board_position_start[1] else -1
            axis_y = 1 if board_position_end[0] > board_position_start[0] else -1
            peek_position = board_position_start
            while peek_position != board_position_end:
                peek_position = [peek_position[0] + axis_y, peek_position[1] + axis_x]
                if Board.assert_board_position_is_valid(peek_position):
                    position_list.append(peek_position)
                else:
                    break
        return position_list

    def build(self):
        global SURFACE_SET

        self._texture = arcade.load_texture(file_name=os.path.join(os.path.dirname(__file__), 'images/board_surface.png'))
        if not SURFACE_SET:
            for row in range(1, 8 + 1):
                if row not in SURFACE.keys():
                    SURFACE[row] = {}
                for column in range(1, 8 + 1):
                    if column not in SURFACE[row].keys():
                        SURFACE[row][column] = None
            SURFACE_SET = True
        self.surface_fill()
        self.update()

    @staticmethod
    def remove_checker(checker_object):
        for row in SURFACE:
            for column in SURFACE[row]:
                if SURFACE[row][column] is not None:
                    checker = SURFACE[row][column]
                    if checker == checker_object:
                        SURFACE[row][column] = None

    @staticmethod
    def remove_checker_from_position(board_position):
        if Board.assert_board_position_is_occupied(board_position):
            row, column = board_position
            SURFACE[row][column] = None

    @staticmethod
    def surface_fill():
        if SURFACE_SET:
            for row in SURFACE:
                for column in SURFACE[row]:
                    board_position = [row, column]
                    if Board.assert_board_position_can_spawn_checker(board_position):
                        spawned_checker = Checker()
                        spawned_checker.build(init_position=board_position, init_color='White' if row <= 3 else 'Black')
                        SURFACE[row][column] = spawned_checker

    @staticmethod
    def surface_clear():
        if SURFACE_SET:
            for row in SURFACE:
                for column in SURFACE[row]:
                    if SURFACE[row][column] is not None:
                        SURFACE[row][column] = None

    @staticmethod
    def surface_reset():
        Board.surface_clear()
        Board.surface_fill()
        Board.update()

    @staticmethod
    def update():
        if SURFACE_SET:
            for row in SURFACE:
                for column in SURFACE[row]:
                    if SURFACE[row][column] is not None:
                        checker = SURFACE[row][column]
                        checker.update()

    def display(self):

        # If texture is uploaded and ready:
        if self._texture is not None:
            arcade.draw_texture_rectangle(
                center_x=self.BOARD_POSITION_X,
                center_y=self.BOARD_POSITION_Y,
                width=self._texture.width,
                height=self._texture.height,
                texture=self._texture,
                angle=0,
                alpha=255,
            )

        # Else, render surface using primitive shapes:
        else:
            
            # Rendering outer margin:
            arcade.draw_rectangle_filled(
                center_x=self.BOARD_POSITION_X,
                center_y=self.BOARD_POSITION_Y,
                width=self.BOARD_SIDE_LEN,
                height=self.BOARD_SIDE_LEN,
                color=self.MARGIN_OUTER_COLOR,
            )

            # Rendering inner margin:
            arcade.draw_rectangle_filled(
                center_x=self.BOARD_POSITION_X,
                center_y=self.BOARD_POSITION_Y,
                width=float(self.BOARD_SIDE_LEN - self.MARGIN_OUTER_LEN * 2),
                height=float(self.BOARD_SIDE_LEN - self.MARGIN_OUTER_LEN * 2),
                color=self.MARGIN_INNER_COLOR
            )

            # Rendering tiles:
            tile_coord_x = int(self.MARGIN_LEN + self.TILE_SIDE_LEN / 2)
            tile_coord_y = int(self.MARGIN_LEN + self.TILE_SIDE_LEN / 2)
            tile_color = self.TILE_COLOR_LIGHT
            for vertical_tile in range(0, self.TILE_COUNT_PER_ROW):
                for horisontal_tile in range(0, self.TILE_COUNT_PER_COLUMN):
                    if tile_color == self.TILE_COLOR_DARK:
                        arcade.draw_rectangle_filled(
                            center_x=tile_coord_x,
                            center_y=tile_coord_y,
                            width=self.TILE_SIDE_LEN,
                            height=self.TILE_SIDE_LEN,
                            color=tile_color
                        )
                    tile_coord_x += self.TILE_SIDE_LEN
                    tile_color = self.TILE_COLOR_LIGHT if tile_color == self.TILE_COLOR_DARK else self.TILE_COLOR_DARK
                tile_coord_x = int(self.MARGIN_LEN + self.TILE_SIDE_LEN / 2)
                tile_coord_y += self.TILE_SIDE_LEN
                tile_color = self.TILE_COLOR_LIGHT if tile_color == self.TILE_COLOR_DARK else self.TILE_COLOR_DARK
                
            # Rendering letter index:
            # TODO: Write script to render letter index on margins
            pass

            # Rendering number index:
            # TODO: Write script to render number index on margins
            pass


    def display_checkers(self):
        if SURFACE_SET:
            for row in SURFACE:
                for column in SURFACE[row]:
                    if SURFACE[row][column] is not None:
                        checker = SURFACE[row][column]
                        checker.display()


class Checker:

    RADIUS_OUTER = int(Board.TILE_SIDE_LEN * 0.85 / 2)
    RADIUS_INNER = int(RADIUS_OUTER * 0.65)

    COLOR_WHITE_MAIN = [235, 235, 235]
    COLOR_WHITE_ALT = [200, 200, 190]
    COLOR_BLACK_MAIN = [65, 65, 45]
    COLOR_BLACK_ALT = [25, 25, 25]
    COLOR_ERROR = [255, 45, 45]

    def __init__(self):
        self.position = [0, 0]
        self.color = None
        self.queen = False
        self.move_list = []
        self.attack_list = []
        self.selected = False
        self._texture = None
        self._selected_angle = 0
        self._scale_index = 1

    def __str__(self):
        information = '{color} checker{type} at {index}'.format(
            color=self.color,
            type=' (queen)' if self.queen else '',
            index=self.index
        )
        return information

    @property
    def coordinates(self):
        coordinates = Board.convert_board_position_coordinates(self.position)
        return coordinates

    @property
    def index(self):
        alphanumeric_index = Board.convert_board_position_to_alphanumeric_index(self.position)
        return alphanumeric_index
    
    @property
    def can_promote(self):
        assertion_result = False
        if not self.queen:
            row = self.position[0]
            if self.color == 'White' and row == 8 or self.color =='Black' and row == 1:
                assertion_result = True
        return assertion_result

    @property
    def can_move(self):
        return True if self.move_list else False

    @property
    def can_attack(self):
        return True if self.attack_list else False

    def select(self):
        if not self.selected:
            self._selected_angle = random.choice((random.randint(-22, -12), random.randint(12, 22)))
            self._scale_index = 1.25
            self.selected = True

    def deselect(self):
        if self.selected:
            self._selected_angle = 0
            self._scale_index = 1.00
            self.selected = False
    
    def promote(self):
        if not self.queen:
            self.queen = True
            self.skin()
            
    
    def build(self, init_position: list, init_color: str):
        self.position = init_position
        self.color = init_color
        self.skin()
    
    def skin(self):
        texture_name = 'checker_{color}{type}.png'.format(
            color=self.color,
            type='_queen' if self.queen else ''
        )
        texture_path = os.path.join(os.path.dirname(__file__), f'images/{texture_name}')
        texture_object = arcade.load_texture(file_name=texture_path)
        self._texture = texture_object
    
    def display(self):

        coord_x, coord_y = self.coordinates

        # If texture is uploaded and ready:
        if self._texture is not None:
            arcade.draw_texture_rectangle(
                center_x=coord_x,
                center_y=coord_y,
                width=self._texture.width * self._scale_index,
                height=self._texture.height * self._scale_index,
                texture=self._texture,
                angle=0 if not self.selected else self._selected_angle,
                alpha=255
            )
        
        # Else, render surface using primitive shapes:
        else:

            # Rendering outer radius:
            arcade.draw_circle_filled(
                center_x=coord_x + 2,
                center_y=coord_y + 1,
                radius=self.RADIUS_OUTER,
                color=self.COLOR_WHITE_ALT if self.color == 'White' else
                      self.COLOR_BLACK_ALT if self.color == 'Black' else
                      self.COLOR_ERROR,
                num_segments=64
            )
            arcade.draw_circle_filled(
                center_x=coord_x - 2,
                center_y=coord_y - 1,
                radius=self.RADIUS_OUTER,
                color=self.COLOR_WHITE_MAIN if self.color == 'White' else
                      self.COLOR_BLACK_MAIN if self.color == 'Black' else
                      self.COLOR_ERROR,
                num_segments=64
            )

            # Rendering inner radius:
            arcade.draw_circle_filled(
                center_x=coord_x - 2,
                center_y=coord_y - 1,
                radius=self.RADIUS_INNER,
                color=self.COLOR_WHITE_ALT if self.color == 'White' else
                      self.COLOR_BLACK_ALT if self.color == 'Black' else
                      self.COLOR_ERROR,
                num_segments=64
            )
            arcade.draw_circle_filled(
                center_x=coord_x + 2,
                center_y=coord_y + 1,
                radius=self.RADIUS_INNER,
                color=self.COLOR_WHITE_MAIN if self.color == 'White' else
                      self.COLOR_BLACK_MAIN if self.color == 'Black' else
                      self.COLOR_ERROR,
                num_segments=64
            )
            

    def look(self):
        self.move_list = []
        self.attack_list = []
        if SURFACE_SET:
            for axis_x in (-1, 1):
                for axis_y in (-1, 1):
                    peek_position = self.position
                    forward = False
                    if axis_y == 1 and self.color == 'White' or axis_y == -1 and self.color == 'Black':
                        forward = True
                    attacking = False
                    while True:
                        peek_position = [peek_position[0] + axis_y, peek_position[1] + axis_x]
                        if Board.assert_board_position_is_valid(peek_position):
                            if Board.assert_board_position_is_occupied(peek_position):
                                checker = Board.get_checker_by_board_position(peek_position)
                                if checker.color == self.color:
                                    break
                                else:
                                    if not attacking:
                                        attacking = True
                                    else:
                                        break
                            else:
                                if attacking:
                                    self.attack_list.append(peek_position)
                                    if peek_position in self.move_list:
                                        self.move_list.remove(peek_position)
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

    def update(self):
        if not self.queen:
            if self.can_promote:
                self.promote()
        self.look()

    def move(self, to_position: list, attacking: bool = False):
        
        # Removing checkers from positions between jump start and jump end:
        if attacking:
            positions_jumped_over = Board.get_board_positions_between(self.position, to_position)
            for position_jumped in positions_jumped_over:
                if Board.assert_board_position_is_occupied(position_jumped):
                    row, column = position_jumped
                    SURFACE[row][column] = None

        # Moving checker and assigning new position to checker object:
        new_row, new_column = to_position
        SURFACE[new_row][new_column] = self
        old_row, old_column = self.position
        SURFACE[old_row][old_column] = None
        Board.remove_checker_from_position(self.position)
        self.position = to_position


class UI:
    def __init__(self):
        self.mode = 0
        self.prev = self.mode
        self._overlay = arcade.load_texture(file_name=os.path.join(os.path.dirname(__file__), 'images/overlay.png'))

    def switch(self, mode: int):
        self.prev = self.mode
        self.mode = mode

    def display(self):
        
        # If game is currently active - ignore:
        if self.mode == 1:
            pass
        
        # Else, render menu:
        else:
            
            # Rendering overlay background:
            arcade.draw_texture_rectangle(
                center_x=Board.BOARD_POSITION_X,
                center_y=Board.BOARD_POSITION_Y,
                width=self._overlay.width,
                height=self._overlay.height,
                texture=self._overlay,
                angle=0,
                alpha=235
            )

            # Rendering logo:
            logo_upper_coord_x = Board.BOARD_POSITION_X
            logo_upper_coord_y = Board.BOARD_POSITION_Y + Board.BOARD_POSITION_Y / 2
            logo_upper_caption = 'zen marathon'
            logo_lower_coord_x = logo_upper_coord_x
            logo_lower_coord_y = logo_upper_coord_y - 32
            logo_lower_caption = 'CHECKERS'
            arcade.draw_text(
                text=logo_upper_caption,
                start_x=logo_upper_coord_x,
                start_y=logo_upper_coord_y,
                color=Board.TILE_COLOR_DARK,
                font_size=18,
                font_name='georgia',
                bold=False,
                italic=False,
                anchor_x='center',
                anchor_y='center',
            )
            arcade.draw_text(
                text=logo_lower_caption,
                start_x=logo_lower_coord_x,
                start_y=logo_lower_coord_y,
                color=Board.TILE_COLOR_DARK,
                font_size=42,
                font_name='georgia',
                bold=False,
                italic=False,
                anchor_x='center',
                anchor_y='center',
            )

            # Rendering menu name:
            menu_caption = str(
                'Single player' if self.mode == 0 else
                'Game paused...' if self.mode == 2 else
                'YAY! You won!' if self.mode == 3 else
                'You lost... Oh, well.' if self.mode == 4 else
                'Draw? How strange!' if self.mode == 5 else
                'Something definately went wrong'
            )
            menu_caption_coord_x = Board.BOARD_POSITION_X
            menu_caption_coord_y = Board.BOARD_POSITION_Y - 18
            arcade.draw_text(
                text=menu_caption.upper(),
                start_x=menu_caption_coord_x,
                start_y=menu_caption_coord_y,
                color=Board.TILE_COLOR_DARK,
                font_size=28,
                font_name='georgia',
                bold=False,
                italic=False,
                anchor_x='center',
                anchor_y='center',
            )

            # Rendering hint:
            hint_caption = str(
                'Press SPACE to start...' if self.mode == 0 else
                'Press SPACE to resume...' if self.mode in (2, 3, 4, 5) else
                'Something definately went wrong'
            )
            hint_caption_coord_x = Board.BOARD_POSITION_X
            hint_caption_coord_y = menu_caption_coord_y - 26
            arcade.draw_text(
                text=hint_caption,
                start_x=hint_caption_coord_x,
                start_y=hint_caption_coord_y,
                color=Board.TILE_COLOR_DARK,
                font_size=16,
                font_name='georgia',
                bold=False,
                italic=True,
                anchor_x='center',
                anchor_y='center',
            )
            

class Gameshell(arcade.Window):

    def __init__(self):

        # Core module elements:
        self.board = Board()
        self.board.build()
        self.ui = UI()

        # Modes:
        #   0 - Main menu
        #   1 - Active game
        #   2 - Pause menu
        #   3 - Game won!
        #   4 - Game lost...
        #   5 - Game draw!
        #   6 - Quit confirmation menu

        super().__init__(
            width=self.board.BOARD_SIDE_LEN,
            height=self.board.BOARD_SIDE_LEN,
            title='ZenCheckersMarathon',
            fullscreen=False,
            resizable=False,
            antialiasing=False,
            update_rate=1/60
        )

        # Highlight controllers:
        self.show_all_available_moves = False
        self.show_all_available_attacks = False
        self.show_selected_checker_highlight = False
        self.show_selected_checkers_moves = False
        self.show_selected_checkers_attacks = False

        # Checker/player controllers:
        self.selected_checker = None
        self.active_player = 'White'
        self.white_player_checkers = []
        self.black_player_checkers = []

        # Arcade library window initializer:
        arcade.set_background_color(color=arcade.color.RED_DEVIL)
        arcade.run()

    def switch_player_turn(self):
        self.active_player = 'White' if self.active_player == 'Black' else 'Black'
        self.reset_highligts()
        self.check_game_condition()
    
    def switch_mode(self, mode: int):
        self.ui.switch(mode=mode)
    
    def reset_highligts(self):
        self.show_all_available_moves = False
        self.show_all_available_attacks = False
        self.show_selected_checker_highlight = False
        self.show_selected_checkers_moves = False
        self.show_selected_checkers_attacks = False
    
    def show_selected_highlights(self):
        self.show_selected_checker_highlight = True
        self.show_selected_checkers_moves = True
        self.show_selected_checkers_attacks = True

    def show_all_highlights(self):
        self.show_selected_checker_highlight = False
        self.show_all_available_moves = True
        self.show_all_available_attacks = True
    
    def feedback(self):
        if SURFACE_SET:
            for row in SURFACE:
                for column in SURFACE[row]:
                    if SURFACE[row][column] is not None:
                        checker = SURFACE[row][column]
                        if checker.color == 'White':
                            self.white_player_checkers.append(checker)
                        else:
                            self.black_player_checkers.append(checker)
    
    def check_game_condition(self):
        self.feedback()

        # One of the players has no checkers to play:
        if self.player_has_no_checkers():

            # White (player by default) has no checkers (Lose condition):
            if self.active_player == 'White':
                self.switch_mode(mode=4)

            # Black (AI opponent by default) has no checkers (Win condition):
            else:
                self.switch_mode(mode=3)
        
        # One of the players cannot move (Draw condition):
        else:
            if self.player_cannot_move():
                self.switch_mode(mode=5)

            # Else, ignored:
            else:
                pass

    def player_cannot_move(self):
        cannot_move = True
        for row in SURFACE:
            for column in SURFACE[row]:
                checker_object = SURFACE[row][column]
                if checker_object is not None:
                    if checker_object.color == self.active_player:
                        if checker_object.can_move:
                            cannot_move = False
                            break
        return cannot_move

    def player_must_attack(self):
        must_attack = False
        for row in SURFACE:
            for column in SURFACE[row]:
                checker_object = SURFACE[row][column]
                if checker_object is not None:
                    if checker_object.color == self.active_player:
                        if checker_object.can_attack:
                            must_attack = True
                            break
        return must_attack            

    def player_has_no_checkers(self):
        no_checkers = True
        for row in SURFACE:
            for column in SURFACE[row]:
                checker_object = SURFACE[row][column]
                if checker_object is not None:
                    if checker_object.color == self.active_player:
                        no_checkers = False
                        break
        return no_checkers
    
    def on_draw(self):

        color_palette_green = [65, 200, 105]
        color_palette_red = [200, 65, 65]
        
        def handle_highlights():
            if self.show_selected_checker_highlight:
                coord_x, coord_y = self.selected_checker.coordinates
                arcade.draw_rectangle_filled(
                    center_x=coord_x,
                    center_y=coord_y,
                    width=int(self.board.TILE_SIDE_LEN * 0.85),
                    height=int(self.board.TILE_SIDE_LEN * 0.85),
                    color=color_palette_green,
                    tilt_angle=0
                )
            if self.show_selected_checkers_moves:
                if self.selected_checker.can_move:
                    for move_position in self.selected_checker.move_list:
                        coordinates = self.board.convert_board_position_coordinates(move_position)
                        coord_x, coord_y = coordinates
                        arcade.draw_rectangle_outline(
                            center_x=coord_x,
                            center_y=coord_y,
                            width=int(self.board.TILE_SIDE_LEN * 0.85),
                            height=int(self.board.TILE_SIDE_LEN * 0.85),
                            color=color_palette_green,
                            border_width=2,
                            tilt_angle=0
                        )
            if self.show_selected_checkers_attacks:
                if self.selected_checker.can_attack:
                    for attack_position in self.selected_checker.attack_list:
                        coordinates = self.board.convert_board_position_coordinates(attack_position)
                        coord_x, coord_y = coordinates
                        arcade.draw_rectangle_outline(
                            center_x=coord_x,
                            center_y=coord_y,
                            width=int(self.board.TILE_SIDE_LEN * 0.85),
                            height=int(self.board.TILE_SIDE_LEN * 0.85),
                            color=color_palette_red,
                            border_width=2,
                            tilt_angle=0
                        )
            checkers_attacking = []
            if self.show_all_available_attacks:
                collection = []
                for row in SURFACE:
                    for column in SURFACE[row]:
                        checker_object = SURFACE[row][column]
                        if checker_object is not None:
                            if checker_object.color == self.active_player:
                                collection.append(checker_object)
                for checker in collection:
                    if checker.can_attack:
                        checkers_attacking.append(checker)
                        coord_x, coord_y = checker.coordinates
                        arcade.draw_rectangle_filled(
                            center_x=coord_x,
                            center_y=coord_y,
                            width=int(self.board.TILE_SIDE_LEN * 0.85),
                            height=int(self.board.TILE_SIDE_LEN * 0.85),
                            color=color_palette_red,
                            tilt_angle=0
                        )
            if self.show_all_available_moves:
                collection = []
                for row in SURFACE:
                    for column in SURFACE[row]:
                        checker_object = SURFACE[row][column]
                        if checker_object is not None:
                            if checker_object.color == self.active_player:
                                collection.append(checker_object)
                for checker in collection:
                    if checker.can_move and checker not in checkers_attacking:
                        coord_x, coord_y = checker.coordinates
                        arcade.draw_rectangle_filled(
                            center_x=coord_x,
                            center_y=coord_y,
                            width=int(self.board.TILE_SIDE_LEN * 0.85),
                            height=int(self.board.TILE_SIDE_LEN * 0.85),
                            color=color_palette_green,
                            tilt_angle=0
                        )

        arcade.start_render()

        self.board.display()
        handle_highlights()
        self.board.display_checkers()

        if self.ui.mode != 1:
            self.ui.display()

    def on_key_press(self, key_pressed, modifiers):
        
        # Active game mode:
        if self.ui.mode == 1:
            if key_pressed == arcade.key.H:
                self.show_all_highlights()
            elif key_pressed == arcade.key.ESCAPE:
                self.switch_mode(mode=2)
        
        # Menu:
        else:
            if self.ui.mode == 0:
                if key_pressed:
                    self.switch_mode(mode=1)
            elif self.ui.mode == 2:
                if key_pressed == arcade.key.ESCAPE:
                    self.switch_mode(mode=self.ui.prev)
                elif key_pressed == arcade.key.Q:
                    self.switch_mode(mode=4)
            elif self.ui.mode in (3, 4, 5):
                if key_pressed:
                    self.switch_mode(mode=0)

    def on_key_release(self, key_released, modifiers):
        
        # Active game mode:
        if self.ui.mode == 1:
            if key_released == arcade.key.H:
                self.reset_highligts()

    def on_mouse_press(self, x, y, button_pressed, modifiers):
        
        def select_checker(checker):
            hide_highlights()
            self.selected_checker = checker
            checker.select()
        
        def deselect_checker():
            self.selected_checker.deselect()
            self.selected_checker = None
            hide_highlights()

        def force_highlights():
            self.show_all_highlights()
        
        def hide_highlights():
            self.reset_highligts()
        
        def show_selected_checker_options():
            self.show_selected_highlights()
        
        def can_move_checker(checker):
            can_move = False
            if checker.color == self.active_player:
                can_move = True
            return can_move


        clicked_coordinates = [x, y]
        # if self.ui.mode == 1:
        if self.board.assert_coordinates_in_board_boundaries(clicked_coordinates):
            clicked_position = self.board.convert_coordinates_to_board_position(clicked_coordinates)
            clicked_checker = None
            if self.board.assert_board_position_is_occupied(clicked_position):
                clicked_checker = self.board.get_checker_by_board_position(clicked_position)
            print('\n',self.ui.mode, clicked_coordinates, clicked_position, clicked_checker)
            if clicked_checker is not None:
                print(' ', clicked_checker.move_list, clicked_checker.attack_list)

            if self.selected_checker is None:
                if clicked_checker is None:
                    hide_highlights()
                else:
                    select_checker(clicked_checker)
                    if can_move_checker(self.selected_checker):
                        show_selected_checker_options()
            else:
                if clicked_checker is None:
                    if can_move_checker(self.selected_checker):
                        if self.player_must_attack():
                            if clicked_position in self.selected_checker.attack_list:
                                self.selected_checker.move(clicked_position, attacking=True)
                                self.board.update()
                                if self.selected_checker.can_attack:
                                    self.feedback()
                                else:
                                    deselect_checker()
                                    hide_highlights()
                                    self.switch_player_turn()
                            else:
                                deselect_checker()
                                force_highlights()
                        else:
                            if clicked_position in self.selected_checker.move_list:
                                self.selected_checker.move(clicked_position, attacking=False)
                                self.board.update()
                                deselect_checker()
                                hide_highlights()
                                self.switch_player_turn()
                            else:
                                deselect_checker()
                                hide_highlights()
                    else:
                        deselect_checker()
                        hide_highlights()
                else:
                    if clicked_checker == self.selected_checker:
                        deselect_checker()
                        hide_highlights()
                    else:
                        deselect_checker()
                        select_checker(clicked_checker)
                        if can_move_checker(self.selected_checker):
                            show_selected_checker_options()
    
    def update(self, delta_time):
        pass


gsh = Gameshell()
