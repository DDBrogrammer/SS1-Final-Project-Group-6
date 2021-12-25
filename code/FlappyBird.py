# Pygame module provide functions to deal with graphic, sound and other features
import hashlib
import random, pygame, sys, time
# Use function without call module name
from pygame.locals import *
import re
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


# Function to manage with data base
def getPlayerListSql():
    m = c.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE_NAME)
    cur = m.cursor(named_tuple=True)
    cur.execute("select * from player")
    listRecord = []
    for i in cur:
        player = Player(i.id, i.name, i.password, i.email, i.rank)
        listRecord.append(player)
    return listRecord


class Player():
    def __init__(self, id, name, password, email, rank):
        self.id = id
        self.name = name
        self.password = password
        self.email = email
        self.rank = rank


def getPlayerByEmail(email):
    m = c.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE_NAME)
    cur = m.cursor(named_tuple=True)
    query="select * from player where email="+ str(email)
    cur.execute(query)
    player = Player()
    for i in cur:
        player = Player(i.id, i.name, i.password, i.email, i.rank)
    return player


def getRecordByPlayerId(id):
    m = c.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE_NAME)
    cur = m.cursor(named_tuple=True)
    query = "select * from score_record where player_id=" + str(id)
    cur.execute(query)
    listRecord = []
    for i in cur:
        record = Record(i.id, i.score, i.play_date, i.player_id)
        listRecord.append(record)
    return listRecord


class Record():
    def __init__(self, id, score, play_date, player_id):
        self.id = id
        self.score = score
        self.play_date = play_date
        self.player_id = player_id


def savePlayer(email, password, name):
    m = c.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE_NAME)
    my = m.cursor()
    my.execute(
        "insert into player(name,password,email) values('{}','{}','{}')".format(str(name), encryptPassword(password),
                                                                                str(email)))
    m.commit()


def savePlayerRecord(playerId, score):
    m = c.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE_NAME)
    my = m.cursor()
    my.execute(
        "insert into score_record(score,player_id) values('{}','{}')".format(score, playerId))
    m.commit()


def encryptPassword(password):
    hashpass = hashlib.md5(password.encode('utf8')).hexdigest()
    return hashpass


# Validate method
def validateEmail(email):
    # pass the regular expression
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # and the string into the fullmatch() method
    duplicate = False
    for p in getPlayerListSql():
        if p.email == email:
            duplicate = True
    if (re.fullmatch(regex, email)) and duplicate == False:
        return True
    else:
        return False


# GAME MODELS

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


# SCENES AND STAGES

class Scenes():
    def __init__(self, option=1):
        self.option = option  # Base on the input to draw new screen (1: gameStart, 2: gamePlay, 3: gameOver, 4: gameHighScore)

    def gameMenu(self):
        menu_heading = MenuHeading("ACCOUNT")
        login = Login("[L] Login")
        register = Register("[R] Register")
        while True:
            # Draw new background
            DISPLAYSURF.blit(IMG_BG, (0, 0))
            chose = False  # Check chosen
            check_register = False
            check_login = False
            # Detect user input
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    # Check for backspace
                    if event.unicode == "r":
                        check_register = True
                        chose = True

                    if event.unicode == "l":
                        check_login = True
                        chose = True

            if chose:
                break
            menu_heading.draw()
            login.draw()
            register.draw()
            pygame.display.update()
            FPSCLOCK.tick(FPS)
        if check_register and chose:
            self.option = 2
        elif check_login and chose:
            self.option = 3

    def gameRegister(self):
        register_heading = MenuHeading("REGISTER")
        form_name = Name("Name: ")
        form_gmail = Gmail("Gmail: ")
        form_password = Password("Password: ")
        name = ""
        input_name = InputName(name)
        email = ""
        input_email = InputGmail(email)
        password = ""
        input_password = InputPassword(password)
        active_input = 1
        check_enter = False
        while True:
            # Draw new background
            DISPLAYSURF.blit(IMG_BG, (0, 0))
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    # Navigate mouse
                    if event.key == pygame.K_DOWN:
                        active_input = int((active_input + 1) % 3)
                    elif event.key == pygame.K_UP:
                        active_input = int((active_input - 1) % 3)
                    # Check for backspace
                    if active_input == 1:
                        if event.key == pygame.K_BACKSPACE:
                            email = email[:-1]
                            input_email.text = email
                        else:
                            email += event.unicode
                            input_email.text = email
                    elif active_input == 2:
                        if event.key == pygame.K_BACKSPACE:
                            password = password[:-1]
                            input_password.text = password
                        else:
                            password += event.unicode
                            input_password.text = password
                    elif active_input == 0:
                        if event.key == pygame.K_BACKSPACE:
                            name = name[:-1]
                            input_name.text = name
                        else:
                            name += event.unicode
                            input_name.text = name
                if event.type == KEYUP:
                    if event.key == pygame.K_RETURN and validateEmail(input_email.text):
                        savePlayer(str(input_email.text), str(input_password.text), str(input_name.text))
                        check_enter = True
            if check_enter:
                break
            register_heading.draw()
            form_name.draw()
            form_gmail.draw()
            form_password.draw()
            input_email.drawBox()
            input_email.drawText()
            input_password.drawBox()
            input_password.drawText()
            input_name.drawBox()
            input_name.drawText()
            pygame.display.update()
            FPSCLOCK.tick(FPS)
        self.option = 4

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
        self.option = 5

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
        self.option = 6

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
        clickToContinue = ClickToST('ClickToContinue')

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
                    mouseClick = True
            if mouseClick == True:
                break
            columns.draw()
            bird.draw()
            headingGameOver.draw()
            clickToContinue.draw()
            clickToContinue.update()
            scoreText.draw()

            pygame.display.update()
            FPSCLOCK.tick(FPS)
        self.option = 7

    # def gameRanking(self, bird, columns):
    #     bird.speed = 0
    #     clickToReplay = ClickToST('Click to replay')
    #     headingRankTable = TableHeading('Bird Ranking')
    #     tableRankingColumnHeader = TableRankingColumn('Rank')
    #     tableNameColumnHeader = TableNameColumn('Bird Name')
    #     tableScoreColumnHeader = TableScoreColumn('Score')
    #     tableDateColumnHeader = TableDateColumn("Date")
    #     while True:
    #         DISPLAYSURF.blit(IMG_BG, (0, 0))
    #         mouseClick = False
    #         for event in pygame.event.get():
    #             if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
    #                 pygame.quit()
    #                 sys.exit()
    #             if event.type == MOUSEBUTTONUP:
    #                 mouseClick = True
    #         if mouseClick == True:
    #             break
    #         columns.draw()
    #         bird.draw()
    #         headingRankTable.draw()
    #         tableRankingColumnHeader.draw()
    #         tableNameColumnHeader.draw()
    #         tableScoreColumnHeader.draw()
    #         tableDateColumnHeader.draw()
    #         i = 0
    #         for record in getPlayerListSql():
    #             i = i + 1
    #             tableRanking = TableRankingColumn('#' + str(i))
    #             tableRanking.updatePosion(i)
    #             tableRanking.draw()
    #             tableName = TableNameColumn(str(record.name))
    #             tableName.updatePosion(i)
    #             tableName.draw()
    #             tableScore = TableScoreColumn(str(record.score))
    #             tableScore.updatePosion(i)
    #             tableScore.draw()
    #             tableDate = TableDateColumn(str(record.date))
    #             tableDate.updatePosion(i)
    #             tableDate.draw()
    #             if i >= 10:
    #                 break
    #         clickToReplay.draw()
    #         clickToReplay.update()
    #         pygame.display.update()
    #         FPSCLOCK.tick(FPS)
    #     self.option = 1


