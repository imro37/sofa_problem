import math

from config import res_x as default_res_x, res_y as default_res_y, sofa_len, sofa_width, span, steps as default_steps, walls


def add_to_boundry_set(x, y, set, squares):
	if 0 <= x < len(squares) and 0 <= y < len(squares[0]):
		if squares[x][y] == (True, False):
			set.add((x, y))
			squares[x][y] = (True, True)


def squares_position(x_idx, y_idx, center_x, center_y, rotation, sofa_len, sofa_width, square_len, square_width):
	angle = math.radians(rotation)

	local_x = -sofa_len / 2 + (x_idx + 0.5) * square_len
	local_y = -sofa_width / 2 + (y_idx + 0.5) * square_width

	world_x = center_x + local_x * math.cos(angle) - local_y * math.sin(angle)
	world_y = center_y + local_x * math.sin(angle) + local_y * math.cos(angle)
	return world_x, world_y


def stayed_in(x, y, square_radius):
	stayed = False
	if x <= 0:
		if walls[1].evaluate(x) - square_radius > y > walls[0].evaluate(x) + square_radius:
			stayed = True
	else:
		if walls[3].evaluate(x) - square_radius > y > walls[2].evaluate(x) + square_radius:
			stayed = True

	return stayed


def fitness(movement, rotation, res_x=default_res_x, res_y=default_res_y, steps=default_steps):
	square_len = sofa_len / res_x
	square_width = sofa_width / res_y
	square_radius = (square_len**2 + square_width**2) ** 0.5 / 2

	# state[x][y] -> (is_alive, was_queued)
	state = [[(True, False) for i in range(res_y)] for i in range(res_x)]
	boundry_squares = set()
	for i in range(res_x):
		boundry_squares.add((i, 0))
		boundry_squares.add((i, res_y - 1))
		state[i][0] = (True, True)
		state[i][res_y - 1] = (True, True)
	for j in range(res_y):
		boundry_squares.add((0, j))
		boundry_squares.add((res_x - 1, j))
		state[0][j] = (True, True)
		state[res_x - 1][j] = (True, True)

	for step in range(steps + 1):
		new_boundry_squares = set()
		while boundry_squares:
			x, y = boundry_squares.pop()
			center_x = -span + 2 * span * step / steps #the center point of the sofa at the current step
			center_y = movement.evaluate(center_x)
			cell_x, cell_y = squares_position(x, y, center_x, center_y, rotation.evaluate(center_x), sofa_len, sofa_width, square_len, square_width)
			if not stayed_in(cell_x, cell_y, square_radius):
				state[x][y] = (False, False)
				add_to_boundry_set(x + 1, y, boundry_squares, state)
				add_to_boundry_set(x - 1, y, boundry_squares, state)
				add_to_boundry_set(x, y + 1, boundry_squares, state)
				add_to_boundry_set(x, y - 1, boundry_squares, state)

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