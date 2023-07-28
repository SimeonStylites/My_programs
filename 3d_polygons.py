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

def center(points):
	center = np.array([0,0,0])
	for point in points:
		center = center + 1/len(points)*point
	return center
	
def draw_point(point,color,is_visible):
	if is_visible:
		projection = coord3d_to_coordscreen(point)
		pixel = coordscreen_to_pixels(projection)
		screen.set_at(pixel,color)
	
def draw_line(point_A,point_B,color,is_visible):
	if is_visible:
		projection_A = coord3d_to_coordscreen(point_A)
		pixel_A = coordscreen_to_pixels(projection_A)
		projection_B = coord3d_to_coordscreen(point_B)
		pixel_B = coordscreen_to_pixels(projection_B)
		aaline(screen, color, pixel_A, pixel_B)
	
def draw_triangle(point_A,point_B,point_C,color,is_visible):
	if is_visible:
		projection_A = coord3d_to_coordscreen(point_A)
		pixel_A = coordscreen_to_pixels(projection_A)
		projection_B = coord3d_to_coordscreen(point_B)
		pixel_B = coordscreen_to_pixels(projection_B)
		projection_C = coord3d_to_coordscreen(point_C)
		pixel_C = coordscreen_to_pixels(projection_C)
		polygon(screen,color,[pixel_A, pixel_B, pixel_C])

def draw_tetr(tetr,color):
	"""
	Draw lines - projections of tetrahedrons ribs
	Not draw some ribs if point is behind plane or a rib is behind two planes
	"""
	
	A = is_point_beside_plane(tetr[1],[tetr[2],tetr[3],tetr[4]])
	B = is_point_beside_plane(tetr[2],[tetr[1],tetr[3],tetr[4]])
	C = is_point_beside_plane(tetr[3],[tetr[1],tetr[2],tetr[4]])
	D = is_point_beside_plane(tetr[4],[tetr[1],tetr[2],tetr[3]])
	AB = (is_point_beside_plane(center([tetr[1],tetr[2]]),[tetr[1],tetr[3],tetr[4]]) or
			is_point_beside_plane(center([tetr[1],tetr[2]]),[tetr[2],tetr[3],tetr[4]]))
	AC = (is_point_beside_plane(center([tetr[1],tetr[3]]),[tetr[1],tetr[2],tetr[4]]) or
			is_point_beside_plane(center([tetr[1],tetr[3]]),[tetr[3],tetr[2],tetr[4]]))
	AD = (is_point_beside_plane(center([tetr[1],tetr[4]]),[tetr[1],tetr[2],tetr[3]]) or
			is_point_beside_plane(center([tetr[1],tetr[4]]),[tetr[4],tetr[2],tetr[3]]))
	BC = (is_point_beside_plane(center([tetr[2],tetr[3]]),[tetr[2],tetr[1],tetr[4]]) or
			is_point_beside_plane(center([tetr[2],tetr[3]]),[tetr[3],tetr[1],tetr[4]]))
	BD = (is_point_beside_plane(center([tetr[2],tetr[4]]),[tetr[2],tetr[1],tetr[3]]) or
			is_point_beside_plane(center([tetr[2],tetr[4]]),[tetr[4],tetr[1],tetr[3]]))
	CD = (is_point_beside_plane(center([tetr[3],tetr[4]]),[tetr[3],tetr[1],tetr[2]]) or
			is_point_beside_plane(center([tetr[3],tetr[4]]),[tetr[4],tetr[1],tetr[2]]))
	ABC = (is_point_beside_plane(center([tetr[1],tetr[2],tetr[3]]),[tetr[1],tetr[2],tetr[4]]) or
			is_point_beside_plane(center([tetr[1],tetr[2],tetr[3]]),[tetr[1],tetr[3],tetr[4]]) or
			is_point_beside_plane(center([tetr[1],tetr[2],tetr[3]]),[tetr[2],tetr[3],tetr[4]]))
	ABD = (is_point_beside_plane(center([tetr[1],tetr[2],tetr[4]]),[tetr[1],tetr[2],tetr[3]]) or
			is_point_beside_plane(center([tetr[1],tetr[2],tetr[4]]),[tetr[1],tetr[3],tetr[4]]) or
			is_point_beside_plane(center([tetr[1],tetr[2],tetr[4]]),[tetr[2],tetr[3],tetr[4]]))
	ACD = (is_point_beside_plane(center([tetr[1],tetr[3],tetr[4]]),[tetr[1],tetr[2],tetr[3]]) or
			is_point_beside_plane(center([tetr[1],tetr[3],tetr[4]]),[tetr[1],tetr[2],tetr[4]]) or
			is_point_beside_plane(center([tetr[1],tetr[3],tetr[4]]),[tetr[2],tetr[3],tetr[4]]))
	BCD = (is_point_beside_plane(center([tetr[2],tetr[3],tetr[4]]),[tetr[1],tetr[2],tetr[3]]) or
			is_point_beside_plane(center([tetr[2],tetr[3],tetr[4]]),[tetr[1],tetr[2],tetr[4]]) or
			is_point_beside_plane(center([tetr[2],tetr[3],tetr[4]]),[tetr[1],tetr[3],tetr[4]]))
	draw_triangle(tetr[1],tetr[2],tetr[3],RED,
					(not A) and (not B) and (not C) and (not AB) and (not BC) and (not AC) and (not ABC))
	draw_triangle(tetr[1],tetr[2],tetr[4],YELLOW,
					(not A) and (not B) and (not D) and (not AB) and (not BD) and (not AD) and (not ABD))
	draw_triangle(tetr[1],tetr[3],tetr[4],GREEN,
					(not A) and (not C) and (not D) and (not AC) and (not CD) and (not AD) and (not ACD))
	draw_triangle(tetr[2],tetr[3],tetr[4],BLUE,
					(not B) and (not C) and (not D) and (not BC) and (not CD) and (not BD) and (not BCD))
	draw_line(tetr[1],tetr[2],color, (not A) and (not B) and (not AB))
	draw_line(tetr[1],tetr[3],color, (not A) and (not C) and (not AC))
	draw_line(tetr[1],tetr[4],color, (not A) and (not D) and (not AD))
	draw_line(tetr[2],tetr[3],color, (not B) and (not C) and (not BC))
	draw_line(tetr[2],tetr[4],color, (not B) and (not D) and (not BD))
	draw_line(tetr[3],tetr[4],color, (not C) and (not D) and (not CD))
		
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
GRAY = (125, 125, 125)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)

