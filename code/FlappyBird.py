# Pygame module provide functions to deal with graphic, sound and other features
import random, pygame, sys, time
# Use function without call module name
from pygame.locals import *

# Use to connect mysql database
import mysql.connector as c

# Background Music
pygame.mixer.init()
pygame.mixer.music.load("music/91476_Glorious_morning.mp3")
pygame.mixer.music.play(-1, 0.0)
FPS = 30

# Size of game screen
WINDOWWIDTH = 600
WINDOWHEIGHT = 600

# Size of bird model (x, y)
SIZE_BIRD = (50, 40)
TIME_CHANGE_BIRD = 4  # Time to change from bird 1 <=> bird 2
SPEED_BIRD_FLY = -15  # Speed of each time bird fly up
IMG_BIRD_1 = pygame.image.load('img/bird1.png')  # Bird model 1
IMG_BIRD_2 = pygame.image.load('img/bird2.png')  # Bird model 2
IMG_COT = pygame.image.load('img/column.png')  # Column model
GRAVITATION = 1.25

# Color R    G    B
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
YELLOW = (255, 255, 0)

# Size of column model
SIZE_COLUMN = 70
SIZE_BLANK = 200  # This is where the bird model can fly throw
DISTANCE_COLUMN = 225
SPEED_COLUMN = 5  # Speed of column move to the left

TIME_CHANGE_COLOR_TEXT = 9

# Database config
HOST = "localhost"
USER = "root"
PASSWORD = ""
DATABASE_NAME = "flappy_bird"


def getRecordListSql():
    m = c.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE_NAME)
    cur = m.cursor(named_tuple=True)
    cur.execute("select * from score_record order by score DESC")
    listRecord = []
    for i in cur:
        record = Record(i.id, i.player_name, i.score, i.play_date)
        listRecord.append(record)
    return listRecord


class Record():
    def __init__(self, id, name, score, date):
        self.id = id
        self.name = name
        self.score = score
        self.date = date


def saveRecord(name, score):
    m = c.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE_NAME)
    my = m.cursor()
    my.execute("insert into score_record(player_name, score) values('{}','{}')".format(name, score))
    m.commit()


# Bird Model
class Bird():
    # (x,y)= Position of bird in game screen, speed= moving speed
    def __init__(self, y=WINDOWHEIGHT / 2 - SIZE_BIRD[1] / 2, speed=0, status=1):
        self.x = WINDOWWIDTH / 2 - SIZE_BIRD[0] / 2
        self.y = y
        self.speed = speed
        self.status = status

    # To draw object in game screen
    def draw(self):
        # Base on status to draw movement of the bird
        if self.status <= TIME_CHANGE_BIRD:
            DISPLAYSURF.blit(IMG_BIRD_1, (self.x, self.y))
        else:
            DISPLAYSURF.blit(IMG_BIRD_2, (self.x, self.y))

    # Update bird status
    def update(self, fly, speed_bird_fly=SPEED_BIRD_FLY):
        if fly == True:  # Bid fly up
            self.speed = speed_bird_fly
        # fall as gravities
        self.y += self.speed + GRAVITATION / 2
        self.speed += GRAVITATION
        # check bird status
        if self.status > TIME_CHANGE_BIRD * 2:
            self.status = 1
        else:
            self.status += 1


# Column model
class Column():
    def __init__(self, x, y='default'):  # x,y is top position of the column
        self.x = x
        self.y = random.randrange(80, WINDOWHEIGHT - SIZE_BLANK - 100, 5)  # Get random y
        if y != 'default':
            self.y = y

    def draw(self):
        # Duplicate to get top and bottom column
        DISPLAYSURF.blit(IMG_COT, (self.x, self.y - 600))
        DISPLAYSURF.blit(IMG_COT, (self.x, self.y + SIZE_BLANK))

    def update(self):
        self.x -= SPEED_COLUMN


