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