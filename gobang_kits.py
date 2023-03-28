import random


def get_nearby_direct(pos_0, pos_1):
    if pos_0[0] + 1 == pos_1[0] and pos_0[1] - 1 == pos_1[1]:
        return 'bl'  # Bottom Left
    elif pos_0[0] + 1 == pos_1[0] and pos_0[1] == pos_1[1]:
        return 'b'  # Bottom
    elif pos_0[0] + 1 == pos_1[0] and pos_0[1] + 1 == pos_1[1]:
        return 'br'  # Bottom Right
    elif pos_0[0] == pos_1[0] and pos_0[1] + 1 == pos_1[1]:
        return 'r'  # Right
    else:
        return 0


def get_nearby_pos(direct, color_ball):
    if direct == 'bl':
        return [(color_ball[0][0] - 1, color_ball[0][1] + 1), (color_ball[-1][0] + 1, color_ball[-1][1] - 1)]
    elif direct == 'b':
        return [(color_ball[0][0] - 1, color_ball[0][1]), (color_ball[-1][0] + 1, color_ball[-1][1])]
    elif direct == 'br':
        return [(color_ball[0][0] - 1, color_ball[0][1] - 1), (color_ball[-1][0] + 1, color_ball[-1][1] + 1)]
    elif direct == 'r':
        return [(color_ball[0][0], color_ball[0][1] - 1), (color_ball[-1][0], color_ball[-1][1] + 1)]


def get_layer_color_ball(layer):
    b_color_ball = []
    w_color_ball = []
    for h in range(len(layer.map)):  # 遍历横行
        for v in range(len(layer.map[h])):  # 遍历纵列
            if layer.map[h][v] == 1:  # 如果是黑子
                for piece in range(len(b_color_ball)):  # 遍历已知黑子
                    for direct in b_color_ball[piece]:  # 遍历棋子方向
                        relation = get_nearby_direct(b_color_ball[piece][direct][-1], (h, v))
                        if direct == relation:  # 顺序连接
                            b_color_ball[piece][direct].append((h, v))
                b_color_ball.append({'bl': [(h, v)], 'b': [(h, v)], 'br': [(h, v)], 'r': [(h, v)]})  # 每颗棋子都是一部字典，涵盖所有方向
            elif layer.map[h][v] == 2:
                for piece in range(len(w_color_ball)):  # 遍历已知白子
                    for direct in w_color_ball[piece]:
                        relation = get_nearby_direct(w_color_ball[piece][direct][-1], (h, v))
                        if direct == relation:
                            w_color_ball[piece][direct].append((h, v))
                w_color_ball.append({'bl': [(h, v)], 'b': [(h, v)], 'br': [(h, v)], 'r': [(h, v)]})
    return b_color_ball, w_color_ball


def get_highest_weight_pos(layer, ai_side):
    piece_weight = weight_analyzer(layer, ai_side)
    if len(piece_weight) == 0:  # 如果找不到权重大于0的位置
        return [random.randint(0, layer.size - 1), random.randint(0, layer.size - 1)]  # 这种情况就是起手，随便下一个位置
    else:
        items = list(piece_weight.items())
        items.sort(key=lambda x: x[1], reverse=True)
        counts = 0
        for pos in items:
            if pos[1] == items[0][1]:
                counts += 1
            else:
                break
        return items[random.randint(0, counts - 1)][0]


def is_legal_pos(h, v, layer):
    if 0 <= h < layer.size and 0 <= v < layer.size and layer.map[h][v] is 0:
        return True
    else:
        return False


