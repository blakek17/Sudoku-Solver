import pygame, time, math, sys
from abc import ABC, abstractmethod 

SCR_WID, SCR_HEI = 580, 670
WHITE = (255, 255, 255)
BLACK = (0, 0, 0) 
FPS = 60
GRID_OFFSET_X, GRID_OFFSET_Y = 15, 15
CELL_BORDER = 5

screen = pygame.display.set_mode((SCR_WID, SCR_HEI))
clock = pygame.time.Clock()

buttonGroup = pygame.sprite.Group()


class SpriteSheet():
    def __init__(self, imageName, cols, rows):
        self.imageName = imageName
        self.image = pygame.image.load(self.imageName)
        self.rect = self.image.get_rect()
        self.cols = cols
        self.rows = rows
        self.totalCells = self.cols * self.rows
        self.currentCellIndex = 9
        self.cellWidth = self.rect.width / self.cols
        self.cellHeight = self.rect.height / self.rows
        self.currentRowIndex = math.floor(self.currentCellIndex / self.cols)
        self.currentColIndex = self.currentCellIndex % self.cols
        self.cellOffsetX = self.currentColIndex * self.cellWidth
        self.cellOffsetY = self.currentRowIndex * self.cellHeight

    def getImage(self):
        return self.image

    def setImage(self, imageName):
        self.image = pygame.image.load(imageName)

    def getImageName(self):
        return self.imageName

    def getCellWidth(self):
        return self.cellWidth

    def getCellHeight(self):
        return self.cellHeight

    def getCellOffsetX(self):
        return self.cellOffsetX

    def getCellOffsetY(self):
        return self.cellOffsetY

    def setCellIndex(self, currentCellIndex):
        self.currentCellIndex = currentCellIndex
        self.currentRowIndex = math.floor(self.currentCellIndex / self.cols)
        self.currentColIndex = self.currentCellIndex % self.cols
        self.cellOffsetX = self.currentColIndex * self.cellWidth
        self.cellOffsetY = self.currentRowIndex * self.cellHeight
        

class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.spriteSheet = SpriteSheet("unselectedSpriteSheet.png", 3, 4)
        width = self.spriteSheet.getCellWidth()
        height = self.spriteSheet.getCellHeight() 
        self.image = self.spriteSheet.getImage().subsurface((
            self.spriteSheet.getCellOffsetX(), self.spriteSheet.getCellOffsetY(),
            self.spriteSheet.getCellWidth(), self.spriteSheet.getCellHeight()))
        self.rect = self.image.get_rect(topleft = (x, y)) 
        self.possibleValues = []

    def updateDisplay(self):
        self.image = self.spriteSheet.getImage().subsurface((
            self.spriteSheet.getCellOffsetX(), self.spriteSheet.getCellOffsetY(),
            self.spriteSheet.getCellWidth(), self.spriteSheet.getCellHeight()))
        self.draw() 

    def select(self):      
        self.spriteSheet.setImage("selectedSpriteSheet.png")
        self.updateDisplay()
        
    def unselect(self):
        self.spriteSheet.setImage("unselectedSpriteSheet.png")
        self.updateDisplay() 

    def setKnownValue(self, digit):
        try:
            digit = int(digit)
            if digit == 0:
                if len(self.possibleValues) != 0:
                    self.possibleValues.pop()
                    self.spriteSheet.setCellIndex(9)
                    self.updateDisplay() 
            elif len(self.possibleValues) == 0:
                self.possibleValues.append(digit)
                self.spriteSheet.setCellIndex(digit - 1) 
                self.updateDisplay()
            else:
                self.possibleValues.clear()
                self.possibleValues.append(digit)
                self.spriteSheet.setCellIndex(digit - 1) 
                self.updateDisplay()
        except ValueError:
            return 

    def deletePossibleValue(self, digit):
        if digit in self.possibleValues:
            self.possibleValues.remove(digit) 

    def getPossibleValues(self):
        return self.possibleValues

    def initializePossibleValues(self):
        self.possibleValues = [1, 2, 3, 4, 5, 6, 7, 8, 9] 
        
    def draw(self):
        screen.blit(self.image, self.rect)

    def getWidth(self):
        return self.spriteSheet.getCellWidth()

    def getHeight(self):
        return self.spriteSheet.getCellHeight()


