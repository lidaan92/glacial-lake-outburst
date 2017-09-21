1. MERGE-IMJA-LAKE-BATHY-ASTDEM2-29m-16bit.tif

This tif file contains our Imja Lake bathymetry now merged with surrounding
topography represented by ASTER GDEM2 data. GDEM2 is ~29mx29m gridded data;
therefore I resampled the bathymetric data to match the exact pixel scale and
16-bit depth of the GDEM2 data. We can work with higher resolution DEMs as they
become available. I transformed the relative bathymetric values to MASL. Imja
Lake surface is almost exactly at 5000m, and I subtracted the (positive-valued)
bathymetric depth data from 5000.

2. MERGE-IMJA-LAKE-BATHY-ASTDEM2-29m-16bit.tfw

This tfw file is a 'world' file that informs the associated tif file of its
geospatial reference. You likely don't need this for you simulations, but not
sure so here it is.

3. IMJA-LAKE-BATHY-MASL-29m-16bit.tif

This file contains only the MASL-transformed Imja Lake bathymetry. Perhaps you
need this to observe where the lake boundary is located. I can also supply
vector files marking the lake outline if necessary.

4. IMJA-LAKE-BATHY-MASL-29m-16bit.tfw

Associated world file as described in (2).