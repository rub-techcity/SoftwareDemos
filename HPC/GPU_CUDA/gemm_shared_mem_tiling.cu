#include <stdio.h>
#include <cuda_runtime.h>
#include <iostream>
#include "host_utils.cuh"
#include "device_utils.cuh"

/*  
 Demo CUDA program
    Author: Ruben Ispiryan
	Date: 2024-06-01

    Prepared as part of the technical assessment for tensorq.ai.

    Demonstrates:
    - GEMM (General Matrix Multiplication)
    - shared-memory tiling optimization in CUDA
    - tiled GPU kernel execution
 */



constexpr int N = 256;
constexpr int TILE = 4;


// Kernel for tiled matrix multiplication
__global__ void tiledGEMM( int* A, int* B, int* C)
{
    __shared__ int tileA[TILE][TILE];
    __shared__ int tileB[TILE][TILE];

    int row = blockIdx.y * TILE + threadIdx.y;

    int col = blockIdx.x * TILE + threadIdx.x;

    int sum = 0;

    int numTiles = (N + TILE - 1) / TILE;


    for (int t = 0; t < numTiles; t++)
    {
        int tiledCol = t * TILE + threadIdx.x;

        int tiledRow = t * TILE + threadIdx.y;

        // Bounds-checked load for A
        if (row < N && tiledCol < N)
        {
            tileA[threadIdx.y][threadIdx.x] = A[row * N + tiledCol];
        }
        else
        {
            tileA[threadIdx.y][threadIdx.x] = 0;
        }

        // Bounds-checked load for B
        if (tiledRow < N && col < N)
        {
            tileB[threadIdx.y][threadIdx.x] =  B[tiledRow * N + col];
        }
        else
        {
            tileB[threadIdx.y][threadIdx.x] = 0;
        }

        __syncthreads();

        for (int k = 0; k < TILE; k++)
        {
            sum = multiplyAdd( tileA[threadIdx.y][k], tileB[k][threadIdx.x], sum);
        }

        __syncthreads();
    }

    if (row < N && col < N)
    {
        C[row * N + col] = sum;
    }
}


int main()
{
	// This is a debug call. In the final version of the code it should be removed. 
    // utility function that uses CUDA occupancy API to recommend optimal block size and minimum grid size 
    // for the given kernel
    host_utils::printOccupancyRecommendation(tiledGEMM);

    int* A; int* B; int* C;

    int size = N * N * sizeof(int);

    cudaMallocManaged(&A, size);
    cudaMallocManaged(&B, size);
    cudaMallocManaged(&C, size);

	// HOST initialization of A and B
    host_utils::initializeMatrix(A, N);
    host_utils::initializeMatrix(B, N);

    dim3 threadsPerBlock( TILE, TILE);

    dim3 blocks( N / TILE, N / TILE);

    // Kernel launch
    tiledGEMM<<<blocks,threadsPerBlock>>>( A, B, C);

	cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess)
    {
        std::cerr << "Kernel launch error: " << cudaGetErrorString(err) << std::endl;
        return 1;
    }

    err = cudaDeviceSynchronize();
    if (err != cudaSuccess)
    {
        std::cerr << "Kernel execution error: " << cudaGetErrorString(err) << std::endl;
        return 1;
    }

	host_utils::printMatrix(C, N);

    cudaFree(A); cudaFree(B); cudaFree(C);
    return 0;
}