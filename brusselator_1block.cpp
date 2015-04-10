#include <math.h>
#include <stdlib.h>
#include "doc/userfuncs.h"
#include <stdio.h>

#define CELLSIZE 2

#define DX 0.1
#define DY 0.1

#define DXM2 100.0
#define DYM2 100.0

#define DX2 0.01
#define DY2 0.01

#define Block0StrideX 1
#define Block0StrideY 10

#define Block0CountX 10
#define Block0CountY 10

#define Block0OffsetX 0.0
#define Block0OffsetY 0.0

#define PAR_COUNT 3

//===================ПАРАМЕТРЫ==================================//
void initDefaultParams(double** pparams, int* pparamscount){
	*pparamscount = PAR_COUNT;
	*pparams = (double *) malloc(sizeof(double)*PAR_COUNT);
	(*pparams)[0] = 0.6;
	(*pparams)[1] = 0.025;
	(*pparams)[2] = 2;
}

void releaseParams(double *params){
	free(params);
}


//===================НАЧАЛЬНЫЕ УСЛОВИЯ==========================//
//начальные условия - только на CPU


//для каждого блока свой набор точечных начальных функций и одна функция-заполнитель
void Block0Initial0(double* result, int idxX, int idxY, int idxZ){
    double x = Block0OffsetX + idxX*DX;
    double y = Block0OffsetY + idxY*DY;
    int idx = (idxY*Block0CountX + idxX)*CELLSIZE;
    result[idx] = x;//15.0;
    result[idx+1] = y;//sin(x)*cos(y);
}


//Заполняет result[idx] начальной функцией с номером из initType[idx]
void Block0FillInitialValues(double* result, unsigned short int* initType){
	printf("Initial array filling by user function started...\n");
    initfunc_ptr_t initFuncArray[1];
    initFuncArray[0] = Block0Initial0;
    for(int idxY = 0; idxY<Block0CountY; idxY++)
        for(int idxX = 0; idxX<Block0CountX; idxX++){
            int idx = (idxY*Block0CountX + idxX)*CELLSIZE;
            int type = initType[idx];
            initFuncArray[0](result, idxX, idxY, 0);
        }
}


//Функции-заполнители нужно собрать в массив и отдать домену
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


//===================ГРАНИЧНЫЕ УСЛОВИЯ И ОСНОВНАЯ ФУНКЦИЯ==========================//
//функции типа дирихле для всех границ всех блоков можно делать одни и те же ,
//а один и тот же Нейман на разных границах разных блоков будет отдельной функцией, т.к. придумывает 
//несуществующую точку в своем направлении и с разными stride

//Основная функция
void Block0CentralFunction(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx+Block0StrideX*CELLSIZE] + source[idx-Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx+Block0StrideY*CELLSIZE] + source[idx-Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx+Block0StrideX*CELLSIZE + 1] + source[idx-Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx+Block0StrideY*CELLSIZE + 1] + source[idx-Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//условия по умолчанию для каждой стороны (4 штук),
//для каждого угла (4 штук)
//Блок0
//y=0, x=0
void Block0DefaultNeumannBound0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
    int idx = ( Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx+Block0StrideX*CELLSIZE] + source[idx+Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx+Block0StrideY*CELLSIZE] + source[idx+Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx+Block0StrideX*CELLSIZE + 1] + source[idx+Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx+Block0StrideY*CELLSIZE + 1] + source[idx+Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//сторона y=0, x центральные
void Block0DefaultNeumannBound1(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx+Block0StrideX*CELLSIZE] + source[idx-Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx+Block0StrideY*CELLSIZE] + source[idx+Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx+Block0StrideX*CELLSIZE + 1] + source[idx-Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx+Block0StrideY*CELLSIZE + 1] + source[idx+Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//сторона y=0, x=xmax
void Block0DefaultNeumannBound2(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx-Block0StrideX*CELLSIZE] + source[idx-Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx+Block0StrideY*CELLSIZE] + source[idx+Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx-Block0StrideX*CELLSIZE + 1] + source[idx-Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx+Block0StrideY*CELLSIZE + 1] + source[idx+Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//y центральные, x=0
void Block0DefaultNeumannBound3(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
    int idx = ( Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx+Block0StrideX*CELLSIZE] + source[idx+Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx+Block0StrideY*CELLSIZE] + source[idx-Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx+Block0StrideX*CELLSIZE + 1] + source[idx+Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx+Block0StrideY*CELLSIZE + 1] + source[idx-Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//y=центральные, x=xmax
void Block0DefaultNeumannBound4(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx-Block0StrideX*CELLSIZE] + source[idx-Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx+Block0StrideY*CELLSIZE] + source[idx-Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx-Block0StrideX*CELLSIZE + 1] + source[idx-Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx+Block0StrideY*CELLSIZE + 1] + source[idx-Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//сторона y=ymax, x=0
void Block0DefaultNeumannBound5(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
    int idx = ( Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx+Block0StrideX*CELLSIZE] + source[idx+Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx-Block0StrideY*CELLSIZE] + source[idx-Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx+Block0StrideX*CELLSIZE + 1] + source[idx+Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx-Block0StrideY*CELLSIZE + 1] + source[idx-Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//сторона y=ymax, x центральные
void Block0DefaultNeumannBound6(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx+Block0StrideX*CELLSIZE] + source[idx-Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx-Block0StrideY*CELLSIZE] + source[idx-Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx+Block0StrideX*CELLSIZE + 1] + source[idx-Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx-Block0StrideY*CELLSIZE + 1] + source[idx-Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//сторона y=ymax, x=xmax
void Block0DefaultNeumannBound7(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx-Block0StrideX*CELLSIZE] + source[idx-Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx-Block0StrideY*CELLSIZE] + source[idx-Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx-Block0StrideX*CELLSIZE + 1] + source[idx-Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx-Block0StrideY*CELLSIZE + 1] + source[idx-Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}



void getFuncArray(func_ptr_t** ppFuncs){
	printf("Welcome into userfuncs.so. Getting main functions...\n");
    func_ptr_t* pFuncs;
    pFuncs = (func_ptr_t*) malloc( ( 1 + 8 ) * sizeof(func_ptr_t) );
    *ppFuncs = pFuncs;
    pFuncs[0] = Block0CentralFunction;
    
    pFuncs[1] = Block0DefaultNeumannBound0;
    pFuncs[2] = Block0DefaultNeumannBound1;
    pFuncs[3] = Block0DefaultNeumannBound2;
    pFuncs[4] = Block0DefaultNeumannBound3;
    pFuncs[5] = Block0DefaultNeumannBound4;
    pFuncs[6] = Block0DefaultNeumannBound5;
    pFuncs[7] = Block0DefaultNeumannBound6;
    pFuncs[8] = Block0DefaultNeumannBound7;
}

void releaseFuncArray(func_ptr_t* Funcs){
    free(Funcs);    
}

