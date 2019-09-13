

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "userfuncs.h"



#define DX 0.03
#define DX2 0.0009
#define DXM1 33
#define DXM2 1111


#define DY 0.02
#define DY2 0.0004
#define DYM1 50
#define DYM2 2500


#define DZ 1
#define DZ2 1
#define DZM1 1
#define DZM2 1


#define DT 1e-05





#define Block0CELLSIZE 1





#define Block0StrideX 1
#define Block0CountX 101
#define Block0OffsetX 0.0

#define Block0StrideY 101
#define Block0CountY 101
#define Block0OffsetY 0.0

#define Block0StrideZ 10201
#define Block0CountZ 1
#define Block0OffsetZ 0


#define PAR_COUNT 4

//////////////////////////////////
#define COUNT_OF_FUNC 6


void Block0CentralFunction_Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0Dirichlet0__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0CentralFunction_Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0Dirichlet0__Eqn2(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void vertex_eq_2_sides_0_0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0CentralFunction_Eqn2(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);


void getBlock0BoundFuncArray(func_ptr_t** ppBoundFuncs);
void getFuncArray(func_ptr_t** ppBoundFuncs, int blockIdx);
void releaseFuncArray(func_ptr_t* BoundFuncs);

