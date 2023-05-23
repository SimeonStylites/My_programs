import pygame
import time
import numpy as np
from pygame.draw import *

def mandelbrot(precision, area):
	"""
	Draw a mandelbrot set in selected area on the screen. Making "precision"
	iterations for every point on the screen.
	area = (xmin,ymin,delta)
	"""
	#start = time.time() #measuring calculating time (starting point))
	#xmin, ymin, delta = area[0], area[1], area[2]
	#array where every number is a number of iterations in this point
	image = np.zeros((points,points))
	#two grid arrays where re is for x coordinate, im is for y coordinate
	re, im = np.mgrid[area[0]:area[0]+area[2]:points*1j,
						area[1]:area[1]+area[2]:points*1j]
	c = re+im*1j
	#numbers that will be itterated
	z = np.zeros_like(c, dtype=complex)
	
	for i in range(precision):
		z = z*z+c
		#put a number of itterations in image
		mask = (np.abs(z) > 4) & (image == 0)
		image[mask] = i
		#stop calculating points where z>4
		z[mask] = np.nan
	
	for n in range(points):
		for k in range(points):
			screen.set_at((n,points-k),(0,0,image[n][k]/precision*255))
	#end = time.time() #measuring calculating time (ending point)
	#print(end-start) #print calculating time

pygame.init()

FPS = 30
points = 1000
screen = pygame.display.set_mode((points, points))
clock = pygame.time.Clock()
finished = False

BLACK = (0,0,0)
delta = 4.0
area = [-2.0,-2.0, delta]
precision = 20
mandelbrot(precision, area)  #number of iterations for every pixel in set
pygame.display.update()
screen.fill(BLACK)

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
        	mouse_re = event.pos[0]/points*area[2]+area[0]
        	part = (points-event.pos[1])/points
        	mouse_im = part*area[2]+area[1]
        	#find the size of new smaller area
        	print(event.pos[0],event.pos[1],part)
        	print(mouse_re,mouse_im)
        	area[0] = mouse_re-area[2]/4
        	area[1] = mouse_im-area[2]/4
        	area[2] /=2.0
        	print(area)
        	mandelbrot(precision,area)
        	pygame.display.update()
        	screen.fill(BLACK)            

pygame.quit()
