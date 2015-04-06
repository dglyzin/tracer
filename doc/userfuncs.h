/*
 * userfuncs.h
 *
 *  Created on: Apr 6, 2015
 *      Author: dglyzin
 */

#ifndef USERFUNCS_H_
#define USERFUNCS_H_

typedef void (*initfunc2d_ptr_t)( double* result, int idxX, int idxY);
typedef void (*initfunc2d_fill_ptr_t)( double* result, int* initType);

typedef void (*func2d_ptr_t)(double* result, double* source, double t, int idxX, int idxY, double* params, double** ic);

void Block0FillInitialValues(double* result, int* initType);
void getInitFuncArray(initfunc2d_fill_ptr_t** ppInitFuncs);
void releaseInitFuncArray(initfunc2d_fill_ptr_t* InitFuncs);

void getFuncArray(func2d_ptr_t** ppFuncs);
void releaseFuncArray(func2d_ptr_t* Funcs);





#endif /* USERFUNCS_H_ */
