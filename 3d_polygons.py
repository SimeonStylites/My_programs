import pygame
import time
import numpy as np
import quaternion
from pygame.draw import *

def coord3d_to_coordscreen(point):
	"""
	Make a projection of a point in 3d on a screen, located on z_screen
	"""
	return np.array([point[0]/point[2]*z_screen,point[1]/point[2]*z_screen])

def coordscreen_to_pixels(projection):
	"""
	transform coordinates to the pixels
	-1<x_coord<1; -1<y_coord<1
	"""
	return (int(500.0*(projection[0]+1.0)),int(-500.0*(projection[1]-1.0)))
	
def is_point_beside_plane(point,plane):
	"""
	Check, does the vector OA intersect triangle BCD?
	A - point,
	triangle BCD (three points) - plane
	"""
	M = np.array([[point[0],plane[0][0]-plane[1][0],plane[0][0]-plane[2][0]],
					 [point[1],plane[0][1]-plane[1][1],plane[0][1]-plane[2][1]],
					 [point[2],plane[0][2]-plane[1][2],plane[0][2]-plane[2][2]]])
	v = np.array([plane[0][0],plane[0][1],plane[0][2]])
	coef = np.linalg.solve(M,v)
	return (0<coef[0]<1) and (coef[1]>0) and (coef[2]>0) and (coef[1]+coef[2]<1)

def center(point_A,point_B):
	return 0.5*(point_A+point_B)
	
def draw_point(point,color):
	projection = coord3d_to_coordscreen(point)
	pixel = coordscreen_to_pixels(projection)
	screen.set_at(pixel,color)
	
def draw_line(point_A,point_B,color):
	projection_A = coord3d_to_coordscreen(point_A)
	pixel_A = coordscreen_to_pixels(projection_A)
	projection_B = coord3d_to_coordscreen(point_B)
	pixel_B = coordscreen_to_pixels(projection_B)
	aaline(screen, color, pixel_A, pixel_B)

def draw_tetr(tetr,color):
	"""
	Draw lines - projections of tetrahedrons ribs
	Not draw some ribs if point is behind plane or a rib is behind two planes
	"""
	A = is_point_beside_plane(tetr[1],[tetr[2],tetr[3],tetr[4]])
	B = is_point_beside_plane(tetr[2],[tetr[1],tetr[3],tetr[4]])
	C = is_point_beside_plane(tetr[3],[tetr[1],tetr[2],tetr[4]])
	D = is_point_beside_plane(tetr[4],[tetr[1],tetr[2],tetr[3]])
	AB = (is_point_beside_plane(center(tetr[1],tetr[2]),[tetr[1],tetr[3],tetr[4]]) or
			is_point_beside_plane(center(tetr[1],tetr[2]),[tetr[2],tetr[3],tetr[4]]))
	AC = (is_point_beside_plane(center(tetr[1],tetr[3]),[tetr[1],tetr[2],tetr[4]]) or
			is_point_beside_plane(center(tetr[1],tetr[3]),[tetr[3],tetr[2],tetr[4]]))
	AD = (is_point_beside_plane(center(tetr[1],tetr[4]),[tetr[1],tetr[2],tetr[3]]) or
			is_point_beside_plane(center(tetr[1],tetr[4]),[tetr[4],tetr[2],tetr[3]]))
	BC = (is_point_beside_plane(center(tetr[2],tetr[3]),[tetr[2],tetr[1],tetr[4]]) or
			is_point_beside_plane(center(tetr[2],tetr[3]),[tetr[3],tetr[1],tetr[4]]))
	BD = (is_point_beside_plane(center(tetr[2],tetr[4]),[tetr[2],tetr[1],tetr[3]]) or
			is_point_beside_plane(center(tetr[2],tetr[4]),[tetr[4],tetr[1],tetr[3]]))
	CD = (is_point_beside_plane(center(tetr[3],tetr[4]),[tetr[3],tetr[1],tetr[2]]) or
			is_point_beside_plane(center(tetr[3],tetr[4]),[tetr[4],tetr[1],tetr[2]]))
	if A:
		draw_line(tetr[2],tetr[3],color)
		draw_line(tetr[2],tetr[4],color)
		draw_line(tetr[3],tetr[4],color)
	elif B:
		draw_line(tetr[1],tetr[3],color)
		draw_line(tetr[1],tetr[4],color)
		draw_line(tetr[3],tetr[4],color)
	elif C:
		draw_line(tetr[1],tetr[2],color)
		draw_line(tetr[1],tetr[4],color)
		draw_line(tetr[2],tetr[4],color)
	elif D:
		draw_line(tetr[1],tetr[2],color)
		draw_line(tetr[1],tetr[3],color)
		draw_line(tetr[2],tetr[3],color)
	else:
		if not AB:
			draw_line(tetr[1],tetr[2],color)
		if not AC:	
			draw_line(tetr[1],tetr[3],color)
		if not AD:
			draw_line(tetr[1],tetr[4],color)
		if not BC:
			draw_line(tetr[2],tetr[3],color)
		if not BD:
			draw_line(tetr[2],tetr[4],color)
		if not CD:
			draw_line(tetr[3],tetr[4],color)
		
