## Table of Contents
* [About the project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
  * [Inputs](#inputs)
  * [Outputs](#outputs)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)


## About the project
The `XSprayDrift.SprayDrift` component is a Landscape Model component that simulates spray-drift depositions at a 
landscape-scale in square-meter resolution. The underlying `XSprayDrift` module is an R implementation that makes use of
the `XDrift` R package ([https://doi.org/10.1016/j.softx.2020.100610](https://doi.org/10.1016/j.softx.2020.100610)).

### Built with
* Landscape Model core version 1.4.1
* XSprayDrift module version 2.1; see `module\README` for details


## Getting Started
The component can be used within Landscape Models that require simulation of spray-drift.

### Prerequisites
A fully set up Landscape Model variant. See the Landscape Model core `README` for further details.

### Installation
1. Copy the `XSprayDrift` component into the `model\variant` sub-folder.
2. Make use of the component by including it into the model composition using `module=XSprayDrift` and 
   `class=SprayDrift`. 


## Usage
The following gives a sample configuration of the `XSprayDrift` component. See [inputs](#inputs) and [outputs](#outputs)
for further details on the component's interface.
```xml
<SprayDrift module="XSprayDrift" class="SprayDrift" enabled="$(SimulateSprayDriftExposure)">
    <ProcessingPath>$(_MCS_BASE_DIR_)\$(_MC_NAME_)\processing\sd</ProcessingPath>
    <SimulationStart type="date">2006-01-01</SimulationStart>
    <SimulationEnd type="date">2015-12-31</SimulationEnd>
    <Geometries>
        <FromOutput component="LULC" output="Geometries"/>
    </Geometries>
    <GeometryCrs>
        <FromOutput component="LULC" output="Crs"/>
    </GeometryCrs>
    <Extent>
        <FromOutput component="LULC" output="Extent"/>
    </Extent>
    <HabitatLulcTypes>
        <FromOutput component="LULC" output="habitat_lulc_types"/>
    </HabitatLulcTypes>
    <FieldDistanceSD type="float" unit="m">0</FieldDistanceSD>
    <EPDistanceSD type="float" unit="m">0</EPDistanceSD>
    <ReportingThreshold type="float" unit="g/ha">0</ReportingThreshold>
    <ApplySimpleDriftFiltering type="bool">false</ApplySimpleDriftFiltering>
    <LulcTypes>
        <FromOutput component="LULC" output="LulcTypeIds"/>
    </LulcTypes>
    <WindDirection type="int" unit="deg">-1</WindDirection>
    <SprayDriftModel>XSprayDrift</SprayDriftModel>
    <SourceExposure unit="g/ha">NA</SourceExposure>
    <RautmannClass>arable</RautmannClass>
    <AppliedFields>
        <FromOutput component="PPM" output="AppliedFields"/>
    </AppliedFields>
    <ApplicationDates>
        <FromOutput component="PPM" output="ApplicationDates"/>
    </ApplicationDates>
    <ApplicationRates>
        <FromOutput component="PPM" output="ApplicationRates"/>
    </ApplicationRates>
    <TechnologyDriftReductions>
        <FromOutput component="PPM" output="TechnologyDriftReductions"/>
    </TechnologyDriftReductions>
    <AppliedAreas>
        <FromOutput component="PPM" output="AppliedAreas"/>
    </AppliedAreas>
    <SpatialOutputScale>1sqm</SpatialOutputScale>
    <RandomSeed type="int">0</RandomSeed>
    <MinimumDistanceToField type="float" unit="m">0</MinimumDistanceToField>
    <FilteringLulcTypes type="list[int]"/>
    <FilteringMinWidth type="float" unit="m">999</FilteringMinWidth>
    <FilteringFraction type="float" unit="1">0</FilteringFraction>
    <AgDriftBoomHeight>NA</AgDriftBoomHeight>
    <AgDriftDropletSize>NA</AgDriftDropletSize>
    <AgDriftQuantile type="float" unit="1">0</AgDriftQuantile>
</SprayDrift>
```

### Inputs
* `ProcessingPath` - The working directory for all files exchange with the module. A string with global scale. Value has
  no unit.
* `SimulationStart` - The first date simulated. A `datetime.date` with global scale. Value has no unit.
* `SimulationEnd` - The last date simulated. A `datetime.date` with global scale. Value has no unit.
* `Geometries` - The base geometries of the simulated landscape in WKB representation. A list\[bytes\] with scale
  space/base_geometry. Values have no unit.
* `GeometryCrs` - The coordinate reference system of the geometries, given in PROJ4 notations. A string with global 
  scale. Value has no unit.
* `Extent` - The extent of the simulated region given as four coordinates (x-min, y-min, x-max, y-max). A tuple\[float\]
  with global scale. Values have unit metre.
* `HabitatLulcTypes` - A comma-space separated list of numerical identifiers relating to habitat LULC types. A string
  with global scale. Values have no unit.
* `FieldDistanceSD` - The standard deviation of a normal distribution that varies the field-habitat distance on a 
  per-application basis. A float with global scale. Value has a unit of m.
* `EPDistanceSD` - The standard deviation of a normal distribution that varies the field-habitat distance on a 
  per-exposure path base. A float with global scale. Value has a unit of m.
* `ReportingThreshold` - The smallest exposure that is reported by the module. A float with global scale. Value has a 
  unit of g/ha.
* `ApplySimpleDriftFiltering` - Specifies whether simple drift filtering is simulated. A bool with global scale. Value
  has no unit.
* `LulcTypes` - Indicates the LULC type per spatial unit. A list\[int\] with scale space/base_geometry. Values have no 
  unit.
* `WindDirection` - The wind direction in the landscape. -1 for a random wind direction per application. An int with 
  global scale. Value has a unit of deg.    
* `SprayDriftModel` - The spray-drift model to use. Should be "XSprayDrift", "90thRautmann" or AgDRIFT. A string with 
  global scale. Value has no unit.    
* `SourceExposure` - The exposure reported for applied areas. Either a numeric value or NA. A string with global scale. 
  Value has a unit of g/ha.   
* `RautmannClass` - The Rautmann crop class used by the XSprayDrift and 90thRautmann models. Should be "orchards.late", 
  "orchards.early", "vines", "arable" or "hops". A string with global scale. Value has no unit.   
* `AppliedFields` - The identifiers of the applied fields. A NumPy array with scale other/application. Values have no 
  unit. 
* `AppliedDates` - The dates of application. A NumPy array with scale other/application. Values have no unit.
* `ApplicationRates` - The application rates of the substance. A NumPy array with scale other/application. Values have a
  unit of g/ha. 
* `TechnologyDriftReductions` - The fraction of drift-reduction due to spray-technology. A NumPy array with scale 
  other/application. Values have a unit of 1.
* `AppliedArea` - The spatial extent of applied areas in WKB representation. A list\[bytes\] scale other/application. 
  Values have no unit.
* `SpatialOutputScale` - Defines the spatial output scale, either 1sqm or base_geometry. A string  with global scale. 
  Value has no unit.
* `RandomSeed` - A fixed random seed or 0 for no random seed. An int with global scale. Value has no unit.
* `FilteringLulcTypes` - The LULC types that are able to filter spray-drift. A list\[int\] with global scale. Values
  have no unit.
* `FilteringMinWidth` - The minimum width of vegetation that is needed for drift-filtering to take place. A float with 
  global scale. Value has a unit of m.
* `FilteringFraction` - The fraction of spray-drift tha is filtered by vegetation. A float with global scale. Value has 
  a unit of 1.
* `MinimumDistanceToField` - The minimum distance that a habitat can have from the field edge. A float with global
  scale. Value has a unit of m.
* `AgDriftBoomHeight` - The boom height used by the AgDRIFT model, either high or low. A string with global scale. Value
  has no unit.
* `AgDriftDropletSize` - The droplet size used by the AgDRIFT model, either medium or fine. A string with global scale. 
  Value has no unit.
* `AgDriftQuantile` - The quantile used by the AgDRIFT model, either 0.5 or 0.9. A float with global scale. Value has a
  unit of 1.

### Outputs
The `XSprayDrift` component has only a single output: `Exposure`. It is a NumPy array with scales time/day, 
space/base_geometry or time/day, space_x/1sqm, space_y/1sqm, depending on the selected spatial output scale. It contains
exposure values in the unit of the application rate.


## Roadmap
The `XSprayDrift` component is stable. No further development takes place at the moment.


## Contributing
Contributions are welcome. Please contact the authors (see [Contact](#contact)).


## License
Distributed under the CC0 License. See `LICENSE` for more information.


## Contact
Thorsten Schad - thorsten.schad@bayer.com
Sascha Bub - sascha.bub.ext@bayer.com


## Acknowledgements
* [GDAL](https://pypi.org/project/GDAL)
* [h5py](https://www.h5py.org)
* [NumPy](htps://numpy.org)
