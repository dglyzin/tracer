

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "userfuncs.h"



#define DX 0.1
#define DX2 0.01
#define DXM1 10
#define DXM2 100


#define DY 0.1
#define DY2 0.01
#define DYM1 10
#define DYM2 100


#define DZ 1
#define DZ2 1
#define DZM1 1
#define DZM2 1


#define DT 0.0001





#define Block0CELLSIZE 1





#define Block0StrideX 1
#define Block0CountX 81
#define Block0OffsetX 3.0

#define Block0StrideY 81
#define Block0CountY 81
#define Block0OffsetY 3.0

#define Block0StrideZ 6561
#define Block0CountZ 1
#define Block0OffsetZ 0


#define PAR_COUNT 4

//////////////////////////////////
#define COUNT_OF_FUNC 17


void Block0CentralFunction_Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0CentralFunction_Eqn2(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0CentralFunction_Eqn3(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0CentralFunction_Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0DefaultNeumann__Bound2__Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0DefaultNeumann__Bound2__Eqn2(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0DefaultNeumann__Bound2__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0Dirichlet__Bound3_1__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0Dirichlet__Bound3_1__Eqn3(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0DefaultNeumann__Bound3__Eqn3(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0DefaultNeumann__Bound3__Eqn2(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0DefaultNeumann__Bound3__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0DefaultNeumann__Bound0__Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0DefaultNeumann__Bound0__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0DefaultNeumann__Bound1__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0Dirichlet__Bound1_1__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0Dirichlet__Bound1_1__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);


void getBlock0BoundFuncArray(func_ptr_t** ppBoundFuncs);
void getFuncArray(func_ptr_t** ppBoundFuncs, int blockIdx);
void releaseFuncArray(func_ptr_t* BoundFuncs);

