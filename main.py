import math
import random
import sys

import pygame
from pygame.locals import DOUBLEBUF, OPENGL, QUIT

from OpenGL.GL import *
from OpenGL.GLU import *


# =========================================================
# CONFIGURAÇÕES GERAIS
# =========================================================
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

FIELD_LENGTH = 105.0
FIELD_WIDTH = 68.0

LINE_WIDTH = 2.5

CENTER_CIRCLE_RADIUS = 9.15
PENALTY_AREA_DEPTH = 16.5
PENALTY_AREA_WIDTH = 40.32
GOAL_AREA_DEPTH = 5.5
GOAL_AREA_WIDTH = 18.32
PENALTY_MARK_DISTANCE = 11.0
CORNER_ARC_RADIUS = 1.0
PENALTY_ARC_RADIUS = 9.15

GOAL_WIDTH = 7.32
GOAL_HEIGHT = 2.44
GOAL_DEPTH = 2.44

OUTER_MARGIN = 18.0

GOAL_POST_THICKNESS = 0.12
FLAG_HEIGHT = 1.8

STAND_HEIGHT = 7.0
STAND_STEP_COUNT = 5
STAND_STEP_DEPTH = 4.0
STAND_GAP = 7.0

# =========================================================
# PLACAR
# =========================================================
LEFT_TEAM_NAME = "CASA"
RIGHT_TEAM_NAME = "VISITANTE"

left_score = 0
right_score = 0


# =========================================================
# TEXTURA
# =========================================================
def load_texture(image_path):
    texture_surface = pygame.image.load(image_path)
    texture_surface = pygame.transform.flip(texture_surface, False, True)
    texture_data = pygame.image.tostring(texture_surface, "RGB", True)

    width = texture_surface.get_width()
    height = texture_surface.get_height()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGB,
        width,
        height,
        0,
        GL_RGB,
        GL_UNSIGNED_BYTE,
        texture_data
    )

    glBindTexture(GL_TEXTURE_2D, 0)
    return texture_id


# =========================================================
# FUNÇÕES BÁSICAS
# =========================================================
def draw_line(x1, y1, x2, y2, z=0.03):
    glBegin(GL_LINES)
    glVertex3f(x1, z, y1)
    glVertex3f(x2, z, y2)
    glEnd()


def draw_rectangle_outline(x_min, y_min, x_max, y_max, z=0.03):
    glBegin(GL_LINE_LOOP)
    glVertex3f(x_min, z, y_min)
    glVertex3f(x_max, z, y_min)
    glVertex3f(x_max, z, y_max)
    glVertex3f(x_min, z, y_max)
    glEnd()


def draw_filled_rectangle(x_min, y_min, x_max, y_max, color, z=0.0):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex3f(x_min, z, y_min)
    glVertex3f(x_max, z, y_min)
    glVertex3f(x_max, z, y_max)
    glVertex3f(x_min, z, y_max)
    glEnd()


def draw_circle(cx, cy, radius, segments=100, z=0.03):
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        glVertex3f(x, z, y)
    glEnd()


def draw_arc(cx, cy, radius, start_angle_deg, end_angle_deg, segments=64, z=0.03):
    start_rad = math.radians(start_angle_deg)
    end_rad = math.radians(end_angle_deg)

    glBegin(GL_LINE_STRIP)
    for i in range(segments + 1):
        t = i / segments
        angle = start_rad + (end_rad - start_rad) * t
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        glVertex3f(x, z, y)
    glEnd()


def draw_point(cx, cy, radius=0.28, segments=28, z=0.03):
    glBegin(GL_POLYGON)
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        glVertex3f(x, z, y)
    glEnd()


