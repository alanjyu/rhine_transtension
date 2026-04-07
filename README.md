# Dataset for "Sustained transtension drives narrow, alternating basins and kinematic transition in the Upper Rhine Graben"

This is a repository of the ASPECT input files, shared libraries for stress regime analysis.

## Programable Filters

The ParaView Programable Filters for calculating the crustal strengthing factor ($\beta$) are stored in [filters/](https://github.com/alanjyu/rhine_transtension/tree/main/filters). 

## Shared Libraries

The source code for stress regime analysis is available in [lib/](https://github.com/alanjyu/rhine_transtension/tree/main/lib). This outputs the fault category and stress regime ratio for each cell.

To install this library:

1. Create a folder containing the source file, header file, and `CMakeLists.txt`. In the source file, make sure the  `include` path points to the correct header file.

2. Create a build directory within, then run `cmake -DAspect_DIR=/path/to/aspect/build/dir -DDEAL_II_DIR=/path/to/dealii/build/dir ..` to configure the build.

3. Once the CMake files are generated, run `make` to compile the source code. If successful, two `.so` files (`release` and `debug`) will be generated in the build directory.

To include the library in a model run:

1. Add `set Additional shared libraries = /path/to/libregime_stress_ratio.release.so` to the preambles in the input `.prm`.

2. For debug runs, use `/path/to/libregime_stress_ratio.debug.so` instead.