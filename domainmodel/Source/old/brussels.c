//03.04.11 dgl created
//.....
#include <omp.h>
#include "brussels.h"
#include "../../../../../c-core/src/core/coreintegr.h"
#include "../../../../../c-core/src/core/rk4.h"
#include "../../../../../c-core/src/core/rk_iterated.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

//#define N 500
//#define N 200
#define ALPH 2.e-3


static int brussels_func(double time, double* s, double*p, 
                         double* r, int firstn, int lastn, int dim){  
#define K1 4.4
#define K2 3.4

  int i,j,idx;
  int N = sqrt(dim/2);
  //first row
  i = 0;
  j = 0;
  idx = 2*i*N+2*j;
  r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
  r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
  for (j=1; j<N-1; j++){
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }
  j = N-1;
  idx = 2*i*N+2*j;
  r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
  r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  //rows 1..N-2
  for (i=1; i<N-1; i++){
    j = 0;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
    for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }
    j = N-1;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }

  //last row
  i = N-1;
  j = 0;
  idx = 2*i*N+2*j;
  r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
  r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
  for (j=1; j<N-1; j++){
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }
  j = N-1;
  idx = 2*i*N+2*j;
  r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
  r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  return C_SUCCESS;
}


//This function is 4-thread only!
static int brussels_func_omp4(double time, double* s, double*p, 
                         double* r, int firstn, int lastn, int dim){  
#define K1 4.4
#define K2 3.4

  int i,j,idx;
  int N = sqrt(dim/2);

  if (firstn==0){
  //first row
  i = 0;
  j = 0;
  idx = 2*i*N+2*j;
  r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
  r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
  for (j=1; j<N-1; j++){
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }
  j = N-1;
  idx = 2*i*N+2*j;
  r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
  r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);

  for (i=1; i<N/4; i++){
    j = 0;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
    for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }
    j = N-1;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }
  } 
  
  if (firstn == N*N*2*1/4){    
  for (i=N/4; i<N/2; i++){
    j = 0;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
    for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }
    j = N-1;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }

  } 

  if (firstn == N*N*2*2/4){
  for (i=N/2; i<3*N/4; i++){
    j = 0;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
    for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }
    j = N-1;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }
  }
  
  if (firstn == N*N*2*3/4){
  for (i=3*N/4; i<N-1; i++){
    j = 0;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
    for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }
    j = N-1;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }
  //last row
  i = N-1;
  j = 0;
  idx = 2*i*N+2*j;
  r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
  r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
  for (j=1; j<N-1; j++){
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }
  j = N-1;
  idx = 2*i*N+2*j;
  r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
  r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }
  return C_SUCCESS;
}
/*
static int brussels_func_omp4_easy(double time, double* s, double*p, 
                         double* r, int firstn, int lastn, int dim){  
#define K1 4.4
#define K2 3.4
  int N = sqrt(dim/2);
  int i,j,idx;
  //first row
  if((firstn==0)||(lastn==1)){
    i = 0;
    j = 0;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
    for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }
    j = N-1;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    for (i=1; i<N/4; i++){
    j = 0;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
    for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }
    j = N-1;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }
  } 
  //rows 1..N-2
  if((firstn==1)||(lastn==1))
    for (i=N/4; i<N/2; i++){
    j = 0;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
    for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }
    j = N-1;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }

  if((firstn==2)||(lastn==1))
    for (i=N/2; i<3*N/4; i++){
      j = 0;
      idx = 2*i*N+2*j;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
      for (j=1; j<N-1; j++){
        idx = 2*i*N+2*j;
        r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
        r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
      }
      j = N-1;
      idx = 2*i*N+2*j;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }


  if((firstn==3)||(lastn==1)){
    for (i=3*N/4; i<N-1; i++){
    j = 0;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
    for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }
    j = N-1;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }
    i = N-1;
    j = 0;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
    for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }
    j = N-1;
    idx = 2*i*N+2*j;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }
  return C_SUCCESS;
}
*/

static int stupid_func(double time, double* s, double*p, 
                         double* r, int firstn, int lastn, int dim){  
#define K1 4.4
#define K2 3.4

  int i;
  for (i=firstn; i<lastn; ++i)
   r[i] = (double)i/dim+sin(sin((double) i/dim))+cos(cos((double)i/dim));

  return C_SUCCESS;
}

