import math
import matplotlib.pyplot as plt
import numpy as np
from random import randrange as ran
from random import choice
import os

#was 18565 new 18565 rotation -351.8869140625066 + 92.47956018066404x -1.1419387817382813x^2 -12.4969482421875x^3 -0.42193469238281234x^4 -48.10613834574996x^5 + 0.3271141052246094x^6 + 0.2197265625x^7 + 3.1250500679016113x^8 + 0.1640625x^9 -2.421875x^12 + 4.8194580078125x^13
#was 18565 new 18565 movement 0.4598683413058291 + 0.16163822515770188x^2 + 0.31718673705802797x^4 + 0.0565152874410003x^6 -0.5547796321004123x^8 -0.5604906904614834x^10 + 0.037592406547916415x^12 -0.2664166220197397x^14 + 0.3057194724892674x^16 -0.24395728691973223x^18 -0.044365315773912166x^20 -0.03301079967581577x^22


class Polynomial:

	def __init__(self, coefficients):
		while len(coefficients) > 1 and coefficients[-1] == 0:
			coefficients.pop()
		self.coefficients = coefficients if coefficients else [0]

	def __repr__(self):
		if not self.coefficients or all(c == 0 for c in self.coefficients):
			return "0"

		terms = []
		for power, coeff in enumerate(self.coefficients):
			if coeff == 0:
				continue

			# Format the coefficient
			if power == 0:
				terms.append(f"{coeff}")
			elif power == 1:
				if coeff == 1:
					terms.append("x")
				elif coeff == -1:
					terms.append("-x")
				else:
					terms.append(f"{coeff}x")
			else:
				if coeff == 1:
					terms.append(f"x^{power}")
				elif coeff == -1:
					terms.append(f"-x^{power}")
				else:
					terms.append(f"{coeff}x^{power}")

		# Join terms with proper signs
		if not terms:
			return "0"

		result = terms[0]
		for term in terms[1:]:
			if term[0] == '-':
				result += f" {term}"
			else:
				result += f" + {term}"
		return result

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

sofa_len = 2*a*(2**(1/2)) + 1 # lenght of the starting block of squares -> fills the corridor
sofa_width = 1

res_x = 400
res_y = int(res_x * sofa_width // sofa_len)
squares = [[True for i in range(res_y)] for i in range(res_x)]
walls = [Polynomial([-(2**(1/2))/2 - a, -1]), Polynomial([(2**(1/2))/2 - a, -1]), Polynomial([-(2**(1/2))/2 - a, 1]), Polynomial([(2**(1/2))/2 - a, 1])]
steps = 120


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
	square_radius = (square_len**2 + square_width**2)**(1/2)
	stayed = False
	if x <= 0:
		if walls[1].evaluate(x)-square_radius > y > walls[0].evaluate(x)+square_radius:
			stayed = True
	else:
		if walls[3].evaluate(x)-square_radius > y > walls[2].evaluate(x)+square_radius:
			stayed = True

	return stayed

def fitness(movement, rotation):
	squares = [[True for i in range(res_y)] for i in range(res_x)]
	for step in range(steps+1):
		for x in range(res_x):
			for y in range(res_y):
				if squares[x][y]:
					center_x = -a + 2*a*step/steps
					center_y = movement.evaluate(center_x)
					cell_x, cell_y = squares_position(x, y, center_x, center_y, rotation.evaluate(center_x))
					if not stayed_in(cell_x, cell_y):
						squares[x][y] = False

	count = 0
	for x in range(res_x):
		for y in range(res_y):
			if squares[x][y]:
				count += 1
	return count, squares


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


base = Polynomial([-a, 1]) * Polynomial([a, 1])  # hits (-a,0) and (a,0)
multiplier = Polynomial([0.47039946367666763, 0, 0.15065507156645208, 0, 0.30669230401581876, 0,  0.07964955243871474, 0, -0.6092269207122406, 0, -0.5098234727965457, 0, -0.024000000000000007, 0, -0.08288412528639996, 0, -0.00390126351073275, 0, -0.3950110865511547])
rotation = Polynomial([-350.3244140625066, 94.5950084838867, -1.1419387817382813, -12.5, -0.42004260253906234, -48.00848209574996, 0.7702903747558594, 0.1953125, 1.5625, 0.06396484375])
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, 'output')


if __name__ == '__main__':
	# Create output directory next to this script
	os.makedirs(output_dir, exist_ok=True)

	c, squares = fitness(base * multiplier, rotation)
	print(c * sofa_len * sofa_width / (res_x * res_y))

	rotation_degree = 15
	movement_degree = 12
	epsilons_rot = [100 for _ in range(rotation_degree)]
	epsilons_mov = [0.1 for _ in range(movement_degree)]

	generations = 10000
	for i in range(generations):
		print("generation", i + 1)
		changing_rot = ran(rotation_degree)
		new_rot = rotation + Polynomial([0] * (changing_rot - 1) + [choice([-1, 1]) * epsilons_rot[changing_rot]])
		new_c, new_squares = fitness(base * multiplier, new_rot)
		print("was", c, "new", new_c, "rotation", new_rot)
		if new_c > c:
			c = new_c
			rotation = new_rot
			squares = new_squares
			epsilons_rot[changing_rot] *= 2.1
		else:
			epsilons_rot[changing_rot] *= 0.5

		changing_mov = ran(movement_degree)
		new_mov = multiplier + Polynomial([0] * (2 * changing_mov) + [choice([-1, 1]) * epsilons_mov[changing_mov]])
		new_c, new_squares = fitness(base * new_mov, rotation)
		print("was", c, "new", new_c, "movement", new_mov)
		if new_c >= c:
			c = new_c
			multiplier = new_mov
			squares = new_squares
			epsilons_mov[changing_mov] *= 1.3
		else:
			epsilons_mov[changing_mov] *= 0.8

		coverage = c * sofa_len * sofa_width / (res_x * res_y)
		print(f"Generation {i+1}: {coverage:.4f} coverage")

		# Save image every generation
		output_file = os.path.join(output_dir, f'gen_{i+1:05d}.png')
		save_sofa_image(output_file)
		print(f"Saved {output_file}")
