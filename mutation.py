from random import randrange, uniform

from polynomial import Polynomial


def change_polynomial(poly, degree, epsilons, mutation_probability=0.2):
	coefficients = poly.coefficients[:]
	while len(coefficients) <= degree:
		coefficients.append(0)

	mutable_indices = [i for i in range(degree + 1) if i < len(epsilons) and epsilons[i] != 0]
	if not mutable_indices:
		return Polynomial(coefficients), []

	changed = []
	for i in mutable_indices:
		if uniform(0, 1) < mutation_probability:
			coefficients[i] += uniform(-1, 1) * epsilons[i]
			changed.append(i)

	if not changed:
		i = mutable_indices[randrange(0, len(mutable_indices))]
		coefficients[i] += uniform(-1, 1) * epsilons[i]
		changed.append(i)

	return Polynomial(coefficients), changed