# TEXT MODELS

# Base Texts class
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


class InputText():
    def __init__(self, text, x, y, size, color):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.rectangle = pygame.Rect(self.x, self.y, 140, 32)

    def drawBox(self):
        pygame.draw.rect(DISPLAYSURF, self.color, self.rectangle)

    def drawText(self):
        fontObj = pygame.font.SysFont('Comic Sans MS', 20)
        text_surface = fontObj.render(self.text, True, YELLOW)
        DISPLAYSURF.blit(text_surface, (self.rectangle.x + 5, self.rectangle.y + 5))
        self.rectangle.w = max(100, text_surface.get_width() + 10)


# Menu Texts
class Login(Text):
    def __init__(self, text, y=WINDOWHEIGHT * 0.6, size=40, color=BLACK):
        super().__init__(text, WINDOWWIDTH / 2 - len(text) / 2, y, size, color)


class Register(Text):
    def __init__(self, text, y=WINDOWHEIGHT * 0.4, size=40, color=BLACK):
        super().__init__(text, WINDOWWIDTH / 2 - len(text) / 2, y, size, color)


class MenuHeading(Text):
    def __init__(self, text, y=WINDOWHEIGHT * 0.2, size=40, color=BLACK):
        super().__init__(text, WINDOWWIDTH / 2 - len(text) / 2, y, size, color)


# Form text


class Gmail(Text):
    def __init__(self, text, y=WINDOWHEIGHT * 0.4, size=40, color=BLACK):
        super().__init__(text, WINDOWWIDTH / 3 - len(text) / 2, y, size, color)


class InputGmail(InputText):
    def __init__(self, text, y=WINDOWHEIGHT * 0.38, size=32, color=BLACK):
        super().__init__(text, 260, y, size, color)


class Password(Text):
    def __init__(self, text, y=WINDOWHEIGHT * 0.6, size=40, color=BLACK):
        super().__init__(text, WINDOWWIDTH / 3 - len(text) / 2, y, size, color)


class InputPassword(InputText):
    def __init__(self, text, y=WINDOWHEIGHT * 0.58, size=32, color=BLACK):
        super().__init__(text, 290, y, size, color)


class Name(Text):
    def __init__(self, text, y=WINDOWHEIGHT * 0.8, size=40, color=BLACK):
        super().__init__(text, WINDOWWIDTH / 3 - len(text) / 2, y, size, color)


class InputName(InputText):
    def __init__(self, text, y=WINDOWHEIGHT * 0.78, size=32, color=BLACK):
        super().__init__(text, 260, y, size, color)


# Ingame texts
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


# RANKING TABLE TEXTS

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


# GAME PLAY CONTROL
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
            scene.gameMenu()
        if scene.option == 2:
            scene.gameRegister()
        elif scene.option == 4:
            scene.gameStart(bird)
        elif scene.option == 5:
            scene.gamePlay(bird, columns, score)
        elif scene.option == 6:
            scene.gameOver(bird, columns, score)
        elif scene.option == 7:
            scene.gameRanking(bird, columns, score)


if __name__ == '__main__':
    main()
