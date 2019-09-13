

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include <cuda.h>
#include <cuda_runtime_api.h>
#include "include/helper_cuda.h"
#include "include/userfuncs.h"



#define DX 0.1
#define DX2 0.01
#define DXM1 10
#define DXM2 100


#define DY 0.1
#define DY2 0.01
#define DYM1 10
#define DYM2 100


#define DZ 1
#define DZ2 1
#define DZM1 1
#define DZM2 1


#define DT 0.0001





#define Block0CELLSIZE 1





#define Block0StrideX 1
#define Block0CountX 81
#define Block0OffsetX 3.0

#define Block0StrideY 81
#define Block0CountY 81
#define Block0OffsetY 3.0

#define Block0StrideZ 6561
#define Block0CountZ 1
#define Block0OffsetZ 0


#define PAR_COUNT 4

//////////////////////////////////
#define COUNT_OF_FUNC 17
#define BLOCK_SIZE 32


// Allocate host side tables to mirror the device side, and later, we
// fill these tables with the function pointers.  This lets us send
// the pointers to the kernel on invocation, as a method of choosing
// which function to run:
func_ptr_t h_funcArray[COUNT_OF_FUNC];


// Declare device side function pointers.  We retrieve them later with
// cudaMemcpyFromSymbol to set our function tables above in some
// particular order specified at runtime:
__device__ func_ptr_t d_funcArray[COUNT_OF_FUNC];




//=========================CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER 0========================//

//0 central function for 2d model for block with number 0
__device__ void Block0CentralFunction_Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;	      
	result[idx + 0] = source[0][idx + 0]+DT*(source[0][idx + 0]+params[0]*((DXM2 * (source[0][idx + 1 * Block0StrideX * Block0CELLSIZE + 0] - 2.0 * source[0][idx + 0 * Block0StrideX * Block0CELLSIZE + 0] + source[0][idx-1 * Block0StrideX * Block0CELLSIZE + 0]))+(DYM2 * (source[0][idx + 1 * Block0StrideY * Block0CELLSIZE + 0] - 2.0 * source[0][idx + 0 * Block0StrideY * Block0CELLSIZE + 0] + source[0][idx-1 * Block0StrideY * Block0CELLSIZE + 0]))));
     
}

//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0CentralFunction_Eqn0 = Block0CentralFunction_Eqn0;




//=========================CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER 0========================//

//2 central function for 2d model for block with number 0
__device__ void Block0CentralFunction_Eqn2(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;	      
	result[idx + 0] = source[0][idx + 0]+DT*(params[2]*((DXM2 * (source[0][idx + 1 * Block0StrideX * Block0CELLSIZE + 0] - 2.0 * source[0][idx + 0 * Block0StrideX * Block0CELLSIZE + 0] + source[0][idx-1 * Block0StrideX * Block0CELLSIZE + 0]))+(DYM2 * (source[0][idx + 1 * Block0StrideY * Block0CELLSIZE + 0] - 2.0 * source[0][idx + 0 * Block0StrideY * Block0CELLSIZE + 0] + source[0][idx-1 * Block0StrideY * Block0CELLSIZE + 0])))-params[3]*0.5 * DYM1 * (source[0][idx + Block0StrideY * Block0CELLSIZE + 0] - source[0][idx - Block0StrideY * Block0CELLSIZE + 0])+source[0][idx + 0]);
     
}

//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0CentralFunction_Eqn2 = Block0CentralFunction_Eqn2;




//=========================CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER 0========================//

//3 central function for 2d model for block with number 0
__device__ void Block0CentralFunction_Eqn3(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;	      
	result[idx + 0] = source[0][idx + 0]+DT*(params[2]*((DXM2 * (source[0][idx + 1 * Block0StrideX * Block0CELLSIZE + 0] - 2.0 * source[0][idx + 0 * Block0StrideX * Block0CELLSIZE + 0] + source[0][idx-1 * Block0StrideX * Block0CELLSIZE + 0])))+source[0][idx + 0]);
     
}