def draw_box(x1, y1, z1, x2, y2, z2, color):
    glColor3f(*color)

    glBegin(GL_QUADS)
    # topo
    glVertex3f(x1, z2, y1)
    glVertex3f(x2, z2, y1)
    glVertex3f(x2, z2, y2)
    glVertex3f(x1, z2, y2)

    # base
    glVertex3f(x1, z1, y1)
    glVertex3f(x1, z1, y2)
    glVertex3f(x2, z1, y2)
    glVertex3f(x2, z1, y1)

    # frente
    glVertex3f(x1, z1, y2)
    glVertex3f(x1, z2, y2)
    glVertex3f(x2, z2, y2)
    glVertex3f(x2, z1, y2)

    # trás
    glVertex3f(x1, z1, y1)
    glVertex3f(x2, z1, y1)
    glVertex3f(x2, z2, y1)
    glVertex3f(x1, z2, y1)

    # esquerda
    glVertex3f(x1, z1, y1)
    glVertex3f(x1, z2, y1)
    glVertex3f(x1, z2, y2)
    glVertex3f(x1, z1, y2)

    # direita
    glVertex3f(x2, z1, y1)
    glVertex3f(x2, z1, y2)
    glVertex3f(x2, z2, y2)
    glVertex3f(x2, z2, y1)
    glEnd()


# =========================================================
# GRAMADO
# =========================================================
def draw_outer_area():
    half_length = FIELD_LENGTH / 2
    half_width = FIELD_WIDTH / 2

    draw_filled_rectangle(
        -half_length - OUTER_MARGIN,
        -half_width - OUTER_MARGIN,
        half_length + OUTER_MARGIN,
        half_width + OUTER_MARGIN,
        (0.09, 0.22, 0.09),
        z=-0.02
    )


def draw_textured_grass(texture_id):
    half_length = FIELD_LENGTH / 2
    half_width = FIELD_WIDTH / 2

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor3f(1.0, 1.0, 1.0)

    repeat_x = 14.0
    repeat_y = 9.0

    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-half_length, 0.0, -half_width)

    glTexCoord2f(repeat_x, 0.0)
    glVertex3f(half_length, 0.0, -half_width)

    glTexCoord2f(repeat_x, repeat_y)
    glVertex3f(half_length, 0.0, half_width)

    glTexCoord2f(0.0, repeat_y)
    glVertex3f(-half_length, 0.0, half_width)
    glEnd()

    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)

def draw_grass_stripes_overlay():
    half_length = FIELD_LENGTH / 2
    half_width = FIELD_WIDTH / 2

    stripe_count = 14
    stripe_width = FIELD_LENGTH / stripe_count

    for i in range(stripe_count):
        x1 = -half_length + i * stripe_width
        x2 = x1 + stripe_width

        if i % 2 == 0:
            glColor4f(1.0, 1.0, 1.0, 0.035)
        else:
            glColor4f(0.0, 0.0, 0.0, 0.03)

        glBegin(GL_QUADS)
        glVertex3f(x1, 0.003, -half_width)
        glVertex3f(x2, 0.003, -half_width)
        glVertex3f(x2, 0.003, half_width)
        glVertex3f(x1, 0.003, half_width)
        glEnd()


def draw_beautiful_grass(texture_id):
    draw_outer_area()
    draw_textured_grass(texture_id)
    draw_grass_stripes_overlay()