/*
static int brussels_func_omp(double time, double* s, double*p, 
                         double* r, int firstn, int lastn, int dim){  
#define K1 4.4
#define K2 3.4

  int i,j,idx;
  int N = sqrt(dim/2);
  //first row
  i = 0;
  j = 0;
  idx = 2*i*N+2*j; 
  if (idx<firstn) goto l1;
  r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
  r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);

l1:
  for (j=1; j<N-1; j++){
    idx = 2*i*N+2*j;
    if (idx<firstn) continue;
    if (idx>lastn) return C_SUCCESS;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }
  j = N-1;
  idx = 2*i*N+2*j;
  if (idx<firstn) goto l2;
  if (idx>lastn) return C_SUCCESS;
  r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
  r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  //rows 1..N-2
l2:
  for (i=1; i<N-1; i++){
    j = 0;
    idx = 2*i*N+2*j;
    if (idx<firstn) goto l3;
    if (idx>lastn) return C_SUCCESS;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
l3:
    for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
      if (idx<firstn) continue;
      if (idx>lastn) return C_SUCCESS;
      r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
      r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
    }
    j = N-1;
    idx = 2*i*N+2*j;
    if (idx<firstn) continue;
    if (idx>lastn) return C_SUCCESS;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }

  //last row
  i = N-1;
  j = 0;
  idx = 2*i*N+2*j;
  if (idx<firstn) goto l4;
  if (idx>lastn) return C_SUCCESS;
  r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]+s[idx+2]+s[idx+2]- 4.0* s[idx]);
  r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx+2+1]- 4.0* s[idx+1]);
l4:
  for (j=1; j<N-1; j++){
    idx = 2*i*N+2*j;
    if (idx<firstn) continue;
    if (idx>lastn) return C_SUCCESS;
    r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]+s[idx+2]+s[idx-2]- 4.0* s[idx]);
    r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]+s[idx+2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  }
  j = N-1;
  idx = 2*i*N+2*j;
  if (idx>lastn) return C_SUCCESS;
  r[idx] = 1 + s[idx]*s[idx]*s[idx+1] - K1*s[idx] + ALPH*(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]+s[idx-2]+s[idx-2]- 4.0* s[idx]);
  r[idx+1] = K2*s[idx] - s[idx]*s[idx]*s[idx+1] + ALPH*(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]+s[idx-2+1]+s[idx-2+1]- 4.0* s[idx+1]);
  return C_SUCCESS;
}*/

static int fill_initbruss(double*xinit, int xdim){
  int i,j;
  double dx = 1.0/(double)(xdim-1);
  for(i=0;i<xdim;i++)
    for(j=0;j<xdim;j++)
    {
      int idx = 2*i*xdim+2*j;
      xinit[idx]=0.5+dx*j;
      xinit[idx+1]=1.0+5.0*dx*i;
    }
  return C_SUCCESS;
}

static int bruss_savetofile(double*state, int xdim, char* fname){
  FILE* stream;
  double dx = 1.0/(double)(xdim-1);
  int i,j;
  stream = fopen(fname, "w");
  for(i=0;i<xdim;i++){
    for (j=0;j<xdim;j++)
      fprintf(stream, "%6.12f %6.12f %6.20f %6.20f\n", i*dx, j*dx, state[2*(i*xdim+j)], state[2*(i*xdim+j)+1]);    
    fprintf(stream, "\n");  
  }
  fclose(stream);
  return C_SUCCESS;
}



