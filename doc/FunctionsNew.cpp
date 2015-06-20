#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "userfuncs.h"

#define DX 0.01
#define DX2 0.0001
#define DXM1 100.0
#define DXM2 10000.0
#define DY 0.01
#define DY2 0.0001
#define DYM1 100.0
#define DYM2 10000.0
#define DZ 1
#define DZ2 1
#define DZM1 1.0
#define DZM2 1.0

#define Block0CELLSIZE 1

#define Block0StrideX 1
#define Block0CountX 100
#define Block0OffsetX 0.0
#define Block0StrideY 100
#define Block0CountY 200
#define Block0OffsetY 0.0
#define Block0StrideZ 20000
#define Block0CountZ 0
#define Block0OffsetZ 0

#define Block1CELLSIZE 1

#define Block1StrideX 1
#define Block1CountX 100
#define Block1OffsetX 2.0
#define Block1StrideY 100
#define Block1CountY 200
#define Block1OffsetY 3.0
#define Block1StrideZ 20000
#define Block1CountZ 0
#define Block1OffsetZ 0

#define PAR_COUNT 3

//===================PARAMETERS==========================//

void initDefaultParams(double** pparams, int* pparamscount){
	*pparamscount = PAR_COUNT;
	*pparams = (double *) malloc(sizeof(double)*PAR_COUNT);
	(*pparams)[0] = 0.65;
	(*pparams)[1] = 2;
	(*pparams)[2] = 0.025;
}

void releaseParams(double *params){
	free(params);
}

//===================INITIAL CONDITIONS==========================//

void Initial0(double* cellstart, double x, double y, double z){
	cellstart[0] = 0.0;
}

void Initial1(double* cellstart, double x, double y, double z){
	cellstart[0] = 50.0;
}

void Initial2(double* cellstart, double x, double y, double z){
	cellstart[0] = sin(0.0) + 10.0;
}

void Initial3(double* cellstart, double x, double y, double z){
	cellstart[0] = 0.3 * exp(0.0);
}

void DirichletInitial0(double* cellstart, double x, double y, double z){
	cellstart[0] = -10.0;
}

void DirichletInitial1(double* cellstart, double x, double y, double z){
	cellstart[0] = 100.0;
}

void Block0FillInitialValues(double* result, unsigned short int* initType){
	initfunc_ptr_t initFuncArray[4];
	initFuncArray[0] = Initial3;
	initFuncArray[1] = Initial0;
	initFuncArray[2] = DirichletInitial0;
	initFuncArray[3] = DirichletInitial1;
	for(int idxY = 0; idxY<Block0CountY; idxY++)
		for(int idxX = 0; idxX<Block0CountX; idxX++){
			int idx = (idxY*Block0CountX + idxX)*Block0CELLSIZE;
			int type = initType[idx];
			initFuncArray[type](result+idx, Block0OffsetX + idxX*DX, Block0OffsetY + idxY*DY, 0);}
}

void Block1FillInitialValues(double* result, unsigned short int* initType){
	initfunc_ptr_t initFuncArray[4];
	initFuncArray[0] = Initial1;
	initFuncArray[1] = Initial0;
	initFuncArray[2] = Initial3;
	initFuncArray[3] = DirichletInitial1;
	for(int idxY = 0; idxY<Block1CountY; idxY++)
		for(int idxX = 0; idxX<Block1CountX; idxX++){
			int idx = (idxY*Block1CountX + idxX)*Block1CELLSIZE;
			int type = initType[idx];
			initFuncArray[type](result+idx, Block1OffsetX + idxX*DX, Block1OffsetY + idxY*DY, 0);}
}

void getInitFuncArray(initfunc_fill_ptr_t** ppInitFuncs){
	printf("Welcome into userfuncs.so. Getting initial functions...\n");
	initfunc_fill_ptr_t* pInitFuncs;
	pInitFuncs = (initfunc_fill_ptr_t*) malloc( 2 * sizeof(initfunc_fill_ptr_t) );
	*ppInitFuncs = pInitFuncs;
	pInitFuncs[0] = Block0FillInitialValues;
	pInitFuncs[1] = Block1FillInitialValues;
}

