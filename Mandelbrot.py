import pygame
import time
from pygame.draw import *

def draw(color, c, area):
    """
    Set pixel with a chosen color on a complex plane
    color - color in RGB format
    c - complex number
    area - range with parameters xmin, ymin, delta; xmin, ymin -
    coordinates of the left down angle delta - width of the
    square area of complex plane
    """
    xmin, ymin, delta = area[0], area[1], area[2]
    x = (c.real-xmin)*1024/delta
    ymax = ymin + delta
    y = (ymax - c.imag)*1024/delta
    #line(screen,color,(x,y),(x,y))
    screen.set_at((int(x),int(y)),color)

def mandelbrot(precision, area):
    """
    Draw a Mandelbrot set. If the recurent expression (z=z*z+c)
    rises fast, the color is darker. Points, where the expression
    is smaller than 4 after N steps, remain black.
    precision - number of steps in cycle, where it is defined,
    is the point in the set or not
    area - range with parameters xmin, ymin, delta; xmin, ymin -
    coordinates of the left down angle delta - width of the
    square area of complex plane
    """
    start = time.time() #measuring calculating time (starting point))
    xmin,ymin,delta = area[0],area[1],area[2]
    #checking every pixel on the window
    for pixel in range(1024*1024):
        c = complex(xmin+(pixel%1024+1)*delta/1024, ymin+(pixel//1024+1)*delta/1024)
        z = complex(0,0)
        i = 0
        #makes some steps until z>=4; if c is big goes to else faster
        while abs(z)<4 and i<precision:
            z = z*z+c
            i += 1
        else:
            if abs(z)>=4:   #c is not in the set
                draw((0,0,int(255*i/precision)),c,area)
    end = time.time() #measuring calculating time (ending point)
    print(end-start) #print calculating time
    print(precision, area)

pygame.init()

FPS = 30
screen = pygame.display.set_mode((1024, 1024))
clock = pygame.time.Clock()
finished = False

BLACK = (0,0,0)
delta = 4.0
area = [-2.0,-2.0, delta]
precision = 20
mandelbrot(precision, area)  #number of iterations for every pixel in set
pygame.display.update()
screen.fill(BLACK)
#Saving an image of a set in current folder
#pygame.image.save(screen, "Mandelbrot.jpeg")

while not finished:
    clock.tick(FPS)
    for event in pygame.event.get():
        window_closed = event.type == pygame.QUIT
        escape_pressed = \
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        if window_closed or escape_pressed:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
        	precision +=20
        	#find the coordinates of the cursor on the complex plane
        	mouse_re = event.pos[0]/1024*area[2]+area[0]
        	mouse_im = -event.pos[1]/1024*area[2]+area[1]+area[2]
        	#find the size of new smaller area
        	area[0] = mouse_re-area[2]/4
        	area[1] = mouse_im-area[2]/4
        	area[2] /=2.0
        	mandelbrot(precision,area)
        	pygame.display.update()
        	screen.fill(BLACK)            

pygame.quit()