static int solver(){
  
  int dimension;
  TOdeSys sys;
  TMethodData data;
  double* xinit;
  double step;
  double time=0.0;
  double params[MAX_PARAMS_NUM];
  double t1,t2, timedp5, timerk4;
  int N = 200;
  double TMAX=0.1;
  dimension = N*N*2;
  
  step = 0.001;
  params[0] = 10.0;

  xinit = (double*)malloc(sizeof(double)*dimension);
  //warmup
  MethodDataInit(&data,dimension,IM_RK4,step,0,0);
  OdeSysInit(&sys,dimension,brussels_func,xinit,time,params);
  RungeKutta4(&sys, &data);
  OdeSysFree(&sys);
  MethodDataFree(&data);

  //RK 1 thread
  fill_initbruss(xinit, N);
  MethodDataInit(&data,dimension,IM_RK4,step,0,0);
  OdeSysInit(&sys,dimension,brussels_func,xinit,time,params);
  t1 = omp_get_wtime();
  while (sys.time<TMAX)  
    RungeKutta4(&sys, &data);     
  t2 = omp_get_wtime(); 
  timerk4 = t2-t1;
  printf("Steps accepted: %d, rej: %d \n", data.accepted, data.rejected);  
  printf("Time: %f\n", t2-t1);
  bruss_savetofile(sys.state, N, "brussels_rk4_10t.dat");
  OdeSysFree(&sys);
  MethodDataFree(&data);

/*
  //RK 4 thread;
  time=0.0;
  fill_initbruss(xinit, N);
  MethodDataInit(&data,dimension,IM_DOPRI54,step,0,0);
  OdeSysInit(&sys,dimension,brussels_func_omp4,xinit,time,params);  
  t1 = omp_get_wtime();
  while (sys.time<TMAX) 
    RungeKutta4_omp(&sys, &data);      
  t2 = omp_get_wtime();   
  printf("Steps accepted: %d, rej: %d \n", data.accepted, data.rejected);  
  printf("Time: %f\n", t2-t1);
  printf("Speedup of RK4: %f\n", timerk4/(t2-t1));
  bruss_savetofile(sys.state, N, "brussels_dp4_4t.dat");
  OdeSysFree(&sys);
  MethodDataFree(&data);
*/

  
  //Dormand-Prince 1 thread
  time=0.0;
  fill_initbruss(xinit, N);
  MethodDataInit(&data,dimension,IM_DOPRI54,step,0.0001,0.0001);
  OdeSysInit(&sys,dimension,brussels_func,xinit,time,params);
  t1 = omp_get_wtime();
  while (sys.time<TMAX)
  {  DoPri54(&sys, &data);
     printf("Step= %f\n", data.step);
  }
  t2 = omp_get_wtime();
  timedp5 = t2-t1;
  printf("Steps accepted: %d, rej: %d \n", data.accepted, data.rejected);
  printf("Time: %f\n", t2-t1);
  bruss_savetofile(sys.state, N, "brussels_dp5_10t.dat");
  OdeSysFree(&sys);
  MethodDataFree(&data);


  //Owre--Zennaro
  time=0.0;
  fill_initbruss(xinit, N);
  MethodDataInit(&data,dimension,IM_OWZEN54,step,0.0001,0.0001);
  OdeSysInit(&sys,dimension,brussels_func,xinit,time,params);
  t1 = omp_get_wtime();
  while (sys.time<TMAX){
    OwZen54(&sys, &data);
    printf("Step= %f\n", data.step);
  }
  t2 = omp_get_wtime();
  timedp5 = t2-t1;
  printf("Steps accepted: %d, rej: %d \n", data.accepted, data.rejected);
  printf("Time: %f\n", t2-t1);
  bruss_savetofile(sys.state, N, "brussels_oz5_10t.dat");
  OdeSysFree(&sys);
  MethodDataFree(&data);

  //4 threads DOPRI 
  /*time=0.0;
  fill_initbruss(xinit, N);
  MethodDataInit(&data,dimension,IM_DOPRI54,step,0.001,0.001);
  OdeSysInit(&sys,dimension,brussels_func_omp4,xinit,time,params);  
  t1 = omp_get_wtime();
  while (sys.time<TMAX)
    DoPri54_omp(&sys, &data);         
  t2 = omp_get_wtime();  
  printf("Steps accepted: %d, rej: %d \n", data.accepted, data.rejected);  
  printf("Time: %f\n", t2-t1);
  printf("Speedup of DoPri5: %f\n", timedp5/(t2-t1));
  bruss_savetofile(sys.state, N, "brussels_dp5_4t.dat");
  OdeSysFree(&sys);
  MethodDataFree(&data);
  free(xinit);
*/
/*
  //now compute 4 times smaller system
  time=0.0;
  N = N/2;
  dimension = N*N*2;
  t1 = omp_get_wtime();
#pragma omp parallel num_threads(OMP_NUMTHREADS)
  {
  TOdeSys locsys;
  TMethodData locdata;
  double* locxinit = (double*)malloc(sizeof(double)*dimension); 
  MethodDataInit(&locdata,dimension,IM_RK4,step,0,0);
  OdeSysInit(&locsys,dimension,brussels_func,locxinit,time,params);
  while (locsys.time<TMAX)
    RungeKutta4(&locsys, &locdata);
  OdeSysFree(&locsys);
  MethodDataFree(&locdata);
  free(locxinit);
  }
  t2 = omp_get_wtime();  
  printf("Time: %f\n", t2-t1);
*/



  return C_SUCCESS;	
}

