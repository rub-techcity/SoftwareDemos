#pragma once

// DEVICE helper functions for matrix multiplication
__device__ inline int multiplyAdd(int a, int b, int sum)
{
    return sum + a * b;
}