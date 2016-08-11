path=`pwd`
export LD_LIBRARY_PATH=$path:$LD_LIBRARY_PATH

./heat2dSimple 0 1 0.001 0.001 0.0000001
./heat2dWithFunc 0 1 0.001 0.001 0.0000001
./heat2dDepend 0 1 0.001 0.001 0.0000001
./heat2dLib 0 1 0.001 0.001 0.0000001