void releaseInitFuncArray(initfunc_fill_ptr_t* InitFuncs){
	free(InitFuncs);
}


//=========================CENTRAL FUNCTION FOR BLOCK WITH NUMBER 0========================//

//Central function for 2d model for block with number 0
void Block0CentralFunction(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = (DXM2 * (1 * source[idx + 1 * Block0StrideX * Block0CELLSIZE + 0] - 2 * source[idx + 0 * Block0StrideX * Block0CELLSIZE + 0] + 1 * source[idx-1 * Block0StrideX * Block0CELLSIZE + 0])) + (DYM2 * (1 * source[idx + 1 * Block0StrideY * Block0CELLSIZE + 0] - 2 * source[idx + 0 * Block0StrideY * Block0CELLSIZE + 0] + 1 * source[idx-1 * Block0StrideY * Block0CELLSIZE + 0]));
}


//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//

//Default boundary condition for boundary y = 0
void Block0DefaultNeumannBound2(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = (DXM2 * (1 * source[idx + 1 * Block0StrideX * Block0CELLSIZE + 0] - 2 * source[idx + 0 * Block0StrideX * Block0CELLSIZE + 0] + 1 * source[idx-1 * Block0StrideX * Block0CELLSIZE + 0])) + (2.0 * DYM2 * (source[idx + Block0StrideY * Block0CELLSIZE + 0] - source[idx + 0] - (0.0) * DY));
}
//Non-default boundary condition for boundary y = 0
void Block0DirichletBound2_0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Default boundary condition for boundary y = y_max
void Block0DefaultNeumannBound3(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = (DXM2 * (1 * source[idx + 1 * Block0StrideX * Block0CELLSIZE + 0] - 2 * source[idx + 0 * Block0StrideX * Block0CELLSIZE + 0] + 1 * source[idx-1 * Block0StrideX * Block0CELLSIZE + 0])) + (2.0 * DYM2 * (source[idx - Block0StrideY * Block0CELLSIZE + 0] - source[idx + 0] + (0.0) * DY));
}
//Default boundary condition for boundary x = 0
void Block0DefaultNeumannBound0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = (2.0 * DXM2 * (source[idx + Block0StrideX * Block0CELLSIZE + 0] - source[idx + 0] - (0.0) * DX)) + (DYM2 * (1 * source[idx + 1 * Block0StrideY * Block0CELLSIZE + 0] - 2 * source[idx + 0 * Block0StrideY * Block0CELLSIZE + 0] + 1 * source[idx-1 * Block0StrideY * Block0CELLSIZE + 0]));
}
//Non-default boundary condition for boundary x = 0
void Block0DirichletBound0_0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Default boundary condition for boundary x = x_max
void Block0DefaultNeumannBound1(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = (2.0 * DXM2 * (source[idx - Block0StrideX * Block0CELLSIZE + 0] - source[idx + 0] + (0.0) * DX)) + (DYM2 * (1 * source[idx + 1 * Block0StrideY * Block0CELLSIZE + 0] - 2 * source[idx + 0 * Block0StrideY * Block0CELLSIZE + 0] + 1 * source[idx-1 * Block0StrideY * Block0CELLSIZE + 0]));
}
//Non-default boundary condition for boundary x = x_max
void Block0DirichletBound1_0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Non-default boundary condition for Vertex between boundaries x = 0 and y = 0
void Block0DirichletBoundForVertex0_2(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Default boundary condition for Vertex between boundaries x = x_max and y = 0
void Block0DefaultNeumannBoundForVertex1_2(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = (2.0 * DXM2 * (source[idx - Block0StrideX * Block0CELLSIZE + 0] - source[idx + 0] + (0.0) * DX)) + (2.0 * DYM2 * (source[idx + Block0StrideY * Block0CELLSIZE + 0] - source[idx + 0] - (0.0) * DY));
}
//Default boundary condition for Vertex between boundaries x = 0 and y = y_max
void Block0DefaultNeumannBoundForVertex0_3(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = (2.0 * DXM2 * (source[idx + Block0StrideX * Block0CELLSIZE + 0] - source[idx + 0] - (0.0) * DX)) + (2.0 * DYM2 * (source[idx - Block0StrideY * Block0CELLSIZE + 0] - source[idx + 0] + (0.0) * DY));
}
//Non-default boundary condition for Vertex between boundaries x = x_max and y = y_max
void Block0DirichletBoundForVertex1_3(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}

//=========================CENTRAL FUNCTION FOR BLOCK WITH NUMBER 1========================//

//Central function for 2d model for block with number 1
void Block1CentralFunction(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = (DXM2 * (1 * source[idx + 1 * Block1StrideX * Block1CELLSIZE + 0] - 2 * source[idx + 0 * Block1StrideX * Block1CELLSIZE + 0] + 1 * source[idx-1 * Block1StrideX * Block1CELLSIZE + 0])) + (DYM2 * (1 * source[idx + 1 * Block1StrideY * Block1CELLSIZE + 0] - 2 * source[idx + 0 * Block1StrideY * Block1CELLSIZE + 0] + 1 * source[idx-1 * Block1StrideY * Block1CELLSIZE + 0]));
}


//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 1======================//

//Default boundary condition for boundary y = 0
void Block1DefaultNeumannBound2(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = (DXM2 * (1 * source[idx + 1 * Block1StrideX * Block1CELLSIZE + 0] - 2 * source[idx + 0 * Block1StrideX * Block1CELLSIZE + 0] + 1 * source[idx-1 * Block1StrideX * Block1CELLSIZE + 0])) + (2.0 * DYM2 * (source[idx + Block1StrideY * Block1CELLSIZE + 0] - source[idx + 0] - (0.0) * DY));
}
//Default boundary condition for boundary y = y_max
void Block1DefaultNeumannBound3(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = (DXM2 * (1 * source[idx + 1 * Block1StrideX * Block1CELLSIZE + 0] - 2 * source[idx + 0 * Block1StrideX * Block1CELLSIZE + 0] + 1 * source[idx-1 * Block1StrideX * Block1CELLSIZE + 0])) + (2.0 * DYM2 * (source[idx - Block1StrideY * Block1CELLSIZE + 0] - source[idx + 0] + (0.0) * DY));
}
//Default boundary condition for boundary x = 0
void Block1DefaultNeumannBound0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = (2.0 * DXM2 * (source[idx + Block1StrideX * Block1CELLSIZE + 0] - source[idx + 0] - (0.0) * DX)) + (DYM2 * (1 * source[idx + 1 * Block1StrideY * Block1CELLSIZE + 0] - 2 * source[idx + 0 * Block1StrideY * Block1CELLSIZE + 0] + 1 * source[idx-1 * Block1StrideY * Block1CELLSIZE + 0]));
}
//Non-default boundary condition for boundary x = 0
void Block1DirichletBound0_0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Default boundary condition for boundary x = x_max
void Block1DefaultNeumannBound1(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = (2.0 * DXM2 * (source[idx - Block1StrideX * Block1CELLSIZE + 0] - source[idx + 0] + (0.0) * DX)) + (DYM2 * (1 * source[idx + 1 * Block1StrideY * Block1CELLSIZE + 0] - 2 * source[idx + 0 * Block1StrideY * Block1CELLSIZE + 0] + 1 * source[idx-1 * Block1StrideY * Block1CELLSIZE + 0]));
}
//Non-default boundary condition for boundary x = x_max
void Block1DirichletBound1_0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Default boundary condition for Vertex between boundaries x = 0 and y = 0
void Block1DefaultNeumannBoundForVertex0_2(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = (2.0 * DXM2 * (source[idx + Block1StrideX * Block1CELLSIZE + 0] - source[idx + 0] - (0.0) * DX)) + (2.0 * DYM2 * (source[idx + Block1StrideY * Block1CELLSIZE + 0] - source[idx + 0] - (0.0) * DY));
}
//Default boundary condition for Vertex between boundaries x = x_max and y = 0
void Block1DefaultNeumannBoundForVertex1_2(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = (2.0 * DXM2 * (source[idx - Block1StrideX * Block1CELLSIZE + 0] - source[idx + 0] + (0.0) * DX)) + (2.0 * DYM2 * (source[idx + Block1StrideY * Block1CELLSIZE + 0] - source[idx + 0] - (0.0) * DY));
}
//Default boundary condition for Vertex between boundaries x = 0 and y = y_max
void Block1DefaultNeumannBoundForVertex0_3(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = (2.0 * DXM2 * (source[idx + Block1StrideX * Block1CELLSIZE + 0] - source[idx + 0] - (0.0) * DX)) + (2.0 * DYM2 * (source[idx - Block1StrideY * Block1CELLSIZE + 0] - source[idx + 0] + (0.0) * DY));
}
//Default boundary condition for Vertex between boundaries x = x_max and y = y_max
void Block1DefaultNeumannBoundForVertex1_3(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = (2.0 * DXM2 * (source[idx - Block1StrideX * Block1CELLSIZE + 0] - source[idx + 0] + (0.0) * DX)) + (2.0 * DYM2 * (source[idx - Block1StrideY * Block1CELLSIZE + 0] - source[idx + 0] + (0.0) * DY));
}
void getBlock0BoundFuncArray(func_ptr_t** ppBoundFuncs){
	func_ptr_t* pBoundFuncs = *ppBoundFuncs;
	pBoundFuncs = (func_ptr_t*) malloc( 12 * sizeof(func_ptr_t) );
	*ppBoundFuncs = pBoundFuncs;

	pBoundFuncs[0] = Block0CentralFunction;
	pBoundFuncs[1] = Block0DirichletBoundForVertex0_2;
	pBoundFuncs[2] = Block0DefaultNeumannBoundForVertex1_2;
	pBoundFuncs[3] = Block0DefaultNeumannBoundForVertex0_3;
	pBoundFuncs[4] = Block0DirichletBoundForVertex1_3;
	pBoundFuncs[5] = Block0DefaultNeumannBound2;
	pBoundFuncs[6] = Block0DirichletBound2_0;
	pBoundFuncs[7] = Block0DefaultNeumannBound3;
	pBoundFuncs[8] = Block0DefaultNeumannBound0;
	pBoundFuncs[9] = Block0DirichletBound0_0;
	pBoundFuncs[10] = Block0DefaultNeumannBound1;
	pBoundFuncs[11] = Block0DirichletBound1_0;
}

