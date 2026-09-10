import os
from random import seed

from config import SEED, epsilon_size as initial_epsilon_size, generations, max_resx, max_steps, min_epsilon, mutation_prob, res_x as initial_res_x, res_y as initial_res_y, rotation_degree, sofa_len, sofa_width, square_len as initial_square_len, square_radius as initial_square_radius, square_width as initial_square_width, span, steps as initial_steps, movement_degree as initial_movement_degree, stagnation_time, walls
from fitness import fitness
from mutation import change_polynomial
from polynomial import Polynomial
from visualization import save_sofa_image, save_sofa_journey_frames


def next_output_index(base_dir):#finds unused name for output files, so can run multiple instances
	i = 0
	while os.path.isdir(os.path.join(base_dir, f'run_{i}')):
		i += 1
	return i


def log_solution(movement, rotation, generation, images_dir, log_file_path, squares):
	output_file = os.path.join(images_dir, f'gen_{generation + 1}.png')
	save_sofa_image(output_file, squares, sofa_len, sofa_width)
	with open(log_file_path, 'a') as log_file:
		log_file.write(f"Generation {generation + 1}: movement {movement} rotation {rotation}\n")


def run():
	seed(SEED)

	res_x = initial_res_x
	res_y = initial_res_y
	square_len = initial_square_len
	square_width = initial_square_width
	square_radius = initial_square_radius
	steps = initial_steps
	epsilon_size = initial_epsilon_size
	movement_degree = initial_movement_degree

	base = Polynomial([-span, 1]) * Polynomial([span, 1])  # hits (-span,0) and (span,0) -> start and endpoint of the sofas jurney
	mov_mult = Polynomial([1 / span]) #the movement polynomial that evolves, the final movement is base*mov_mult, base*mov_mult is inicialized to hit the center of the corner
	rotation_base = Polynomial([0.0, 45.0 / span])  # fixed line that hits -45° at x=-span and 45° at x=span
	rot_mult = Polynomial([0.0])  # evolving correction; multiplied by base so the endpoints stay fixed
	prev_mov_mult = mov_mult
	prev_rot_mult = rot_mult

	script_dir = os.path.dirname(os.path.abspath(__file__))
	output_ind = next_output_index(script_dir)
	run_dir = os.path.join(script_dir, f'run_{output_ind}')
	images_dir = os.path.join(run_dir, 'images')
	final_animation_dir = os.path.join(run_dir, 'final_animation')
	os.makedirs(images_dir)
	os.makedirs(final_animation_dir)
	log_file_path = os.path.join(run_dir, 'best_solution_log.txt')

	cover, squares = fitness(base * mov_mult, rotation_base + base * rot_mult, res_x=res_x, res_y=res_y, steps=steps)
	save_sofa_image(os.path.join(images_dir, 'gen_0.png'), squares, sofa_len, sofa_width)
	print(cover * sofa_len * sofa_width / (res_x * res_y))

	epsilons_rot = [0.0 if i % 2 == 0 else 10.0 for i in range(rotation_degree + 1)] # forces an odd polynomial
	epsilons_mov = [1 if i % 2 == 0 else 0 for i in range(movement_degree + 1)]	 	 # forces an even polynomial
	stagnation = 0
	repeat_last_change = False
	for generation in range(generations):
		if repeat_last_change:
			new_rot = rot_mult + (rot_mult - prev_rot_mult)
			new_mov = mov_mult + (mov_mult - prev_mov_mult)
		else:
			new_rot, changed_rot = change_polynomial(rot_mult, rotation_degree, epsilons_rot, mutation_probability=mutation_prob)
			new_mov, changed_mov = change_polynomial(mov_mult, movement_degree, epsilons_mov, mutation_probability=mutation_prob)
		new_cover, new_squares = fitness(base * new_mov, rotation_base + base * new_rot, res_x=res_x, res_y=res_y, steps=steps)
		if new_cover > cover:
			prev_rot_mult = rot_mult
			prev_mov_mult = mov_mult
			cover = new_cover
			rot_mult = new_rot
			mov_mult = new_mov
			squares = new_squares
			log_solution(base * mov_mult, rotation_base + base * rot_mult, generation, images_dir, log_file_path, squares)

			rot_coeffs = rot_mult.coefficients[:]
			while len(rot_coeffs) <= rotation_degree:
				rot_coeffs.append(0)
			epsilons_rot = [0.0 if idx % 2 == 0 else max(0.01, epsilon_size * abs(rot_coeffs[idx])) for idx in range(rotation_degree + 1)]

			mov_coeffs = mov_mult.coefficients[:]
			while len(mov_coeffs) <= movement_degree:
				mov_coeffs.append(0)
			epsilons_mov = [max(0.01, epsilon_size * abs(mov_coeffs[idx])) if idx % 2 == 0 else 0.0 for idx in range(movement_degree + 1)]
			repeat_last_change = True

		elif stagnation > stagnation_time:
			repeat_last_change = False
			stagnation = 0
			if res_x < max_resx:
				res_x = min(int(res_x * 1.1), max_resx)
				res_y = int(res_x * sofa_width / sofa_len)
				square_len = sofa_len / res_x
				square_width = sofa_width / res_y
				square_radius = (square_len**2 + square_width**2)**0.5 / 2
			if steps < max_steps:
				steps = min(int(steps * 1.1), max_steps)
			epsilon_size = max(epsilon_size * 0.95, min_epsilon)
			cover, squares = fitness(base * mov_mult, rotation_base + base * rot_mult, res_x=res_x, res_y=res_y, steps=steps)
		else:
			repeat_last_change = False
			stagnation += 1


		coverage = cover * sofa_len * sofa_width / (res_x * res_y)
		print(f"Generation {generation + 1}: {coverage} coverage")
		print("covered squares before:", cover, "new:", new_cover)

	cover, squares = fitness(base * mov_mult, rotation_base + base * rot_mult, res_x=800, res_y=int(800 * sofa_width / sofa_len), steps=500)
	print("Final high-res coverage:")
	print(cover * sofa_len * sofa_width / (800 * int(800 * sofa_width / sofa_len)))
	save_sofa_journey_frames(
		squares,
		base * mov_mult,
		rotation_base + base * rot_mult,
		walls,
		final_animation_dir,
		steps=100,
		a=span,
		sofa_len=sofa_len,
		sofa_width=sofa_width,
	)