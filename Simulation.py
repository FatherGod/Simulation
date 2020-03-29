import pygame
import numpy as np
import random
import matplotlib.pyplot as plt
from tkinter import *
from functools import partial

class Particule:

    def __init__(self, x, y, xMax, yMax, rect):
        self.xPos = [x]
        self.yPos = [y]
        self.xMax = xMax
        self.yMax = yMax
        self.neighboors = []
        self.rect = [rect]
        self.clusterSize = 1
        for i in [[0, -1], [-1, 0], [1, 0], [0, 1]]:
            if 0 <= x + i[0] < xMax and 0 <= y + i[1] < yMax:
                self.neighboors.append([x + i[0], y + i[1]])

    def aggregate(self, particule):
        for i in range(len(particule.xPos)):
            self.xPos.append(particule.xPos[i])
            self.yPos.append(particule.yPos[i])
            self.neighboors.pop(self.neighboors.index([particule.xPos[i], particule.yPos[i]]))
        for i in particule.neighboors:
            self.neighboors.append(i)
        for i in particule.rect:
            self.rect.append(i)
        self.clusterSize += particule.clusterSize

    def getRect(self, x, y):
        for i in range(len(self.xPos)):
            if self.xPos[i] == x and self.yPos[i] == y:
                return self.rect[i], i
        return None


def simulation(padh, pagg, sizeX, sizeY):

    if type(padh) is StringVar:
        padh = float(padh.get())
        pagg = float(pagg.get())
        sizeX = int(sizeX.get())
        sizeY = int(sizeY.get())

    data = {0: []}
    listCluster = []

    width = 1080
    height = 720
    rectSize = 0.9

    successes, failures = pygame.init()
    print("{0} successes and {1} failures".format(successes, failures))

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Simulation')  # Window Name

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    screen.fill(BLACK)

    stepX = width / sizeX
    stepY = height / sizeY

    for i in range(1, sizeX):
        pygame.draw.line(screen, WHITE, (i * stepX, 0), (i * stepX, height))
    for i in range(1, sizeY):
        pygame.draw.line(screen, WHITE, (0, i * stepY), (width, i * stepY))

    position = np.zeros((sizeX, sizeY, 2))
    for i in range(sizeX):
        for j in range(sizeY):
            position[i, j, 0] = i * stepX + stepX / 2
            position[i, j, 1] = j * stepY + stepY / 2
    position = position.astype(int)

    freeSpace = np.ones((sizeX, sizeY))
    particle = [[None for j in range(sizeY)] for i in range(sizeX)]
    running = True
    inCreation = False
    inAggregation = False
    aggregationFailed = False
    currentParticule = None
    image = None
    x = None
    y = None
    rect = None

    while running:

        pygame.display.update()  # Or pygame.display.flip()
        if inCreation:
            if random.random() < padh:
                image.fill(RED)
                screen.blit(image, currentParticule.rect[0])
                particle[x][y] = currentParticule
                listCluster.append(currentParticule)
                freeSpace[x, y] = 0
            else:
                image.fill(BLACK)
                screen.blit(image, currentParticule.rect[0])
            inCreation = False

        elif inAggregation:
            if len(currentParticule.neighboors) > 0:
                neighboorNumber = random.randint(0, len(currentParticule.neighboors) - 1)
                nextPos = currentParticule.neighboors[neighboorNumber]
                if freeSpace[nextPos[0], nextPos[1]] == 1:
                    if random.random() < pagg:
                        newParticule = Particule(nextPos[0], nextPos[1], sizeX, sizeY, pygame.Rect(
                            position[nextPos[0], nextPos[1], 0] + stepX * ((1 - rectSize) / 2 - 0.5),
                            position[nextPos[0], nextPos[1], 1] + stepY * ((1 - rectSize) / 2 - 0.5),
                            rectSize * stepX,
                            rectSize * stepY))
                        rect = rect.union(newParticule.rect[0])
                        image = pygame.Surface((rect.width, rect.height))
                        currentParticule.aggregate(newParticule)
                        particle[nextPos[0]][nextPos[1]] = currentParticule
                        freeSpace[nextPos[0], nextPos[1]] = 0
                else:
                    currentParticule.neighboors.pop(neighboorNumber)
            image.fill(RED)
            screen.blit(image, rect)
            inAggregation = False

        else:
            if 1 in freeSpace:
                if not aggregationFailed:
                    x = random.randint(0, sizeX - 1)
                    y = random.randint(0, sizeY - 1)

                if freeSpace[x, y] == 1:
                    rect = pygame.draw.rect(screen, BLACK, pygame.Rect(
                        position[x, y, 0] + stepX * ((1 - rectSize) / 2 - 0.5),
                        position[x, y, 1] + stepY * ((1 - rectSize) / 2 - 0.5),
                        rectSize * stepX,
                        rectSize * stepY))
                    currentParticule = Particule(x, y, sizeX, sizeY, rect)
                    image = pygame.Surface((currentParticule.rect[0].width, currentParticule.rect[0].height))
                    image.fill(BLUE)
                    screen.blit(image, currentParticule.rect[0])
                    inCreation = True

                else:
                    currentParticule = particle[x][y]
                    rect, rectNumber = currentParticule.getRect(x, y)
                    image = pygame.Surface((rect.width, rect.height))
                    image.fill(GREEN)
                    screen.blit(image, rect)
                    inAggregation = True

        for i in listCluster:
            if i.clusterSize not in data.keys():
                data[i.clusterSize] = [0 for i in range(len(data[0]))]

        for i in data.keys():
            data[i].append(0)

        data[0][-1] = np.size(freeSpace[freeSpace == 1])
        for i in listCluster:
            data[i.clusterSize][-1] += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

        if 1 not in freeSpace:
            running = False
            pygame.quit()

    for i in data.keys():
        plt.plot(data[i], label=f"Size={i}")
    plt.legend(title="Cluster's size", loc="lower right")
    plt.title(f"Evolution of the clusters' number through time with padh={padh} and pagg={pagg}")
    plt.xlabel("Time")
    plt.ylabel(f"Clusters' number")
    plt.show()

if __name__ == '__main__':
    root = Tk()

    padhLabel = Label(root, text="Probability of adhesion")
    padh = StringVar()
    padhEntry = Entry(root, textvariable=padh)
    padhLabel.pack()
    padhEntry.pack()

    paggLabel = Label(root, text="Probability of aggregation")
    pagg = StringVar()
    paggEntry = Entry(root, textvariable=pagg)
    paggLabel.pack()
    paggEntry.pack()

    sizeXLabel = Label(root, text="Size for abscissa")
    sizeX = StringVar()
    sizeXEntry = Entry(root, textvariable=sizeX)
    sizeXLabel.pack()
    sizeXEntry.pack()

    sizeYLabel = Label(root, text="Size for ordinate")
    sizeY = StringVar()
    sizeYEntry = Entry(root, textvariable=sizeY)
    sizeYLabel.pack()
    sizeYEntry.pack()

    launcher = Button(root, text="test", command=partial(simulation, padh, pagg, sizeX, sizeY))
    launcher.pack()

    root.mainloop()