class Grid():
    def __init__(self):
        self.contents = [ [ [[], [], []], [[], [], []], [[], [], []] ],
                     [ [[], [], []], [[], [], []], [[], [], []] ],
                     [ [[], [], []], [[], [], []], [[], [], []] ] ]
        self.digitFont = pygame.font.Font(pygame.font.get_default_font(), 30)
        
        offsetX, offsetY = GRID_OFFSET_X, GRID_OFFSET_Y
        for squareRow in range(0, 3):
            for squareColumn in range(0, 3):
                for cellRow in range(0, 3):
                    for cellColumn in range(0, 3):
                        cell = Cell(offsetX, offsetY)
                        cell.draw() 
                        self.contents[squareRow][squareColumn][cellRow].append(cell) 
                        offsetX += cell.getWidth() - CELL_BORDER
                    offsetX -= cell.getWidth() * 3
                    offsetX += CELL_BORDER * 3
                    offsetY += cell.getHeight() - CELL_BORDER
                offsetX += cell.getWidth() * 3
                offsetX -= CELL_BORDER * 2
                offsetY -= cell.getHeight() * 3
                offsetY += CELL_BORDER * 3
            offsetX -= cell.getWidth() * 9
            offsetX += CELL_BORDER * 6
            offsetY += cell.getHeight() * 3
            offsetY -= CELL_BORDER * 2      
        self.cellWidth = cell.getWidth()

        self.cellHeight = cell.getHeight()
        self.squareWidth = self.cellWidth * 3 - CELL_BORDER * 2
        self.squareHeight = self.cellHeight * 3 - CELL_BORDER * 2
        self.gridWidth = self.squareWidth * 3
        self.gridHeight = self.squareHeight * 3
        self.currentCell = None

    def isClicked(self, mousePos):
        return (mousePos[0] >= GRID_OFFSET_X and mousePos[0] < GRID_OFFSET_X + self.gridWidth
                and mousePos[1] >= GRID_OFFSET_Y and mousePos[1] < GRID_OFFSET_Y + self.gridHeight)

    def accessCell(self, mousePos):
        squareRow = math.floor((mousePos[1] - GRID_OFFSET_Y) / self.squareHeight)
        squareColumn = math.floor((mousePos[0] - GRID_OFFSET_X) / self.squareWidth)
        cellRow = math.floor((mousePos[1] - (GRID_OFFSET_Y + self.squareHeight * squareRow)) / self.cellHeight)
        cellColumn = math.floor((mousePos[0] - (GRID_OFFSET_X + self.squareWidth * squareColumn)) / self.cellWidth)

        if self.currentCell == [squareRow, squareColumn, cellRow, cellColumn]:
            self.contents[squareRow][squareColumn][cellRow][cellColumn].unselect()
            self.currentCell = None
        else:
            if self.currentCell is not None:
                self.contents[self.currentCell[0]][self.currentCell[1]][self.currentCell[2]][self.currentCell[3]].unselect()
            self.contents[squareRow][squareColumn][cellRow][cellColumn].select()
            self.currentCell = [squareRow, squareColumn, cellRow, cellColumn]

    def getCurrentCell(self):
        if self.currentCell is None:
            return None
        else:
            return self.contents[self.currentCell[0]][self.currentCell[1]][self.currentCell[2]][self.currentCell[3]]

    def unselectCurrentCell(self):
        if self.currentCell is not None:
            self.contents[self.currentCell[0]][self.currentCell[1]][self.currentCell[2]][self.currentCell[3]].unselect()

    def initializeEmptyCells(self):
        for squareRow in range(0, 3):
            for squareColumn in range(0, 3):
                for cellRow in range(0, 3):
                    for cellColumn in range(0, 3):
                        if len(self.contents[squareRow][squareColumn][cellRow][cellColumn].getPossibleValues()) == 0:
                            self.contents[squareRow][squareColumn][cellRow][cellColumn].initializePossibleValues()
                        
    def solve(self):
        for currentSquareRow in range(0, 3):
            for currentSquareColumn in range(0, 3):
                for currentCellRow in range(0, 3):
                    for currentCellColumn in range(0, 3):
                        currentCell = [currentSquareRow, currentSquareColumn, currentCellRow, currentCellColumn]                        
                        if len(self.contents[currentCell[0]][currentCell[1]][currentCell[2]][currentCell[3]].getPossibleValues()) == 1:
                            self.checkRelatedCells(currentCell)
                               
        for currentSquareRow in range(0, 3):
            for currentSquareColumn in range(0, 3):
                for currentCellRow in range(0, 3):
                    for currentCellColumn in range(0, 3):
                        if len(self.contents[currentSquareRow][currentSquareColumn]
                            [currentCellRow][currentCellColumn].getPossibleValues()) > 1:
                            print("Error: Not enough info to solve puzzle")
                            return
        print("Puzzle solved") 

    def checkRelatedCells(self, currentCell):
        #square:
        for relatedCellRow in range(0, 3):
            for relatedCellColumn in range(0, 3):
                relatedCell = [currentCell[0], currentCell[1], relatedCellRow, relatedCellColumn]
                if relatedCell != currentCell:
                    currentCellDigit = self.contents[currentCell[0]][currentCell[1]][currentCell[2]][currentCell[3]].getPossibleValues()[0]
                    if currentCellDigit in self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].getPossibleValues():
                        self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].deletePossibleValue(currentCellDigit)
                        if len(self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].getPossibleValues()) == 0:
                            print("Error: Puzzle is not solvable")
                            return
                        elif len(self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].getPossibleValues()) == 1:
                            self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].setKnownValue(
                                self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].getPossibleValues()[0])
                            pygame.display.update()
                            self.checkRelatedCells(relatedCell)

        #row
        for relatedSquareColumn in range(0, 3):
            for relatedCellColumn in range(0, 3):
                relatedCell = [currentCell[0], relatedSquareColumn, currentCell[2], relatedCellColumn]
                if relatedCell != currentCell:
                    currentCellDigit = self.contents[currentCell[0]][currentCell[1]][currentCell[2]][currentCell[3]].getPossibleValues()[0]
                    if currentCellDigit in self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].getPossibleValues():
                        self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].deletePossibleValue(currentCellDigit)
                        if len(self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].getPossibleValues()) == 0:
                            print("Error: Puzzle is not solvable")
                            return
                        elif len(self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].getPossibleValues()) == 1:
                            self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].setKnownValue(
                                self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].getPossibleValues()[0])
                            pygame.display.update()
                            self.checkRelatedCells(relatedCell)
            
        #column
        for relatedSquareRow in range(0, 3):
            for relatedCellRow in range(0, 3):
                relatedCell = [relatedSquareRow, currentCell[1], relatedCellRow, currentCell[3]]
                if relatedCell != currentCell:
                    currentCellDigit = self.contents[currentCell[0]][currentCell[1]][currentCell[2]][currentCell[3]].getPossibleValues()[0]
                    if currentCellDigit in self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].getPossibleValues():
                        self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].deletePossibleValue(currentCellDigit)
                        if len(self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].getPossibleValues()) == 0:
                            print("Error: Puzzle is not solvable")
                            return
                        elif len(self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].getPossibleValues()) == 1:
                            self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].setKnownValue(
                                self.contents[relatedCell[0]][relatedCell[1]][relatedCell[2]][relatedCell[3]].getPossibleValues()[0])
                            pygame.display.update()
                            self.checkRelatedCells(relatedCell)
                                      
