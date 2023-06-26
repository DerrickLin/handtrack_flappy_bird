import pygame, sys, random, os
from pygame.locals import *
from video import threadVideo

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 585
pygame.init()
pygame.mixer.init()
win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Flappy 紫色恐怖')


P_WIDTH = 30
P_HEIGHT = 30
G = 0.3
SPEEDFLY = -4
PURPLE_IMG = pygame.image.load('img/purple.png')
PURPLE_IMG = pygame.transform.scale(PURPLE_IMG, (39, 62))

COLUMN_WIDTH = 60
COLUMN_HEIGHT = 500
BLANK = 250   #水管上下間距
DISTANCE = 300   #水管左右間距
COLUMN_SPEED = 1
COLUMN_IMG = pygame.image.load('img/column_3.png')
BACKGROUND = pygame.image.load('img/bg.png')

# pygame.init()
FPS = 60
fpsClock = pygame.time.Clock()

coin_sound = pygame.mixer.Sound(os.path.join("sound", "coin03.mp3")) 
death = pygame.mixer.Sound(os.path.join("sound", "death.mp3")) 
pygame.mixer.music.load(os.path.join("sound", "loading.mp3"))
pygame.mixer.music.set_volume(0.4)

#角色
class Bird():
    def __init__(self):
        #定義屬性
        self.width = P_WIDTH
        self.height = P_HEIGHT
        self.x = (WINDOW_WIDTH - self.width)/2
        self.y = (WINDOW_HEIGHT- self.height)/2
        self.speed = 0
        self.suface = PURPLE_IMG

    def draw(self):
        win.blit(self.suface, (int(self.x), int(self.y)))
    
    def update(self, mouseClick):
        self.y += self.speed + 0.5 * G  #根據重力值G和角色的速度，更新角色的垂直位置 self.y 和速度 self.speed
        self.speed += G
        if mouseClick == True:
            self.speed = SPEEDFLY

# 水管
class Columns():
    def __init__(self):
        self.width = COLUMN_WIDTH
        self.height = COLUMN_HEIGHT
        self.blank = BLANK
        self.distance = DISTANCE
        self.speed = COLUMN_SPEED
        self.surface = COLUMN_IMG
        self.ls = []
        
        #儲存水管的位子並寫進list裡
        for i in range(3):
            x = WINDOW_WIDTH + i*self.distance
            y = random.randrange(60, WINDOW_HEIGHT - self.blank - 60, 20)
            self.ls.append([x, y])
        
    def draw(self):
        for i in range(3):
            win.blit(self.surface, (self.ls[i][0], self.ls[i][1] - self.height))
            win.blit(self.surface, (self.ls[i][0], self.ls[i][1] + self.blank))
    
    #更新水管的位置
    def update(self):
        for i in range(3):
            self.ls[i][0] -= self.speed  # self.ls[i][0] 減去水管的速度 self.speed，使水管向左移動
        
        if self.ls[0][0] < -self.width:  #如果最前面的水管完全離開了視窗，則將其從列表中移除並在最後添加一個新的水管。
            self.ls.pop(0)
            x = self.ls[1][0] + self.distance
            y = random.randrange(60, WINDOW_HEIGHT - self.blank - 60, 10)
            self.ls.append([x, y])
     
        
#判斷是否有碰撞            
def rectCollision(rect1, rect2):
    if rect1[0] <= rect2[0] + rect2[2] and rect2[0] <= rect1[0] + rect1[2] and rect1[1] <= rect2[1] + rect2[3] and rect2[1] <= rect1[1] + rect1[3]:
        return True
    return False


#檢測遊戲是否結束，角色是否碰撞到水管或超出視窗範圍
def isGameOver(bird, columns):
    for i in range(3):
        rectBird = [bird.x, bird.y, bird.width, bird.height]
        rectColumn1 = [columns.ls[i][0], columns.ls[i][1] - columns.height, columns.width, columns.height]
        rectColumn2 = [columns.ls[i][0], columns.ls[i][1] + columns.blank, columns.width, columns.height]
        if rectCollision(rectBird, rectColumn1) == True or rectCollision(rectBird, rectColumn2) == True:
            return True
    if bird.y + bird.height < 0 or bird.y + bird.height > WINDOW_HEIGHT:
        return True
    return False


