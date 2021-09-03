## Table of Contents
* [About the project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
  * [Preparation of Input Data](#preparation-of-input-data)
  * [Running the Model](#running-the-module)
  * [Output Data](#output-data)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)


## About the project
The `XSpraDrift` module is an R implementation for landscape-scale simulation of spray-drift deposition based on the
`XDrift` R package ([https://doi.org/10.1016/j.softx.2020.100610](https://doi.org/10.1016/j.softx.2020.100610)).

### Built with
`XSprayDrift` was build with the following software: 
* [XDrift 1.0.9999](https://doi.org/10.1016/j.softx.2020.100610)
* [R](https://cran.r-project.org) v3.5.1


## Getting Started
`XSprayDrift` is a portable stand-alone application. It includes its own R runtime environment and can be started after
compiling all input data into an HDF5 file (see [usage](#usage)).

### Prerequisites
`XSprayDrift` requires a 64-bit Windows to run.

### Installation
Copy `XSprayDrift` to any folder and start the module via command line (see [usage](#usage)).


## Usage
### Preparation of Input Data
`XSprayDrift` input data must be organized in a specific folder structure that looks like the following. The
base directory may have any name, with the other names being mandatory. The module additionally requires another 
shapefile that may be located anywhere in the file system.
```
sim.x3df/
 +-- geom
 |    +-- base.dbf
 |    +-- base.prj
 |    +-- base.shp
 |    \-- base.shx
 \-- arr.dat
``` 

The `geom` folder contains an ESRI shapefile with the following properties:
* It shows all spatial units in the simulated region that are relevant for spray-drift (applied fields, habitats, 
  drift-filtering vegetation) as Polygon or Multipolygon features. It may also contain features that are not relevant
  for spray-drift simulation. These features will be ignored.
* Geometries use a projected coordinate reference system that uses meters as horizontal units.
* It has an integer attribute `FID` that assigns a unique value to each feature in the shapefile, starting with 0 and 
  using only consecutive values.

The `arr.dat` is a HDF5 file that contains the non-spatial inputs of the module and follows a specific format. It is 
set up in the following:
* It contains a dataset group `/dims/time` that has a 32-bit integer attribute `id` with a value of 0.
* It contains a dataset group `/dims/space` that has a 32-bit integer attribute `id` with a value of 1.
* It contains a one-dimensional dataset `/scales/0/simulation` of size 1.
* It contains a one-dimensional dataset `/scales/0/day` of size _n_ where _n_ is the number of days simulated.
* The `/scales/0/day` dataset has a 32-bit integer attribute `t_offset` that specifies the number of days between the 
  first day simulated, and the POSIX timestamp 0.
* The `/scales/0/day` dataset has a string attribute `transform` with a value of "Day".
* It contains a one-dimensional dataset `/scales/1/region` of size 1. 
* It contains a one-dimensional dataset `/scales/1/base_geometry` of size _n_ where _n_ is the exact number of features
  in the `base.shp` shapefile.
* The `/scales/1/base_geometry` dataset has a string attribute `geometries` with a value of "base.shp".
* It contains a two-dimensional dataset `/scales/1/1sqm` of size _m_ x _n_ where _m_ is the rounded-up x-extent and 
  _n_ is the rounded-up y-extent of the region. The geometries of the `base.shp` must reside within this region.
* The `/scales/1/1sqm` dataset has a 64-bit floating point attribute `t_offset` of size 2. It specifies the x- and 
  y-coordinate od the lower-left corner of the simulated region.
* The `/scales/1/1sqm` dataset has a string attribute `tarnsform` with a value of "Geographic".
* It contains a one-dimensional string dataset `data/simulation/region/ppm/shapefile` of size 1 containing the absolute
  file path to a second shapefile with information about applied areas (see below). The dataset has a string attribute
  `set` with a value of "TRUE".
* It contains a two-dimensional 32-bit floating point dataset 
  `data/simulation/region/spray-drift/params/ag_drift_quantile` of size 1 x 1 containing the quantile used when AgDrift 
  is selected as spray-drift model. Must be a value of either 0.5 or 0.9. The dataset has an 8-bit enum attribute `set` 
  with a value of "TRUE".
* It contains a two-dimensional 8-bit enum dataset (0=FALSE, 1=TRUE)
  `data/simulation/region/spray-drift/params/apply_simple1_drift_filtering` of size 1 x 1 containing an indication of
  whether drift filtering is applied. The dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value 
  of 1.
* It contains a two-dimensional string dataset `data/simulation/region/spray-drift/params/boom_height` of size 1 x 1 
  that specifies the boom height for the AgDrift filter model. Allowed values are "low" and "high". The dataset has an 
  8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional string dataset `data/simulation/region/spray-drift/params/crop` of size 1 x 1 
  that specifies the Rautmann or xSprayDrift model crop. Allowed values are "orchards.late", "orchards.early", "vines",
  "arable" and "hops". The dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional string dataset `data/simulation/region/spray-drift/params/crop` of size 1 x 1 
  that specifies the Rautmann or xSprayDrift model crop. Allowed values are "orchards.late", "orchards.early", "vines",
  "arable" and "hops". The dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional string dataset `data/simulation/region/spray-drift/params/droplet_size` of size 1 x 1 
  that specifies the droplet size assumed if using the AgDrift model. Allowed values are "fine" and "medium". The 
  dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional 32-bit floating point dataset `data/simulation/region/spray-drift/params/ep_dist_sd` of 
  size 1 x 1 that contains the standard deviation of a normal PDF. This PDF varies the distance between field and 
  habitat for an entire exposure path. The dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 
  1.
* It contains a two-dimensional 32-bit floating point dataset `data/simulation/region/spray-drift/params/ep_width` that
  defines the width of an exposure path in meters. The dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set` with 
  a value of 1.
* It contains a two-dimensional 32-bit floating point dataset `data/simulation/region/spray-drift/params/field_dist_sd` 
  of size 1 x 1 that contains the standard deviation of a normal PDF. This PDF varies the distance between field and 
  habitat for an entire application. The dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional 32-bit floating point dataset 
  `data/simulation/region/spray-drift/params/filtering_fraction` of size 1 x 1 that specifies by which fraction 
  spray-drift is filtered if drift-filtering is enabled. The dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set`
  with a value of 1.
* It contains a two-dimensional string dataset `data/simulation/region/spray-drift/params/filtering_types` of 
  size 1 x 1 that contains a comma-and-space separated list of numerical type identifiers of drift-filtering 
  land-use / land-cover types. This value applies if drift-filtering is enabled. The dataset has an 8-bit enum attribute
  (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional 32-bit floating point dataset 
  `data/simulation/region/spray-drift/params/filtering_min_width` of size 1 x 1 that defines the minimum width of 
  drift-filtering vegetation that has to be passed in meters before drift-filtering is applied . The dataset has an 
  8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional string dataset `data/simulation/region/spray-drift/params/habitat_types` of 
  size 1 x 1 that contains a comma-and-space separated list of numerical type identifiers of habitat land-use / 
  land-cover types.The dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional 32-bit floating point dataset 
  `data/simulation/region/spray-drift/params/max_angular_deviation` of size 1 x 1 that defines the maximum angle between
  source and sink receptors that still leads to spray-drift exposure. The dataset has an 8-bit enum attribute 
  (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional 32-bit floating point dataset `data/simulation/region/spray-drift/params/min_dist` of
  size 1 x 1 that defines the minimum distance between field and habitat for geometrical distances. The dataset has an 
  8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional string dataset `data/simulation/region/spray-drift/params/model` of size 1 x 1 
  that specifies the model to use. Allowed values are "XSprayDrift", "90thRautmann" and "AgDRIFT". The dataset has an 
  8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional string dataset `data/simulation/region/spray-drift/params/model` of size 1 x 1 that 
  specifies the PDF to use for the XSprayDrift model. Allowed values are "gamma", "normal", "lognormal",
  "beta" and "uniform". The dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional 32-bit integer dataset `data/simulation/region/spray-drift/params/random_seed` of size 
  1 x 1 that allows to use a fixed seed. Use 0 to disable the use of a fixed seed. The dataset has an 8-bit enum 
  attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional 32-bit floating point dataset 
  `data/simulation/region/spray-drift/params/reporting_threshold` of size 1 x 1 that specifies the minimum exposure 
  (in application rate units) that is reported. The dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a 
  value of 1.
* It contains a two-dimensional string dataset `data/simulation/region/spray-drift/params/source_exposure` of size 1 x 1
  that specifies the reported in-field exposure. Allowed values are "NA" and numerical values. The dataset has an 
  8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional string dataset `data/simulation/region/spray-drift/params/spatial_output_scale` of size 
  1 x 1 that specifies the spatial scale of reported exposure. Allowed values are "1sqm" and "base_geometry". The 
  dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional 16-bit unsigned integer dataset `data/simulation/region/weather/wind_direction` of size 
  1 x 1 that defines the wind direction in degrees. A value of 65535 means to draw the wind direction from a 
  uniform PDF for each application. The dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) `set` with a value of 1.
* It contains a two-dimensional 16-bit unsigned integer dataset `data/simulation/base_geometrylandscape/feature_type` 
  of size 1 x _n_ where _n_ is the number of features in the `base.shp`. For each feature, it lists the numerical 
  identifier of the feature's land-use / land-cover type. The dataset has an 8-bit enum attribute (0=FALSE, 1=TRUE) 
  `set` with a value of 1.
* It contains one of the following two datasets. This dataset should contain only zeroes. Make sure to enable 
  compression on this dataset and chunk it for fast access over space.
  * If the spatial output scale is "1sqm", a three-dimensional 32-bit floating point dataset 
    `/data/day/1sqm/spray_drift/exposure` of size _m_ x _n_ x _o_ should be present. _m_ is the number of simulated
    days, _n_ the x-extent of the simulated region and _o_ the y-extent of the simulated region.
  * If the spatial output scale is "base-geometry", a two-dimensional 32-bit floating point dataset 
    `/data/day/1sqm/spray_drift/exposure` of size _m_ x _n_ should be present. _m_ is the number of simulated days and 
    _n_ the number of features in the `base.shp`.

The additional shapefile provided as input to `XSprayDrift` has the following properties:
  * For each application, it contains the exact geometry of the applied area. within the applied field. This may result
    in a layer with many overlapping geometries.
  * The shapefile uses the same coordinate reference system as the `base.shp`.
  * It has an integer `Field` attribute that indicates to which feature of the `base.shp` the applied area relates.
  * It has a Date `Date` attribute that specifies the date of application.
  * It has a real `Rate` attribute that specifies the application rate used for the application.
  * It has a real `DriftRed` attribute that indicates the fraction of drift-reduction due to the drift technology used
    during application.

### Running the Module
The module can be run from the command line by passing the input file path as parameter:
```cmd
R-3.5.3\bin\x64\RScript.exe --vanilla SDModel_XSprayDrift_x3df_2.R <path_to_input_folder>
```

### Output Data
The `XSprayDrift` module updates the `exposure` dataset found within the `arr.dat`. Simulated exposure values per day
and unit at the selected output scale can be retrieved from this dataset.


## Roadmap
The `XSprayDrift` module is stable. No further development are ongoing at the moment.


## Contributing
Contributions are welcome. Please contact the authors (see [Contact](#contact)).


## License
Distributed under the CC0 License. See `LICENSE` for more information.


## Contact
Thorsten Schad - thorsten.schad@bayer.com
Sascha Bub - sascha.bub.ext@bayer.com


## Acknowledgements
* [Apply function progress bars](https://cran.r-project.org/web/packages/pbapply)
* [data.table](https://cran.r-project.org/web/packages/data.table)
* [R GDAL bindings](https://cran.r-project.org/web/packages/rgdal)
* [sp](https://cran.r-project.org/web/packages/sp)
* x3df
