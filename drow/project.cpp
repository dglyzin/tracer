#include <math.h>
#include <stdlib.h>
#include "../hybriddomain/doc/userfuncs.h"
#include <stdio.h>


#define DX 0.01
 #define DY 0.01
 #define DZ 1
 #define DX2 0.0001
 #define DY2 0.0001
 #define DZ2 1
 #define DXM 100.0
 #define DYM 100.0
 #define DZM 1
 #define DXM2 10000.0
 #define DYM2 10000.0
 #define DZM2 1
 #define DXYM2 10000.0
 #define DXZM 100.0
 #define DYZM 100.0
 #define DXM3 1000000.0
 #define DYM3 1000000.0
 #define DZM3 1
 #define Block0StrideX 1 
 #define Block0StrideY 100 
 #define Block0StrideZ 20000
 #define Block0CountX 100 
 #define Block0CountY 200 
 #define Block0CountZ 1
 #define CELLSIZE 1

#define Block0OffsetX 0.0
#define Block0OffsetY 0.0

//=====================
#define dx1 0.1
#define dy1 0.1
#define dz1 0.1

#define dx2 0.01
#define dy2 0.01
#define dz2 0.01

#define dx1dy1 0.01
#define dx1dz1 0.01
#define dy1dz1 0.01

#define dx3 0.001
#define dy3 0.001
#define dz3 0.001

#define dx2dy1 0.001
#define dx2dz1 0.001
#define dx1dy2 0.001
#define dx1dz2 0.001
#define dy1dz2 0.001
#define dy2dz1 0.001
#define dx1dy1dz1 0.001

#define PAR_COUNT 3

//===================PARAMETRY==================================//
void initDefaultParams(double** pparams, int* pparamscount){
	*pparamscount = PAR_COUNT;
	*pparams = (double *) malloc(sizeof(double)*PAR_COUNT);
	(*pparams)[0] = 0.65;
(*pparams)[1] = 0.025;
(*pparams)[2] = 2;

}

void releaseParams(double *params){
	free(params);
}


//===================NAChAL''NYE USLOVIJa==========================//
//nachal'nye uslovija - tol'ko na CPU


//dlja kazhdogo bloka svoj nabor tochechnyh nachal'nyh funkcij i odna funkcija-zapolnitel'
void BlockAllInitial0(double* result, int idxX, int idxY, int idxZ){ 
    double x = Block0OffsetX + idxX*DX; 
    double y = Block0OffsetY + idxY*DY; 
    int idx = (idxY*Block0CountX + idxX)*CELLSIZE; 
    result[idx+0] = 0.0;
 
}
void Block0InitialDirihle0(double* result, int idxX, int idxY, int idxZ){ 
    double x = Block0OffsetX + idxX*DX; 
    double y = Block0OffsetY + idxY*DY; 
    int idx = (idxY*Block0CountX + idxX)*CELLSIZE; 
    result[idx+0] = 100.0;
 
}void Block0InitialDirihle1(double* result, int idxX, int idxY, int idxZ){ 
    double x = Block0OffsetX + idxX*DX; 
    double y = Block0OffsetY + idxY*DY; 
    int idx = (idxY*Block0CountX + idxX)*CELLSIZE; 
    result[idx+0] = 100.0;
 
}void Block0InitialDirihle2(double* result, int idxX, int idxY, int idxZ){ 
    double x = Block0OffsetX + idxX*DX; 
    double y = Block0OffsetY + idxY*DY; 
    int idx = (idxY*Block0CountX + idxX)*CELLSIZE; 
    result[idx+0] = -10.0;
 
}void Block0InitialDirihle3(double* result, int idxX, int idxY, int idxZ){ 
    double x = Block0OffsetX + idxX*DX; 
    double y = Block0OffsetY + idxY*DY; 
    int idx = (idxY*Block0CountX + idxX)*CELLSIZE; 
    result[idx+0] = -10.0;
 
}

//Zapolnjaet result[idx] nachal'noj funkciej s nomerom iz initType[idx]
//izmenilsja kod


void Block0FillInitialValues(double* result, unsigned short int* initType){
 printf("Initial array filling by user function started...\n ");
 initfunc_ptr_t initFuncArray[5];
 initFuncArray[0] = BlockAllInitial0;
initFuncArray[1] = Block0InitialDirihle0;
initFuncArray[2] = Block0InitialDirihle1;
initFuncArray[3] = Block0InitialDirihle2;
initFuncArray[4] = Block0InitialDirihle3;
 
 for(int idxY = 0; idxY<Block0CountY; idxY++)
    for(int idxX = 0; idxX<Block0CountX; idxX++){
       int idx = (idxY*Block0CountX + idxX);
       int type = initType[idx];
       initFuncArray[type](result, idxX, idxY, 0);
       }
 }


//Funkcii-zapolniteli nuzhno sobrat' v massiv i otdat' domenu
void getInitFuncArray(initfunc_fill_ptr_t** ppInitFuncs){
	printf("Welcome into userfuncs.so. Getting initial functions...\n");

    initfunc_fill_ptr_t* pInitFuncs;
    pInitFuncs = (initfunc_fill_ptr_t*) malloc( 1 * sizeof(initfunc_fill_ptr_t) );
    *ppInitFuncs = pInitFuncs;
	pInitFuncs[0] = Block0FillInitialValues;
    //pInitFuncs[0] = Block0FillInitialValues;   
}