def weight_analyzer(layer, ai_side):
    # 一级：下此处直接赢：己方四联有位 10000
    # 二级：不下此处对方赢：对方四联有位，对方有威胁性的中缺一 1000
    # 三级：无威胁情况下下此处下一步赢：己方三联有双位 500
    # 四级：无手段情况下不下此处下一步对方赢：对方三联有双位 100
    # 五级：此类情况叠加起来可能构成威胁：对方双联有双位 50
    # 五级：下此处有利于构建优势：己方三联有单位，己方双联有双位 10
    # 六级：下此处与其它棋子相邻 1
    piece_weight = {}  # 字典（坐标：权重）
    b_color_ball, w_color_ball = get_layer_color_ball(layer)
    player_color_ball, ai_color_ball = (b_color_ball, w_color_ball) if ai_side == 2 else (w_color_ball, b_color_ball)
    if len(player_color_ball) > 0:  # 检查玩家棋子：堵策略
        for piece in player_color_ball:
            for direct in piece:
                nearly_pos, able_pos = get_nearby_pos(direct, piece[direct]), []
                for pos in nearly_pos:  # 把合法位置全提出来
                    if is_legal_pos(pos[0], pos[1], layer):
                        able_pos.append(pos)

                if len(piece[direct]) >= 2:  # 检查成联的串
                    has_inner_pos = False
                    meta_check = get_nearby_pos(direct, nearly_pos)  # 检查中缺一
                    for i in range(len(meta_check)):
                        if layer.map[meta_check[i][0]][meta_check[i][1]] == (1 if ai_side == 2 else 2) and \
                           layer.map[nearly_pos[i][0]][nearly_pos[i][1]] == 0:  # 间位同，邻位空，此位是中缺一
                            if len(piece[direct]) == 2:  # 如果为二联，要排除是否存在威胁
                                inner_color_ball = [(meta_check[i] if i == 0 else piece[direct][0]), (meta_check[i] if i == 1 else piece[direct][-1])]
                                inner_color_ball_np, inner_color_ball_ap = get_nearby_pos(direct, inner_color_ball), []
                                for pos in inner_color_ball_np:  # 把合法位置全提出来
                                    if is_legal_pos(pos[0], pos[1], layer):
                                        inner_color_ball_ap.append(pos)
                                if len(inner_color_ball_ap) > 1:  # 二联含邻位后的一串（长度为4）有双位，存在威胁
                                    piece_weight[nearly_pos[i]] = piece_weight.get(nearly_pos[i], 0) + 1000
                                else:  # 二联中缺一一整串没有双位，不构成威胁
                                    piece_weight[nearly_pos[i]] = piece_weight.get(nearly_pos[i], 0) + 1
                            else:  # 除了二联中缺一，三联及以上都是致命的威胁，无论有没有双位
                                piece_weight[nearly_pos[i]] = piece_weight.get(nearly_pos[i], 0) + 1000
                            has_inner_pos = True
                    if has_inner_pos is False:  # 无中缺一
                        if (len(able_pos) > 1 and len(piece[direct]) == 3) or (len(able_pos) >= 1 and len(piece[direct]) == 4):
                            for pos in able_pos:
                                piece_weight[pos] = piece_weight.get(pos, 0) + (1000 if len(piece[direct]) == 4 else 100)  # 无中缺一，对方三、四联构成威胁
                        elif len(able_pos) > 1:
                            for pos in able_pos:
                                piece_weight[pos] = piece_weight.get(pos, 0) + 50  # 无中缺一，有双位，无威胁
                        else:
                            for pos in able_pos:
                                piece_weight[pos] = piece_weight.get(pos, 0) + 1  # 无中缺一，无双位，无威胁
                else:
                    for pos in able_pos:
                        piece_weight[pos] = piece_weight.get(pos, 0) + 1  # 独子，不构成威胁

    if len(ai_color_ball) > 0:  # 检查己方棋子：添策略
        for piece in ai_color_ball:
            for direct in piece:
                nearly_pos, able_pos = get_nearby_pos(direct, piece[direct]), []
                for pos in nearly_pos:  # 把合法位置全提出来
                    if is_legal_pos(pos[0], pos[1], layer):
                        able_pos.append(pos)
                if len(able_pos) > 1:  # 己方双位
                    if len(piece[direct]) >= 3:
                        for pos in able_pos:
                            piece_weight[pos] = piece_weight.get(pos, 0) + (10000 if len(piece[direct]) == 4 else 500)
                            # 己方四联有双位、三联有双位
                    else:
                        for pos in able_pos:
                            piece_weight[pos] = piece_weight.get(pos, 0) + (10 if len(piece[direct]) == 2 else 1)
                            # 己方二联有双位、己方独子有双位
                elif len(able_pos) == 1 and len(piece[direct]) >= 3:  # 己方三、四联有单位
                    piece_weight[able_pos[0]] = piece_weight.get(able_pos[0], 0) + (
                        10000 if len(piece[direct]) == 4 else 10)
                elif len(able_pos) == 1:  # 己方二联、独子有单位
                    piece_weight[able_pos[0]] = piece_weight.get(able_pos[0], 0) + 1
    return piece_weight
