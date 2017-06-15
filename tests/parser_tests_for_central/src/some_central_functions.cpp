For equation: 
U'=D[U(t-1.1),{y,1}]+D[U(t-5.9),{y,2}]+U(t-1)
result: 

//=========================CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER 0========================//

//0 central function for 2d model for block with number 0
void Block0CentralFunction0(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block0StrideY + idxZ * Block0StrideZ) * Block0CELLSIZE;
	 result[idx + 0] = 0.5 * DYM1 * (source[2][idx + Block0StrideY * Block0CELLSIZE + 0] - source[2][idx - Block0StrideY * Block0CELLSIZE + 0]) + (DYM2 * (1 * source[3][idx + 1 * Block0StrideY * Block0CELLSIZE + 0] - 2 * source[3][idx + 0 * Block0StrideY * Block0CELLSIZE + 0] + 1 * source[3][idx-1 * Block0StrideY * Block0CELLSIZE + 0])) + source[1][idx + 0];
}

For equation: 
U'=a*(D[U,{y,2}])+U(t-3)
result: 

//=========================CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER 1========================//

//0 central function for 2d model for block with number 1
void Block1CentralFunction1(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block1StrideY + idxZ * Block1StrideZ) * Block1CELLSIZE;
	 result[idx + 0] = params[0] * ((DYM2 * (1 * source[0][idx + 1 * Block1StrideY * Block1CELLSIZE + 0] - 2 * source[0][idx + 0 * Block1StrideY * Block1CELLSIZE + 0] + 1 * source[0][idx-1 * Block1StrideY * Block1CELLSIZE + 0]))) + source[1][idx + 0];
}

For equation: 
U'=a*(D[U(t-2),{y,3}])+U(t-3)
result: 

//=========================CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER 2========================//

//0 central function for 2d model for block with number 2
void Block2CentralFunction2(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block2StrideY + idxZ * Block2StrideZ) * Block2CELLSIZE;
	 result[idx + 0] = params[0] * ((DYM3 * (1 * source[1][idx + 1 * Block2StrideY * Block2CELLSIZE + 0] - 3 * source[1][idx + 0 * Block2StrideY * Block2CELLSIZE + 0] + 3 * source[1][idx-1 * Block2StrideY * Block2CELLSIZE + 0] - 1 * source[1][idx-2 * Block2StrideY * Block2CELLSIZE + 0]))) + source[2][idx + 0];
}

For equation: 
U'=a*(D[U(t-1),{y,2}] + D[U(t-5),{x,1}])
result: 

//=========================CENTRAL FUNCTIONS FOR BLOCK WITH NUMBER 3========================//

//0 central function for 2d model for block with number 3
void Block3CentralFunction3(double* result, double** source, double t, int idxX, int idxY, int idxZ, double* params, double** ic){
	 int idx = ( idxX + idxY * Block3StrideY + idxZ * Block3StrideZ) * Block3CELLSIZE;
	 result[idx + 0] = params[0] * ((DYM2 * (1 * source[1][idx + 1 * Block3StrideY * Block3CELLSIZE + 0] - 2 * source[1][idx + 0 * Block3StrideY * Block3CELLSIZE + 0] + 1 * source[1][idx-1 * Block3StrideY * Block3CELLSIZE + 0])) + 0.5 * DXM1 * (source[2][idx + Block3StrideX * Block3CELLSIZE + 0] - source[2][idx - Block3StrideX * Block3CELLSIZE + 0]));
}


 