# =========================================================
# CAMPO
# =========================================================
def draw_field_lines():
    half_length = FIELD_LENGTH / 2
    half_width = FIELD_WIDTH / 2

    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(LINE_WIDTH)

    draw_rectangle_outline(-half_length, -half_width, half_length, half_width)
    draw_line(0.0, -half_width, 0.0, half_width)
    draw_circle(0.0, 0.0, CENTER_CIRCLE_RADIUS)
    draw_point(0.0, 0.0)

    left_penalty_x = -half_length + PENALTY_AREA_DEPTH
    draw_rectangle_outline(
        -half_length, -PENALTY_AREA_WIDTH / 2,
        left_penalty_x, PENALTY_AREA_WIDTH / 2
    )

    left_goal_area_x = -half_length + GOAL_AREA_DEPTH
    draw_rectangle_outline(
        -half_length, -GOAL_AREA_WIDTH / 2,
        left_goal_area_x, GOAL_AREA_WIDTH / 2
    )

    left_penalty_mark_x = -half_length + PENALTY_MARK_DISTANCE
    draw_point(left_penalty_mark_x, 0.0)

    angle_left = math.degrees(
        math.acos((PENALTY_AREA_DEPTH - PENALTY_MARK_DISTANCE) / PENALTY_ARC_RADIUS)
    )
    draw_arc(left_penalty_mark_x, 0.0, PENALTY_ARC_RADIUS, -angle_left, angle_left)

    right_penalty_x = half_length - PENALTY_AREA_DEPTH
    draw_rectangle_outline(
        right_penalty_x, -PENALTY_AREA_WIDTH / 2,
        half_length, PENALTY_AREA_WIDTH / 2
    )

    right_goal_area_x = half_length - GOAL_AREA_DEPTH
    draw_rectangle_outline(
        right_goal_area_x, -GOAL_AREA_WIDTH / 2,
        half_length, GOAL_AREA_WIDTH / 2
    )

    right_penalty_mark_x = half_length - PENALTY_MARK_DISTANCE
    draw_point(right_penalty_mark_x, 0.0)

    angle_right = math.degrees(
        math.acos((PENALTY_AREA_DEPTH - PENALTY_MARK_DISTANCE) / PENALTY_ARC_RADIUS)
    )
    draw_arc(right_penalty_mark_x, 0.0, PENALTY_ARC_RADIUS, 180 - angle_right, 180 + angle_right)

    # arcos de escanteio para dentro do campo
    draw_arc(-half_length,  half_width, CORNER_ARC_RADIUS, 270, 360)
    draw_arc(-half_length, -half_width, CORNER_ARC_RADIUS,   0,  90)
    draw_arc( half_length,  half_width, CORNER_ARC_RADIUS, 180, 270)
    draw_arc( half_length, -half_width, CORNER_ARC_RADIUS,  90, 180)


# =========================================================
# GOLS 3D
# =========================================================
def draw_goal_frame(side="left"):
    half_length = FIELD_LENGTH / 2
    half_goal = GOAL_WIDTH / 2
    t = GOAL_POST_THICKNESS

    if side == "left":
        x_front = -half_length
        x_back = -half_length - GOAL_DEPTH
    else:
        x_front = half_length
        x_back = half_length + GOAL_DEPTH

    y1 = -half_goal
    y2 = half_goal
    white = (0.95, 0.95, 0.95)

    draw_box(x_front - t / 2, y1 - t / 2, 0.0, x_front + t / 2, y1 + t / 2, GOAL_HEIGHT, white)
    draw_box(x_front - t / 2, y2 - t / 2, 0.0, x_front + t / 2, y2 + t / 2, GOAL_HEIGHT, white)
    draw_box(x_front - t / 2, y1 - t / 2, GOAL_HEIGHT - t / 2, x_front + t / 2, y2 + t / 2, GOAL_HEIGHT + t / 2, white)

    draw_box(
        min(x_front, x_back) - t / 2, y1 - t / 2, GOAL_HEIGHT - t / 2,
        max(x_front, x_back) + t / 2, y1 + t / 2, GOAL_HEIGHT + t / 2, white
    )
    draw_box(
        min(x_front, x_back) - t / 2, y2 - t / 2, GOAL_HEIGHT - t / 2,
        max(x_front, x_back) + t / 2, y2 + t / 2, GOAL_HEIGHT + t / 2, white
    )

    draw_box(x_back - t / 2, y1 - t / 2, 0.0, x_back + t / 2, y1 + t / 2, GOAL_HEIGHT, white)
    draw_box(x_back - t / 2, y2 - t / 2, 0.0, x_back + t / 2, y2 + t / 2, GOAL_HEIGHT, white)
    draw_box(x_back - t / 2, y1 - t / 2, GOAL_HEIGHT - t / 2, x_back + t / 2, y2 + t / 2, GOAL_HEIGHT + t / 2, white)


