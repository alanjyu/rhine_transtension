# Dataset for "Sustained transtension shapes narrow, alternating basins and kinematic transition in the Upper Rhine Graben"

This repository contains ASPECT input files, programmable filters for crustal stretching factors, and ASPECT shared libraries for stress regime analysis.


## Tested Environment

- [ParaView](https://www.paraview.org/) 6.0
- [Python](https://www.python.org/) 3.12
- [ASPECT](https://aspect.geodynamics.org/) 3.1.0-pre ([commit 984f6ff](https://github.com/geodynamics/aspect/commit/984f6ff64efb91c792525caca3b2864c9fad4d50))
- [Fastscape](https://fastscape.org/fastscapelib-fortran/) in Fortran ([commit 45f9036](https://github.com/fastscape-lem/fastscapelib-fortran/commit/45f9036b9e8a4bcb14b9ddd0a1c5cbfaec8eb4fc))


## Reference Model Input Files

The ASPECT input file (including Fastscape parameters), output log, and statistics, are stored in [ref/](https://github.com/alanjyu/rhine_transtension/tree/main/ref). The output movie is included as a Supplimentary Movie 1 in the manuscript.


## Coupling of ASPECT and Fastscape

The coupling interface between ASPECT and Fastscape has been implemented in the main branch of ASPECT. In order to install ASPECT with FastScape:

1. Create a build directory for FastScape and compile it with an added flag for creating a shared library: `cmake -DBUILD_FASTSCAPELIB_SHARED=ON /path/to/fastscape/build` then `make` to compile.

2. Create a build directory for ASPECT and compile it with an added flag pointing to the fastscape build folder as a shared library: `cmake -DFASTSCAPE_DIR=/path/to/fastscape/build /path/to/aspect/build` then `make`.


## Programable Filters

The ParaView Programable Filters for calculating the crustal strengthing factor ($\beta$) are stored in [filters/](https://github.com/alanjyu/rhine_transtension/tree/main/filters). To use the filters:

1. [Script 1](https://github.com/alanjyu/rhine_transtension/tree/main/filters) is used to extract the topography of the upper surface of a selected layer. Edit [Script 1](https://github.com/alanjyu/rhine_transtension/blob/main/filters/1-get_topo_top_z.py) so that the input variable name matches your desired field.

2. In ParaView, select the target layer and apply a Programmable Filter via `Filters → Programmable Filters`, copy the edited script and paste in `Script`. Copy the edited Script 1 into the `Script` field. You may adjust the output type if needed. Click `Apply` to generate a new output object. 

3. Perform the same procedure for the second layer.

4. Once the desired surfaces have been extracted, In ParaView, select the two outputs and add another Programmable Filter. The first input corresponds to `self.GetInputDataObject(0, 0)`, and the second to `self.GetInputDataObject(1, 0)`. Paste [Script 2](https://github.com/alanjyu/rhine_transtension/blob/main/filters/2-get_crustal_thickness.py) into the Script field and click `Apply`. The script will output the thickness between the two extracted surfaces.

4. Compute the $\beta$-factor by dividing the calculated layer thickness by its original thickness using `Filters → Calculator`.


## Shared Libraries

The source code for stress regime analysis is available in [lib/](https://github.com/alanjyu/rhine_transtension/tree/main/lib). This outputs the fault category and stress regime ratio for each cell.

To install this library:

1. Create a folder containing the source file, header file, and `CMakeLists.txt`. In the source file, make sure the  `include` path points to the correct header file.

2. Create a build directory within, then run `cmake -DAspect_DIR=/path/to/aspect/build/dir -DDEAL_II_DIR=/path/to/dealii/build/dir ..` to configure the build.

3. Once the CMake files are generated, run `make` to compile the source code. If successful, two `.so` files (`release` and `debug`) will be generated in the build directory.

To include the library in a model run:

1. Add `set Additional shared libraries = /path/to/libregime_stress_ratio.release.so` to the preambles in the input `.prm`.

2. For debug runs, use `/path/to/libregime_stress_ratio.debug.so` instead.