#include <iostream>
#include "host_utils.cuh"

namespace host_utils
{
    void initializeMatrix(int* M, int N)
    {
        for (int i = 0; i < N * N; i++)
        {
            M[i] = 1;
        }
    }

	void printMatrix(int* M, int N)
	{
        std::cout << "The result of multiplication" << std::endl;
        int row = 0; int col = 0;
        for (int i = 0; i < N * N; i++)
        {
            row = i / N; col = i % N;
            std::cout << "M[" << row << "][" << col << "] = " << M[i] << std::endl;
        }
	}

}