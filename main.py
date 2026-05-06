import math
import matplotlib.pyplot as plt
import numpy as np
from random import randrange as ran
from random import choice
from random import uniform
import os
from collections import deque

#-0.018133582982462038,32.13476850022717,-6.764182218722893,27.28943420259416,-3.1117282328240505,-14.475513908592891,9.982331246469954
#0.16784911590000998,0,0.1350140697785042,0,0.030517957308613893,0,0.07845157466374399,0,0.033766605551466974,0,0.12073815527159326,0,-0.06514352427361955,0,-0.019258157334110942

class Polynomial:

	def __init__(self, coefficients):
		while len(coefficients) > 1 and coefficients[-1] == 0:
			coefficients.pop()
		self.coefficients = coefficients if coefficients else [0]

	def __repr__(self):
		if not self.coefficients or all(c == 0 for c in self.coefficients):
			return "0"

		return ",".join(str(coeff) for coeff in self.coefficients)

	def __add__(self, other):
		"""Add two polynomials: self + other"""
		if not isinstance(other, Polynomial):
			raise TypeError("Can only add Polynomial to Polynomial")

		# Make copies and pad to same length
		len1 = len(self.coefficients)
		len2 = len(other.coefficients)
		max_len = max(len1, len2)

		result = []
		for i in range(max_len):
			c1 = self.coefficients[i] if i < len1 else 0
			c2 = other.coefficients[i] if i < len2 else 0
			result.append(c1 + c2)

		return Polynomial(result)

	def __sub__(self, other):
		"""Subtract two polynomials: self - other"""
		if not isinstance(other, Polynomial):
			raise TypeError("Can only subtract Polynomial from Polynomial")

		len1 = len(self.coefficients)
		len2 = len(other.coefficients)
		max_len = max(len1, len2)

		result = []
		for i in range(max_len):
			c1 = self.coefficients[i] if i < len1 else 0
			c2 = other.coefficients[i] if i < len2 else 0
			result.append(c1 - c2)

		return Polynomial(result)

	def __mul__(self, other):
		"""Multiply two polynomials: self * other"""
		if not isinstance(other, Polynomial):
			raise TypeError("Can only multiply Polynomial by Polynomial")

		# Result will have degree = sum of degrees
		result_len = len(self.coefficients) + len(other.coefficients) - 1
		result = [0] * result_len

		# Multiply each coefficient
		for i, c1 in enumerate(self.coefficients):
			for j, c2 in enumerate(other.coefficients):
				result[i + j] += c1 * c2

		return Polynomial(result)

	def evaluate(self, x):
		"""Evaluate the polynomial at a given value of x."""
		result = 0
		for power, coeff in enumerate(self.coefficients):
			result += coeff * (x ** power)
		return result

	def degree(self):
		"""Return the degree of the polynomial."""
		return len(self.coefficients) - 1


a = 1

sofa_len = 3.6#2*a*(2**(1/2)) + 1 # lenght of the starting block of squares -> fills the corridor
sofa_width = 1

res_x = 600
res_y = int(res_x * sofa_width // sofa_len)
squares = [[True for i in range(res_y)] for i in range(res_x)]
walls = [Polynomial([-(2**(1/2))/2 - a, -1]), Polynomial([(2**(1/2))/2 - a, -1]), Polynomial([-(2**(1/2))/2 - a, 1]), Polynomial([(2**(1/2))/2 - a, 1])]
steps = 100


def squares_position(x_idx, y_idx, center_x, center_y, rotation):
	angle = math.radians(rotation)

	# Positive angles are counterclockwise.
	square_len = sofa_len / res_x
	square_width = sofa_width / res_y

	# Map the grid cell to the sofa's local center coordinates.
	# x_idx indexes along sofa_len (x-direction), y_idx indexes along sofa_width (y-direction)
	local_x = -sofa_len / 2 + (x_idx + 0.5) * square_len
	local_y = -sofa_width / 2 + (y_idx + 0.5) * square_width

	world_x = center_x + local_x * math.cos(angle) - local_y * math.sin(angle)
	world_y = center_y + local_x * math.sin(angle) + local_y * math.cos(angle)
	return world_x, world_y

def stayed_in(x,y):
	square_len = sofa_len / res_x
	square_width = sofa_width / res_y
	square_radius = 0.5 * (square_len**2 + square_width**2)**(1/2)
	stayed = False
	if x <= 0:
		if walls[1].evaluate(x)-square_radius > y > walls[0].evaluate(x)+square_radius:
			stayed = True
	else:
		if walls[3].evaluate(x)-square_radius > y > walls[2].evaluate(x)+square_radius:
			stayed = True

	return stayed

def add_to_set_if_not_there(x,y,set,squares):
	if 0 <= x < res_x and 0 <= y < res_y:
		if squares[x][y] == (True, False):	
			set.add((x,y))
			squares[x][y] = (True,True)

def fitness(movement, rotation):
	# state[x][y] -> (is_alive, was_queued)
	state = [[(True, False) for i in range(res_y)] for i in range(res_x)]
	boundry_squares = set()
	for i in range(res_x):
		boundry_squares.add((i, 0))
		boundry_squares.add((i, res_y-1))
		state[i][0] = (True, True)
		state[i][res_y-1] = (True, True)
	for j in range(res_y):
		boundry_squares.add((0, j))
		boundry_squares.add((res_x-1, j))
		state[0][j] = (True, True)
		state[res_x-1][j] = (True, True)

	for step in range(steps+1):
		new_boundry_squares = set()
		while boundry_squares:
			x, y = boundry_squares.pop()
			center_x = -a + 2*a*step/steps #the center point of the sofa at the current step
			center_y = movement.evaluate(center_x)
			cell_x, cell_y = squares_position(x, y, center_x, center_y, rotation.evaluate(center_x))
			if not stayed_in(cell_x, cell_y):
				state[x][y] = (False, False)
				add_to_set_if_not_there(x+1,y,boundry_squares, state)
				add_to_set_if_not_there(x-1,y,boundry_squares, state)
				add_to_set_if_not_there(x,y+1,boundry_squares, state)
				add_to_set_if_not_there(x,y-1,boundry_squares, state)

			else:
				new_boundry_squares.add((x, y))

		boundry_squares = new_boundry_squares


	count = 0
	alive_squares = [[False for i in range(res_y)] for i in range(res_x)]
	for x in range(res_x):
		for y in range(res_y):
			if state[x][y][0]:
				count += 1
				alive_squares[x][y] = True
	return count, alive_squares

def save_sofa_image(filename):
	"""Save the current sofa grid as an image using a fixed grid coordinate system.

	This draws only the boolean `squares` grid (no rotation or world mapping), so
	each saved image is directly comparable to previous generations.
	"""

	# Build a 2D array where rows correspond to y (width) and cols to x (length)
	arr = np.zeros((res_y, res_x), dtype=np.uint8)
	for x in range(res_x):
		for y in range(res_y):
			arr[y, x] = 1 if squares[x][y] else 0

	fig_width = 10
	fig_height = max(2, fig_width * (sofa_width / sofa_len))
	fig, ax = plt.subplots(figsize=(fig_width, fig_height))

	# extent maps array coordinates to physical sofa coordinates [x0,x1,y0,y1]
	extent = [0, sofa_len, 0, sofa_width]
	ax.imshow(arr, cmap='Greens', interpolation='nearest', origin='lower', extent=extent, aspect='equal')

	ax.set_xlim(0, sofa_len)
	ax.set_ylim(0, sofa_width)
	ax.set_xlabel('sofa length')
	ax.set_ylabel('sofa width')
	plt.tight_layout()
	plt.savefig(filename, dpi=150, bbox_inches='tight')
	plt.close()

def change_polynomial(poly, degree, epsilons, mutation_probability=0.2):
	coefficients = poly.coefficients[:]
	while len(coefficients) < degree:
		coefficients.append(0)

	changed = []
	for i in range(degree):
		if uniform(0, 1) < mutation_probability:
			coefficients[i] += uniform(-1, 1) * epsilons[i]
			changed.append(i)

	if not changed:
		i = ran(degree)
		coefficients[i] += uniform(-1, 1) * epsilons[i]
		changed.append(i)

	return Polynomial(coefficients), changed

base = Polynomial([-a, 1]) * Polynomial([a, 1])  # hits (-a,0) and (a,0) -> start and endpoint of the sofas jurney
multiplier = Polynomial([1])
rotation = Polynomial([0])
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, 'output')


