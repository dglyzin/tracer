//03.04.11 dgl created
//.....
#include <omp.h>
#include "brus.h"
//#include "../core/coreintegr.h"
//#include "../core/rk4.h"
//#include "../core/rk_iterated.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

//#define N 500
//#define N 200
#define C_SUCCESS 0
#define ALPH 2.e-3


static int brussels_func(double time, double* s, double*p, 
                         double* r, int firstn, int lastn, int dim){  
//#define K1 4.4
//#define K2 3.4
#define k1 1 
#define a 1 
#define k2 1 


  int i,j,idx;
  int N = sqrt(dim/2);
  //first row
  i = 0;
  j = 0;
  idx = 2*i*N+2*j;
  r[idx]=1+(s[idx]*s[idx])*s[idx+1]-k1*s[idx]+a*((N-1)*(N-1)*(s[idx+2]+s[idx+2]- 2*s[idx])+(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]- 2*s[idx]));
  r[idx+1]=k2*s[idx]-(s[idx]*s[idx])*s[idx+1]+a*((N-1)*(N-1)*(s[idx+2+1]+s[idx+2+1]- 2*s[idx+1])+(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]- 2*s[idx+1]));
  for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
  r[idx]=1+(s[idx]*s[idx])*s[idx+1]-k1*s[idx]+a*((N-1)*(N-1)*(s[idx+2]+s[idx-2]- 2*s[idx])+(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]- 2*s[idx]));
  r[idx+1]=k2*s[idx]-(s[idx]*s[idx])*s[idx+1]+a*((N-1)*(N-1)*(s[idx+2+1]+s[idx-2+1]- 2*s[idx+1])+(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]- 2*s[idx+1]));
    }
  j = N-1;
  idx = 2*i*N+2*j;
  r[idx]=1+(s[idx]*s[idx])*s[idx+1]-k1*s[idx]+a*((N-1)*(N-1)*(s[idx+2]+s[idx+2]- 2*s[idx])+(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]- 2*s[idx]));
  r[idx+1]=k2*s[idx]-(s[idx]*s[idx])*s[idx+1]+a*((N-1)*(N-1)*(s[idx+2+1]+s[idx+2+1]- 2*s[idx+1])+(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]- 2*s[idx+1]));
    //rows 1..N-2
  for (i=1; i<N-1; i++){
    j = 0;
    idx = 2*i*N+2*j;
	r[idx]=1+(s[idx]*s[idx])*s[idx+1]-k1*s[idx]+a*((N-1)*(N-1)*(s[idx+2]+s[idx+2]- 2*s[idx])+(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]- 2*s[idx]));
  r[idx+1]=k2*s[idx]-(s[idx]*s[idx])*s[idx+1]+a*((N-1)*(N-1)*(s[idx+2+1]+s[idx+2+1]- 2*s[idx+1])+(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]- 2*s[idx+1]));
    for (j=1; j<N-1; j++){
      idx = 2*i*N+2*j;
	  r[idx]=1+(s[idx]*s[idx])*s[idx+1]-k1*s[idx]+a*((N-1)*(N-1)*(s[idx+2]+s[idx-2]- 2*s[idx])+(N-1)*(N-1)*(s[idx+2*N]+s[idx-2*N]- 2*s[idx]));
  r[idx+1]=k2*s[idx]-(s[idx]*s[idx])*s[idx+1]+a*((N-1)*(N-1)*(s[idx+2+1]+s[idx-2+1]- 2*s[idx+1])+(N-1)*(N-1)*(s[idx+2*N+1]+s[idx-2*N+1]- 2*s[idx+1]));
	}
    j = N-1;
    idx = 2*i*N+2*j;
	r[idx]=1+(s[idx]*s[idx])*s[idx+1]-k1*s[idx]+a*((N-1)*(N-1)*(s[idx+2]+s[idx+2]- 2*s[idx])+(N-1)*(N-1)*(s[idx+2*N]+s[idx+2*N]- 2*s[idx]));
  r[idx+1]=k2*s[idx]-(s[idx]*s[idx])*s[idx+1]+a*((N-1)*(N-1)*(s[idx+2+1]+s[idx+2+1]- 2*s[idx+1])+(N-1)*(N-1)*(s[idx+2*N+1]+s[idx+2*N+1]- 2*s[idx+1]));
  }

  //last row
  i = N-1;
  j = 0;
  idx = 2*i*N+2*j;
  r[idx]=1+(s[idx]*s[idx])*s[idx+1]-k1*s[idx]+a*((N-1)*(N-1)*(s[idx-2]+s[idx+2]- 2*s[idx])+(N-1)*(N-1)*(s[idx-2*N]+s[idx+2*N]- 2*s[idx]));
  r[idx+1]=k2*s[idx]-(s[idx]*s[idx])*s[idx+1]+a*((N-1)*(N-1)*(s[idx-2+1]+s[idx+2+1]- 2*s[idx+1])+(N-1)*(N-1)*(s[idx-2*N+1]+s[idx+2*N+1]- 2*s[idx+1]));
    for (j=1; j<N-1; j++){
	   idx = 2*i*N+2*j;
	   r[idx]=1+(s[idx]*s[idx])*s[idx+1]-k1*s[idx]+a*((N-1)*(N-1)*(s[idx-2]+s[idx-2]- 2*s[idx])+(N-1)*(N-1)*(s[idx-2*N]+s[idx-2*N]- 2*s[idx]));
  r[idx+1]=k2*s[idx]-(s[idx]*s[idx])*s[idx+1]+a*((N-1)*(N-1)*(s[idx-2+1]+s[idx-2+1]- 2*s[idx+1])+(N-1)*(N-1)*(s[idx-2*N+1]+s[idx-2*N+1]- 2*s[idx+1]));
    }
  j = N-1;
  idx = 2*i*N+2*j;
  r[idx]=1+(s[idx]*s[idx])*s[idx+1]-k1*s[idx]+a*((N-1)*(N-1)*(s[idx-2]+s[idx+2]- 2*s[idx])+(N-1)*(N-1)*(s[idx-2*N]+s[idx+2*N]- 2*s[idx]));
  r[idx+1]=k2*s[idx]-(s[idx]*s[idx])*s[idx+1]+a*((N-1)*(N-1)*(s[idx-2+1]+s[idx+2+1]- 2*s[idx+1])+(N-1)*(N-1)*(s[idx-2*N+1]+s[idx+2*N+1]- 2*s[idx+1]));
  return C_SUCCESS;
}

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

int main(void)
{
    printf("Hello world!\n");
    return C_SUCCESS;
}





