echo Welcome to generated kernel launcher!
export LD_LIBRARY_PATH=/home/tester/Tracer1/Heat_test:$LD_LIBRARY_PATH
srun -N 2 -p debug /home/dglyzin/hybridsolver/bin/HS /home/tester/Tracer1/Heat_test/project.dom
