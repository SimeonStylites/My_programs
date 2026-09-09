import pygame
import time
import numpy as np
import quaternion
from pygame.draw import *
import colorsys

BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (125, 125, 125)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)

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
	try:
		coef = np.linalg.solve(M,v)
	except np.linalg.LinAlgError:
		return False
	return (0<coef[0]<1) and (coef[1]>=-1e-9) and (coef[2]>=-1e-9) and (coef[1]+coef[2]<=1+1e-9)

def center(points):
	center = np.array([0,0,0])
	for point in points:
		center = center + 1/len(points)*point
	return center
	
def draw_polygon_with_lights(vertices, color, radius=2):
	"""
	Залить выпуклую грань освещёнными точками по одной общей сетке,
	чтобы не было швов между треугольниками разбиения.
	vertices — 3D-точки грани по порядку.
	"""
	vs = [np.asarray(v, dtype=float) for v in vertices]
	if len(vs) < 3:
		return
	M = projection_point_plane(point_S, [vs[0], vs[1], vs[2]])
	m = np.linalg.norm(M, ord=2)
	p0 = vs[0]
	N = np.cross(vs[1] - p0, vs[2] - p0)
	norm_N = np.linalg.norm(N)
	if norm_N < 1e-12:
		return
	N = N / norm_N
	u = (vs[1] - p0) / np.linalg.norm(vs[1] - p0)
	v = np.cross(N, u)
	uv = np.array([[np.dot(p - p0, u), np.dot(p - p0, v)] for p in vs])
	min_x, max_x = uv[:, 0].min(), uv[:, 0].max()
	min_y, max_y = uv[:, 1].min(), uv[:, 1].max()
	span = max(max_x - min_x, max_y - min_y)
	if span < 1e-9:
		return
	n = 72
	step = span / n
	xs = np.arange(min_x, max_x + step, step)
	ys = np.arange(min_y, max_y + step, step)
	gx, gy = np.meshgrid(xs, ys)
	pts2d = np.column_stack([gx.ravel(), gy.ravel()])
	area2 = 0.0
	for i in range(len(vs)):
		a = uv[i]
		b = uv[(i + 1) % len(vs)]
		area2 += a[0] * b[1] - b[0] * a[1]
	ccw = area2 > 0
	inside = np.ones(len(pts2d), dtype=bool)
	for i in range(len(vs)):
		a = uv[i]
		b = uv[(i + 1) % len(vs)]
		cross = (b[0] - a[0]) * (pts2d[:, 1] - a[1]) - (b[1] - a[1]) * (pts2d[:, 0] - a[0])
		if ccw:
			inside &= (cross >= -1e-9)
		else:
			inside &= (cross <= 1e-9)
	pts2d = pts2d[inside]
	if len(pts2d) == 0:
		return
	P = p0 + pts2d[:, 0, None] * u + pts2d[:, 1, None] * v
	S = np.asarray(point_S, dtype=float)
	R = P - S
	r = np.linalg.norm(R, axis=1)
	r3 = r * r * r
	with np.errstate(divide="ignore", invalid="ignore"):
		ds = np.minimum(m / r3, 1.0)
	ds = np.nan_to_num(ds, nan=1.0, posinf=1.0)
	col = np.floor(np.asarray(color, dtype=float) * ds[:, None] * 0.5 + 0.5).astype(np.uint8)
	sx = P[:, 0] / P[:, 2] * z_screen
	sy = P[:, 1] / P[:, 2] * z_screen
	ix = np.floor(500.0 * (sx + 1.0)).astype(int)
	iy = np.floor(-500.0 * (sy - 1.0)).astype(int)
	for x, y, c in zip(ix.tolist(), iy.tolist(), col.tolist()):
		circle(screen, tuple(c), (x, y), radius)

class Polyhedron:
	def __init__(self, vertices, faces, face_colors=None):
		self.vertices = np.array(vertices, dtype=float)
		self.faces = [tuple(f) for f in faces]
		if face_colors is None:
			face_colors = [WHITE] * len(self.faces)
		self.face_colors = list(face_colors)

	def move(self, v):
		self.vertices += np.asarray(v, dtype=float)

	def rotate(self, rot):
		center = self.vertices.mean(axis=0)
		for k in range(len(self.vertices)):
			rel = self.vertices[k] - center
			q = np.quaternion(0, rel[0], rel[1], rel[2])
			q = rot * q * rot**(-1)
			self.vertices[k] = center + np.array([q.x, q.y, q.z])

	def face_visible(self, face_index):
		face = self.faces[face_index]
		mid = center([self.vertices[i] for i in face])
		for j, other in enumerate(self.faces):
			if j == face_index:
				continue
			pts = [self.vertices[k] for k in other]
			for t in range(1, len(pts) - 1):
				if is_point_beside_plane(mid, [pts[0], pts[t], pts[t+1]]):
					return False
		return True

	def draw(self):
		for idx, face in enumerate(self.faces):
			if not self.face_visible(idx):
				continue
			pts = [self.vertices[i] for i in face]
			draw_polygon_with_lights(pts, self.face_colors[idx])

PHI = (1 + 5**0.5) / 2

def normalize_vertices(vertices):
	"""Привести радиус описанной сферы к 1 (вершины заданы вокруг начала координат)."""
	v = np.array(vertices, dtype=float)
	v /= np.linalg.norm(v, axis=1).max()
	return v

