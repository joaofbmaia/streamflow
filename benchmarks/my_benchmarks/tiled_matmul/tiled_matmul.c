#include <stdint.h>

#define NI 1024
#define NJ 1024
#define NK 1024

#define TILE_SIZE 4

float E[NI][NJ];
float A[NI][NK];
float B[NK][NJ];

// Tiled Matrix Multiplication
void kernel_mm()
{
    for (int i = 0; i < NI; i += TILE_SIZE)
        for (int j = 0; j < NJ; j += TILE_SIZE)
            for (int k = 0; k < NK; k += TILE_SIZE)
                #pragma cgra_map
                for (int ii = 0; ii < TILE_SIZE; ii++)
                    for (int jj = 0; jj < TILE_SIZE; jj++)
                        for (int kk = 0; kk < TILE_SIZE; kk++)
                            E[i + ii][j + jj] += A[i + ii][k + kk] * B[k + kk][j + jj];
}

int main() {
    kernel_mm();
}