class Button(pygame.sprite.Sprite, ABC):
    def __init__(self, imageName, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(imageName)
        self.rect = self.image.get_rect(topleft = (location))

    def isClicked(self, mousePos):
        return self.rect.collidepoint(mousePos) 

    @abstractmethod
    def execute(self):
        pass
    

class ResetButton(Button):
    def __init__(self, imageName, location):
        Button.__init__(self, imageName, location)

    def execute(self):
        return False
        

class SolveButton(Button):
    def __init__(self, imageName, location):
        Button.__init__(self, imageName, location)

    def execute(self):
        return True
    

def main():
    pygame.init()
    screen.fill(WHITE)
    grid = Grid()
    resetButton = ResetButton("resetButton.png", (30, 570))
    solveButton = SolveButton("solveButton.png", (355, 570))
    buttonGroup.add(resetButton)
    buttonGroup.add(solveButton)
    buttonGroup.draw(screen) 
     
    running = True
    solving = False
    currentCell = None 
    while (running):
        while (not solving):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit() 
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mousePos = pygame.mouse.get_pos()
                    if grid.isClicked(mousePos):
                        grid.accessCell(mousePos)
                    elif resetButton.isClicked(mousePos):
                        solving = resetButton.execute()
                        grid = Grid() 
                    elif solveButton.isClicked(mousePos):
                        solving = solveButton.execute()
                elif event.type == pygame.KEYDOWN and grid.getCurrentCell() is not None:
                    grid.getCurrentCell().setKnownValue(event.unicode) 
            pygame.display.update() 
            clock.tick(FPS)

        grid.unselectCurrentCell() 
        grid.initializeEmptyCells()                 
        grid.solve()
        solving = False
                
        pygame.display.update() 
        clock.tick(FPS)

    pygame.quit()

main() 
        
        

    
