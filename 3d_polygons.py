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

def projection_point_plane(point,plane):
	"""
	Return point_A', which is projection of point_A on the plane
	"""
	M1 = np.array([[plane[1][0]-plane[0][0],plane[1][1]-plane[0][1],plane[1][2]-plane[0][2]],
					 [plane[2][0]-plane[0][0],plane[2][1]-plane[0][1],plane[2][2]-plane[0][2]]])
	M2 = np.array([[plane[1][0]-plane[0][0],plane[2][0]-plane[0][0]],
					 [plane[1][1]-plane[0][1],plane[2][1]-plane[0][1]],
					 [plane[1][2]-plane[0][2],plane[2][2]-plane[0][2]]])
	v1 = np.array([np.dot(point,plane[1]-plane[0]),
					np.dot(point,plane[2]-plane[0])])
	uv = np.linalg.solve(np.dot(M1,M2),v1-np.dot(M1,plane[0]))
	return plane[0]+np.dot(M2,uv)
	
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
		is_visible2 = point[2]<-1 and point[2]<point[0]<-point[2] and point[2]<point[1]<-point[2]
		if is_visible2:
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
		
def draw_triangle_with_lights(point_A,point_B,point_C,color,is_visible):
	if is_visible:
		M = projection_point_plane(point_S,[point_A,point_B,point_C])
		m = np.linalg.norm(M,ord=2)
		pixel_A = np.array(coordscreen_to_pixels(coord3d_to_coordscreen(point_A)))
		pixel_B = np.array(coordscreen_to_pixels(coord3d_to_coordscreen(point_B)))
		pixel_C = np.array(coordscreen_to_pixels(coord3d_to_coordscreen(point_C)))
		u, v = pixel_B-pixel_A, pixel_C-pixel_A
		AB, AC = point_B-point_A, point_C-point_A
		n_points = 60
		for i in range(n_points):
			for j in range(n_points-i):
				R = point_A+AB*i/n_points+AC*j/n_points-point_S
				r = np.linalg.norm(R,ord=2)
				sin = m/r
				ds = sin / (r*r)
				if ds>1:
					ds = 1
				pixel = pixel_A + u*i/n_points + v*j/n_points
				color_light = (int(color[0]*ds),int(color[1]*ds),int(color[2]*ds))
				screen.set_at((int(pixel[0]),int(pixel[1])),color_light)
				

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
	draw_triangle_with_lights(tetr[1],tetr[2],tetr[3],RED,
					(not A) and (not B) and (not C) and (not AB) and (not BC) and (not AC) and (not ABC))
	draw_triangle_with_lights(tetr[1],tetr[2],tetr[4],YELLOW,
					(not A) and (not B) and (not D) and (not AB) and (not BD) and (not AD) and (not ABD))
	draw_triangle_with_lights(tetr[1],tetr[3],tetr[4],GREEN,
					(not A) and (not C) and (not D) and (not AC) and (not CD) and (not AD) and (not ACD))
	draw_triangle_with_lights(tetr[2],tetr[3],tetr[4],BLUE,
					(not B) and (not C) and (not D) and (not BC) and (not CD) and (not BD) and (not BCD))
	#draw_line(tetr[1],tetr[2],color, (not A) and (not B) and (not AB))
	#draw_line(tetr[1],tetr[3],color, (not A) and (not C) and (not AC))
	#draw_line(tetr[1],tetr[4],color, (not A) and (not D) and (not AD))
	#draw_line(tetr[2],tetr[3],color, (not B) and (not C) and (not BC))
	#draw_line(tetr[2],tetr[4],color, (not B) and (not D) and (not BD))
	#draw_line(tetr[3],tetr[4],color, (not C) and (not D) and (not CD))
		
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

#Point of view / origin point
point_O = np.array([0,0,0])
#Light
point_S = np.array([0,0,0])
#First coordinates of the center of tetrahedron
point_T = np.array([0,0,-1.5])
#First local coordinates of tetrahedron points
vec_TA = np.array([3**0.5/6,-6**0.5/12,0.5])
vec_TB = np.array([-3**0.5/3,-6**0.5/12,0])
vec_TC = np.array([3**0.5/6,-6**0.5/12,-0.5])
vec_TD = np.array([0,6**0.5/4,0])
tetrahedron = np.array([point_T,point_T+vec_TA,point_T+vec_TB,
						point_T+vec_TC,point_T+vec_TD])
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

rot_010 = False
rot_010r = False
rot_100 = False
rot_100r = False
rot_001 = False
rot_001r = False

light_right = False
light_left = False
light_up = False
light_down = False
light_away = False
light_towards = False

while not finished:
	clock.tick(FPS)
	for event in pygame.event.get():
		window_closed = event.type == pygame.QUIT
		escape_pressed = \
			event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
		if window_closed or escape_pressed:
			finished = True
		elif event.type == pygame.KEYDOWN:
			
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
			
			if event.key == pygame.K_l:
				light_right = True
			if event.key == pygame.K_j:
				light_left = True
			if event.key == pygame.K_i:
				light_up = True
			if event.key == pygame.K_k:
				light_down = True
			
		elif event.type == pygame.KEYUP:
			
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
			
			if event.key == pygame.K_l:
				light_right = False
			if event.key == pygame.K_j:
				light_left = False
			if event.key == pygame.K_i:
				light_up = False
			if event.key == pygame.K_k:
				light_down = False

	pressed_keys = pygame.key.get_pressed()

	move_direction = np.zeros(3)
	if pressed_keys[pygame.K_RIGHT]:
		move_direction[0] += +0.01
	if pressed_keys[pygame.K_LEFT]:
		move_direction[0] += -0.01

	if pressed_keys[pygame.K_UP]:
		move_direction[1] += +0.01
	if pressed_keys[pygame.K_DOWN]:
		move_direction[1] += -0.01

	if pressed_keys[pygame.K_w]:
		move_direction[2] += -0.01
	if pressed_keys[pygame.K_s]:
		move_direction[2] += +0.01

	figure_move(tetrahedron, move_direction)

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
	
	if light_right:
		point_S = point_S + np.array([0.01,0,0])
	if light_left:
		point_S = point_S + np.array([-0.01,0,0])
	if light_up:
		point_S = point_S + np.array([0,0.01,0])
	if light_down:
		point_S = point_S + np.array([0,-0.01,0])
	
	draw_tetr(tetrahedron,WHITE)
	pygame.display.update()
	screen.fill(BLACK)

pygame.quit()
