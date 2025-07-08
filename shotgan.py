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

# フォントを日本語に設定
font_path = pygame.font.match_font("msgothic")
if not os.path.exists(font_path):
    font_path = pygame.font.match_font("msgothic")
font = pygame.font.Font(font_path, 28) if font_path else pygame.font.SysFont("msgothic", 28)

# ゲームの初期値
bullet_count = 2
chamber_size = 6
game_over = False
message = "ゲーム開始！"
action_log = ""
chamber = []
turn_count = 0

# 空弾の数をランダムに設定
def load_bullets():
    global chamber
    chamber = [0] * chamber_size
    bullets = random.sample(range(chamber_size), bullet_count)
    for i in bullets:
        chamber[i] = 1

def rotate_chamber():
    random.shuffle(chamber)

# テキスト表示
def draw_text(text, x, y, color=BLACK):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# 操作ボタンの表示
def draw_button(text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h))
    draw_text(text, x + 10, y + 10)
    return pygame.Rect(x, y, w, h)

#アイテムボックスとアイテムの画像
item_box_img = pygame.image.load("fig/alien1.png")
item_box_img = pygame.transform.scale(item_box_img, (100, 100))
item_list = [
    ("虫眼鏡", pygame.image.load("fig/0.png")),
    ("タバコ", pygame.image.load("fig/1.png")),
    ("ノコギリ", pygame.image.load("fig/2.png")),
    ("手錠", pygame.image.load("fig/3.png"))    
]
selected_item = None
show_use_confirm = False 

# 銃を撃つ
def shoot(shooter, target):
    global message, game_over, turn_count, action_log
    if chamber:
        round = chamber.pop(0)
        turn_count += 1
        if round == 1:
            message = f"バン！ {target} が撃たれた！"
            action_log = f"{shooter} が撃った対象： {target}. {target} が撃たれた！"
            game_over = True
        else:
            message = f"カチッ！ {target} は生き残った。"
            action_log = f"{shooter} が撃った対象： {target}. {target} は生き残った。"
    else:
        message = "弾はもう残っていません。"
        action_log = "弾切れ。ゲームオーバー。"
        game_over = True

# アップデート
load_bullets()
rotate_chamber()

def main():
    global selected_item
    selected_item = None
    player_turn = True
    while True:
        screen.fill(WHITE)

        draw_text("こうかとん・ルーレット", 280, 50)
        draw_text(f"ターン： {'プレイヤー' if player_turn else '相手'}", 300, 100)
        draw_text(message, 250, 150)
        draw_text(f"ターン数： {turn_count}", 300, 200)
        draw_text(f"弾数： {chamber.count(1)}", 300, 240)
        draw_text(f"空砲： {chamber.count(0)}", 300, 280)
        draw_text(f"アクション： {action_log}", 100, 320)

        # 操作ボタンを表示
        shoot_self_btn = draw_button("自分を撃つ", 200, 400, 150, 50, RED)
        shoot_opponent_btn = draw_button("Shoot 相手", 450, 400, 150, 50, BLUE)

        item_box_rect = pygame.Rect(800, 100, 100, 100)  # アイテムボックスの範囲
        screen.blit(item_box_img, item_box_rect.topleft)

        # アイテム表示（選ばれていれば）
        if player_turn:
            screen.blit(item_box_img, (800, 100))
        if selected_item:
            name, img = selected_item
            screen.blit(img, (800, 220))  # アイテム画像の表示位置
            draw_text(name, 800, 310)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if player_turn and event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if shoot_self_btn.collidepoint(event.pos):
                    shoot("プレイヤー", "プレイヤー")
                    player_turn = False
                    selected_item = None
                elif shoot_opponent_btn.collidepoint(event.pos):
                    shoot("プレイヤー", "相手")
                    player_turn = False
                    selected_item = None
                elif item_box_rect.collidepoint(event.pos):
                    selected_item = random.choice(item_list)

        # 相手の動き
        if not player_turn and not game_over:
            pygame.time.wait(1000)
            target = random.choice(["プレイヤー", "相手"])
            shoot("相手", target)
            player_turn = True

        pygame.display.flip()
if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()
    sys.exit()
