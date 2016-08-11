#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <fstream>

#include <iostream>
#include <vector>


#define SAVE_FILE_CODE 253
#define GEOM_FILE_CODE 254
#define VERSION_MAJOR 1
#define VERSION_MINOR 0

#define SIZE_CHAR sizeof(char)
#define SIZE_INT sizeof(int)
#define SIZE_DOUBLE sizeof(double)
#define SIZE_UN_SH_INT sizeof(unsigned short int)


using namespace std;

void saveGeneralInfo(char* path, double currentTime, double timeStep) {
  ofstream out;
  out.open(path, ios::binary);

  char save_file_code = SAVE_FILE_CODE;
  char version_major = VERSION_MAJOR;
  char version_minor = VERSION_MINOR;

  out.write((char*) &save_file_code, SIZE_CHAR);
  out.write((char*) &version_major, SIZE_CHAR);
  out.write((char*) &version_minor, SIZE_CHAR);

  out.write((char*) &currentTime, SIZE_DOUBLE);
  out.write((char*) &timeStep, SIZE_DOUBLE);

  out.close();
}

void saveStateData(char* path, double* array, int size) {
  ofstream out;
  out.open(path, ios::binary | ios::app);
  out.write((char*) array, SIZE_DOUBLE * size);
  out.close();
}

void saveState(char* path, double currentTime, double timeStep, double* array, int size) {
  saveGeneralInfo(path, currentTime, timeStep);
  saveStateData(path, array, size);
}

void initArray(double* array, int size, double value) {
  for(int i = 0; i < size; i++)
    array[i] = value;
}

void printArray(double* array, int size) {
  printf("\n\n");
  for(int i = 0; i < size; i++)
    printf("%.8f ", array[i]);
  printf("\n\n");
}

void computeOneNode(double* result, double* source, double dt, double dx2, int idx, int sideLength) {
  result[idx] = source[idx] + dt * (
	  ((source[idx - 1] - 2 * source[idx] + source[idx + 1]) / dx2) + 
	  ((source[idx - sideLength] - 2 * source[idx] + source[idx + sideLength]) / dx2)
	);
}

int main(int argc, char * argv[]) {
  double fromX = atof(argv[1]);
  double toX = atof(argv[2]);
  double finishTime = atof(argv[3]);
  double dx = atof(argv[4]);
  double dt = atof(argv[5]);
  
  double dx2 = dx*dx;
  
  double currentTime = 0.0;
  
  int sideLength = (int)((toX - fromX) / dx );
  int gridNodeCount = sideLength * sideLength;
  
  printf("side & gridNodeCount %d %d\n",sideLength, gridNodeCount); 
  
  double* currentState = new double [gridNodeCount];
  double* nextState = new double [gridNodeCount];
  
  /*std::vector<double> currentState(gridNodeCount);
  std::vector<double> nextState(gridNodeCount);*/
  
  initArray(currentState, gridNodeCount, 0.0);
  initArray(nextState, gridNodeCount, 0.0);
  
  /*for(int i = 0; i < gridNodeCount; i++) {
    currentState[i] = nextState[i] = 0.0;
  }*/
  
  /*currentState[0] = 0.0;
  currentState[gridNodeCount-1] = 10.0;
  nextState[0] = 0.0;
  nextState[gridNodeCount-1] = 10.0;*/
  
  for(int i = 0; i < sideLength; i++) {
    currentState[i] = 10;
    nextState[i] = 10;
    
    currentState[sideLength * i + 0] = 0.0;
    nextState[sideLength * i + 0] = 0.0;
    
    currentState[sideLength * i + sideLength - 1] = 0.0;
    nextState[sideLength * i + sideLength - 1] = 0.0;
    
    currentState[sideLength * (sideLength - 1) + i] = 0.0;
    nextState[sideLength * (sideLength - 1) + i] = 0.0;
  }
  
  double* tmp;
  
  double start;
  double finish;
  
  start = omp_get_wtime();
  
  while(currentTime < finishTime) {
#pragma omp parallel for
    for(int i = 1; i < sideLength - 1; i++) {
      for(int j = 1; j < sideLength - 1; j++) {
	int idx = sideLength * i + j;
	
	/*nextState[idx] = currentState[idx] + dt * (
	  ((currentState[idx - 1] - 2 * currentState[idx] + currentState[idx + 1]) / dx2) + 
	  ((currentState[idx - sideLength] - 2 * currentState[idx] + currentState[idx + sideLength]) / dx2)
	);*/
	computeOneNode(nextState, currentState, dt, dx2, idx, sideLength);
      }
    }
    
    tmp = currentState;
    currentState = nextState;
    nextState = tmp;
    
    currentTime += dt;
  }
  
  finish = omp_get_wtime();
  
  double t = finish - start;
  
  printf("Time: %f\n", t);
  printf("currentTime: %.8f\n", currentTime);
  
  int stepCount = (int)(finishTime / dt);
  double speed = (double) (gridNodeCount) * stepCount / t / 1000000;
  
  printf("Stepcount: %d\n", stepCount);
  printf("Speed: %.8f\n", speed);
  
  //printArray(currentState, gridNodeCount);
  saveState("heat2dResult.lbin", currentTime, dt, currentState, gridNodeCount);
  
  delete currentState;
  delete nextState;
  
  return 0;
}