#First coordinates of the center of tetrahedron
point_O = np.array([-0.5,-0.5,-2])
#First local coordinates of tetrahedron points
vec_OA = np.array([3**0.5/6,-6**0.5/12,0.5])
vec_OB = np.array([-3**0.5/3,-6**0.5/12,0])
vec_OC = np.array([3**0.5/6,-6**0.5/12,-0.5])
vec_OD = np.array([0,6**0.5/4,0])
tetrahedron = np.array([point_O,point_O+vec_OA,point_O+vec_OB,
						point_O+vec_OC,point_O+vec_OD])
#rotation around vector (0,1,0) on 2 degree in a frame
alpha = np.pi/180
rot1 = np.quaternion(np.cos(alpha),0,np.sin(alpha),0)
rot1r = np.quaternion(np.cos(alpha),0,-np.sin(alpha),0)
rot2 = np.quaternion(np.cos(alpha),np.sin(alpha),0,0)
rot2r = np.quaternion(np.cos(alpha),-np.sin(alpha),0,0)
rot3 = np.quaternion(np.cos(alpha),0,0,np.sin(alpha))
rot3r = np.quaternion(np.cos(alpha),0,0,-np.sin(alpha))
draw_tetr(tetrahedron,WHITE)
pygame.display.update()
screen.fill(BLACK)

move_right = False
move_left = False
move_up = False
move_down = False
move_away = False
move_towards = False
rot_010 = False
rot_010r = False
rot_100 = False
rot_100r = False
rot_001 = False
rot_001r = False

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
			if event.key == pygame.K_t:
				rot_010 = True
			if event.key == pygame.K_r:
				rot_010r = True
			if event.key == pygame.K_f:
				rot_100 = True
			if event.key == pygame.K_g:
				rot_100r = True
			if event.key == pygame.K_v:
				rot_001 = True
			if event.key == pygame.K_b:
				rot_001r = True
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
			if event.key == pygame.K_t:
				rot_010 = False
			if event.key == pygame.K_r:
				rot_010r = False
			if event.key == pygame.K_f:
				rot_100 = False
			if event.key == pygame.K_g:
				rot_100r = False
			if event.key == pygame.K_v:
				rot_001 = False
			if event.key == pygame.K_b:
				rot_001r = False
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
	if rot_010:
		rotate(rot1,tetrahedron)
	if rot_010r:
		rotate(rot1r,tetrahedron)
	if rot_100:
		rotate(rot2,tetrahedron)
	if rot_100r:
		rotate(rot2r,tetrahedron)
	if rot_001:
		rotate(rot3,tetrahedron)
	if rot_001r:
		rotate(rot3r,tetrahedron)
	
	draw_tetr(tetrahedron,WHITE)
	pygame.display.update()
	screen.fill(BLACK)

pygame.quit()
