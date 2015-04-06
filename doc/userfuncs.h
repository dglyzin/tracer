/*
 * userfuncs.h
 *
 *  Created on: Apr 6, 2015
 *      Author: dglyzin
 */

#ifndef USERFUNCS_H_
#define USERFUNCS_H_

typedef void (*initfunc_ptr_t)( double* result, int idxX, int idxY, int idxZ);
typedef void (*initfunc_fill_ptr_t)( double* result, unsigned short int* initType);

typedef void (*func_ptr_t)(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic);

void Block0FillInitialValues(double* result, int* initType);
void getInitFuncArray(initfunc_fill_ptr_t** ppInitFuncs);
void releaseInitFuncArray(initfunc_fill_ptr_t* InitFuncs);

void getFuncArray(func_ptr_t** ppFuncs);
void releaseFuncArray(func_ptr_t* Funcs);

void initDefaultParams(double **pparams, int* pparamscount);
void releaseParams(double *params);



#endif /* USERFUNCS_H_ */
