import math
import matplotlib.pyplot as plt
import numpy as np
from random import randrange
from random import uniform
import os

best_movement =  [0.09028615342502605,0,-0.009740252911162787,0,0.9813074069726829,0,-0.47865520222657537,0,0.30557278861697523,0,-0.3102728815657489,0,-0.030020618627862015,0,-0.3982886223111034,0,0.11943979386601072,0,0.2184937846571669] 
best_rotation =  [0.36969438580912795,54.60791672333049,0.33119821539801886,6.037682262039188,0.8350660735035955,-17.431440526432493,-1.8420354407091328,1.1390813438361806,0.2517998107395694,0.6465559356472826]

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
		result = 0
		for power, coeff in enumerate(self.coefficients):
			result += coeff * (x ** power)
		return result

	def degree(self):
		return len(self.coefficients) - 1

a = 1 #the x coordinate of the -start and endpoint of the sofa's journey

sofa_len = 3.35  #lenght of the starting block of squares, 2*a*(2**(1/2)) + 1 would be using all available space, 3.35 is just a heuristic from known solution
sofa_width = 1	 #matches the width of the corridor

res_x = 600 #number of pixels along the sofa's length (resolution)
res_y = int(res_x * sofa_width / sofa_len)
square_len = sofa_len / res_x
square_width = sofa_width / res_y
square_radius = (square_len**2 + square_width**2)**0.5 / 2 # for checking if the square stayed in bounds
squares = [[True for i in range(res_y)] for i in range(res_x)]
walls = [Polynomial([-(2**(1/2))/2 - a, -1]), Polynomial([(2**(1/2))/2 - a, -1]), Polynomial([-(2**(1/2))/2 - a, 1]), Polynomial([(2**(1/2))/2 - a, 1])]
steps = 200 #number of simulation steps, the sofa will take from -a to a


def squares_position(x_idx, y_idx, center_x, center_y, rotation):
	angle = math.radians(rotation)

	local_x = -sofa_len / 2 + (x_idx + 0.5) * square_len
	local_y = -sofa_width / 2 + (y_idx + 0.5) * square_width

	world_x = center_x + local_x * math.cos(angle) - local_y * math.sin(angle)
	world_y = center_y + local_x * math.sin(angle) + local_y * math.cos(angle)
	return world_x, world_y

def stayed_in(x,y):
	stayed = False
	if x <= 0:
		if walls[1].evaluate(x)-square_radius > y > walls[0].evaluate(x)+square_radius:
			stayed = True
	else:
		if walls[3].evaluate(x)-square_radius > y > walls[2].evaluate(x)+square_radius:
			stayed = True

	return stayed

def add_to_boundry_set(x,y,set,squares):
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
				add_to_boundry_set(x+1,y,boundry_squares, state)
				add_to_boundry_set(x-1,y,boundry_squares, state)
				add_to_boundry_set(x,y+1,boundry_squares, state)
				add_to_boundry_set(x,y-1,boundry_squares, state)

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

def save_sofa_image(filename, squares):
	res_x = len(squares)
	res_y = len(squares[0])
	arr = np.zeros((res_y, res_x), dtype=np.uint8)
	for x in range(res_x):
		for y in range(res_y):
			arr[y, x] = 1 if squares[x][y] else 0

	fig_width = 10
	fig_height = max(2, fig_width * (sofa_width / sofa_len))
	fig, ax = plt.subplots(figsize=(fig_width, fig_height))

	extent = [0, sofa_len, 0, sofa_width]
	ax.imshow(arr, cmap='Greens', interpolation='nearest', origin='lower', extent=extent, aspect='equal')

	ax.set_xlim(0, sofa_len)
	ax.set_ylim(0, sofa_width)
	ax.set_xlabel('sofa length')
	ax.set_ylabel('sofa width')
	plt.tight_layout()
	plt.savefig(filename, dpi=150, bbox_inches='tight')
	plt.close()

def change_polynomial(poly, degree, epsilons, mutation_probability=0.2, even = False):
	coefficients = poly.coefficients[:]
	while len(coefficients) < degree*2 -1:
		coefficients.append(0)

	changed = []
	for i in range(degree):
		j = i
		if even:
			i = i*2
		if uniform(0, 1) < mutation_probability:
			coefficients[i] += uniform(-1, 1) * epsilons[j]
			changed.append(j)

	if not changed:
		i = randrange(0, degree)
		j = i
		if even:
			i = i*2
		coefficients[i] += uniform(-1, 1) * epsilons[j]
		changed.append(j)

	return Polynomial(coefficients), changed

base = Polynomial([-a, 1]) * Polynomial([a, 1])  # hits (-a,0) and (a,0) -> start and endpoint of the sofas jurney
multiplier = Polynomial([1])
rotation = Polynomial([0])

script_dir = os.path.dirname(os.path.abspath(__file__))
output_ind = 99 #just for running the script multiple times without overwriting previous outputs(could be done smarter)
output_dir = os.path.join(script_dir, f'output_{output_ind}') 


if __name__ == '__main__':
	os.makedirs(output_dir, exist_ok=True)

	c, squares = fitness(base * multiplier, rotation)
	print(c * sofa_len * sofa_width / (res_x * res_y))

	rotation_degree = 12
	movement_degree = 12
	epsilon_size = 0.1
	epsilons_rot = [10.0 for _ in range(rotation_degree)]
	epsilons_mov = [0.1 for _ in range(movement_degree)]

	generations = 100000
	stagnation = 0
	for i in range(generations):
		got_better = False
		new_rot, changed_rot = change_polynomial(rotation, rotation_degree, epsilons_rot, mutation_probability=0.35)
		new_mov, changed_mov = change_polynomial(multiplier, movement_degree, epsilons_mov, mutation_probability=0.35, even=True)
		new_c, new_squares = fitness(base * new_mov, new_rot)
		print("was", c, "new", new_c)
		if new_c > c:
			c = new_c
			rotation = new_rot
			multiplier = new_mov
			squares = new_squares

			if i > 50: #first 50 generations are for exploration, the epsilons are not based on the coefficients, but just set to a high value to encourage exploration
				rot_coeffs = rotation.coefficients[:]
				while len(rot_coeffs) < rotation_degree:
					rot_coeffs.append(0)
				epsilons_rot = [max(0.05,  epsilon_size * abs(rot_coeffs[idx])) for idx in range(rotation_degree)]

				mov_coeffs = multiplier.coefficients[:]
				while len(mov_coeffs) < movement_degree * 2 - 1:
					mov_coeffs.append(0)
				epsilons_mov = [max(0.005, epsilon_size * abs(mov_coeffs[idx * 2])) for idx in range(movement_degree)]

			got_better = True

		coverage = c * sofa_len * sofa_width / (res_x * res_y)
		print(f"Generation {i+1}: {coverage:.4f} coverage")

		if got_better:
			output_file = os.path.join(output_dir, f'gen_{i+1:05d}.png')
			save_sofa_image(output_file, squares)
			print(f"Saved image")
			with open(f'best_solution_log_{output_ind}.txt', 'a') as log_file:
				log_file.write(f"Generation {i+1}: movement {multiplier} rotation {rotation}\n")
		else:
			stagnation += 1
			if stagnation > 10000:		
					stagnation = 0
					res_x = min(int(res_x*1.2), 1000)
					res_y = int(res_x * sofa_width // sofa_len)
					square_len = sofa_len / res_x
					square_width = sofa_width / res_y
					steps = min(int(steps*1.2), 300)
					c, squares = fitness(base * multiplier, rotation)
					


