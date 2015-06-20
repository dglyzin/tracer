#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "../hybriddomain/doc/userfuncs.h"

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

void DirichletInitial0(double* cellstart, double x, double y, double z){
	cellstart[0] = 0.0;
}

void DirichletInitial1(double* cellstart, double x, double y, double z){
	cellstart[0] = 100.0;
}

void DirichletInitial2(double* cellstart, double x, double y, double z){
	cellstart[0] = 100.0;
}

void DirichletInitial3(double* cellstart, double x, double y, double z){
	cellstart[0] = 100.0;
}

void Block0FillInitialValues(double* result, unsigned short int* initType){
	initfunc_ptr_t initFuncArray[3];
	initFuncArray[0] = Initial0;
	initFuncArray[1] = DirichletInitial0;
	initFuncArray[2] = DirichletInitial1;
	for(int idxY = 0; idxY<Block0CountY; idxY++)
		for(int idxX = 0; idxX<Block0CountX; idxX++){
			int idx = (idxY*Block0CountX + idxX)*Block0CELLSIZE;
			int type = initType[idx];
			initFuncArray[type](result+idx, Block0OffsetX + idxX*DX, Block0OffsetY + idxY*DY, 0);}
}

void getInitFuncArray(initfunc_fill_ptr_t** ppInitFuncs){
	printf("Welcome into userfuncs.so. Getting initial functions...\n");
	initfunc_fill_ptr_t* pInitFuncs;
	pInitFuncs = (initfunc_fill_ptr_t*) malloc( 1 * sizeof(initfunc_fill_ptr_t) );
	*ppInitFuncs = pInitFuncs;
	pInitFuncs[0] = Block0FillInitialValues;
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


//=========================DEFAULT BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0========================//

//Default boundary condition for boundary x = 0
void Block0DefaultNeumannBound0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = (2.0 * DXM2 * (source[idx + Block0StrideX * Block0CELLSIZE + 0] - source[idx + 0] - (0.0) * DX)) + (DYM2 * (1 * source[idx + 1 * Block0StrideY * Block0CELLSIZE + 0] - 2 * source[idx + 0 * Block0StrideY * Block0CELLSIZE + 0] + 1 * source[idx-1 * Block0StrideY * Block0CELLSIZE + 0]));
}
//Default boundary condition for boundary x = x_max
void Block0DefaultNeumannBound1(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = (2.0 * DXM2 * (source[idx - Block0StrideX * Block0CELLSIZE + 0] - source[idx + 0] + (0.0) * DX)) + (DYM2 * (1 * source[idx + 1 * Block0StrideY * Block0CELLSIZE + 0] - 2 * source[idx + 0 * Block0StrideY * Block0CELLSIZE + 0] + 1 * source[idx-1 * Block0StrideY * Block0CELLSIZE + 0]));
}
//Default boundary condition for boundary y = 0
void Block0DefaultNeumannBound2(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = (DXM2 * (1 * source[idx + 1 * Block0StrideX * Block0CELLSIZE + 0] - 2 * source[idx + 0 * Block0StrideX * Block0CELLSIZE + 0] + 1 * source[idx-1 * Block0StrideX * Block0CELLSIZE + 0])) + (2.0 * DYM2 * (source[idx + Block0StrideY * Block0CELLSIZE + 0] - source[idx + 0] - (0.0) * DY));
}
//Default boundary condition for boundary y = y_max
void Block0DefaultNeumannBound3(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = (DXM2 * (1 * source[idx + 1 * Block0StrideX * Block0CELLSIZE + 0] - 2 * source[idx + 0 * Block0StrideX * Block0CELLSIZE + 0] + 1 * source[idx-1 * Block0StrideX * Block0CELLSIZE + 0])) + (2.0 * DYM2 * (source[idx - Block0StrideY * Block0CELLSIZE + 0] - source[idx + 0] + (0.0) * DY));
}

//=============================OTHER BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//

//Non-default boundary condition for boundary y = 0
void Block0DirichletBound2_0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Non-default boundary condition for boundary y = y_max
void Block0DirichletBound3_0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Non-default boundary condition for boundary y = y_max
void Block0DirichletBound3_1(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Non-default boundary condition for boundary x = 0
void Block0DirichletBound0_0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Non-default boundary condition for boundary x = 0
void Block0DirichletBound0_1(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Non-default boundary condition for boundary x = x_max
void Block0DirichletBound1_0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Non-default boundary condition for boundary x = x_max
void Block0DirichletBound1_1(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Non-default boundary condition for Vertex between boundaries x = 0 and y = 0
void Block0DirichletBoundForVertex0_2(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Non-default boundary condition for Vertex between boundaries x = x_max and y = 0
void Block0DirichletBoundForVertex1_2(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Non-default boundary condition for Vertex between boundaries x = 0 and y = y_max
void Block0DirichletBoundForVertex0_3(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}
//Non-default boundary condition for Vertex between boundaries x = x_max and y = y_max
void Block0DirichletBoundForVertex1_3(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.0;
}

//===================================FILL FUNCTIONS===========================//

void getBlock0BoundFuncArray(func_ptr_t** ppBoundFuncs){
	func_ptr_t* pBoundFuncs = *ppBoundFuncs;
	pBoundFuncs = (func_ptr_t*) malloc( 16 * sizeof(func_ptr_t) );
	*ppBoundFuncs = pBoundFuncs;

	pBoundFuncs[0] = Block0CentralFunction;
	pBoundFuncs[1] = Block0DirichletBoundForVertex0_2;
	pBoundFuncs[2] = Block0DirichletBoundForVertex1_2;
	pBoundFuncs[3] = Block0DirichletBoundForVertex0_3;
	pBoundFuncs[4] = Block0DirichletBoundForVertex1_3;
	pBoundFuncs[5] = Block0DefaultNeumannBound2;
	pBoundFuncs[6] = Block0DirichletBound2_0;
	pBoundFuncs[7] = Block0DefaultNeumannBound3;
	pBoundFuncs[8] = Block0DirichletBound3_0;
	pBoundFuncs[9] = Block0DirichletBound3_1;
	pBoundFuncs[10] = Block0DefaultNeumannBound0;
	pBoundFuncs[11] = Block0DirichletBound0_0;
	pBoundFuncs[12] = Block0DirichletBound0_1;
	pBoundFuncs[13] = Block0DefaultNeumannBound1;
	pBoundFuncs[14] = Block0DirichletBound1_0;
	pBoundFuncs[15] = Block0DirichletBound1_1;
}

void getFuncArray(func_ptr_t** ppBoundFuncs, int blockIdx){
	getBlock0BoundFuncArray(ppBoundFuncs);
}

void releaseBoundFuncArray(func_ptr_t* BoundFuncs){
	free(BoundFuncs);
}

