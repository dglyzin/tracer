#include "libheat2d.h"

void computeOneNode(double* result, double* source, double dt, double dx2, int idx, int sideLength) {
  result[idx] = source[idx] + dt * (
	  ((source[idx - 1] - 2 * source[idx] + source[idx + 1]) / dx2) + 
	  ((source[idx - sideLength] - 2 * source[idx] + source[idx + sideLength]) / dx2)
	);
}