if __name__ == '__main__':
	os.makedirs(output_dir, exist_ok=True)

	c, squares = fitness(base * multiplier, rotation)
	print(c * sofa_len * sofa_width / (res_x * res_y))

	rotation_degree = 10
	movement_degree = 10
	epsilons_rot = [12.0 for _ in range(rotation_degree)]
	epsilons_mov = [0.02 for _ in range(movement_degree)]
	epsilon_growth = 1.1
	epsilon_decay = 0.95
	epsilon_rot_min, epsilon_rot_max = 0.05, 500 #0.05, 60.0
	epsilon_mov_min, epsilon_mov_max = 1e-4, 3.0 #1e-4, 1.0

	generations = 10000
	stagnation = 0
	for i in range(generations):
		got_better = False
		new_rot, changed_rot = change_polynomial(rotation, rotation_degree, epsilons_rot, mutation_probability=0.35)
		new_c, new_squares = fitness(base * multiplier, new_rot)
		print("was", c, "new", new_c, "rotation", new_rot)
		if new_c > c:
			c = new_c
			rotation = new_rot
			squares = new_squares
			for idx in changed_rot:
				epsilons_rot[idx] *= epsilon_growth
				epsilons_rot[idx] = min(epsilon_rot_max, max(epsilon_rot_min, epsilons_rot[idx]))
			got_better = True
		else:
			for idx in changed_rot:
				epsilons_rot[idx] *= epsilon_decay
				epsilons_rot[idx] = min(epsilon_rot_max, max(epsilon_rot_min, epsilons_rot[idx]))

		new_mov, changed_mov = change_polynomial(multiplier, movement_degree, epsilons_mov, mutation_probability=0.35)
		new_c, new_squares = fitness(base * new_mov, rotation)
		print("was", c, "new", new_c, "movement", new_mov)
		if new_c > c:
			c = new_c
			multiplier = new_mov
			squares = new_squares
			for idx in changed_mov:
				epsilons_mov[idx] *= epsilon_growth
				epsilons_mov[idx] = min(epsilon_mov_max, max(epsilon_mov_min, epsilons_mov[idx]))
			got_better = True
		else:
			for idx in changed_mov:
				epsilons_mov[idx] *= epsilon_decay
				epsilons_mov[idx] = min(epsilon_mov_max, max(epsilon_mov_min, epsilons_mov[idx]))

		coverage = c * sofa_len * sofa_width / (res_x * res_y)
		print(f"Generation {i+1}: {coverage:.4f} coverage")
		print(f"Epsilons rotation: {epsilons_rot}")
		print(f"Epsilons movement: {epsilons_mov}")

		if got_better:
			output_file = os.path.join(output_dir, f'gen_{i+1:05d}.png')
			save_sofa_image(output_file)
			print(f"Saved image")
		else:
			stagnation += 1
			if stagnation > 120:		
					stagnation = 0	
					epsilons_rot = [e*10 for e in epsilons_rot]
					epsilons_mov = [e*10 for e in epsilons_mov]