//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0CentralFunction_Eqn3 = Block0CentralFunction_Eqn3;




//=========================CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER 0========================//

//1 central function for 2d model for block with number 0
__device__ void Block0CentralFunction_Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;	      
	result[idx + 0] = source[0][idx + 0]+DT*(source[0][idx + 0]+params[1]*((DXM2 * (source[0][idx + 1 * Block0StrideX * Block0CELLSIZE + 0] - 2.0 * source[0][idx + 0 * Block0StrideX * Block0CELLSIZE + 0] + source[0][idx-1 * Block0StrideX * Block0CELLSIZE + 0]))+(DYM2 * (source[0][idx + 1 * Block0StrideY * Block0CELLSIZE + 0] - 2.0 * source[0][idx + 0 * Block0StrideY * Block0CELLSIZE + 0] + source[0][idx-1 * Block0StrideY * Block0CELLSIZE + 0]))));
     
}

//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0CentralFunction_Eqn1 = Block0CentralFunction_Eqn1;





//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//
//Boundary condition for boundary y = 0
__device__ void Block0DefaultNeumann__Bound2__Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
     
     
	 result[idx + 0] = 500.0;
     
     
}
//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0DefaultNeumann__Bound2__Eqn0 = Block0DefaultNeumann__Bound2__Eqn0;



//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//
//Boundary condition for boundary y = 0
__device__ void Block0DefaultNeumann__Bound2__Eqn2(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
     
     
	 result[idx + 0] = 500.0;
     
     
}
//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0DefaultNeumann__Bound2__Eqn2 = Block0DefaultNeumann__Bound2__Eqn2;



//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//
//Boundary condition for boundary y = 0
__device__ void Block0DefaultNeumann__Bound2__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
     
     
	 result[idx + 0] = 500.0;
     
     
}
//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0DefaultNeumann__Bound2__Eqn1 = Block0DefaultNeumann__Bound2__Eqn1;



//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//
//Boundary condition for boundary y = y_max
__device__ void Block0Dirichlet__Bound3_1__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
     
     
	 result[idx + 0] = 300.0;
     
     
}
//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0Dirichlet__Bound3_1__Eqn1 = Block0Dirichlet__Bound3_1__Eqn1;



//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//
//Boundary condition for boundary y = y_max
__device__ void Block0Dirichlet__Bound3_1__Eqn3(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
     
     
	 result[idx + 0] = 300.0;
     
     
}
//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0Dirichlet__Bound3_1__Eqn3 = Block0Dirichlet__Bound3_1__Eqn3;



//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//
//Boundary condition for boundary y = y_max
__device__ void Block0DefaultNeumann__Bound3__Eqn3(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
     
     
	 result[idx + 0] = 500.0;
     
     
}
//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0DefaultNeumann__Bound3__Eqn3 = Block0DefaultNeumann__Bound3__Eqn3;



//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//
//Boundary condition for boundary y = y_max
__device__ void Block0DefaultNeumann__Bound3__Eqn2(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
     
     
	 result[idx + 0] = 500.0;
     
     
}
//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0DefaultNeumann__Bound3__Eqn2 = Block0DefaultNeumann__Bound3__Eqn2;



//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//
//Boundary condition for boundary y = y_max
__device__ void Block0DefaultNeumann__Bound3__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
     
     
	 result[idx + 0] = 500.0;
     
     
}
//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0DefaultNeumann__Bound3__Eqn1 = Block0DefaultNeumann__Bound3__Eqn1;



//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//
//Boundary condition for boundary x = 0
__device__ void Block0DefaultNeumann__Bound0__Eqn0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
     
     
	 result[idx + 0] = 500.0;
     
     
}
//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0DefaultNeumann__Bound0__Eqn0 = Block0DefaultNeumann__Bound0__Eqn0;



