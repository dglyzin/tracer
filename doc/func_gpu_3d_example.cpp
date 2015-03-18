#include <math.h>
//функции типа дирихле для всех границ можно делать одни и те же (если температра одинаковая), .
//а один и тот же Нейман на разных границах будет отдельной функцией, т.к. придумывает 
//несуществующую точку в своем направлении.

//важный момент: оптимизировать только скорость
//много кода - нестрашно, т.к. генерируется автоматически по одному шаблону

#define StepX 0.1
#define StepY 0.1
#define StepZ 0.1

#define Block0StrideZ 10000
#define Block0StrideY 100

#define Block0CountZ 100
#define Block0CountY 100
#define Block0CountX 100

#define Block0OffsetX 0.0
#define Block0OffsetY 0.0
#define Block0OffsetZ 0.0

#define Block1StrideZ 100
#define Block1StrideY 10

#define Block1CountZ 10
#define Block1CountY 10
#define Block1CountX 10

#define Block1OffsetX 10.0
#define Block1OffsetY 5.0
#define Block1OffsetZ 5.0



//начальные условия - только на CPU
typedef void (*initfunc_ptr_t)( double*, double, double, double );

void Initial0(double* cellstart, double x, double y, double z){
    cellstart[0] = 15.0;
    cellstart[1] = sin(x)*cos(y);    
}

void Initial1(double* cellstart, double x, double y, double z){
    cellstart[0] = 200.0;
    cellstart[1] = 100.0;    
}

//Заполняет result[idx] начальной функцией с номером из initType[idx]
void BlockFillInitialValues(double* result, int* initType,
                            int BlockCountX, int BlockCountY, int BlockCountZ,                            
                            int BlockOffsetX, int BlockOffsetY, int BlockOffsetZ){    

    initfunc_ptr_t initFuncArray[2];  
    initFuncArray[0] = Initial0;
    initFuncArray[1] = Initial1;
    
    for(int idxZ = 0; idxZ<BlockCountZ; idxZ++)
        for(int idxY = 0; idxY<BlockCountY; idxY++)
            for(int idxX = 0; idxX<BlockCountX; idxX++){
                int idx = idxZ*BlockCountY*BlockCountX + idxY*BlockCountX + idxX;
                int type = initType[idx];
                initFuncArray[type](result+idx, BlockOffsetX + idxX*StepX, BlockOffsetY + idxY*StepY, BlockOffsetZ + idxZ*StepZ);
            }

}

