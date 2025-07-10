import pygame 
import random
import sys
import os

pygame.init()

# 環境設定
WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("こうかとん・ルーレット")

# 色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GREEN = (0, 200, 0)

# フォント
font_path = pygame.font.match_font("msgothic")
font = pygame.font.Font(font_path, 28) if font_path else pygame.font.SysFont("msgothic", 28)

# ゲームの初期値
bullet_count = 2
chamber_size = 6
game_over = False
message = "ゲーム開始！"
item_message = ""
action_log = ""
turn_phase = "player"
enemy_action_timer = 0
chamber = []
turn_count = 0
skip_opponent_turn = False
player_turn = True
used_items = set()
item_used_this_turn = False
item_box_clicked_this_turn = False
selected_item = None
show_use_confirm = False
use_confirm_rects = {}
enemy_can_use_items = True

# 弾の装填
def load_bullets():
    global chamber
    chamber = [0] * chamber_size
    bullets = random.sample(range(chamber_size), bullet_count)
    for i in bullets:
        chamber[i] = 1

def rotate_chamber():
    random.shuffle(chamber)

# テキスト描画
def draw_text(text, x, y, color=BLACK):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# ボタン描画
def draw_button(text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h))
    draw_text(text, x + 10, y + 10)
    return pygame.Rect(x, y, w, h)

def shoot(shooter, target):
    global message, game_over, turn_count, action_log
    global player_hp, opponent_hp
    global player_turn, skip_opponent_turn 

    if chamber:
        round = chamber.pop(0)
        turn_count += 1
        if round == 1:
            message = f"バン！ {target} が撃たれた！"
            action_log = f"{shooter} が撃った対象： {target}. {target} が撃たれた！"
            if target == "プレイヤー":
                player_hp -= 1
            else:
                opponent_hp -= 1
        else:
            message = f"カチッ！ {target} は生き残った。"
            action_log = f"{shooter} が撃った対象： {target}. {target} は生き残った。"
    else:
        message = "弾はもう残っていません。"
        action_log = "弾切れ。ゲームオーバー。"
        game_over = True
        return "empty"


# アイテム画像
item_box_img = pygame.image.load("fig/alien1.png")
item_box_img = pygame.transform.scale(item_box_img, (100, 100))
item_list = [
    ("虫眼鏡", pygame.image.load("fig/0.png")),
    ("タバコ", pygame.image.load("fig/1.png")),
    ("のこぎり", pygame.image.load("fig/2.png")),
    ("手錠", pygame.image.load("fig/3.png"))    
]

# 確認ボタン描画
def draw_use_confirm_buttons():
    global use_confirm_rects
    yes_btn = draw_button("はい", 800, 370, 80, 40, GREEN)
    no_btn = draw_button("いいえ", 900, 370, 80, 40, RED)
    use_confirm_rects = {"yes": yes_btn, "no": no_btn}

# アイテム効果適用
def apply_item_effect(name):
    global player_hp,opponent_hp
    if name == "虫眼鏡":
        Item.searchglass(chamber[0])
    elif name == "タバコ":
        player_hp = Item.tobacco(player_hp)
        opponent_hp = Item.tobacco(opponent_hp)
    elif name == "のこぎり":
        player_hp = Item.saw(chamber[0], player_hp)
        opponent_hp = Item.saw(chamber[0], opponent_hp)
    elif name == "手錠":
        Item.handcuffs()

# 初期化
load_bullets()
rotate_chamber()

