"""SET; A boring card game for one, possibly lonley, player.

Read more about the game and see examples in:
    https://en.wikipedia.org/wiki/Set_(card_game).
Created by Eli as part of the course (Hebrew):
    https://github.com/PythonFreeCourse/Notebooks. (week 7, chapter 4).
Images of cards were scraped from:
    https://www.setgame.com/set/puzzle.
"""


# os is used to access files, mainly the card images.
# random is used to shuffle the deck - aka 'package'.
# sys is used to ensure closing the game when needed.
# time is used to manage temporary messages.
import os
import random
import sys
import time
# pygame is the main package on which the game is created.
# pillow is used to handle images, mainly cards'.
import pygame
from PIL import Image

# Initiate pygame and its font. Both are required.
# pygame.init: If raises, please ignore "Module 'pygame' has no 'init'...".
pygame.init()
pygame.font.init()


# Class of a SET card
class Card:
    """SET game card class. Contains 4 defining propeties + a matching image.

    Args:
        n (int between 1-3): Represents the number of shapes on the card.
                            (1 == 1, 2 == 2, 3 == 3).
        s (int between 1-3): Represents the shape on the card.
                            (1 == squiggle, 2 == diamond, 3 == oval)
        c (int between 1-3): Represents the color on the card.
                            (1 == red, 2 == purple, 3 == green)
        f (int between 1-3): Represents the shading ('fill') on the card.
                            (1 == solid, 2 == striped, 3 == open)

    Attributes:
        number (int): 1ts property; the value of n.
        shape (int): 2nd property; the value of s.
        color (int): 3rd property; the value of c.
        fill (int): 4th property; the value of f.
        properties (list): All the 4 properties above.
        image_file (str): The path of this cards' image file.
        image_sur (pygame.Surface): A surface obj. of the cards' image file.
    """

    def __init__(self, n: int, s: int, c: int, f: int):
        """Initiate."""
        self.number = n
        self.shape = s
        self.color = c
        self.fill = f
        self.properties = [self.number, self.shape, self.color, self.fill]
        self.image_file = self.find_card_pic_file()
        self.image_sur = pygame.image.load(self.image_file).convert()

    def find_card_pic_file(self):
        """Find the correct image file path for the card in the assets folder.

        Returns:
            str: The relative path of the image, based on file names.

        Raises:
            Exception: If couldn't find the cards' image file.
        """
        folder = os.path.join('assets', 'organized_cards')
        card_code = f'n{self.number}s{self.shape}c{self.color}f{self.fill}'
        for file_name in os.listdir(folder):
            if card_code in file_name:
                return os.path.join(folder, file_name)
        raise Exception("Couldn't find cards' image file.")


# Set the frame rate and the clock for it. 10 is good enough.
FPS = 10
CLOCK = pygame.time.Clock()
# Determine font and general colors.
GAME_FONT = pygame.font.SysFont("DejaVuSerif", 20, bold=False)
TEXT_COLOR = BLACK = (0, 0, 0)
TEXT_COLOR_VALID = BLUE = (0, 0, 255)
TEXT_COLOR_INVALID = RED = (255, 0, 100)
BG_COLOR = GREENISH = (26, 255, 140)
SHADE_COLOR = KAKI = (153, 153, 102)
BUTTON_COLOR = YELLOWISH = (255, 253, 84)
# Set the main screen (window) surfcae. Measuring is pixels.
SIZE = WIDTH, HIEGHT = 900, 500
WIN = pygame.display.set_mode(SIZE)
WIN.fill(BG_COLOR)
pygame.display.set_caption('Game Of Set')
# Cards and spaces measurements.
CARDS_WIDTH, CARDS_HEIGHT = 129, 83
SPACE_TO_X = CARDS_WIDTH+20
SPACE_TO_Y = CARDS_HEIGHT+20