void getBlock1BoundFuncArray(func_ptr_t** ppBoundFuncs){
	func_ptr_t* pBoundFuncs = *ppBoundFuncs;
	pBoundFuncs = (func_ptr_t*) malloc( 11 * sizeof(func_ptr_t) );
	*ppBoundFuncs = pBoundFuncs;

	pBoundFuncs[0] = Block1CentralFunction;
	pBoundFuncs[1] = Block1DefaultNeumannBoundForVertex0_2;
	pBoundFuncs[2] = Block1DefaultNeumannBoundForVertex1_2;
	pBoundFuncs[3] = Block1DefaultNeumannBoundForVertex0_3;
	pBoundFuncs[4] = Block1DefaultNeumannBoundForVertex1_3;
	pBoundFuncs[5] = Block1DefaultNeumannBound2;
	pBoundFuncs[6] = Block1DefaultNeumannBound3;
	pBoundFuncs[7] = Block1DefaultNeumannBound0;
	pBoundFuncs[8] = Block1DirichletBound0_0;
	pBoundFuncs[9] = Block1DefaultNeumannBound1;
	pBoundFuncs[10] = Block1DirichletBound1_0;
}

void getFuncArray(func_ptr_t** ppBoundFuncs, int blockIdx){
	if (blockIdx == 0)
		getBlock0BoundFuncArray(ppBoundFuncs);
	if (blockIdx == 0)
		getBlock1BoundFuncArray(ppBoundFuncs);
}

void releaseBoundFuncArray(func_ptr_t* BoundFuncs){
	free(BoundFuncs);
}