//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//
//Boundary condition for boundary x = 0
__device__ void Block0DefaultNeumann__Bound0__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
     
     
	 result[idx + 0] = 500.0;
     
     
}
//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0DefaultNeumann__Bound0__Eqn1 = Block0DefaultNeumann__Bound0__Eqn1;



//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//
//Boundary condition for boundary x = x_max
__device__ void Block0DefaultNeumann__Bound1__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
     
     
	 result[idx + 0] = 500.0;
     
     
}
//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0DefaultNeumann__Bound1__Eqn1 = Block0DefaultNeumann__Bound1__Eqn1;



//=============================BOUNDARY CONDITIONS FOR BLOCK WITH NUMBER 0======================//
//Boundary condition for boundary x = x_max
__device__ void Block0Dirichlet__Bound1_1__Eqn1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
     
     
	 result[idx + 0] = 300.0;
     
     
}
//device side function pointer declaration and init:
__device__ func_ptr_t p_Block0Dirichlet__Bound1_1__Eqn1 = Block0Dirichlet__Bound1_1__Eqn1;




// only for block 0
// Copy the pointers from the function arrays to the host side
void setup_func_arrays()
{
    // Dynamically assign the function array.
    // Copy the function pointers to their appropriate locations according to the enum
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[0], p_Block0CentralFunction_Eqn0, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[1], p_Block0CentralFunction_Eqn2, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[2], p_Block0CentralFunction_Eqn3, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[3], p_Block0CentralFunction_Eqn1, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[4], p_Block0DefaultNeumann__Bound2__Eqn0, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[5], p_Block0DefaultNeumann__Bound2__Eqn2, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[6], p_Block0DefaultNeumann__Bound2__Eqn1, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[7], p_Block0Dirichlet__Bound3_1__Eqn1, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[8], p_Block0Dirichlet__Bound3_1__Eqn3, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[9], p_Block0DefaultNeumann__Bound3__Eqn3, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[10], p_Block0DefaultNeumann__Bound3__Eqn2, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[11], p_Block0DefaultNeumann__Bound3__Eqn1, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[12], p_Block0DefaultNeumann__Bound0__Eqn0, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[13], p_Block0DefaultNeumann__Bound0__Eqn1, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[14], p_Block0DefaultNeumann__Bound1__Eqn1, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[15], p_Block0Dirichlet__Bound1_1__Eqn1, sizeof(func_ptr_t)));
   
    checkCudaErrors(cudaMemcpyFromSymbol(&h_funcArray[16], p_Block0Dirichlet__Bound1_1__Eqn1, sizeof(func_ptr_t)));
   
   
    // now copy the function arrays back to the device, so if we wish we can use an index into the array to choose them
    // We have now set the order in the function array according to our enum.
    checkCudaErrors(cudaMemcpyToSymbol(d_funcArray, h_funcArray, sizeof(func_ptr_t)*COUNT_OF_FUNC));

}

// device side function pointer declaretion:
__device__ func_ptr_t  device_func;


__global__ void kernel(int *  funcIdxs,
	   	       double* result, double** source, double* params, double** ic)
{
  int idxX = blockDim.x*blockIdx.x+threadIdx.x;
  int idxY = blockDim.y*blockIdx.y+threadIdx.y;
  
  if(idxX < Block0CountX)
  if(idxY < Block0CountY)
  {
     int idx = ( idxX + idxY * Block0StrideY ) * Block0CELLSIZE;  // + idxZ * Block0StrideZ
  
     device_func =  d_funcArray[funcIdxs[idx]];
     (*device_func)(result, source, 0.0, idxX, idxY, 0, params, ic);
  }

/*
  // for debug
  int idx = ( idxX + idxY * Block0StrideY ) * Block0CELLSIZE;  // + idxZ * Block0StrideZ
  result[idx + 0] = (2 * source[0][idx + 0 * Block0StrideY * Block0CELLSIZE + 0]);
  result[idx] = idx;
  result[idx] = funcIdxs[idx];
*/
/*
  // for debug with Block0CELLSIZE = 3;

  int idx = ( idxX + idxY * Block0StrideY ) * Block0CELLSIZE;
  result[idx] = idx;
  result[idx+1] = idx;
  result[idx+2] = idx;
*/  
}