class Columns():
    def __init__(self):
        self.listColumn = []
        # The column list will show in the screen
        for i in range(3):
            self.listColumn.append(Column((DISTANCE_COLUMN * i) + WINDOWWIDTH))

    # Make new column list when start game
    def makeNewListColumn(self):
        self.listColumn = []
        for i in range(3):
            self.listColumn.append(Column((DISTANCE_COLUMN * i) + WINDOWWIDTH))

    def draw(self):
        for i in range(len(self.listColumn)):
            self.listColumn[i].draw()

    def update(self):
        for i in range(len(self.listColumn)):
            self.listColumn[i].update()
        # Delete left column when bird move throw and make new column
        if self.listColumn[0].x < -SIZE_COLUMN:
            self.listColumn.pop(0)
            self.listColumn.append(Column(self.listColumn[1].x + DISTANCE_COLUMN))


class Scenes():
    def __init__(self, option=1):
        self.option = option  # Base on the input to draw new screen (1: gameStart, 2: gamePlay, 3: gameOver, 4: gameHighScore)

    def gameStart(self, bird):
        bird.y = WINDOWHEIGHT / 2 - SIZE_BIRD[1] / 2
        bird.speed = 0
        clickToStart = ClickToST('Click to start')
        headingFlappyBird = Heading('FLAPPY BIRD')
        # Game stage 1 loop
        while True:
            # Draw new background
            DISPLAYSURF.blit(IMG_BG, (0, 0))
            mouseClick = False  # Check mouse click
            # Detect user input
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONUP:
                    mouseClick = True
            if mouseClick == True:
                break
            isFly = False
            if bird.y > WINDOWHEIGHT / 2:
                isFly = True
            bird.draw()
            bird.update(isFly, -10)
            clickToStart.draw()
            clickToStart.update()
            headingFlappyBird.update()
            headingFlappyBird.draw()
            pygame.display.update()
            FPSCLOCK.tick(FPS)
        self.option = 2

    def gamePlay(self, bird, columns, score):
        score.text = '0'
        columns.makeNewListColumn()
        bird.speed = SPEED_BIRD_FLY
        while True:
            DISPLAYSURF.blit(IMG_BG, (0, 0))
            mouseClick = False  # Check mouse click
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONUP:
                    mouseClick = True
            bird.draw()
            bird.update(mouseClick)
            columns.draw()
            columns.update()
            # Add score
            if GameControl.isAddScore(columns) == True:
                score.update()
            score.draw()

            # Check collide
            isCollide = GameControl.isCollide(bird, columns)
            if isCollide == True:
                break

            pygame.display.update()
            FPSCLOCK.tick(FPS)
        self.option = 3

    def gameOver(self, bird, columns, score):
        bird.speed = 0
        headingGameOver = Heading('GAMEOVER')
        birdStatus = bird.status
        isBirdAminationFinish = False  # Check bird fall
        inHeadingAminationFinish = False  # Check heading fall
        while True:
            DISPLAYSURF.blit(IMG_BG, (0, 0))
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()

            columns.draw()
            bird.draw()
            bird.update(False)
            bird.status = birdStatus
            if bird.y >= WINDOWHEIGHT - SIZE_BIRD[1]:
                bird.y = WINDOWHEIGHT - SIZE_BIRD[1]
                bird.speed = 0
                isBirdAminationFinish = True
            headingGameOver.draw()
            headingGameOver.update()
            if headingGameOver.y >= WINDOWHEIGHT / 2 - 90:
                headingGameOver.y = WINDOWHEIGHT / 2 - 90
                headingGameOver.speed = 0
                inHeadingAminationFinish = True
            if isBirdAminationFinish == True and inHeadingAminationFinish == True:
                break
            pygame.display.update()
            FPSCLOCK.tick(FPS)
        clickToContinue = ClickToST('Enter')
        # Variable to store user name
        enterName = EnterName("Name:")
        user_text = ""
        base_font = pygame.font.SysFont('Comic Sans MS', 20)
        input_rect = pygame.Rect(360, WINDOWHEIGHT * 0.58, 140, 32)
        color_active = pygame.Color('lightskyblue3')
        color_passive = pygame.Color('chartreuse4')
        active = False
        while True:
            scoreText = Text('Score: ' + score.text, WINDOWWIDTH / 2 - len('Score: ' + score.text) / 2,
                             WINDOWHEIGHT / 2, 50, BLACK)
            DISPLAYSURF.blit(IMG_BG, (0, 0))
            mouseClick = False
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        active = True
                    else:
                        active = False

                if event.type == pygame.KEYDOWN:
                    # Check for backspace
                    if event.key == pygame.K_BACKSPACE:
                        # get text input from 0 to -1 i.e. end.
                        user_text = user_text[:-1]
                    # Unicode standard is used for string
                    # formation
                    else:
                        user_text += event.unicode
                if event.type == KEYUP:
                    if event.key == pygame.K_RETURN:
                        saveRecord(user_text[0:-1], int(score.text))
                        print(score)
                        mouseClick = True
            if mouseClick == True:
                break
            columns.draw()
            bird.draw()
            headingGameOver.draw()
            clickToContinue.draw()
            clickToContinue.update()
            scoreText.draw()
            enterName.draw()
            if active:
                color = color_active
            else:
                color = color_passive
            pygame.draw.rect(DISPLAYSURF, color, input_rect)
            text_surface = base_font.render(user_text, True, YELLOW)
            # render at position stated in arguments
            DISPLAYSURF.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            # set width of textfield so that text cannot get
            # outside of user's text input
            input_rect.w = max(100, text_surface.get_width() + 10)
            # display.flip() will update only a portion of the
            # screen to updated, not full area
            pygame.display.update()
            FPSCLOCK.tick(FPS)
        self.option = 4

    def gameRanking(self, bird, columns, score):
        bird.speed = 0
        clickToReplay = ClickToST('Click to replay')
        headingRankTable = TableHeading('Bird Ranking')
        tableRankingColumnHeader = TableRankingColumn('Rank')
        tableNameColumnHeader = TableNameColumn('Bird Name')
        tableScoreColumnHeader = TableScoreColumn('Score')
        tableDateColumnHeader = TableDateColumn("Date")

        while True:
            DISPLAYSURF.blit(IMG_BG, (0, 0))
            mouseClick = False
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONUP:
                    mouseClick = True
            if mouseClick == True:
                break
            columns.draw()
            bird.draw()
            headingRankTable.draw()
            tableRankingColumnHeader.draw()
            tableNameColumnHeader.draw()
            tableScoreColumnHeader.draw()
            tableDateColumnHeader.draw()
            i = 0
            for record in getRecordListSql():
                i = i + 1
                tableRanking = TableRankingColumn('#' + str(i))
                tableRanking.updatePosion(i)
                tableRanking.draw()
                tableName = TableNameColumn(str(record.name))
                tableName.updatePosion(i)
                tableName.draw()
                tableScore = TableScoreColumn(str(record.score))
                tableScore.updatePosion(i)
                tableScore.draw()
                tableDate = TableDateColumn(str(record.date))
                tableDate.updatePosion(i)
                tableDate.draw()
                if i >= 10:
                    break
            clickToReplay.draw()
            clickToReplay.update()
            pygame.display.update()
            FPSCLOCK.tick(FPS)
        self.option = 1

