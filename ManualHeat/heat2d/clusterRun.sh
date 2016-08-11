path=`pwd`
export LD_LIBRARY_PATH=$path:$LD_LIBRARY_PATH

echo "\nSimple"
srun -N1 -p debug heat2dSimple 0 1 0.01 0.001 0.0000001

echo "\nWith function in this file"
srun -N1 -p debug heat2dWithFunc 0 1 0.01 0.001 0.0000001

echo "\nWith function in another file"
srun -N1 -p debug heat2dDepend 0 1 0.01 0.001 0.0000001

echo "\nWith lib.so"
srun -N1 -p debug heat2dLib 0 1 0.01 0.001 0.0000001