void releaseInitFuncArray(initfunc_fill_ptr_t* InitFuncs){
    free(InitFuncs);    
}

//===================GRANIChNYE USLOVIJa I OSNOVNAJa FUNKCIJa==========================//
//funkcii tipa dirihle dlja vseh granic vseh blokov mozhno delat' odni i te zhe ,
//a odin i tot zhe Nejman na raznyh granicah raznyh blokov budet otdel'noj funkciej, t.k. pridumyvaet 
//nesushhestvujushhuju tochku v svoem napravlenii i s raznymi stride

//osnova 
 void Block0CentralFunction(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
     int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
     result[idx]=DXM2*(source[idx+Block0StrideX*CELLSIZE]+source[idx-Block0StrideX*CELLSIZE]- 2*source[idx])+DYM2*(source[idx+Block0StrideY*CELLSIZE]+source[idx-Block0StrideY*CELLSIZE]- 2*source[idx]);
   
 } 
 //y=0, x=0 
 void Block0DefaultNeumannBound0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
     int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
     result[idx]=DXM2*(source[idx+Block0StrideX*CELLSIZE]+source[idx+Block0StrideX*CELLSIZE]- 2*source[idx])+DYM2*(source[idx+Block0StrideY*CELLSIZE]+source[idx+Block0StrideY*CELLSIZE]- 2*source[idx]);
   
 } 
 //y=0, x centr 
 void Block0DefaultNeumannBound1(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
     int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
     result[idx]=DXM2*(source[idx+Block0StrideX*CELLSIZE]+source[idx-Block0StrideX*CELLSIZE]- 2*source[idx])+DYM2*(source[idx+Block0StrideY*CELLSIZE]+source[idx+Block0StrideY*CELLSIZE]- 2*source[idx]);
   
 } 
 //y=0, x=xmax 
 void Block0DefaultNeumannBound2(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
     int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
     result[idx]=DXM2*(source[idx-Block0StrideX*CELLSIZE]+source[idx-Block0StrideX*CELLSIZE]- 2*source[idx])+DYM2*(source[idx+Block0StrideY*CELLSIZE]+source[idx+Block0StrideY*CELLSIZE]- 2*source[idx]);
   
 }  
 //y centr, x=0 
 void Block0DefaultNeumannBound3(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
     int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
     result[idx]=DXM2*(source[idx+Block0StrideX*CELLSIZE]+source[idx+Block0StrideX*CELLSIZE]- 2*source[idx])+DYM2*(source[idx+Block0StrideY*CELLSIZE]+source[idx-Block0StrideY*CELLSIZE]- 2*source[idx]);
   
 } 
 //y centr, x=xmax 
 void Block0DefaultNeumannBound4(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
     int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
     result[idx]=DXM2*(source[idx-Block0StrideX*CELLSIZE]+source[idx-Block0StrideX*CELLSIZE]- 2*source[idx])+DYM2*(source[idx+Block0StrideY*CELLSIZE]+source[idx-Block0StrideY*CELLSIZE]- 2*source[idx]);
   
 } 
 //y=ymax, x=0 
 void Block0DefaultNeumannBound5(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
     int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
     result[idx]=DXM2*(source[idx+Block0StrideX*CELLSIZE]+source[idx+Block0StrideX*CELLSIZE]- 2*source[idx])+DYM2*(source[idx-Block0StrideY*CELLSIZE]+source[idx-Block0StrideY*CELLSIZE]- 2*source[idx]);
   
 } 
 //y=ymax, x centr 
 void Block0DefaultNeumannBound6(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
     int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
     result[idx]=DXM2*(source[idx+Block0StrideX*CELLSIZE]+source[idx-Block0StrideX*CELLSIZE]- 2*source[idx])+DYM2*(source[idx-Block0StrideY*CELLSIZE]+source[idx-Block0StrideY*CELLSIZE]- 2*source[idx]);
   
 } 
 //y=ymax, x=xmax 
 void Block0DefaultNeumannBound7(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
     int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
     result[idx]=DXM2*(source[idx-Block0StrideX*CELLSIZE]+source[idx-Block0StrideX*CELLSIZE]- 2*source[idx])+DYM2*(source[idx-Block0StrideY*CELLSIZE]+source[idx-Block0StrideY*CELLSIZE]- 2*source[idx]);
   
 } 
 
  
 
 void Block0Bound1_0(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
    result[idx+0] = 0;
 
}void Block0Bound1_1(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
    result[idx+0] = 0;
 
}void Block0Bound1_2(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
    result[idx+0] = 0;
 
}void Block0Bound1_3(double* result, double* source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){ 
    int idx = ( idxY * Block0StrideY + idxX) * CELLSIZE; 
    result[idx+0] = 0;
 
} 
 void getFuncArray(func_ptr_t** ppFuncs){ 
 printf("Welcome into userfuncs.so. Getting main functions...\n "); 
  func_ptr_t* pFuncs; 
  pFuncs = (func_ptr_t*) malloc( ( 1 + 8 +4 ) * sizeof(func_ptr_t) ); 
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
 pFuncs[9] = Block0Bound1_0;
pFuncs[10] = Block0Bound1_1;
pFuncs[11] = Block0Bound1_2;
pFuncs[12] = Block0Bound1_3;
  }


void releaseFuncArray(func_ptr_t* Funcs){
    free(Funcs);    
}