# This class to specify and draw text on screen
class Text():
    def __init__(self, text, x, y, size, color):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self):
        fontObj = pygame.font.SysFont('Comic Sans MS', self.size)
        textSurfaceObj = fontObj.render(self.text, False, self.color)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (self.x, self.y)
        DISPLAYSURF.blit(textSurfaceObj, textRectObj)


class Score(Text):
    def __init__(self, text, x=WINDOWWIDTH / 2, y=WINDOWHEIGHT / 6, size=50, color=BLACK):
        super().__init__(text, x, y, size, color)

    def update(self):
        self.text = str(int(self.text) + 1)


class EnterName(Text):
    def __init__(self, text, y=WINDOWHEIGHT * 0.6, size=40, color=BLACK):
        super().__init__(text, WINDOWWIDTH / 2 - len(text) / 2, y, size, color)


class ClickToST(Text):
    def __init__(self, text, y=WINDOWHEIGHT * 0.7, size=40, color=BLACK):
        super().__init__(text, WINDOWWIDTH / 2 - len(text) / 2, y, size, color)
        self.status = 1

    def update(self):
        # Chọn màu dựa vào status
        if self.status <= TIME_CHANGE_COLOR_TEXT:
            self.color = BLACK
        else:
            self.color = GREY
        if self.status > TIME_CHANGE_COLOR_TEXT * 2:
            self.status = 1
        else:
            self.status += 1


