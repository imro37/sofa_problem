SEED = 42

span = 0.8        # the sofa center moves from -span to span

from polynomial import Polynomial

# the corridor walls defined as polynomials; the sofa center moves from (-span, 0) to (span, 0)
walls = [Polynomial([-(2 ** (1 / 2)) / 2 - span, -1]), Polynomial([(2 ** (1 / 2)) / 2 - span, -1]), Polynomial([-(2 ** (1 / 2)) / 2 - span, 1]), Polynomial([(2 ** (1 / 2)) / 2 - span, 1])]

sofa_len = 3.35  # does not fill the corridor fully, but longer than all "good" solutions
sofa_width = 1  # matches the corridor width

res_x = 100                                                   # the initial resoultion, gets increased after stagnation
res_y = int(res_x * sofa_width / sofa_len)
square_len = sofa_len / res_x                                 # size of individual squares/pixels
square_width = sofa_width / res_y
square_radius = (square_len**2 + square_width**2) ** 0.5 / 2  # square is approximated as a circle when detecting collisions
steps = 50                                                    # the initial number of samples along the sofa's journey, gets increased after stagnation

rotation_degree = 16    # degree of the rotation polynomial
movement_degree = 16    # degree of the movement polynomial
mutation_prob = 0.35
epsilon_size = 0.2      # size of the mutation step

# limits for the optimization process - increasing resolution when stagnating up untill this limits
max_resx = 600
max_steps = 150
min_epsilon = 0.05

stagnation_time = 50
generations = 1200