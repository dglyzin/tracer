#include <math.h>
#include <stdlib.h>
#include "../hybriddomain/doc/userfuncs.h"
#include <stdio.h>


$PasteDefine$

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
	$initParams$
}

void releaseParams(double *params){
	free(params);
}


//===================NAChAL''NYE USLOVIJa==========================//
//nachal'nye uslovija - tol'ko na CPU


//dlja kazhdogo bloka svoj nabor tochechnyh nachal'nyh funkcij i odna funkcija-zapolnitel'
$Block0Initial$


//Zapolnjaet result[idx] nachal'noj funkciej s nomerom iz initType[idx]
//izmenilsja kod
void Block0FillInitialValues(double* result, unsigned short int* initType){
	printf("Initial array filling by user function started...\n");
    initfunc_ptr_t initFuncArray[1];
    $Block0InitialFill$
    for(int idxY = 0; idxY<Block0CountY; idxY++)
        for(int idxX = 0; idxX<Block0CountX; idxX++){
            int idx = (idxY*Block0CountX + idxX)*CELLSIZE;
            int type = initType[idx];
            $Block0InitFuncArray$
        }
}


//Funkcii-zapolniteli nuzhno sobrat' v massiv i otdat' domenu
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

//===================GRANIChNYE USLOVIJa I OSNOVNAJa FUNKCIJa==========================//
//funkcii tipa dirihle dlja vseh granic vseh blokov mozhno delat' odni i te zhe ,
//a odin i tot zhe Nejman na raznyh granicah raznyh blokov budet otdel'noj funkciej, t.k. pridumyvaet 
//nesushhestvujushhuju tochku v svoem napravlenii i s raznymi stride

$BlockReplace$


void releaseFuncArray(func_ptr_t* Funcs){
    free(Funcs);    
}