def distinct_colors(n):
	"""Сгенерировать n различимых цветов."""
	cols = []
	for i in range(n):
		h = (i * 0.618033988749895) % 1.0
		r, g, b = colorsys.hsv_to_rgb(h, 0.85, 1.0)
		cols.append((int(r*255), int(g*255), int(b*255)))
	return cols

PLATONIC_SOLIDS = {
	"Тетраэдр": {
		"vertices": normalize_vertices([(1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)]),
		"faces": [(0,1,2),(0,3,2),(1,3,2),(1,3,0)],
		"colors": [RED, YELLOW, GREEN, BLUE],
	},
	"Куб": {
		"vertices": normalize_vertices([(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]),
		"faces": [(2,3,0,1),(1,5,4,0),(3,7,4,0),(2,6,5,1),(2,3,7,6),(5,6,7,4)],
	},
	"Октаэдр": {
		"vertices": normalize_vertices([(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]),
		"faces": [(3,5,1),(3,5,0),(3,4,1),(3,4,0),(2,5,0),(2,5,1),(2,4,0),(2,4,1)],
	},
	"Додекаэдр": {
		"vertices": normalize_vertices([
			(1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1),(-1,1,1),(-1,1,-1),(-1,-1,1),(-1,-1,-1),
			(0,1/PHI,PHI),(0,1/PHI,-PHI),(0,-1/PHI,PHI),(0,-1/PHI,-PHI),
			(1/PHI,PHI,0),(1/PHI,-PHI,0),(-1/PHI,PHI,0),(-1/PHI,-PHI,0),
			(PHI,0,1/PHI),(PHI,0,-1/PHI),(-PHI,0,1/PHI),(-PHI,0,-1/PHI),
		]),
		"faces": [
			(9,11,7,19,5),(5,14,12,1,9),(4,14,5,19,18),
			(2,13,15,6,10),(3,13,15,7,11),(6,15,7,19,18),
			(2,16,17,3,13),(3,11,9,1,17),(1,17,16,0,12),
			(6,18,4,8,10),(2,16,0,8,10),(4,14,12,0,8),
		],
	},
	"Икосаэдр": {
		"vertices": normalize_vertices([
			(0,1,PHI),(0,1,-PHI),(0,-1,PHI),(0,-1,-PHI),
			(1,PHI,0),(1,-PHI,0),(-1,PHI,0),(-1,-PHI,0),
			(PHI,0,1),(PHI,0,-1),(-PHI,0,1),(-PHI,0,-1),
		]),
		"faces": [
			(0,6,10),(2,5,8),(0,2,8),(0,2,10),(5,9,8),
			(3,9,1),(3,9,5),(3,11,1),(6,11,1),(6,11,10),
			(0,4,8),(4,6,0),(4,6,1),(4,9,1),(4,9,8),
			(2,7,10),(3,7,5),(2,7,5),(7,11,3),(7,11,10),
		],
	},
}

names = list(PLATONIC_SOLIDS)
print("Платоновы тела:")
for i, name in enumerate(names, 1):
	print("  %d. %s" % (i, name))
while True:
	answer = input("Выберите номер (1-%d) или Enter для Тетраэдра: " % len(names)).strip()
	if answer == "":
		chosen = names[0]
		break
	if answer.isdigit() and 1 <= int(answer) <= len(names):
		chosen = names[int(answer) - 1]
		break
	print("Неверный ввод, попробуйте ещё раз.")
solid = PLATONIC_SOLIDS[chosen]

pygame.init()


FPS = 30
z_screen = -1
x_pixels = 1000
y_pixels = 1000
screen = pygame.display.set_mode((x_pixels, y_pixels))
clock = pygame.time.Clock()
finished = False

#Point of view / origin point
point_O = np.array([0,0,0])
#Light
point_S = np.array([0,0,0])
#Scale and center of the selected solid
SCALE = 0.6
CENTER = np.array([0.0, 0.0, -1.5])
polyhedron = Polyhedron(
	[np.array(v) * SCALE + CENTER for v in solid["vertices"]],
	solid["faces"],
	solid.get("colors") or distinct_colors(len(solid["faces"])))
#rotation around vector (0,1,0) on 2 degree in a frame
alpha = np.pi/180
rot1 = np.quaternion(np.cos(alpha),0,np.sin(alpha),0)
rot1r = np.quaternion(np.cos(alpha),0,-np.sin(alpha),0)
rot2 = np.quaternion(np.cos(alpha),np.sin(alpha),0,0)
rot2r = np.quaternion(np.cos(alpha),-np.sin(alpha),0,0)
rot3 = np.quaternion(np.cos(alpha),0,0,np.sin(alpha))
rot3r = np.quaternion(np.cos(alpha),0,0,-np.sin(alpha))
polyhedron.draw()
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

	polyhedron.move(move_direction)

	if rot_010:
		polyhedron.rotate(rot1)
	if rot_010r:
		polyhedron.rotate(rot1r)
	if rot_100:
		polyhedron.rotate(rot2)
	if rot_100r:
		polyhedron.rotate(rot2r)
	if rot_001:
		polyhedron.rotate(rot3)
	if rot_001r:
		polyhedron.rotate(rot3r)
	
	if light_right:
		point_S = point_S + np.array([0.01,0,0])
	if light_left:
		point_S = point_S + np.array([-0.01,0,0])
	if light_up:
		point_S = point_S + np.array([0,0.01,0])
	if light_down:
		point_S = point_S + np.array([0,-0.01,0])
	
	polyhedron.draw()
	pygame.display.update()
	screen.fill(BLACK)

pygame.quit()