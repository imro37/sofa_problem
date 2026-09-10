import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def _sofa_points(squares, sofa_len, sofa_width):
	res_x = len(squares)
	res_y = len(squares[0])
	square_len = sofa_len / res_x
	square_width = sofa_width / res_y

	points = []
	for x in range(res_x):
		for y in range(res_y):
			if squares[x][y]:
				local_x = -sofa_len / 2 + (x + 0.5) * square_len
				local_y = -sofa_width / 2 + (y + 0.5) * square_width
				points.append((local_x, local_y))

	return np.array(points)


def save_sofa_image(filename, squares, sofa_len, sofa_width):
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


def save_sofa_journey_frames(
	squares,
	movement,
	rotation,
	walls,
	output_dir,
	steps=100,
	a=1,
	sofa_len=3.35,
	sofa_width=1,
):
	"""Save absolute-coordinate frames of the sofa moving through the walls."""
	os.makedirs(output_dir, exist_ok=True)
	local_points = _sofa_points(squares, sofa_len, sofa_width)
	x_values = np.linspace(-a - sofa_len / 2, a + sofa_len / 2, 400)

	for step in range(steps):
		center_x = -a + 2 * a * step / (steps - 1)
		center_y = movement.evaluate(center_x)
		angle = np.radians(rotation.evaluate(center_x))

		world_x = center_x + local_points[:, 0] * np.cos(angle) - local_points[:, 1] * np.sin(angle)
		world_y = center_y + local_points[:, 0] * np.sin(angle) + local_points[:, 1] * np.cos(angle)

		fig, ax = plt.subplots(figsize=(10, 6))
		ax.scatter(world_x, world_y, s=1, color="green", marker="s", linewidths=0)

		for wall in walls:
			ax.plot(x_values, [wall.evaluate(x) for x in x_values], color="black", linewidth=1.5)

		ax.set_aspect("equal", adjustable="box")
		ax.set_xlim(x_values[0], x_values[-1])
		ax.set_ylim(-sofa_len / 2, sofa_len / 2)
		ax.set_xlabel("x")
		ax.set_ylabel("y")
		ax.set_title(f"Frame {step + 1}/{steps}")
		plt.tight_layout()
		plt.savefig(os.path.join(output_dir, f"frame_{step + 1:03d}.png"), dpi=150)
		plt.close(fig)