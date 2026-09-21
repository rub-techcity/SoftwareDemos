#pragma once

namespace host_utils
{
    void initializeMatrix( int* M, int N);
    void printMatrix( int* M, int N);

	// HOST helper function to get the recommendig block size. SHould be called in peparation, not in vinal version.
    // Template function to accept any kernel function pointer
    template<typename KernelFunc>
    void printOccupancyRecommendation(KernelFunc kernel)
    {
        int minGridSize;
        int recommendedBlockSize;

        cudaOccupancyMaxPotentialBlockSize(
            &minGridSize,
            &recommendedBlockSize,
            kernel,
            0,
            0);

        std::cout << "Recommended block size: " << recommendedBlockSize << std::endl;
        std::cout << "Minimum grid size: " << minGridSize << std::endl;
    }


}