# メインループ
def main():
    global selected_item, show_use_confirm, game_over
    global enemy_can_use_items
    global item_used_this_turn, item_box_clicked_this_turn
    global player_turn, skip_opponent_turn
    global message
    global turn_phase,enemy_action_timer
    while True:
        screen.fill(WHITE)

        draw_text("こうかとん・ルーレット", 280, 50)
        draw_text(f"ターン： {'プレイヤー' if player_turn else '相手'}", 300, 100)
        draw_text(f"ターン数： {turn_count}", 300, 140)
        draw_text(f"弾数： {chamber.count(1)}", 300, 180)
        draw_text(f"空砲： {chamber.count(0)}", 300, 220)
        draw_text(f"アクション： {action_log}", 100, 340)
        draw_text(message, 100, 380)

        shoot_self_btn = draw_button("自分を撃つ", 200, 450, 150, 50, RED)
        shoot_opponent_btn = draw_button("Shoot 相手", 450, 450, 150, 50, BLUE)
        item_box_rect = pygame.Rect(800, 100, 100, 100)
        if player_turn:
            screen.blit(item_box_img, item_box_rect.topleft)

        if selected_item:
            name, img = selected_item
            screen.blit(img, (800, 220))
            draw_text(name, 800, 310)

        if show_use_confirm:
            draw_text("このアイテムを使いますか？", 800, 340)
            draw_use_confirm_buttons()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if player_turn and event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if show_use_confirm:
                    if use_confirm_rects.get("yes") and use_confirm_rects["yes"].collidepoint(event.pos):
                        apply_item_effect(selected_item[0])
                        used_items.add(selected_item[0])
                        item_used_this_turn = True
                        selected_item = None
                        show_use_confirm = False
                    elif use_confirm_rects.get("no") and use_confirm_rects["no"].collidepoint(event.pos):
                        selected_item = None
                        show_use_confirm = False
                else:
                    if shoot_self_btn.collidepoint(event.pos):
                        result = shoot("プレイヤー", "プレイヤー")
                        if result == "miss":
                            player_turn = True  # 空砲ならもう一度自分のターン
                        else:
                            turn_phase = "enemy_wait"
                            enemy_action_timer = pygame.time.get_ticks()
                            player_turn = False
                        selected_item = None
                        item_used_this_turn = False
                        item_box_clicked_this_turn = False
                    elif shoot_opponent_btn.collidepoint(event.pos):
                        shoot("プレイヤー", "相手")
                        turn_phase = "enemy_wait"
                        enemy_action_timer = pygame.time.get_ticks()
                        player_turn = False
                        selected_item = None
                        item_used_this_turn = False
                        item_box_clicked_this_turn = False
                    elif item_box_rect.collidepoint(event.pos) and not item_box_clicked_this_turn:
                        available_items = [item for item in item_list if item[0] not in used_items]
                        if available_items:
                            selected_item = random.choice(available_items)
                            item_box_clicked_this_turn = True
                    elif selected_item and not item_used_this_turn:
                        name, img = selected_item
                        item_rect = pygame.Rect(800, 220, img.get_width(), img.get_height())
                        if item_rect.collidepoint(event.pos):
                            show_use_confirm = True

        # 相手のターン処理
        if not player_turn and not game_over:
            pygame.time.wait(1000)
            # 敵の行動フェーズ
        if turn_phase == "enemy_wait":
            if skip_opponent_turn:
                message = "相手のターンはスキップされました。"
                skip_opponent_turn = False
                turn_phase = "player"
                player_turn = True 
                item_used_this_turn = False
                item_box_clicked_this_turn = False
            elif pygame.time.get_ticks() - enemy_action_timer > 1000:
                turn_phase = "enemy_action"
        # フェーズ処理：敵の行動（アイテム＋攻撃）
        elif turn_phase == "enemy_action":
            if not game_over:
                if enemy_can_use_items and random.random() < 0.3:
                    enemy_item = random.choice(item_list)
                    item_name = enemy_item[0]
                    message = f"相手が「{item_name}」を使った！"

                    if item_name == "虫眼鏡":
                        Item.searchglass(chamber[0])
                    elif item_name == "タバコ":
                        opponent_hp = Item.tobacco(opponent_hp)
                    elif item_name == "のこぎり":
                        opponent_hp = Item.saw(chamber[0], opponent_hp)
                    elif item_name == "手錠":
                        Item.handcuffs()
                target = random.choice(["プレイヤー", "相手"])
                shoot("相手", target)

            #プレイヤーのターンに戻す
            turn_phase = "player"
            player_turn = True  
            item_used_this_turn = False
            item_box_clicked_this_turn = False

        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()
    sys.exit()