/*static int solver_radau(){
  FILE* stream;
  int i, j, dimension,idx;
  TOdeSys sys;
  TMethodData data;
  double* xinit;
  double step, dx;
  double time=0.0;
  double params[MAX_PARAMS_NUM];
  double t1,t2;


  dimension = N*N*2;
  dx = 1.0/(double)(N-1);
  step = 0.001;
  params[0] = 10.0;

  xinit = (double*)malloc(sizeof(double)*dimension);
  //rk4 first
  for(i=0;i<N;i++)
    for(j=0;j<N;j++)
    {
      idx = 2*i*N+2*j;
      xinit[idx]=0.5+dx*j;
      xinit[idx+1]=1.0+5*dx*i;
    }

  MethodDataInit(&data,dimension,IM_RADAUIIA,step,0,0);
  OdeSysInit(&sys,dimension,brussels_func,xinit,time,params);
  t1 = omp_get_wtime();
  while (sys.time<1)  {
    //DoPri54(&sys, &data);
   
    RadauIIA(&sys, &data);    
  }
  printf("EqTime = %f, accepted: %d, rej: %d \n", sys.time, data.accepted, data.rejected);
  // printf("Sys.time=%6.12f \n", sys.time);
  t2 = omp_get_wtime();
  stream = fopen("brussels_radau.dat", "w");
  for(i=0;i<N;i++){
    for (j=0;j<N;j++)
      fprintf(stream, "%6.12f %6.12f %6.20f\n", i*dx, j*dx, sys.state[2*(i*N+j)]);  
      //fprintf(stream, "%6.12f %6.12f %6.20f\n", i*dx, j*dx, sys.state[i*N+j]);  
    fprintf(stream, "\n");  
  }
  fclose(stream);
  printf("Step is %f. \n", data.step);
  printf("Steps done: %d\n", data.accepted);
  printf("Time: %f\n", t2-t1);
  OdeSysFree(&sys);
  MethodDataFree(&data);

  free(xinit);	


  return C_SUCCESS;	
}*/




static int stage1(double* x1, double* xinit, double* x2, int start, int fin, double step)
{
    const double c1 = 0.5;
    int i;
    for (i=start;i<=fin;i++)
        x1[i]=xinit[i]+step*x2[i]*c1;
    return 0;
}
static int stage2(double* x1, double* xinit, double* x2, int start, int fin, double step)
{
    const double c1 = 0.5;
    int i;
    for (i=start;i<=fin;i++)
        x1[i]=xinit[i]+step*x2[i]*c1;
    return 0;
}
static int stage3(double* x1, double* xinit, double* x2, int start, int fin, double step)
{
    const double c1 = 0.5;
    int i;
    for (i=start;i<=fin;i++)
        x1[i]=xinit[i]+step*x2[i];
    return 0;
}
//static int stage4(double* x0, double* x1, double* x2, double* x3, double* x4, int start, int fin, double step)
static int stage4(double* x0, double** x, int start, int fin, double step)
{
    const double c1 = 1.0/6.0;
    const double c2 = 1.0/3.0;
    int i;
    for (i=start;i<=fin;i++)
        x0[i]+=step*(c1*x[1][i]+c2*x[2][i]+c2*x[3][i]+c1*x[4][i]);
    return 0;
}