def draw_goal_net(side="left"):
    half_length = FIELD_LENGTH / 2
    half_goal = GOAL_WIDTH / 2

    if side == "left":
        x_front = -half_length
        x_back = -half_length - GOAL_DEPTH
    else:
        x_front = half_length
        x_back = half_length + GOAL_DEPTH

    y1 = -half_goal
    y2 = half_goal

    spacing_y = 0.5
    spacing_z = 0.4
    spacing_x = 0.5

    glColor4f(0.9, 0.9, 0.95, 0.45)
    glLineWidth(1.0)

    glBegin(GL_LINES)
    z = 0.0
    while z <= GOAL_HEIGHT + 1e-6:
        glVertex3f(x_back, z, y1)
        glVertex3f(x_back, z, y2)
        z += spacing_z

    y = y1
    while y <= y2 + 1e-6:
        glVertex3f(x_back, 0.0, y)
        glVertex3f(x_back, GOAL_HEIGHT, y)
        y += spacing_y
    glEnd()

    glBegin(GL_LINES)
    x_start = min(x_front, x_back)
    x_end = max(x_front, x_back)

    x = x_start
    while x <= x_end + 1e-6:
        glVertex3f(x, GOAL_HEIGHT, y1)
        glVertex3f(x, GOAL_HEIGHT, y2)
        x += spacing_x

    y = y1
    while y <= y2 + 1e-6:
        glVertex3f(x_front, GOAL_HEIGHT, y)
        glVertex3f(x_back, GOAL_HEIGHT, y)
        y += spacing_y
    glEnd()

    for y_side in [y1, y2]:
        glBegin(GL_LINES)
        x = x_start
        while x <= x_end + 1e-6:
            glVertex3f(x, 0.0, y_side)
            glVertex3f(x, GOAL_HEIGHT, y_side)
            x += spacing_x

        z = 0.0
        while z <= GOAL_HEIGHT + 1e-6:
            glVertex3f(x_front, z, y_side)
            glVertex3f(x_back, z, y_side)
            z += spacing_z
        glEnd()


# =========================================================
# BANDEIRINHAS
# =========================================================
def draw_corner_flag(x, y, pole_color=(1.0, 1.0, 0.2), flag_color=(1.0, 0.1, 0.1)):
    pole_thickness = 0.05

    draw_box(
        x - pole_thickness / 2,
        y - pole_thickness / 2,
        0.0,
        x + pole_thickness / 2,
        y + pole_thickness / 2,
        FLAG_HEIGHT,
        pole_color
    )

    glColor3f(*flag_color)
    glBegin(GL_TRIANGLES)
    glVertex3f(x, FLAG_HEIGHT, y)
    glVertex3f(x, FLAG_HEIGHT - 0.55, y)
    glVertex3f(x + 0.65, FLAG_HEIGHT - 0.22, y)
    glEnd()


def draw_all_corner_flags():
    half_length = FIELD_LENGTH / 2
    half_width = FIELD_WIDTH / 2

    draw_corner_flag(-half_length, -half_width, flag_color=(1.0, 0.1, 0.1))
    draw_corner_flag(-half_length,  half_width, flag_color=(1.0, 0.9, 0.1))
    draw_corner_flag( half_length, -half_width, flag_color=(0.1, 0.3, 1.0))
    draw_corner_flag( half_length,  half_width, flag_color=(1.0, 0.5, 0.1))


# =========================================================
# ARQUIBANCADAS E CADEIRAS
# =========================================================
def seat_palette():
    return [
        (0.86, 0.12, 0.12),
        (0.10, 0.35, 0.85),
        (0.92, 0.82, 0.12),
        (0.10, 0.65, 0.25),
        (0.92, 0.52, 0.12),
        (0.85, 0.85, 0.88),
        (0.52, 0.18, 0.72),
    ]


