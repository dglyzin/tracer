#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <fstream>


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

int main(int argc, char * argv[]) {
  double fromX = atof(argv[1]);
  double toX = atof(argv[2]);
  double finishTime = atof(argv[3]);
  double dx = atof(argv[4]);
  double dt = atof(argv[5]);
  
  double currentTime = 0.0;
  
  int gridNodeCount = (int)((toX - fromX) / dx);
  
  double* currentState = new double [gridNodeCount];
  double* nextState = new double [gridNodeCount];
  
  initArray(currentState, gridNodeCount, 0.0);
  initArray(nextState, gridNodeCount, 0.0);
  
  currentState[0] = 0.0;
  currentState[gridNodeCount-1] = 10.0;
  nextState[0] = 0.0;
  nextState[gridNodeCount-1] = 10.0;
  
  double dx2 = dx*dx;
  double* tmp;
  
  double start;
  double finish;
  
  start = omp_get_wtime();
  
  while(currentTime < finishTime) {
#pragma omp parallel for
    for(int i = 1; i < gridNodeCount-1; i++)
      nextState[i] = currentState[i] + dt * (currentState[i-1] - 2 * currentState[i] + currentState[i+1]) / dx2;
    
    tmp = currentState;
    currentState = nextState;
    nextState = tmp;
    
    currentTime += dt;
  }
  
  finish = omp_get_wtime();
  printf("Time: %f\n", finish - start);
  printf("currentTime: %.8f\n", currentTime);
  
  saveState("heat1dResult.lbin", currentTime, dt, currentState, gridNodeCount);
  
  delete currentState;
  delete nextState;
  
  return 0;
}