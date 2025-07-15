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


# フォントを日本語に設定
font_path = pygame.font.match_font("msgothic")
font = pygame.font.Font(font_path, 28) if font_path else pygame.font.SysFont("msgothic", 28)

# サウンドの設定
pygame.mixer.init()
gunshot_sound = pygame.mixer.Sound("sound\拳銃を撃つ.mp3")  #銃声を読み込み
blank_sound = pygame.mixer.Sound("sound\拳銃の弾切れ.mp3")  #空砲音を読み込み


# ゲームの初期値
# bullet_count = 2
chamber_size = random.randint(1, 7)
game_over = False
message = "リロード完了！"
item_message = ""
action_log = ""
turn_phase = "player"
enemy_action_timer = 0
chamber = []
turn_count = 0
skip_opponent_turn = False
player_turn = True
enemy_can_use_items = True
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

# HP初期設定
player_hp = 3
opponent_hp = 3

# 最後に表示するターン名（ゲームオーバー後用）
final_turn_text = "あなた" if player_turn else "こうかとん"

# 弾をロード
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
    bullet_count = random.randint(1, chamber_size-1)
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
    global message, game_over, turn_count, action_log
    global player_hp, opponent_hp, chamber, final_turn_text
    global player_turn, skip_opponent_turn 

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
                    gunshot_sound.play()
                    game_over = True
            else:
                opponent_hp -= 1
                message = f"バン！ {target} が撃たれた！ 残りHP: {opponent_hp}"
                action_log = f"{shooter} は {target} に向かって撃った！"
                if opponent_hp <= 0:
                    message = "こうかとんのHPは0 あなたの勝ち！"
                    gunshot_sound.play()
                    game_over = True
        else:  # 空砲
            message = f"カチッ！ {target} は生き残った。"
            action_log = f"{shooter} は {target} に向かって撃った！"
            blank_sound.play()
    else:
        if player_hp != 0 and opponent_hp !=0:  # もし弾がなくなっても双方のHPが残っていたらリロード
            load_bullets()
            rotate_chamber()

        # 最後のターン表示を固定
    if game_over:
        final_turn_text = "あなた" if player_turn else "こうかとん"


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
    global player_turn,message

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

# アイテム画像
item_box_img = pygame.image.load("fig/itembox.png")
item_box_img = pygame.transform.scale(item_box_img, (100, 100))
item_list = [
    ("虫眼鏡", pygame.image.load("fig/searchglass.png")),
    ("タバコ", pygame.image.load("fig/tobacco.png")),
    ("のこぎり", pygame.image.load("fig/saw.png")),
    ("手錠", pygame.image.load("fig/handcuffs.png"))    
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


# メインループ
def main():
    global player_turn, game_over, skip_opponent_turn
    global selected_item, show_use_confirm
    global enemy_can_use_items
    global item_used_this_turn, item_box_clicked_this_turn
    global message
    global turn_phase,enemy_action_timer
    global player_hp,opponent_hp
    load_bullets()  # 最初にリロード
    rotate_chamber()


    while True:
        draw_main_screen()

        screen.blit(background_img, (0, 0))
        screen.blit(current_enemy_img, (0, 0))
        draw_text(f"ターン： {'プレイヤー' if player_turn else '相手'}", 30, 80, BLACK, WHITE)
        draw_text(message, 30, 130, BLACK, WHITE)
        draw_text(f"ターン数： {turn_count}", 30, 180, BLACK, WHITE)
        draw_text(f"弾数： {chamber.count(1)}", 470, 420, BLACK, WHITE)
        draw_text(f"空砲： {chamber.count(0)}", 470, 460, BLACK, WHITE)
        draw_text(f"アクション： {action_log}", 30, 330, BLACK, WHITE)

        # 操作ボタン
        if not game_over and player_turn:
            shoot_self_btn = draw_button("自分を撃つ", 200, 400, 150, 50, RED)
            shoot_opponent_btn = draw_button("相手を撃つ", 700, 400, 150, 50, BLUE)
            item_box_rect = pygame.Rect(800, 100, 100, 100)
        elif game_over:
            draw_text("ESCで終了", 500, 400, RED)

        pygame.display.flip()

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
                        result = shoot("あなた", "あなた")
                        if result == "miss":
                            player_turn = True
                        else:
                            turn_phase = "enemy_wait"
                            enemy_action_timer = pygame.time.get_ticks()
                            player_turn = False
                            selected_item = None
                            item_used_this_turn = False
                            item_box_clicked_this_turn = False
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
                        turn_phase = "enemy_wait"
                        enemy_action_timer = pygame.time.get_ticks()
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
            elif game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()   
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