def choose_seat_color(index_a, index_b):
    palette = seat_palette()
    return palette[(index_a * 3 + index_b * 5) % len(palette)]


def draw_seat_horizontal(x, y, z, color, facing="down"):
    seat_w = 0.9
    seat_d = 0.75
    seat_h = 0.12
    back_h = 0.55
    back_t = 0.08
    leg_t = 0.06

    darker = tuple(max(0.0, c * 0.75) for c in color)

    if facing == "down":
        y_front = y - 0.12
    else:
        y_front = y + 0.12

    # Assento
    draw_box(
        x - seat_w / 2,
        y_front - seat_d / 2,
        z,
        x + seat_w / 2,
        y_front + seat_d / 2,
        z + seat_h,
        color
    )

    # Encosto
    if facing == "down":
        draw_box(
            x - seat_w / 2,
            y_front + seat_d / 2 - back_t,
            z + seat_h,
            x + seat_w / 2,
            y_front + seat_d / 2,
            z + seat_h + back_h,
            darker
        )
    else:
        draw_box(
            x - seat_w / 2,
            y_front - seat_d / 2,
            z + seat_h,
            x + seat_w / 2,
            y_front - seat_d / 2 + back_t,
            z + seat_h + back_h,
            darker
        )

    # Pés
    leg_offset_x = 0.25
    leg_offset_y = 0.18

    draw_box(
        x - leg_offset_x - leg_t / 2,
        y_front - leg_offset_y - leg_t / 2,
        z - 0.22,
        x - leg_offset_x + leg_t / 2,
        y_front - leg_offset_y + leg_t / 2,
        z,
        darker
    )
    draw_box(
        x + leg_offset_x - leg_t / 2,
        y_front - leg_offset_y - leg_t / 2,
        z - 0.22,
        x + leg_offset_x + leg_t / 2,
        y_front - leg_offset_y + leg_t / 2,
        z,
        darker
    )


def draw_seat_vertical(x, y, z, color, facing="right"):
    seat_w = 0.9
    seat_d = 0.75
    seat_h = 0.12
    back_h = 0.55
    back_t = 0.08
    leg_t = 0.06

    darker = tuple(max(0.0, c * 0.75) for c in color)

    if facing == "right":
        x_front = x - 0.12
    else:
        x_front = x + 0.12

    # Assento
    draw_box(
        x_front - seat_d / 2,
        y - seat_w / 2,
        z,
        x_front + seat_d / 2,
        y + seat_w / 2,
        z + seat_h,
        color
    )

    # Encosto
    if facing == "right":
        draw_box(
            x_front + seat_d / 2 - back_t,
            y - seat_w / 2,
            z + seat_h,
            x_front + seat_d / 2,
            y + seat_w / 2,
            z + seat_h + back_h,
            darker
        )
    else:
        draw_box(
            x_front - seat_d / 2,
            y - seat_w / 2,
            z + seat_h,
            x_front - seat_d / 2 + back_t,
            y + seat_w / 2,
            z + seat_h + back_h,
            darker
        )

    # Pés
    leg_offset_y = 0.25
    leg_offset_x = 0.18

    draw_box(
        x_front - leg_offset_x - leg_t / 2,
        y - leg_offset_y - leg_t / 2,
        z - 0.22,
        x_front - leg_offset_x + leg_t / 2,
        y - leg_offset_y + leg_t / 2,
        z,
        darker
    )
    draw_box(
        x_front - leg_offset_x - leg_t / 2,
        y + leg_offset_y - leg_t / 2,
        z - 0.22,
        x_front - leg_offset_x + leg_t / 2,
        y + leg_offset_y + leg_t / 2,
        z,
        darker
    )


