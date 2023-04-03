import pygame
from pygame.draw import *

def draw(color,c):
    """
    Set pixel with a chosen color on a complex plane. Center
    of the screen has coordinates (0,0)
    color - color in RGB format
    c - complex number
    """
    x = 512 + 256*c.real
    y = 513 - 256*c.imag
    line(screen,color,(x,y),(x,y))

def mandelbrot_bw(precision):
    """
    Draw a Mandelbrot set. If the recurent expression (z=z*z+c)
    rises fast, the color is darker. Points, where the expression
    is smaller than 2 after N steps, remain black.
    precision - number of steps in cycle, where it is defined,
    is the point in the set or not
    """
    #checking every pixel
    for pixel in range(1024*1024):
        c = complex(-2+(pixel%1024+1)/256, -2+(pixel//1024+1)/256)
        z = complex(0,0)
        i = 0
        #makes some steps until z>=2; if c is big goes to else faster
        while abs(z)<2 and i<precision:
            z = z*z+c
            i += 1
        else:
            if abs(z)>=2:   #c is not in the set
                draw((0,0,int(255*i/precision)),c)

pygame.init()

FPS = 30
screen = pygame.display.set_mode((1024, 1024))
clock = pygame.time.Clock()
finished = False

mandelbrot_bw(100)  #number of iterations for every pixel in set
pygame.display.update()
pygame.image.save(screen, "Mandelbrot.jpeg")

while not finished:
    clock.tick(FPS)
    for event in pygame.event.get():
        window_closed = event.type == pygame.QUIT
        escape_pressed = \
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        if window_closed or escape_pressed:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            continue
    pygame.display.update()            

pygame.quit()
