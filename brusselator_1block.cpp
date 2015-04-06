#include <math.h>
#include <stdlib.h>
#include "doc/userfuncs.h"

#define CELLSIZE 2

#define DX 0.1
#define DY 0.1

#define DXM2 100.0
#define DYM2 100.0

#define DX2 0.01
#define DY2 0.01

#define Block0StrideX 1
#define Block0StrideY 100

#define Block0CountX 100
#define Block0CountY 100

#define Block0OffsetX 0.0
#define Block0OffsetY 0.0

//===================НАЧАЛЬНЫЕ УСЛОВИЯ==========================//
//начальные условия - только на CPU


//для каждого блока свой набор точечных начальных функций и одна функция-заполнитель
void Block0Initial0(double* result, int idxX, int idxY){    
    double x = Block0OffsetX + idxX*DX;
    double y = Block0OffsetY + idxY*DY;
    int idx = (idxY*Block0CountX + idxX)*CELLSIZE;
    result[idx] = 15.0;
    result[idx+1] = sin(x)*cos(y);    
}


//Заполняет result[idx] начальной функцией с номером из initType[idx]
void Block0FillInitialValues(double* result, int* initType){
    initfunc2d_ptr_t initFuncArray[1];
    initFuncArray[0] = Block0Initial0;
    for(int idxY = 0; idxY<Block0CountY; idxY++)
        for(int idxX = 0; idxX<Block0CountX; idxX++){
            int idx = (idxY*Block0CountX + idxX)*CELLSIZE;
            int type = initType[idx];
            initFuncArray[type](result, idxX, idxY);
        }
}


//Функции-заполнители нужно собрать в массив и отдать домену
void getInitFuncArray(initfunc2d_fill_ptr_t** ppInitFuncs){
    initfunc2d_fill_ptr_t* pInitFuncs = *ppInitFuncs;
    pInitFuncs = (initfunc2d_fill_ptr_t*) malloc( 1 * sizeof(initfunc2d_fill_ptr_t) );            
    pInitFuncs[0] = Block0FillInitialValues;   
}

void releaseInitFuncArray(initfunc2d_fill_ptr_t* InitFuncs){
    free(InitFuncs);    
}


//===================ГРАНИЧНЫЕ УСЛОВИЯ И ОСНОВНАЯ ФУНКЦИЯ==========================//
//функции типа дирихле для всех границ всех блоков можно делать одни и те же ,
//а один и тот же Нейман на разных границах разных блоков будет отдельной функцией, т.к. придумывает 
//несуществующую точку в своем направлении и с разными stride

//Основная функция
void Block0CentralFunction(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic){       
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
void Block0DefaultNeumannBound0(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic){
    int idx = ( Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx+Block0StrideX*CELLSIZE] + source[idx+Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx+Block0StrideY*CELLSIZE] + source[idx+Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx+Block0StrideX*CELLSIZE + 1] + source[idx+Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx+Block0StrideY*CELLSIZE + 1] + source[idx+Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//сторона y=0, x центральные
void Block0DefaultNeumannBound1(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic){       
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx+Block0StrideX*CELLSIZE] + source[idx-Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx+Block0StrideY*CELLSIZE] + source[idx+Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx+Block0StrideX*CELLSIZE + 1] + source[idx-Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx+Block0StrideY*CELLSIZE + 1] + source[idx+Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//сторона y=0, x=xmax
void Block0DefaultNeumannBound2(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic){       
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx-Block0StrideX*CELLSIZE] + source[idx-Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx+Block0StrideY*CELLSIZE] + source[idx+Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx-Block0StrideX*CELLSIZE + 1] + source[idx-Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx+Block0StrideY*CELLSIZE + 1] + source[idx+Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//y центральные, x=0
void Block0DefaultNeumannBound3(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic){
    int idx = ( Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx+Block0StrideX*CELLSIZE] + source[idx+Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx+Block0StrideY*CELLSIZE] + source[idx-Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx+Block0StrideX*CELLSIZE + 1] + source[idx+Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx+Block0StrideY*CELLSIZE + 1] + source[idx-Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//y=центральные, x=xmax
void Block0DefaultNeumannBound4(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic){       
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx-Block0StrideX*CELLSIZE] + source[idx-Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx+Block0StrideY*CELLSIZE] + source[idx-Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx-Block0StrideX*CELLSIZE + 1] + source[idx-Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx+Block0StrideY*CELLSIZE + 1] + source[idx-Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//сторона y=ymax, x=0
void Block0DefaultNeumannBound5(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic){
    int idx = ( Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx+Block0StrideX*CELLSIZE] + source[idx+Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx-Block0StrideY*CELLSIZE] + source[idx-Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx+Block0StrideX*CELLSIZE + 1] + source[idx+Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx-Block0StrideY*CELLSIZE + 1] + source[idx-Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//сторона y=ymax, x центральные
void Block0DefaultNeumannBound6(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic){       
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx+Block0StrideX*CELLSIZE] + source[idx-Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx-Block0StrideY*CELLSIZE] + source[idx-Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx+Block0StrideX*CELLSIZE + 1] + source[idx-Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx-Block0StrideY*CELLSIZE + 1] + source[idx-Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}

//сторона y=ymax, x=xmax
void Block0DefaultNeumannBound7(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic){
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE;
    result[idx]  = 1.0 + source[idx]*source[idx]*source[idx+1] - params[1]*source[idx] + params[0] * (
                 + DXM2*(source[idx-Block0StrideX*CELLSIZE] + source[idx-Block0StrideX*CELLSIZE] - 2.0*source[idx])
                 + DYM2*(source[idx-Block0StrideY*CELLSIZE] + source[idx-Block0StrideY*CELLSIZE] - 2.0*source[idx]) );
    result[idx+1] =  params[2] * source[idx] - source[idx] * source[idx] * source[idx+1] + params[0] * (
                  + DXM2*(source[idx-Block0StrideX*CELLSIZE + 1] + source[idx-Block0StrideX*CELLSIZE + 1] - 2.0*source[idx+1])
                  + DYM2*(source[idx-Block0StrideY*CELLSIZE + 1] + source[idx-Block0StrideY*CELLSIZE + 1] - 2.0*source[idx+1]) );
}



void getFuncArray(func2d_ptr_t** ppFuncs){
    func2d_ptr_t* pFuncs = *ppFuncs;
    pFuncs = (func2d_ptr_t*) malloc( ( 1 + 8 + 2 + 1 ) * sizeof(func2d_ptr_t) );        
    
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

void releaseFuncArray(func2d_ptr_t* Funcs){
    free(Funcs);    
}