def draw_horizontal_stand(y_near, y_far):
    half_length = FIELD_LENGTH / 2 + 8.0
    step_height = STAND_HEIGHT / STAND_STEP_COUNT

    for i in range(STAND_STEP_COUNT):
        z1 = i * step_height
        z2 = (i + 1) * step_height
        d1 = i * STAND_STEP_DEPTH
        d2 = (i + 1) * STAND_STEP_DEPTH

        if y_far > y_near:
            ys1 = y_near + d1
            ys2 = y_near + d2
        else:
            ys1 = y_near - d1
            ys2 = y_near - d2

        color = (0.48 - i * 0.03, 0.48 - i * 0.03, 0.50 - i * 0.03)
        draw_box(-half_length, min(ys1, ys2), z1, half_length, max(ys1, ys2), z2, color)


def draw_vertical_stand(x_near, x_far):
    half_width = FIELD_WIDTH / 2 + 8.0
    step_height = STAND_HEIGHT / STAND_STEP_COUNT

    for i in range(STAND_STEP_COUNT):
        z1 = i * step_height
        z2 = (i + 1) * step_height
        d1 = i * STAND_STEP_DEPTH
        d2 = (i + 1) * STAND_STEP_DEPTH

        if x_far > x_near:
            xs1 = x_near + d1
            xs2 = x_near + d2
        else:
            xs1 = x_near - d1
            xs2 = x_near - d2

        color = (0.44 - i * 0.03, 0.44 - i * 0.03, 0.46 - i * 0.03)
        draw_box(min(xs1, xs2), -half_width, z1, max(xs1, xs2), half_width, z2, color)


def draw_horizontal_seats(top=True):
    half_length = FIELD_LENGTH / 2 + 7.0
    base_y = FIELD_WIDTH / 2 + STAND_GAP if top else -FIELD_WIDTH / 2 - STAND_GAP

    rows = STAND_STEP_COUNT
    seat_spacing_x = 1.25
    usable_half_length = half_length - 3.0
    seat_count = int((usable_half_length * 2) / seat_spacing_x)

    step_height = STAND_HEIGHT / STAND_STEP_COUNT

    for row in range(rows):
        z = (row + 1) * step_height + 0.02
        y_offset = row * STAND_STEP_DEPTH + (STAND_STEP_DEPTH * 0.58)

        y = base_y + y_offset if top else base_y - y_offset
        facing = "down" if top else "up"

        start_x = -usable_half_length
        for col in range(seat_count):
            x = start_x + col * seat_spacing_x
            color = choose_seat_color(row, col)
            draw_seat_horizontal(x, y, z, color, facing=facing)


def draw_vertical_seats(right=True):
    half_width = FIELD_WIDTH / 2 + 7.0
    base_x = FIELD_LENGTH / 2 + STAND_GAP if right else -FIELD_LENGTH / 2 - STAND_GAP

    rows = STAND_STEP_COUNT
    seat_spacing_y = 1.25
    usable_half_width = half_width - 3.0
    seat_count = int((usable_half_width * 2) / seat_spacing_y)

    step_height = STAND_HEIGHT / STAND_STEP_COUNT

    for row in range(rows):
        z = (row + 1) * step_height + 0.02
        x_offset = row * STAND_STEP_DEPTH + (STAND_STEP_DEPTH * 0.58)

        x = base_x + x_offset if right else base_x - x_offset
        facing = "left" if right else "right"

        start_y = -usable_half_width
        for col in range(seat_count):
            y = start_y + col * seat_spacing_y
            color = choose_seat_color(row + 10, col)
            draw_seat_vertical(x, y, z, color, facing=facing)