def figure_move(tetr,v):
	"""
	Move all points of tetrahedron
	"""
	tetr[:,0:3]+=v
	
def rotate(rot,tetr):
	"""
	Rotate tetrahedron around point O which is tetr[0] and vector rot
	"""
	OA = tetr[1]-tetr[0]
	OB = tetr[2]-tetr[0]
	OC = tetr[3]-tetr[0]
	OD = tetr[4]-tetr[0]
	q_1 = np.quaternion(0,OA[0],OA[1],OA[2])
	q_2 = np.quaternion(0,OB[0],OB[1],OB[2])
	q_3 = np.quaternion(0,OC[0],OC[1],OC[2])
	q_4 = np.quaternion(0,OD[0],OD[1],OD[2])
	q_1 = rot*q_1*rot**(-1)
	q_2 = rot*q_2*rot**(-1)
	q_3 = rot*q_3*rot**(-1)
	q_4 = rot*q_4*rot**(-1)
	tetr[1] = [tetr[0][0]+q_1.x,tetr[0][1]+q_1.y,tetr[0][2]+q_1.z]
	tetr[2] = [tetr[0][0]+q_2.x,tetr[0][1]+q_2.y,tetr[0][2]+q_2.z]
	tetr[3] = [tetr[0][0]+q_3.x,tetr[0][1]+q_3.y,tetr[0][2]+q_3.z]
	tetr[4] = [tetr[0][0]+q_4.x,tetr[0][1]+q_4.y,tetr[0][2]+q_4.z]


pygame.init()


FPS = 30
z_screen = -1
x_pixels = 1000
y_pixels = 1000
screen = pygame.display.set_mode((x_pixels, y_pixels))
clock = pygame.time.Clock()
finished = False

BLACK = (0,0,0)
WHITE = (255,255,255)
#First coordinates of the center of tetrahedron
point_O = np.array([-1,-1,-3])
#First local coordinates of tetrahedron points
vec_OA = np.array([3**0.5/6,-6**0.5/12,0.5])
vec_OB = np.array([-3**0.5/3,-6**0.5/12,0])
vec_OC = np.array([3**0.5/6,-6**0.5/12,-0.5])
vec_OD = np.array([0,6**0.5/4,0])
tetrahedron = np.array([point_O,point_O+vec_OA,point_O+vec_OB,
						point_O+vec_OC,point_O+vec_OD])
#rotation around vector (0,1,0) on 1 degree in a frame
rot = np.quaternion(np.cos(np.pi/360),0,np.sin(np.pi/360),0)
draw_point(point_O,WHITE)
draw_tetr(tetrahedron,WHITE)
pygame.display.update()
screen.fill(BLACK)

move_right = False
move_left = False
move_up = False
move_down = False
move_away = False
move_towards = False

while not finished:
	clock.tick(FPS)
	for event in pygame.event.get():
		window_closed = event.type == pygame.QUIT
		escape_pressed = \
			event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
		if window_closed or escape_pressed:
			finished = True
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RIGHT:
				move_right = True
			if event.key == pygame.K_LEFT:
				move_left = True
			if event.key == pygame.K_UP:
				move_up = True
			if event.key == pygame.K_DOWN:
				move_down = True
			if event.key == pygame.K_w:
				move_away = True
			if event.key == pygame.K_s:
				move_towards = True
		elif event.type == pygame.KEYUP:
			if event.key == pygame.K_RIGHT:
				move_right = False
			if event.key == pygame.K_LEFT:
				move_left = False
			if event.key == pygame.K_UP:
				move_up = False
			if event.key == pygame.K_DOWN:
				move_down = False
			if event.key == pygame.K_w:
				move_away = False
			if event.key == pygame.K_s:
				move_towards = False
	if move_right:
		figure_move(tetrahedron,[0.01,0,0])
	if move_left:
		figure_move(tetrahedron,[-0.01,0,0])
	if move_up:
		figure_move(tetrahedron,[0,0.01,0])
	if move_down:
		figure_move(tetrahedron,[0,-0.01,0])
	if move_away:
		figure_move(tetrahedron,[0,0,-0.01])
	if move_towards:
		figure_move(tetrahedron,[0,0,0.01])
	rotate(rot,tetrahedron)
	draw_tetr(tetrahedron,WHITE)
	pygame.display.update()
	screen.fill(BLACK)

pygame.quit()
