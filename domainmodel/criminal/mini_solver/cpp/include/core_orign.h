#include <math.h>
#include <stdio.h>
#include <stdlib.h>

// CHANGE 1
#include "userfuncs.h"


#define DX 0.5
#define DX2 0.25
#define DXM1 2.0
#define DXM2 4.0


#define DY 0.1
#define DY2 0.01
#define DYM1 10.0
#define DYM2 100.0


#define DZ 1
#define DZ2 1
#define DZM1 1.0
#define DZM2 1.0

#define Block0CELLSIZE 1
#define DT 0.0001


#define Block0StrideX 1
#define Block0CountX 64
#define Block0OffsetX 3.0

#define Block0StrideY 64
#define Block0CountY 64
#define Block0OffsetY 3.0

#define Block0StrideZ 567
#define Block0CountZ 1
#define Block0OffsetZ 0

#define PAR_COUNT 4
#define COUNT_OF_FUNC 9

void Block0CentralFunction_Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);
void Block0DefaultNeumann__Bound2__Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);
void Block0DefaultNeumann__Bound3__Eqn3(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);
void Block0DefaultNeumann__Bound0__Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);
void Block0DefaultNeumann__Bound1__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);
void Block0Default_Vertex0_2__Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);
void Block0Default_Vertex2_1__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);
void Block0Default_Vertex1_3__Eqn2(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);
void Block0Default_Vertex3_0__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);
void getBlock0BoundFuncArray(func_ptr_t** ppBoundFuncs);
void getFuncArray(func_ptr_t** ppBoundFuncs, int blockIdx);
void releaseFuncArray(func_ptr_t* BoundFuncs);