def draw_stands():
    half_length = FIELD_LENGTH / 2
    half_width = FIELD_WIDTH / 2

    draw_horizontal_stand(
        half_width + STAND_GAP,
        half_width + STAND_GAP + STAND_STEP_COUNT * STAND_STEP_DEPTH
    )
    draw_horizontal_stand(
        -half_width - STAND_GAP,
        -half_width - STAND_GAP - STAND_STEP_COUNT * STAND_STEP_DEPTH
    )
    draw_vertical_stand(
        -half_length - STAND_GAP,
        -half_length - STAND_GAP - STAND_STEP_COUNT * STAND_STEP_DEPTH
    )
    draw_vertical_stand(
        half_length + STAND_GAP,
        half_length + STAND_GAP + STAND_STEP_COUNT * STAND_STEP_DEPTH
    )

    draw_horizontal_seats(top=True)
    draw_horizontal_seats(top=False)
    draw_vertical_seats(right=False)
    draw_vertical_seats(right=True)


# =========================================================
# PLACAR 2D
# =========================================================
def draw_text_2d(x, y, text, font, color=(255, 255, 255), bg=None):
    text_surface = font.render(text, True, color, bg)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    width = text_surface.get_width()
    height = text_surface.get_height()

    glWindowPos2d(x, y)
    glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, text_data)


def draw_scoreboard(window_width, window_height, font_title, font_score):
    global left_score, right_score

    board_width = 360
    board_height = 90

    x = (window_width - board_width) // 2
    y = window_height - 110

    glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT)

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor4f(0.05, 0.05, 0.05, 0.82)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + board_width, y)
    glVertex2f(x + board_width, y + board_height)
    glVertex2f(x, y + board_height)
    glEnd()

    glColor4f(1.0, 1.0, 1.0, 0.85)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + board_width, y)
    glVertex2f(x + board_width, y + board_height)
    glVertex2f(x, y + board_height)
    glEnd()

    glBegin(GL_LINES)
    glVertex2f(x + board_width / 2, y + 10)
    glVertex2f(x + board_width / 2, y + board_height - 10)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    draw_text_2d(x + 35, y + 55, LEFT_TEAM_NAME, font_title, (255, 255, 255))
    draw_text_2d(x + 210, y + 55, RIGHT_TEAM_NAME, font_title, (255, 255, 255))

    draw_text_2d(x + 125, y + 18, str(left_score), font_score, (255, 255, 255))
    draw_text_2d(x + 225, y + 18, str(right_score), font_score, (255, 255, 255))
    draw_text_2d(x + 173, y + 18, "-", font_score, (255, 255, 255))

    glPopAttrib()


# =========================================================
# CENA
# =========================================================
def draw_field_scene(grass_texture):
    draw_beautiful_grass(grass_texture)
    draw_stands()
    draw_field_lines()
    draw_goal_frame("left")
    draw_goal_frame("right")
    draw_goal_net("left")
    draw_goal_net("right")
    draw_all_corner_flags()


# =========================================================
# OPENGL
# =========================================================
def setup_opengl(width, height):
    glViewport(0, 0, width, height)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, width / height, 0.1, 500.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glEnable(GL_LINE_SMOOTH)

    glClearColor(0.05, 0.15, 0.06, 1.0)


def set_inclined_camera():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    gluLookAt(
        0.0, 75.0, 95.0,
        0.0, 0.0, 0.0,
        0.0, 1.0, 0.0
    )


# =========================================================
# LOOP PRINCIPAL
# =========================================================
def main():
    pygame.init()
    pygame.display.set_caption("Campo de Futebol 3D")

    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
    setup_opengl(WINDOW_WIDTH, WINDOW_HEIGHT)

    try:
        grass_texture = load_texture("grass.jpg")
    except pygame.error as e:
        print("Erro ao carregar 'grass.jpg'. Coloque a imagem na mesma pasta do arquivo Python.")
        print(f"Detalhe: {e}")
        pygame.quit()
        sys.exit()

    pygame.font.init()
    scoreboard_font_title = pygame.font.SysFont("Arial", 22, bold=True)
    scoreboard_font_score = pygame.font.SysFont("Arial", 34, bold=True)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        set_inclined_camera()
        draw_field_scene(grass_texture)
        draw_scoreboard(
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            scoreboard_font_title,
            scoreboard_font_score
        )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()