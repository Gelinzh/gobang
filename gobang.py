import re
import sys
import turtle
import gobang_kits

title_info = "[INFO] "
title_warn = "[WARN] "


class Layer:
    def __init__(self, size=15, unit_width=30, piece_radius=6):
        self.size = size
        self.unit_width = unit_width
        self.piece_radius = piece_radius
        self.winning_chain = [0, []]
        self.ai_side = 2
        self.map = []
        for h in range(size):
            self.map.append([])
            for v in range(size):
                self.map[h].append(0)

    def set_default(self):
        for h in range(len(self.map)):
            for v in range(len(self.map[h])):
                self.map[h][v] = 0
        self.winning_chain = [0, []]


def input_ec(request):
    input_str = input()
    if input_str is "exit":
        print(title_info + "System Shutting Down...")
        sys.exit(0)
    elif request is int:
        try:
            return int(input_str)
        except ValueError:
            print(title_warn + "Wrong Type! Please Input Integer:")
            return None
    elif request is tuple:
        result = re.search(r"^.*(\d)[,\s]+(\d).*$", input_str)
        if result is not None:
            return tuple((result.group(1), result.group(2)))
        else:
            print(title_warn + "Wrong Type! Please Input Tuple:")
            return None
    else:
        return input_str


def print_gobang_layer(obj):
    unit_width = obj.unit_width
    main_width = (obj.size - 1) * unit_width
    origin_point = (- main_width / 2, main_width / 2)

    turtle.hideturtle()
    turtle.clear()
    # turtle.speed(10)
    # turtle.delay(0)
    turtle.tracer(False)
    turtle.penup()
    for i in range(obj.size):
        turtle.setpos(origin_point[0], origin_point[1] - (unit_width * i))
        turtle.pendown()
        turtle.forward(main_width)
        turtle.penup()
    turtle.right(90)
    for i in range(obj.size):
        turtle.setpos(origin_point[0] + (unit_width * i), origin_point[1])
        turtle.pendown()
        turtle.forward(main_width)
        turtle.penup()
    turtle.left(90)

    if obj.winning_chain[0]:
        turtle.pensize(4)
        turtle.setpos(origin_point[0] + (unit_width * obj.winning_chain[1][0][1]), origin_point[1] - (unit_width * obj.winning_chain[1][0][0]))
        turtle.pendown()
        turtle.setpos(origin_point[0] + (unit_width * obj.winning_chain[1][-1][1]), origin_point[1] - (unit_width * obj.winning_chain[1][-1][0]))
        turtle.pensize(1)
        turtle.penup()

    for i in range(len(obj.map)):
        for j in range(len(obj.map[i])):
            if obj.map[i][j] == 1:
                turtle.setpos(origin_point[0] + (unit_width * j), origin_point[1] - (unit_width * i) - obj.piece_radius)
                turtle.fillcolor('black')
                turtle.pendown()
                turtle.begin_fill()
                turtle.circle(obj.piece_radius)
                turtle.end_fill()
                turtle.penup()
            elif obj.map[i][j] == 2:
                turtle.setpos(origin_point[0] + (unit_width * j), origin_point[1] - (unit_width * i) - obj.piece_radius)
                turtle.fillcolor('white')
                turtle.pendown()
                turtle.begin_fill()
                turtle.circle(obj.piece_radius)
                turtle.end_fill()
                turtle.penup()


def is_game_continue(obj):
    no_space = True
    for line in obj.map:  # 没位置了
        if 0 in line:
            no_space = False
    if no_space:
        return False

    b_color_ball, w_color_ball = gobang_kits.get_layer_color_ball(obj)
    for piece in b_color_ball:
        for direct in piece:
            if len(piece[direct]) >= 5:
                obj.winning_chain[0], obj.winning_chain[1] = 1, piece[direct]
                return False
    for piece in w_color_ball:
        for direct in piece:
            if len(piece[direct]) >= 5:
                obj.winning_chain[0], obj.winning_chain[1] = 2, piece[direct]
                return False
    return True


def process_placing_piece(h, v):
    global layer, side, isGameContinue

    if not isGameContinue:  # 如果标记游戏结束
        layer.set_default()
        side = 1
        isGameContinue = True
        print_gobang_layer(layer)
        turtle.done()
        return

    if layer.map[h][v] != 0:
        return

    layer.map[h][v] = side  # 下子位置赋给图层
    side = (2 if side == 1 else 1)  # 切换黑白
    print_gobang_layer(layer)  # 打印图层
    isGameContinue = is_game_continue(layer)  # 判断是否游戏结束
    if not isGameContinue:  # 游戏结束，做标记，打印一划拉
        print_gobang_layer(layer)
        if layer.winning_chain == [0, []]:
            print(title_info + "Game Over! You Made A Draw.")
        else:
            print(title_info + "Game Over! Winner is " + ("Black." if layer.winning_chain[0] == 1 else "White."))
    elif side == layer.ai_side:  # 如果轮到AI了，那让AI下一步棋
        ai_decision = gobang_kits.get_highest_weight_pos(layer, 2)  # 得到AI想下什么棋
        process_placing_piece(ai_decision[0], ai_decision[1])  # 执行下棋
    turtle.done()


def on_screen_click(x, y):
    global layer

    unit_width = layer.unit_width
    main_width = (layer.size - 1) * unit_width
    origin_point = (- main_width / 2, main_width / 2)
    v, h = round((x - origin_point[0]) / unit_width), round((origin_point[1] - y) / unit_width)
    if not gobang_kits.is_legal_pos(h, v, layer):
        return

    process_placing_piece(h, v)


print(title_info + "Welcome to GoBang! Please Enter CheckerBoard Size:")

while True:
    init_layer_size = input_ec(int)
    if init_layer_size is None:
        continue
    elif not 10 <= init_layer_size <= 50:
        print(title_warn + "Out of Range! Figure Should Be In [10, 50]:")
    else:
        break

sc = turtle.Screen()
sc.onscreenclick(on_screen_click)
layer, side, isGameContinue = Layer(init_layer_size), 1, True

print_gobang_layer(layer)
turtle.done()