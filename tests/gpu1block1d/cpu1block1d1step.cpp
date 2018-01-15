#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "/home/dglyzin/Tracer/hybriddomain/doc/userfuncs.h"

#define DX 0.01
#define DX2 0.0001
#define DXM1 100.0
#define DXM2 10000.0
#define DY 1
#define DY2 1
#define DYM1 1.0
#define DYM2 1.0
#define DZ 1
#define DZ2 1
#define DZM1 1.0
#define DZM2 1.0

#define Block0CELLSIZE 1

#define Block0StrideX 1
#define Block0CountX 501
#define Block0OffsetX 0.0
#define Block0StrideY 501
#define Block0CountY 1
#define Block0OffsetY 0
#define Block0StrideZ 501
#define Block0CountZ 1
#define Block0OffsetZ 0

#define PAR_COUNT 1

//===================PARAMETERS==========================//

void initDefaultParams(double** pparams, int* pparamscount){
	*pparamscount = PAR_COUNT;
	*pparams = (double *) malloc(sizeof(double)*PAR_COUNT);
	(*pparams)[0] = 1;
}

void releaseParams(double *params){
	free(params);
}

//===================INITIAL CONDITIONS==========================//

void Initial0(double* cellstart, double x, double y, double z){
	cellstart[0] = x;
}

void Block0FillInitialValues(double* result, unsigned short int* initType){
	initfunc_ptr_t initFuncArray[1];
	initFuncArray[0] = Initial0;
	for(int idxX = 0; idxX<Block0CountX; idxX++){
		int idx = idxX;
		int type = initType[idx];
		initFuncArray[type](result+idx*Block0CELLSIZE, Block0OffsetX + idxX*DX, 0, 0);
	}
}

void getInitFuncArray(initfunc_fill_ptr_t** ppInitFuncs){
	initfunc_fill_ptr_t* pInitFuncs;
	pInitFuncs = (initfunc_fill_ptr_t*) malloc( 1 * sizeof(initfunc_fill_ptr_t) );
	*ppInitFuncs = pInitFuncs;
	pInitFuncs[0] = Block0FillInitialValues;
}

void releaseInitFuncArray(initfunc_fill_ptr_t* InitFuncs){
	free(InitFuncs);
}


//=========================CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER 0========================//

//0 central function for 1d model for block with number 0
void Block0CentralFunction0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = params[0] * (DXM2 * (1 * source[0][idx + 1 * Block0StrideX * Block0CELLSIZE + 0] - 2 * source[0][idx + 0 * Block0StrideX * Block0CELLSIZE + 0] + 1 * source[0][idx-1 * Block0StrideX * Block0CELLSIZE + 0]));
}


//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//

//Boundary condition for boundary x = 0
void Block0DefaultNeumann__Bound0__Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = params[0] * (2.0 * DXM2 * (source[0][idx + Block0StrideX * Block0CELLSIZE + 0] - source[0][idx + 0] - (0.0) * DX));
}
//Boundary condition for boundary x = x_max
void Block0DefaultNeumann__Bound1__Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = params[0] * (2.0 * DXM2 * (source[0][idx - Block0StrideX * Block0CELLSIZE + 0] - source[0][idx + 0] + (0.0) * DX));
}

//===================================FILL FUNCTIONS===========================//

void getBlock0BoundFuncArray(func_ptr_t** ppBoundFuncs){
	func_ptr_t* pBoundFuncs = *ppBoundFuncs;
	pBoundFuncs = (func_ptr_t*) malloc( 3 * sizeof(func_ptr_t) );
	*ppBoundFuncs = pBoundFuncs;

	pBoundFuncs[0] = Block0CentralFunction0;
	pBoundFuncs[1] = Block0DefaultNeumann__Bound0__Eqn0;
	pBoundFuncs[2] = Block0DefaultNeumann__Bound1__Eqn0;
}

void getFuncArray(func_ptr_t** ppBoundFuncs, int blockIdx){
	getBlock0BoundFuncArray(ppBoundFuncs);
}

void releaseFuncArray(func_ptr_t* BoundFuncs){
	free(BoundFuncs);
}