static int brussloop1p (double* xinit, double* xres, int xdim, double ttime, double step){
  const double a1 = 0.5;
  double x=0;
  int i;
  int dimension = xdim*xdim*2;
  double ** storage;
  double params[10];
  double time=0;
  
  int start = 0;
  int fin = dimension-1;

  storage = (double**) malloc(8*sizeof(double*));

  for (i=0; i<8; i++)
    
    storage[i] = (double*) malloc(dimension*sizeof(double));

  
  while (time<ttime)  {
    //brussels_func(time,xinit,params,storage[1],start,fin,dimension);
    //for (i=start;i<=fin;i++)
    //    storage[2][i]=xinit[i]+step*storage[1][i];
      for (i=start;i<=fin;i++)
        storage[2][i]=storage[2][i]+step*storage[2][i];
/*
    brussels_func(time,storage[1],params,storage[2],start,fin,dimension);
    brussels_func(time,storage[2],params,storage[3],start,fin,dimension);
    brussels_func(time,storage[3],params,storage[4],start,fin,dimension);
    brussels_func(time,storage[4],params,storage[5],start,fin,dimension);
    brussels_func(time,storage[5],params,storage[6],start,fin,dimension);
    brussels_func(time,storage[6],params,storage[7],start,fin,dimension);
*/
    //stage1(storage[0],xinit,storage[1],start,fin,step);
    //brussels_func(time+a1*step,storage[0],params,storage[2],start,fin,dimension);
    //stage2(storage[4],xinit,storage[2],start,fin,step);
    //brussels_func(time+a1*step,storage[4],params,storage[3],start,fin,dimension);
    //stage3(storage[0],xinit,storage[3],start,fin,step);
    //brussels_func(time+step,storage[0],params,storage[4],start,fin,dimension);
    //stage4(storage[0],storage[1],storage[2],storage[3],storage[4],start,fin,step);
    //stage4(xinit,storage,start,fin,step);
    //x+=xres[0];
    time+=step;
  }
  for (i=0; i<8; i++)
    free(storage[i]);
  free(storage);
  
  xres[0] = xinit[0];
  return C_SUCCESS;
}



static int brussloop4p_outerloop (double* xinit, double* xres, int xdim, double ttime, double step){
   const double a1 = 0.5;
    double* params;
  int dimension = xdim*xdim*2;
  
    
    double time=0;
    double x[4];
    int ii;
    double ** storage;
    storage = (double**) malloc(8*sizeof(double*));
    for (ii=0; ii<8; ii++)
    storage[ii] = (double*) malloc(dimension*sizeof(double));
    x[0] = x[1] =x[2] = x[3] =0;

    while (time<ttime)  {
      #pragma omp parallel num_threads(OMP_NUMTHREADS)
      {
       int i;
       int idx = omp_get_thread_num();
       int start = dimension/OMP_NUMTHREADS*idx;
       int fin = dimension/OMP_NUMTHREADS*(idx+1)-1;
       //int len = dimension/OMP_NUMTHREADS;
       double* locxinit=xinit+start;
       //printf("Hello from %d !!!\n",idx); 
       //brussels_func_omp4(time,xinit,params,storage[1],start,0,dimension);
       for (i=start;i<=fin;i++)
        storage[2+idx][i]=storage[2+idx][i]+step*storage[2+idx][i];
       //for (i=0;i<len;i++)
        //storage[2+idx][start+i]=locxinit[i]+step*storage[2+idx][start+i];
/*
       #pragma omp barrier
       brussels_func_omp4(time,storage[1],params,storage[2],start,fin,dimension);
       #pragma omp barrier
       brussels_func_omp4(time,storage[2],params,storage[3],start,fin,dimension);
       #pragma omp barrier
       brussels_func_omp4(time,storage[3],params,storage[4],start,fin,dimension);
       #pragma omp barrier
       brussels_func_omp4(time,storage[4],params,storage[5],start,fin,dimension);
       #pragma omp barrier
       brussels_func_omp4(time,storage[5],params,storage[6],start,fin,dimension);
       #pragma omp barrier
       brussels_func_omp4(time,storage[6],params,storage[7],start,fin,dimension);
*/


       //stage1(storage[0],xinit,storage[1],start,fin,step);
       //#pragma omp barrier
       //brussels_func_omp4(time+a1*step,storage[0],params,storage[2],start,fin,dimension);
       //stage2(storage[4],xinit,storage[2],start,fin,step);
       //#pragma omp barrier
       //brussels_func_omp4(time+a1*step,storage[4],params,storage[3],start,fin,dimension);
      // stage3(storage[0],xinit,storage[3],start,fin,step);
       //#pragma omp barrier
       //brussels_func_omp4(time+step,storage[0],params,storage[4],start,fin,dimension);
       //stage4(storage[0],storage[1],storage[2],storage[3],storage[4],start,fin,step);
      // stage4(xinit,storage,start,fin,step);
           
       //#pragma omp barrier
       //#pragma omp single
       //  x[idx]+=xres[start];
      }      
      time+=step;
    }
  //bruss_savetofile(xres, xdim, "brussels_1call_4t.dat");
  xres[0] = xinit[0];
  xres[1] = xinit[1];
  xres[2] = xinit[2];
  xres[3] = xinit[3];
  for (ii=0; ii<8; ii++)
    free(storage[ii]);
  free(storage);
  return C_SUCCESS;
}





