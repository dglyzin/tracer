path=`pwd`
export LD_LIBRARY_PATH=$path:$LD_LIBRARY_PATH

srun -N1 -p debug heat2dSimple 0 1 1.0 0.001 0.0000001
srun -N1 -p debug heat2dWithFunc 0 1 1.0 0.001 0.0000001
srun -N1 -p debug heat2dDepend 0 1 0.1.0 0.001 0.0000001
srun -N1 -p debug heat2dLib 0 1 1.0 0.001 0.0000001