class Heading(Text):
    def __init__(self, text, y=-100, size=90, color=BLACK):
        super().__init__(text, WINDOWWIDTH / 2 - len(text) / 2, y, size, color)
        self.speed = 0

    def update(self):
        # Rơi theo gia tốc đến vị trí xác định
        self.y += self.speed + GRAVITATION / 2
        self.speed += GRAVITATION
        if self.y >= WINDOWHEIGHT / 2 - 90:
            self.y = WINDOWHEIGHT / 2 - 90


class TableHeading(Text):
    def __init__(self, text, y=30, size=50, color=YELLOW):
        super().__init__(text, WINDOWWIDTH / 2 - len(text) / 2, y, size, color)
        self.speed = 0


class TableRankingColumn(Text):
    def __init__(self, text, y=80, size=25, color=YELLOW):
        super().__init__(text, (WINDOWWIDTH / 6) * 0.75 - len(text) / 2, y, size, color)
        self.speed = 0

    def updatePosion(self, time):
        u = self.y
        self.y = u + 25 * time


class TableNameColumn(Text):
    def __init__(self, text, y=80, size=25, color=YELLOW):
        super().__init__(text, (WINDOWWIDTH / 6) * 2.25 - len(text) / 2, y, size, color)
        self.speed = 0

    def updatePosion(self, time):
        u = self.y
        self.y = u + 25 * time


class TableScoreColumn(Text):
    def __init__(self, text, y=80, size=25, color=YELLOW):
        super().__init__(text, (WINDOWWIDTH / 6) * 3.75 - len(text) / 2, y, size, color)
        self.speed = 0

    def updatePosion(self, time):
        u = self.y
        self.y = u + 25 * time


class TableDateColumn(Text):
    def __init__(self, text, y=80, size=25, color=YELLOW):
        super().__init__(text, (WINDOWWIDTH / 6) * 5 - len(text) / 2, y, size, color)
        self.speed = 0

    def updatePosion(self, time):
        u = self.y
        self.y = u + 25 * time


class GameControl():
    def isCollide(bird, columns):  # Check collide
        def isCollide1Column(bird, column):
            # Các giới hạn chim
            limitBirdTop = bird.y
            limitBirdBottom = bird.y + SIZE_BIRD[1]
            limitBirdLeft = bird.x
            limitBirdRight = bird.x + SIZE_BIRD[0]
            # Column limit
            limitColumnLeft = column.x
            limitColumnRight = column.x + SIZE_COLUMN
            limitColumnTop = column.y
            limitColumnBottom = column.y + SIZE_BLANK
            # Check collide
            if limitBirdLeft > limitColumnRight - SIZE_COLUMN / 4:
                return False
            if (limitBirdRight - limitColumnLeft) > 0 and (limitColumnTop - limitBirdTop) > 0:
                return True
            if (limitBirdBottom - limitColumnBottom) > 0 and (limitBirdRight - limitColumnLeft) > 0:
                return True
            if limitBirdBottom >= WINDOWHEIGHT or limitBirdTop < -100:
                return True
            return False

        # Check collide for all column
        for i in range(len(columns.listColumn)):
            if isCollide1Column(bird, columns.listColumn[i]):
                return True
        return False

    def isAddScore(columns):  # Add score
        midWindow = WINDOWWIDTH / 2
        # When the column in middle of the screen
        for i in range(len(columns.listColumn)):
            midColumn = columns.listColumn[i].x + SIZE_COLUMN / 2
            if abs(midWindow - midColumn) <= SPEED_COLUMN / 2:
                return True
        return False


def main():
    global FPSCLOCK, DISPLAYSURF, IMG_BG
    # Call this first to let other functions of pygame work
    pygame.init()
    pygame.display.set_caption('GROUP 6: FLAPPY BIRD')
    FPSCLOCK = pygame.time.Clock()
    # This function to set window size
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    # Set logo
    logo = pygame.image.load('img/logo.png')
    pygame.display.set_icon(logo)
    IMG_BG = pygame.image.load('img/bg.png').convert()
    scene = Scenes()
    bird = Bird()
    columns = Columns()
    score = Score('0')
    # Main game loop
    while True:
        if scene.option == 1:
            scene.gameStart(bird)
        elif scene.option == 2:
            scene.gamePlay(bird, columns, score)
        elif scene.option == 3:
            scene.gameOver(bird, columns, score)
        elif scene.option == 4:
            scene.gameRanking(bird, columns, score)


if __name__ == '__main__':
    main()