static int simple_caller(){
  int  dimension;
  TOdeSys sys;
  TMethodData data;
  double* xres, *xinit;
  double step, dx;
  double time=10.0;
  double params[MAX_PARAMS_NUM];
  double reft,t1,t2;
  int N = 200;
  dimension = N*N*2;
  dx = 1.0/(double)(N-1);
  step = 0.001;
  params[0] = 10.0;

  xinit = (double*)malloc(sizeof(double)*dimension);
  xres = (double*)malloc(sizeof(double)*dimension);


  //warmup
  MethodDataInit(&data,dimension,IM_RK4,step,0,0);
  OdeSysInit(&sys,dimension,brussels_func,xinit,time,params);
  RungeKutta4(&sys, &data);
  OdeSysFree(&sys);
  MethodDataFree(&data);


  //1 thread
  fill_initbruss(xinit,N);
  t1 = omp_get_wtime();
  brussloop1p(xinit, xres, N, time, step);
  t2 = omp_get_wtime();
  reft = t2-t1;
  printf("x= %f\n", xres[0]);
  printf("Time: %f\n", t2-t1);
 
//OMP - Re-parallel 
  fill_initbruss(xinit,N);
  t1 = omp_get_wtime();
  brussloop4p_outerloop(xinit, xres, N, time, step);
  t2 = omp_get_wtime();
  printf("x= %f\n", xres[0]);
  printf("Time: %f\n", t2-t1);    
  printf("Speedup of pragma inside loop: %f\n", reft/(t2-t1));

  free(xinit);	
  free(xres);	
  return C_SUCCESS;	
}


int omp_perf()
{
int n, i, iter_n, shift;
double *a, *b, *c;
double time1, time2;

int len= 100000000;
double s =0.001;

a = (double*) malloc(sizeof(double)*len);
b = (double*) malloc(sizeof(double)*len);
c = (double*) malloc(sizeof(double)*len);

for(i=0;i<len;++i){a[i]=3.2;b[i]=1.7;}
time1 = omp_get_wtime();
for (i=0;i<len;++i)
    c[i] = a[i]+s*b[i];
time2 = omp_get_wtime();
omp_set_num_threads(4);
printf("1 thread, c[0]= %f, time = %f.\n", c[0], time2-time1);

for(i=0;i<len;++i){a[i]=3.2;b[i]=1.7;}
time1 = omp_get_wtime();
#pragma omp parallel for
    for (i=0;i<len;++i)
      c[i] = a[i]+s*b[i];
time2 = omp_get_wtime();
printf("4 threads, c[0]= %f, time = %f.\n", c[0], time2-time1);



for(i=0;i<len;++i){a[i]=3.2;b[i]=1.7;}
time1 = omp_get_wtime();
for (i=0;i<len;++i)
    c[i] = a[i]+s*b[i];
time2 = omp_get_wtime();
omp_set_num_threads(4);
printf("1 thread, c[0]= %f, time = %f.\n", c[0], time2-time1);

for(i=0;i<len;++i){a[i]=3.2;b[i]=1.7;}
time1 = omp_get_wtime();
#pragma omp parallel for
    for (i=0;i<len;++i)
      c[i] = a[i]+s*b[i];
time2 = omp_get_wtime();
printf("4 threads, c[0]= %f, time = %f.\n", c[0], time2-time1);


free(c);
free(b);
free(a);


}

int brussels_solver(){
  solver();
  //omp_perf();


  
  //simple_caller();
  //solver_radau();
  return C_SUCCESS;
}