extern "C" {
void compute_for_ctype(int *  funcIdxs,
     	               double* result, double** source, double* params, double** ic,
	    	       int SIZE_OF_RESULT, int COUNT_OF_DELAYS, int COUNT_OF_PARAMS,
		       int ITERATION_COUNT)
{

    //int SIZE = Block0CELLSIZE*Block0CountX*Block0CountY;
  
    double* d_result;

    // make device memory:
    checkCudaErrors(cudaMalloc( (void**)&d_result, SIZE_OF_RESULT * sizeof(double)));

    // FOR pointers at device side
    double** h_source;
    double ** d_source;

    // pointers at host side:
    h_source = (double**)malloc(COUNT_OF_DELAYS*sizeof(double*));

    // pointers at device side:
    checkCudaErrors(cudaMalloc( (void**)&d_source, COUNT_OF_DELAYS * sizeof(double*)));

    for(int i=0; i<COUNT_OF_DELAYS; i++)
    {
       // pointers at host side, memory at device side:
       checkCudaErrors(cudaMalloc((void**)&h_source[i], SIZE_OF_RESULT * sizeof(double)));
       checkCudaErrors(cudaMemcpy(h_source[i], source[i], SIZE_OF_RESULT * sizeof(double),
       			          cudaMemcpyHostToDevice));
    }
    // copy pointers from host side to device side:
    checkCudaErrors(cudaMemcpy(d_source, h_source, COUNT_OF_DELAYS * sizeof(double*),
    			       cudaMemcpyHostToDevice));
   // END FOR 
    
    double* d_params;

    checkCudaErrors(cudaMalloc( (void**)&d_params, COUNT_OF_PARAMS * sizeof(double)));    
    checkCudaErrors(cudaMemcpy(d_params, params, COUNT_OF_PARAMS * sizeof(double), cudaMemcpyHostToDevice));
    
    // interconnect dont used now:
    double** d_ic;
    checkCudaErrors(cudaMalloc((void**)&d_ic, 1 * sizeof(double*)));    

    int * d_funcIdxs;
    checkCudaErrors(cudaMalloc( (void**)&d_funcIdxs, SIZE_OF_RESULT * sizeof(int)));    
    checkCudaErrors(cudaMemcpy(d_funcIdxs, funcIdxs, SIZE_OF_RESULT * sizeof(int), cudaMemcpyHostToDevice));
    
    // fill funcArrays at device
    setup_func_arrays();

    // make grid:    
    //dim3 threads (Block0CountX, Block0CountY);
    //dim3 blocks  (1, 1);

    dim3 threads ( BLOCK_SIZE, BLOCK_SIZE );
    dim3 blocks  ( (int)ceil((double)Block0CountX / threads.x),
    	 	   (int)ceil((double)Block0CountY / threads.y) );
/*
    printf("\n*source \n");
    for (int i=0;i<SIZE_OF_RESULT;i++)
      printf(" %f ; ", (*source)[i]);
    printf("\nend of *source \n");

    printf("\nresult \n");
    for (int i=0;i<SIZE_OF_RESULT;i++)
      printf(" %f ; ", (result)[i]);
    printf("\nend of result \n");

    printf("\nstart kernel circle\n");
*/  
    // main code:

    for(int  i = 0; i < ITERATION_COUNT; i++) {

        kernel <<< blocks, threads >>> (d_funcIdxs,
	   	                        d_result, d_source, d_params, d_ic);
	/*
	// general scheme without delays:				    
        double * tmp = *d_source;
        *d_source = d_result;
        d_result = tmp;
	*/	


        // FOR exchange source and result:

        // h_source is host array with device pointers:
        double * tmp = *h_source;
        // printf("\n * tmp = *d_source; \n");

        //make changes at host side:
        *h_source = d_result;
        // make changes at device side (transfer pointers at device side from host):
        checkCudaErrors(cudaMemcpy(d_source, h_source, COUNT_OF_DELAYS * sizeof(double*),
    	   		           cudaMemcpyHostToDevice));
        /// printf("\n *d_source = d_result \n");

        d_result = tmp;
        /// printf("\n end of exchange \n");
        // END FOR

    }

/*
    kernel <<< blocks, threads >>> (d_funcIdxs,
     	   	                    d_result, d_source, d_params, d_ic);
    printf("\n end kernel  circle\n");


    double * tmp = *h_source;
    printf("\n * tmp = *d_source; \n");
    *h_source = d_result;
    //                                   distenation  source
    //checkCudaErrors(cudaMemcpyFromSymbol(tmp, d_source, sizeof(double*)));

    //                                   symbol   source
    //checkCudaErrors(cudaMemcpyToSymbol(d_array, h_array, sizeof(double*)*1));

    checkCudaErrors(cudaMemcpy(d_source, h_source, COUNT_OF_DELAYS * sizeof(double*),
    			       cudaMemcpyHostToDevice));

    printf("\n *d_source = d_result \n");
    d_result = tmp;
    printf("\n end of exchange \n");
*/
	
    // get result:
    cudaMemcpy(result, d_result, SIZE_OF_RESULT * sizeof(double), cudaMemcpyDeviceToHost);
    cudaMemcpy(*source, *h_source, SIZE_OF_RESULT * sizeof(double), cudaMemcpyDeviceToHost);


    printf("\nresult \n");
    for (int i=0;i<30;i++)
      printf(" %f ; ", (result)[i]);
    printf("\nend of result \n");

    printf("\n*source \n");
    for (int i=0;i<30;i++)
      printf(" %f ; ", (*source)[i]);
    printf("\nend of *source \n");

    printf("\nresult \n");
    for (int i=0;i<30;i++)
      printf(" %f ; ", (result)[i]);
    printf("\nend of result \n");

    printf("\n end get result \n");


    // FOR free
    cudaFree(d_result);

    for(int i=0; i<COUNT_OF_DELAYS; i++)
    {
       // pointers at host side, memory at device side:
       cudaFree(h_source[i]);
    }
    free(h_source);
    cudaFree(d_source);

    cudaFree(d_params);
    cudaFree(d_ic);
    cudaFree(d_funcIdxs);
    cudaFree(d_funcArray);
    cudaFree(h_funcArray);
}
}