TABLE_PLACES = dict()  # To contain the cards on the table (k:(x,y), v:Card).
full_package = []  # Main deck. Will populate by Card obj. as the game starts.
sets_found = []  # To store all the cards that removed from the table.
clicked = []  # To store up to 3 on-table cards, on which the player clicked.
hint = []  # To store a combination of 3 on-table cards that makes a set.
show_hint = False  # Indicate whether or not show hint to the player.
can_restart = False  # Indicate whether the player can restart or not.
to_sleep = False  # Dumb way to hold the game when displays some messages.
key_time_msg_to_show = ''  # To store one key of message to be shown.
# All possible text messages {name: [text, font color, (x, y)], ...}.
messages = {
    'start': ['Let\'s GO!', TEXT_COLOR, (400, 450)],
    'end': ['No more SETs. GAME OVER.', TEXT_COLOR, (300, 450)],
    'restart': ['Press SPACE to restart', TEXT_COLOR, (350, 450)],
    'valid': ['It\'s a SET!', TEXT_COLOR_VALID, (400, 450)],
    'invalid': ['Not a SET..', TEXT_COLOR_INVALID, (400, 450)],
    'shuffle': ['No SETs. Will shuffle and deal again.',
                TEXT_COLOR, (300, 450)]
}

# Populate the TABLE_PLACES only with its keys ((x,y) pos. on main screen-WIN).
for line in range(4):
    for column in range(3):
        x_pos = 187+(SPACE_TO_X * line)
        y_pos = 104+(SPACE_TO_Y * column)
        TABLE_PLACES[x_pos, y_pos] = None

# pygame.Surface: If raises, please ignore "Too many positional arguments...".
# Create 1 Surface for each usecase, then create as many Rectangles as needed:
# Surface + 12 Rectangles for shades - places for cards on the table.
shade_card_sur = pygame.Surface((CARDS_WIDTH, CARDS_HEIGHT))
shades_cards_rects = []
for place in TABLE_PLACES.keys():
    shades_cards_rects.append(shade_card_sur.get_rect(topleft=(place)))

