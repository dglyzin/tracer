#include <mpi.h>

int main(int argc, char** argv){

    MPI_Init(&argc, &argv);

    int rank;
    double drank;

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    drank = rank;

    MPI_Send(&drank, 1, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);

    MPI_Finalize();
}


