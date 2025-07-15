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
font = pygame.font.Font(font_path, 28) if font_path else pygame.font.SysFont("msgothic", 28)


# ゲームの初期値
bullet_count = 1  # 実弾は1発
empty_count = random.randint(1, 3)  # 空砲は1〜3発ランダム
chamber_size = bullet_count + empty_count
player_turn = True
game_over = False
message = "リロード完了！"
action_log = ""
chamber = []
turn_count = 0
skip_opponent_turn = False
player_turn = True
enemy_can_use_items = True


# HP初期設定
player_hp = 3
opponent_hp = 3

# 最後に表示するターン名（ゲームオーバー後用）
final_turn_text = "あなた" if player_turn else "こうかとん"

# 弾をロード
def load_bullets():
    global chamber
    chamber = [1] * bullet_count + [0] * empty_count
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


# 銃を撃つ
def shoot(shooter, target):
    global message, game_over, turn_count, action_log
    global player_hp, opponent_hp, chamber, final_turn_text

    if chamber:
        round = chamber.pop(0)  # 次の弾を取り出す
        turn_count += 1
        if round == 1:  # 実弾
            if target == "あなた":
                player_hp -= 1
                message = f"バン！ {target} が撃たれた！ 残りHP: {player_hp}"
                action_log = f"{shooter} は {target} に向かって撃った！"
                if player_hp <= 0:
                    message = "あなたのHPは0 こうかとんの勝ち！"
                    game_over = True
            else:
                opponent_hp -= 1
                message = f"バン！ {target} が撃たれた！ 残りHP: {opponent_hp}"
                action_log = f"{shooter} は {target} に向かって撃った！"
                if opponent_hp <= 0:
                    message = "こうかとんのHPは0 あなたの勝ち！"
                    game_over = True
        else:  # 空砲
            message = f"カチッ！ {target} は生き残った！"
            action_log = f"{shooter} は {target} に向かって撃った！"
    else:
        message = "弾はもう残っていません"
        action_log = "弾切れ　ゲームオーバー"
        game_over = True

    # 最後のターン表示を固定
    if game_over:
        final_turn_text = "あなた" if player_turn else "こうかとん"


class Item:
    """
    アイテムに関するクラス
    """
    #次の弾が実弾か空弾かを判定し、結果を出力
    @staticmethod
    def searchglass(round):
        global message
        if round == 1:
            message = "次の弾は実弾だ。"
        else:
            message = "虫眼鏡：次の弾は空弾です。"
    
    #HP1を回復させる
    @staticmethod
    def tobacco(hp):
        global message
        if hp < 3:
            hp += 1
            message = "タバコを使ってHPを1回復した。"
        else:
            message = "タバコを使ったが、HPはすでに最大だった。"
        return hp

    #実弾だった場合、ダメージが2倍になる
    @staticmethod
    def saw(round, hp):
        global message
        if round == 1:
            hp -= 2
            message = "のこぎりを使った。ダメージが2倍になった。"
        return hp
        
    #相手のターンを一回スキップする
    @staticmethod
    def handcuffs():
        global skip_opponent_turn,message,enemy_can_use_items
        skip_opponent_turn = True
        enemy_can_use_items = False
        message = "手錠を使って相手のターンをスキップした。"
 
# 共通画面描画
def draw_main_screen():
    screen.fill(WHITE)

    # ターン表示（ゲーム終了後は固定）
    turn_display = "ターン： " + (final_turn_text if game_over else ("あなた" if player_turn else "こうかとん"))
    draw_text("こうかとん・ルーレット", (WIDTH - font.size("こうかとん・ルーレット")[0]) // 2, 40)
    draw_text(turn_display, 200, 100)
    draw_text(message, 200, 250)
    draw_text(f"ターン数： {turn_count}", 200, 150)
    draw_text(f"残りの弾数： {len(chamber)}", 200, 300)
    draw_text(f"アクション： {action_log}", 200, 200)
    draw_text(f"あなたのHP： {player_hp}", 180, 500, RED)
    draw_text(f"こうかとんのHP： {opponent_hp}", 650, 500, BLUE)

def opponent_turn():
    """こうかとんのターン演出"""
    global player_turn

    draw_main_screen()
    pygame.display.flip()
    pygame.time.wait(2000)  # 2秒待機

    target = random.choice(["あなた", "こうかとん"])
    message = f"こうかとんは {target} を狙った！"
    draw_main_screen()
    pygame.display.flip()
    pygame.time.wait(1000)  # 1秒表示

    shoot("こうかとん", target)
    draw_main_screen()
    pygame.display.flip()
    pygame.time.wait(3000)  # 結果を3秒表示

    # クリックで自分のターンへ
    waiting_for_click = True
    while waiting_for_click and not game_over:
        draw_main_screen()
        draw_text("クリックであなたのターンへ", 370, 400, BLACK)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting_for_click = False
    player_turn = True

def main():
    global player_turn, game_over, skip_opponent_turn

    load_bullets()  # 最初にリロード

    while True:
        draw_main_screen()

        # 操作ボタン
        if not game_over and player_turn:
            shoot_self_btn = draw_button("自分を撃つ", 200, 400, 150, 50, RED)
            shoot_opponent_btn = draw_button("相手を撃つ", 700, 400, 150, 50, BLUE)
        elif game_over:
            draw_text("ESCで終了", 500, 400, RED)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over and player_turn:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if shoot_self_btn.collidepoint(event.pos):
                        shoot("あなた", "あなた")
                        draw_main_screen()
                        pygame.display.flip()
                        pygame.time.wait(3000)  # 結果を3秒表示
                        player_turn = False
                    elif shoot_opponent_btn.collidepoint(event.pos):
                        shoot("あなた", "こうかとん")
                        draw_main_screen()
                        pygame.display.flip()
                        pygame.time.wait(3000)  # 結果を3秒表示
                        player_turn = False
            elif game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if not player_turn and not game_over:

            pygame.time.wait(1000)
            if skip_opponent_turn:
                skip_opponent_turn = False
                player_turn = True
            else:
                opponent_turn()


if __name__ == "__main__":
    pygame.init()
    main()
    pygame.quit()
    sys.exit()
