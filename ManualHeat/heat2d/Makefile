all: simple withfunc depend lib

simple:
	g++ -O3 heat2dSimple.cpp -o heat2dSimple -fopenmp

withfunc:
	g++ -O3 heat2dWithFunc.cpp -o heat2dWithFunc -fopenmp
	
depend:
	g++ -O3 libheat2d.cpp heat2dDepend.cpp -o heat2dDepend -fopenmp
	
lib:
	g++ -O3 -shared libheat2d.cpp -o libheat2d.so
	g++ -O3 heat2dDepend.cpp -o heat2dLib -L . -l heat2d -fopenmp