// for tests: when main used directly.
// not forget about PAR_COUNT = 4 and change indexes for each side in
// fill_func_idxs  for that case

//===================INITIAL CONDITIONS==========================//
void Initial0(double* cellstart, double x, double y, double z){
     
	cellstart[0] = 4.0;
     
}

void Block0FillInitialValues(double* result){
    for(int idxY = 0; idxY<Block0CountY; idxY++)
		for(int idxX = 0; idxX<Block0CountX; idxX++){
			int idx = idxY*Block0CountX + idxX;
			Initial0(result+idx*Block0CELLSIZE, Block0OffsetX + idxX*DX, Block0OffsetY + idxY*DY, 0);
    }
    
}


//===================PARAMETERS==========================//
void initDefaultParams(double** pparams, int* pparamscount){

	*pparamscount = PAR_COUNT;

	*pparams = (double *) malloc(sizeof(double)*PAR_COUNT);
     
	(*pparams)[0] = 1.0;
     
	(*pparams)[1] = 0.3;
     
	(*pparams)[2] = 0.1;
     
	(*pparams)[3] = 0.01;
     
}
void releaseParams(double *params){
	free(params);
}

void fill_func_idxs(int* funcIdxs){ 
    for(int idxY = 0; idxY<Block0CountY; idxY++)
		for(int idxX = 0; idxX<Block0CountX; idxX++){
		  int idx = idxY*Block0CountX + idxX;

		  // default
		  funcIdxs[idx] = 0;
		  
		  // bounds
		  // side 0
		  if (idxX == 0)
		    funcIdxs[idx] = 16;

		  // side 1
		  if (idxX == Block0CountX-1)
		    funcIdxs[idx] = 16;

		  // side 2
		  if (idxY == 0)
		    funcIdxs[idx] = 16;

		  // side 3
		  if (idxY == Block0CountY-1)
		    funcIdxs[idx] = 16;
		 
		  // vertex
		  // [0, 2]
		  if (idxY == 0 & idxX == 0)
		    funcIdxs[idx] = 16;

		  // [2, 1]
		  if (idxY == 0 & idxX == Block0CountX-1)
		    funcIdxs[idx] = 16;
		  
		  // [3, 1]
		  if (idxY == Block0CountY-1 & idxX == Block0CountX-1)
		    funcIdxs[idx] = 16;

		  // [3, 0]
		  if (idxY == Block0CountY-1 & idxX == 0)
		    funcIdxs[idx] = 16;
		  
		  
		}
}