/*
//граничные условия
__device__ double DirichletBound0(){
    return 10.0;
}


__device__ double DirichletBound1(){
    return 20.0;
}


__device__ double NeumannBound1(double* source, int idx, int strideX, int strideY, int strideZ){
    //example of Neumann conditions for side x=0 
    double bound_value = 4.0;
    double nonexistent = source[idx+strideX] - 2.0* bound_value * dx2;
    double result =  dx2*(source[idx+strideX] + nonexistent - 2.0*source[idx]) //вторая по x
                   + dy2*(source[idx+strideY] + source[idx-strideY] - 2.0*source[idx]) //вторая по y
                   + dz2*(source[idx+strideZ] + source[idx-strideZ] - 2.0*source[idx]);//вторая по z
    return result;
}


__device__ double NeumannBound2(double* source, int idx, int strideX, int strideY, int strideZ){
    //example of Neumann conditions for side z=z_max 
    double bound_value = -24.0;
    double nonexistent = source[idx-strideZ] - 2.0* bound_value * dz2;
    double result =  dx2*(source[idx+strideX] + source[idx+strideX] - 2.0*source[idx]) //вторая по x
                   + dy2*(source[idx+strideY] + source[idx-strideY]- 2.0*source[idx]) //вторая по y
                   + dz2*(nonexistent + source[idx-strideZ]- 2.0*source[idx]);//вторая по z
    return result;
}


//основная функция
__global__ void func_kernel(double* result, 
                     double time, double* source,  //исходный X
                     int countX, int countY, int countZ, int cellSize,
                     double dx2, double dy2, double dz2,
                     int** borderTypes,  // 0 = Дирихле, 1 = Нейман, 2 = склейка
                     int** borders,      // номер соответствующего условия,
                                         // функции из набора Дирихле, набора Неймана
                                         // или набора интерконнектов (набор у каждого блока свой,
                                         // чтобы не плодить, а список функций один для всех)
                     double** ic,
                     NeumannBounds,  DirichletBounds){

    int idxZ = threadIdx.z + blockIdx.z*blockSize.z;
    int idxY = threadIdx.y + blockIdx.y*blockSize.y;
    int idxX = threadIdx.x + blockIdx.x*blockSize.x;

    int cellStart = (idxZ*countY*countX + idxY*countX + idxX) * cellSize;

    int strideX = cellSize;
    int strideY = cellSize*countX;
    int strideZ = cellSize*countX*countY;

    if (idxZ == 0) 
        if ( (idxY>0)&&(idxX>0)&&(idxY<countY-1)&&(idxX<countX-1) ){            
            cellStart2D = idxY*countX + idxX;
            for (int idx = 0; idx<cellSize; idx++)
                if (borderTypes[BD_ZSTART][cellstart2D+idx] == BT_DIRICHLET)
                    result[cellstart+idx] = DirichletBounds[ borders[BD_ZSTART][cellstart2D+idx] ] ();
                else if (borderTypes[BD_ZSTART][cellstart2D+idx] == BT_NEUMANN)
                    result[cellstart+idx] = NeumannBounds[ borders[BD_ZSTART][cellstart2D+idx] ] (source,);    
                else //interconnect
                    result[cellstart+idx] = 
        }
    if (idxZ == countZ-1) 
    if (idxY == 0) 
    if (idxY == countY-1) 
    if (idxX == 0) 
    if (idxX == countX-1) 

    if ( (idxZ>0)&&(idxY>0)&&(idxX>0)&&(idxZ<countZ)&&(idxY<countY-1)&&(idxX<countX-1) )
        for (int idx = cellStart; idx<cellStart+cellSize; idx++)
            result[idx] = dx2*(source[idx+strideX]+source[idx-strideX]- 2.0*source[idx]) //вторая по x
                        + dy2*(source[idx+strideY]+source[idx-strideY]- 2.0*source[idx]) //вторая по y
                        + dz2*(source[idx+strideZ]+source[idx-strideZ]- 2.0*source[idx]);//вторая по z

}

void funcGPU( double* result, 
              double time, double* source,  //исходный X
              int countX, int countY, int countZ, int cellSize,
              double dx2, double dy2, double dz2,
              int** borderTypes,  // 0 = Дирихле, 1 = Нейман, 2 = склейка
              int** borders,       // номер соответствующего условия,
                                  // функции из набора Дирихле, набора Неймана
                                  // или набора интерконнектов (набор у каждого блока свой,
                                  // чтобы не плодить, а список функций один для всех)
              double** ic, 
              NeumannBounds,  DirichletBounds //эти функции солвер получил отсюда же через getBoundFuncArray
            ){ 
    
    dim3 threads(16,16,1);
    dim3 blocks(countX/threads.x, countY/threads.y, countZ/threads.z);
    func_kernel<<<blocks, threads>>>(result, time, source,
                 countX, countY, countZ, cellSize, dx2,dy2,dz2,
                 borderTypes, border, ic,
                 NeumannBounds, DirichletBounds );    
    
}


//вспомогательные функции
void getBoundFuncArray(??? NeumannBounds, ??? DirichletBounds){
      NeumannBounds = 
      DirichletBounds =   
      NeumannBounds[0] = NeumannBound0;
      NeumannBounds[1] = NeumannBound1;
      NeumannBounds[2] = NeumannBound2;    
      DirichletBounds[0] = DirichletBound0;
      DirichletBounds[1] = DirichletBound1;      
}*/