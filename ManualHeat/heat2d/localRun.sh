path=`pwd`
export LD_LIBRARY_PATH=$path:$LD_LIBRARY_PATH

echo "\nSimple"
./heat2dSimple 0 1 0.001 0.001 0.0000001

echo "\nWith function in this file"
./heat2dWithFunc 0 1 0.001 0.001 0.0000001

echo "\nWith function in another file"
./heat2dDepend 0 1 0.001 0.001 0.0000001

echo "\nWith lib.so"
./heat2dLib 0 1 0.001 0.001 0.0000001