int main(int argc, char **argv)
{
  // size of source and result:
  int SIZE_OF_RESULT = Block0CELLSIZE*Block0CountX*Block0CountY;
  int COUNT_OF_DELAYS = 1;
  int COUNT_OF_PARAMS = PAR_COUNT;
  // count of iteration:
  int ITERATION_COUNT = 4;

  double * result = (double *)malloc(SIZE_OF_RESULT*sizeof(double));
  
  //double ** source = (double *)malloc(ITERS*sizeof(double*));
  double ** source = (double **)malloc(COUNT_OF_DELAYS*sizeof(double*));
  *source = (double *)malloc(SIZE_OF_RESULT*sizeof(double));

  double ** ic;
  ic = (double **)malloc(COUNT_OF_DELAYS*sizeof(double*));

  // FOR params
  double *  params;// = (double *) malloc(sizeof(double)*PAR_COUNT);
  int paramscount = 0;
  initDefaultParams(&params, &paramscount);
  printf("\n paramscount %d \n", paramscount);
  // END FOR

  // FOR funcIdxs:
  int *  funcIdxs = (int *)malloc(SIZE_OF_RESULT*sizeof(int));
  fill_func_idxs(funcIdxs);
  
  /*
  printf("\nfuncIdxs\n");
  for (int i=0;i<SIZE_OF_fARRAY;i++)
    printf(" %d ; ", funcIdxs[i]);
  printf("\n end of funcIdxs\n");
  */
  // END FOR

  // main code:
  Block0FillInitialValues(*source);
 
 /*
  printf("\ninitial values \n");
  for (int i=0;i<SIZE_OF_RESULT;i++)
    printf(" %f ; ", (*source)[i]);
  printf("\nend of initial values \n");
  */

  compute_for_ctype(funcIdxs, result, source, params, ic,
		    SIZE_OF_RESULT, COUNT_OF_DELAYS, COUNT_OF_PARAMS,
		    ITERATION_COUNT);
  
 
  printf("\nresult \n");
  for (int i=0;i<10;i++)
    printf(" %f ; ", (result)[i]);
  printf("\nend of result \n");
 
  printf("\n*source \n");
  for (int i=0;i<10;i++)
    printf(" %f ; ", (*source)[i]);
  printf("\nend of *source \n");
 
  // free memory:
  free(result);
  free(*source);
  free(source);
  releaseParams(params);
  //releaseFuncArray(funcArray);
  free(funcIdxs);
  free(ic);
}