#分數
class Score():
    def __init__(self):
        self.score = 0
        self.addScore = True
    
    def draw(self):
        last_score = max_score()
        font = pygame.font.SysFont('consolas', 17)
        record_Surface = font.render('Record: ' + str(last_score), True, (255, 255, 255))
        win.blit(record_Surface, (300, 15))
   
        font = pygame.font.SysFont('consolas', 40)
        scoreSuface = font.render(str(self.score), True, (255, 255, 255))
        textSize = scoreSuface.get_size()
        win.blit(scoreSuface, (int((WINDOW_WIDTH - textSize[0])/2), 100))
    
    def update(self, bird, columns):
        collision = False
        for i in range(3):
            rectColumn = [columns.ls[i][0] + columns.width, columns.ls[i][1], 1, columns.blank]
            rectBird = [bird.x, bird.y, bird.width, bird.height]
            if rectCollision(rectBird, rectColumn) == True:
                collision = True
                break
        if collision == True:
            if self.addScore == True:
                coin_sound.play()
                self.score += 1  # 過一根水管加一分
                columns.speed += 0.15  # 隨分數越高速度越快 
            self.addScore = False
        else:
            self.addScore = True


#更新紀錄分數
def update_score(new_score):
    score = max_score()
    with open("score.txt", "w") as f:
        if int(score) > new_score:
            f.write(str(score))
        else:
            f.write(str(new_score))

#保存紀錄分數並回傳
def max_score():
    with open("score.txt", "r") as f:
        lines = f.readlines()
        score = lines[0].strip()
    return score    

#遊戲開始畫面
def gameStart(bird):
    bird.__init__()
    font = pygame.font.SysFont('consolas', 50)
    headingSurface = font.render('Flappy Purple', True, (255, 48, 48)) #遊戲名稱
    headingSize = headingSurface.get_size()
    
    font = pygame.font.SysFont('consolas', 30)
    commentSurface = font.render('Click to start', True, (255, 255, 255))
    commentSize = commentSurface.get_size()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                return

        win.blit(BACKGROUND, (0, 0))
        bird.draw()
        win.blit(headingSurface, (int((WINDOW_WIDTH - headingSize[0])/2), 100))
        win.blit(commentSurface, (int((WINDOW_WIDTH - commentSize[0])/2), 500))

        pygame.display.update()
        fpsClock.tick(FPS)


#遊戲進行畫面
def gamePlay(bird, columns, score, xyz):
    bird.__init__()
    bird.speed = SPEEDFLY
    columns.__init__()
    score.__init__()
    pygame.mixer.music.play(-1)
    while True:
        mouseClick = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mouseClick = True
        if xyz.dist < 0.1:
            mouseClick = True
        print(xyz.dist)    # 印出兩指距離
        win.blit(BACKGROUND, (0, 0))

        #呼叫函式
        columns.draw()
        columns.update()
        bird.draw()
        bird.update(mouseClick)
        score.draw()
        score.update(bird, columns)

        if isGameOver(bird, columns) == True:
            return

        pygame.display.update()
        fpsClock.tick(FPS)

#失敗畫面
def gameOver(bird, columns, score):
    font = pygame.font.SysFont('consolas', 60)
    headingSurface = font.render('GAMEOVER', True, (255, 48, 48))
    headingSize = headingSurface.get_size()
    
    font = pygame.font.SysFont('consolas', 25)
    commentSurface = font.render('Press "space" to replay', True, (255, 255, 255))
    commentSize = commentSurface.get_size()

    font = pygame.font.SysFont('consolas', 30)
    scoreSurface = font.render('Score: ' + str(score.score), True, (255, 255, 255))
    scoreSize = scoreSurface.get_size()

    death.play()
    pygame.mixer.music.stop()
    
    while True:
        update_score(score.score)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYUP:
                if event.key == K_SPACE:
                    return
        
        win.blit(BACKGROUND, (0, 0))
        # pygame.display.flip()
        columns.draw()
        bird.draw()
        win.blit(headingSurface, (int((WINDOW_WIDTH - headingSize[0])/2), 100))
        win.blit(commentSurface, (int((WINDOW_WIDTH - commentSize[0])/2), 500))
        win.blit(scoreSurface, (int((WINDOW_WIDTH - scoreSize[0])/2), 250))
        
        pygame.display.update()
        fpsClock.tick(FPS)

pygame.mixer.music.play(-1)  # 背景音樂持續撥放


#主程式
def main():
    bird = Bird()
    columns = Columns()
    score = Score()
    xyz = threadVideo()
    xyz.start()
    
    #遊戲迴圈
    while True:
        gameStart(bird)
        gamePlay(bird, columns, score, xyz)
        gameOver(bird, columns, score)

if __name__ == '__main__':
    main()