# Surface + Rectangle for the package shade.
shade_package_sur = pygame.Surface((CARDS_HEIGHT, CARDS_WIDTH))
shade_package_rect = shade_package_sur.get_rect(center=(100, HIEGHT//2))

# Surface + Rectangle for the package back-side.
back_card_im_source = os.path.join('assets', 'back_side_90.png')
back_card_sur = pygame.image.load(back_card_im_source).convert()
back_card_rect = back_card_sur.get_rect(center=(100, HIEGHT//2))

# Surface + Rectangle for the hint button.
hint_button_sur = pygame.Surface((80, 40))
hint_button_rect = hint_button_sur.get_rect(topleft=(780, 400))

# Surface for the hinting dot. Rectangle will be while running, when needed.
blue_dot_sur = pygame.image.load(os.path.join('assets', 'blue_dot.png'))


# Functions - Logic
def package():
    """Create a full 81 cards deck based on Card class.

    Returns:
        package (list): list of 81 cards, one for each possible combination.
    """
    package = []
    for number in range(1, 3+1):
        for shape in range(1, 3 + 1):
            for color in range(1, 3 + 1):
                for fill in range(1, 3 + 1):
                    package.append(Card(number, shape, color, fill))
    return package


def deal_cards():
    """Fill cards to empty places in TABLE_PLACES.

    Returns:
        None.

    Raises:
        Exception: If too many time dealt cards with no sets.
    """
    done = False
    times_run = 0
    while not done and times_run < 50:
        times_run += 1
        # Check if there are any cards to deal. Else, end game.
        if full_package:
            # Find empty places and fill them using cards from package.
            for k_pos, v_card in TABLE_PLACES.items():
                if not v_card:
                    TABLE_PLACES[k_pos] = full_package.pop()
            # If there is a possible set - we done; Else, shuffle and loop.
            if check_possibilities():
                done = True
            else:
                manage_messages('shuffle')
                undeal_cards()
                random.shuffle(full_package)
        else:
            done = True
            end_game()
    if times_run >= 50:
        raise Exception('No sets on the table for 50 times')


def undeal_cards():
    """Take all the cards from TABLE_PLACES back to package.

    Returns:
        None.
    """
    for k_pos, v_card in TABLE_PLACES.items():
        if v_card:
            full_package.append(v_card)
            TABLE_PLACES[k_pos] = None


def set_no_set(clicks):
    """Call check_set() for given set, and deal with the outcome.

    Args:
        clicks (list): list of 3 cards chosen as set by the player.

    Returns:
        None.
    """
    global show_hint
    its_set = check_set(clicked)
    if its_set:
        manage_messages('valid')
        # Remove the set from TABLE_PLACES to sets_found.
        for card in clicked:
            for k_pos, v_card in TABLE_PLACES.items():
                if v_card == card:
                    TABLE_PLACES[k_pos] = None
                    sets_found.append(card)
        clicked.clear()
        show_hint = False
        deal_cards()
    else:
        manage_messages('invalid')
        clicked.clear()


def check_set(clicks):
    """Check if geven 3 cards is a valid SET.

    Args:
        clicks (list): list of 3 cards chosen as set by the player.

    Returns:
        bool: True if SET is valid, False if not.
    """
    # Unpack the chosen cards.
    first, second, third = clicks
    # Unpack the properties of each card.
    n1, s1, c1, f1 = first.properties
    n2, s2, c2, f2 = second.properties
    n3, s3, c3, f3 = third.properties
    # Get a bool for each property of the SET.
    number = n1 == n2 == n3 or n1 != n2 != n3 != n1
    shape = s1 == s2 == s3 or s1 != s2 != s3 != s1
    color = c1 == c2 == c3 or c1 != c2 != c3 != c1
    fill = f1 == f2 == f3 or f1 != f2 != f3 != f1
    # Return bool base on the verdict.
    if number and shape and color and fill:
        return True
    else:
        return False


def check_possibilities():
    """Check if there is possible SET on the table. use 2 nested funcs.

    Returns:
        there_are_sets (bool): True if there is a poss. SET, False if not.
    """
    def compare(card1: Card, card2: Card) -> Card:
        # For 2 given cards - Return the third needed for a valid SET.
        n = third(card1.number, card2.number)
        s = third(card1.shape, card2.shape)
        c = third(card1.color, card2.color)
        f = third(card1.fill, card2.fill)
        to_find = Card(n, s, c, f)
        return to_find

    def third(a: int, b: int) -> int:
        # For 2 given numbers - Return the third needed for a valid SET.
        if a == b:  # If equals
            return a
        elif max(a, b) == 2:  # If 1,2
            return 3
        else:  # So it's 1,3 or 2,3
            return 3 - min(a, b)

    global hint
    hint.clear()
    there_are_sets = False
    all_cards = [v for v in TABLE_PLACES.values() if v]
    # Choose 2 separated cards, go over the rest looking for SET.
    for first_card in all_cards:
        for second_card in all_cards[all_cards.index(first_card)+1:]:
            to_find = compare(first_card, second_card)
            for third_card in all_cards[all_cards.index(second_card)+1:]:
                if third_card.properties == to_find.properties:
                    there_are_sets = True
                    # Update the hint list.
                    hint += first_card, second_card, third_card
                    break
            if there_are_sets:
                break
        if there_are_sets:
            break
    return there_are_sets


def collisions(event):
    """Manage all player clicks on clickable rectangles.

    Args:
        event: a pygame.event.MOUSEBUTTONDOWN obj.

    Returns:
        None.
    """
    global show_hint
    # Check if clicked on a new card.
    # Make Rectangle for each card on TABLE_PLACES.
    for k_xy, v_card in TABLE_PLACES.items():
        if v_card:
            card_rect = v_card.image_sur.get_rect(topleft=(k_xy))

            # Refer only to clicks on cards.
            on_card = card_rect.collidepoint(event.pos)
            # Ignore multiple clicks on same card.
            unique = v_card not in clicked
            # Player can choose up to 3 cards at a time.
            can_click = len(clicked) < 3

            if on_card and unique and can_click:
                clicked.append(v_card)

    # Check if clicked the hint button.
    if hint_button_rect.collidepoint(event.pos):
        show_hint = True


def end_game():
    """Inform the player about the end and allow them to restart."""
    global can_restart
    now = time.time()
    can_restart = now
    manage_messages('end')


def restart():
    """Restore variables to empty state and restart the game."""
    undeal_cards()
    full_package = []
    sets_found = []
    clicked = []
    hint = []
    show_hint = False
    to_sleep = False
    key_time_msg_to_show = ''
    globals().update(locals())
    main()


# Functions - Graphics
def draw_shades():
    """Draw 12 shades for cards on the table."""
    for rect in shades_cards_rects:
        pygame.draw.rect(WIN, SHADE_COLOR, rect)
    # Draw a shade for the package (deck).
    pygame.draw.rect(WIN, SHADE_COLOR, shade_package_rect)
    # If there are any cards in package - Draw the back of a card.
    if full_package:
        WIN.blit(back_card_sur, back_card_rect)


def draw_cards():
    """Draw card in position for card in TABLE_PLACES."""
    for k_pos, v_card in TABLE_PLACES.items():
        if v_card:
            card_img_sur = TABLE_PLACES[k_pos].image_sur
            card_rect = card_img_sur.get_rect(topleft=(k_pos))
            WIN.blit(card_img_sur, card_rect)


def draw_button():
    """Draw the hint button."""
    pygame.draw.rect(WIN, BUTTON_COLOR, hint_button_rect)


def draw_texts():
    """Draw all static text on the screen."""
    # Text of package and number of cards in it.
    package_text = GAME_FONT.render(f'Package:', 1, TEXT_COLOR)
    package_num = GAME_FONT.render(str(len(full_package)), 1, TEXT_COLOR)
    WIN.blit(package_text, (60, 325))
    WIN.blit(package_num, (90, 345))
    # Text of sets fond and number of sets in it.
    found_text = GAME_FONT.render(f'Sets found:', 1, TEXT_COLOR)
    found_num = GAME_FONT.render(str(len(sets_found)//3), 1, TEXT_COLOR)
    WIN.blit(found_text, (780, 225))
    WIN.blit(found_num, (830, 245))
    # Text on the hint bottun.
    hint_text = GAME_FONT.render(f'HINT', 1, TEXT_COLOR)
    WIN.blit(hint_text, (790, 410))


def manage_messages(message_key):
    """Keep only newest message, and give it a timestamp."""
    global key_time_msg_to_show
    global to_sleep
    now = time.time()
    key_time_msg_to_show = [message_key, now]
    if message_key == 'restart':
        key_time_msg_to_show[1] = now + 10000
    elif message_key == 'shuffle':
        to_sleep = True


def draw_messages():
    """Draw temporary message on the screen."""
    global key_time_msg_to_show
    now = time.time()
    print(key_time_msg_to_show)
    if key_time_msg_to_show:
        msg_key, msg_stime = key_time_msg_to_show
        msg_text, msg_color, xy_pos = messages[msg_key]

        if now <= msg_stime + 2:
            message_text = GAME_FONT.render(msg_text, 1, msg_color)
            WIN.blit(message_text, xy_pos)
        else:
            key_time_msg_to_show = ''


def draw_hint_dots():
    """Draw blue dot on top-left of each card in the list hint."""
    for k_xy, v_card in TABLE_PLACES.items():
        if v_card in hint:
            dot_rect = blue_dot_sur.get_rect(center=(k_xy))
            WIN.blit(blue_dot_sur, dot_rect)


def draw_all():
    """Execute all the drawing functions and then update the screen."""
    global to_sleep
    WIN.fill(BG_COLOR)
    draw_shades()
    draw_cards()
    draw_button()
    draw_texts()
    draw_messages()
    if show_hint:
        draw_hint_dots()
    pygame.display.update()
    if to_sleep:
        time.sleep(2)
        to_sleep = False


# Main
def main():
    """Play the game."""
    global full_package
    global can_restart
    # Create a new package (deck).
    full_package = package()
    # Shuffle it good and well.
    random.shuffle(full_package)
    # Put 12 cards on the table.
    deal_cards()
    # Manage a wellcoming message to be drawn
    manage_messages('start')

    can_restart = False

    run = True
    while run:  # Main game loop.
        CLOCK.tick(FPS)  # Set the frame rate.
        now = time.time()
        # Manage player clicks.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                collisions(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and can_restart:
                    restart()

        # Check set if the player chose 3 cards.
        if len(clicked) == 3:
            set_no_set(clicked)
        # Message about restart if passed 2 sec. since the game ended.
        if can_restart and can_restart + 2 <= now:
            manage_messages('restart')

        # Uptade the graphics on the screen.
        draw_all()


if __name__ == '__main__':
    main()
