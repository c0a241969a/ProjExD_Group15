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
last_dead = None  # 誰がやられたか（"player" or "opponent"）
# 画像読み込み
enemy_normal_img = pygame.image.load("fig/enemy.png")
enemy_normal_img = pygame.transform.scale(enemy_normal_img, (WIDTH, HEIGHT))
enemy_damage_img = pygame.image.load("fig/enemy_damage.png")
enemy_damage_img = pygame.transform.scale(enemy_damage_img, (WIDTH, HEIGHT))
current_enemy_img = enemy_normal_img
background_img = pygame.image.load(f"fig/background.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
start_btn_img = pygame.image.load(f"fig/start_button.png")
start_btn_img = pygame.transform.scale(start_btn_img, (WIDTH, HEIGHT))
title_img = pygame.image.load(f"fig/title.png")
title_img = pygame.transform.scale(title_img, (WIDTH, HEIGHT))
gameclear_img = pygame.image.load(f"fig/gameclear.png")
gameclear_img = pygame.transform.scale(gameclear_img, (WIDTH, HEIGHT))
gameover_player_img = pygame.image.load(f"fig/gameover_player.png")
gameover_player_img = pygame.transform.scale(gameover_player_img, (WIDTH, HEIGHT))

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
def draw_text(text, x, y, color=BLACK, outline_color=WHITE, outline_thickness=2):
    # 縁取り（outline）を先に描画
    for dx in [-outline_thickness, 0, outline_thickness]:
        for dy in [-outline_thickness, 0, outline_thickness]:
            if dx == 0 and dy == 0:
                continue
            outline_img = font.render(text, True, outline_color)
            screen.blit(outline_img, (x + dx, y + dy))
    # メインの文字（中央）
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# 操作ボタンの表示
def draw_button(text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h))
    draw_text(text, x + 10, y + 10)
    return pygame.Rect(x, y, w, h)

# 銃を撃つ
def shoot(shooter, target):
    global message, game_over, turn_count, action_log, last_dead, current_enemy_img
    if chamber:
        round = chamber.pop(0)
        turn_count += 1
        if round == 1:
            message = f"バン！ {target} が撃たれた！"
            action_log = f"{shooter} が撃った対象： {target}. {target} が撃たれた！"
            last_dead = "player" if target == "プレイヤー" else "opponent"

            if target == "相手":
                current_enemy_img = enemy_damage_img  # ← ダメージ画像に差し替え！

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


def draw_image_button(img, x, y):
    screen.blit(img, (x, y))
    rect = pygame.Rect(x, y, img.get_width(), img.get_height())
    return rect


def show_title_screen():
    while True:
        screen.blit(title_img, (0, 0))
        start_btn = draw_image_button(start_btn_img, 0, 0)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    return


def main():
    player_turn = True
    while True:
        screen.blit(background_img, (0, 0))
        screen.blit(current_enemy_img, (0, 0))
        draw_text(f"ターン： {'プレイヤー' if player_turn else '相手'}", 30, 80, BLACK, WHITE)
        draw_text(message, 30, 130, BLACK, WHITE)
        draw_text(f"ターン数： {turn_count}", 30, 180, BLACK, WHITE)
        draw_text(f"弾数： {chamber.count(1)}", 470, 420, BLACK, WHITE)
        draw_text(f"空砲： {chamber.count(0)}", 470, 460, BLACK, WHITE)
        draw_text(f"アクション： {action_log}", 30, 330, BLACK, WHITE)

        # 操作ボタン
        shoot_self_btn = draw_button("自分を撃つ", 300, 500, 150, 50, RED)
        shoot_opponent_btn = draw_button("相手を撃つ", 650, 500, 150, 50, BLUE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if player_turn and event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if shoot_self_btn.collidepoint(event.pos):
                    shoot("プレイヤー", "プレイヤー")
                    player_turn = False
                elif shoot_opponent_btn.collidepoint(event.pos):
                    shoot("プレイヤー", "相手")
                    player_turn = False

        # 相手の動き
        if not player_turn and not game_over:
            pygame.time.wait(1000)
            target = random.choice(["プレイヤー", "相手"])
            shoot("相手", target)
            player_turn = True

        # --- ゲームオーバー画面処理（プレイヤー負け時のみ画像） ---
        if game_over:
            if last_dead == "player":
                screen.blit(gameover_player_img, (0, 0))
                pygame.display.update()
                pygame.time.wait(3000)
                pygame.quit()
                sys.exit()
            elif last_dead == "opponent":
                screen.blit(enemy_damage_img, (0, 0))
                pygame.display.update()
                pygame.time.wait(700)

                # 勝利画像を表示
                screen.blit(gameclear_img, (0, 0))
                pygame.display.update()
                pygame.time.wait(3000)
                pygame.quit()
                sys.exit()
            else:
                screen.blit(gameclear_img, (0, 0))
                pygame.display.update()
                pygame.time.wait(3000)
                pygame.quit()
                sys.exit()


        pygame.display.flip()
if __name__ == "__main__":
    pygame.init()
    show_title_screen()
    main()
    pygame.quit()
    sys.exit()
