"""Class definition of the SprayDrift component."""
from osgeo import ogr, osr
import datetime
import h5py
import numpy as np
import os
import base
import attrib


class SprayDrift(base.Component):
    """
    A Landscape Model component that simulates spray-drift using XDrift. XDrift is an R package that supports the use
    of different spray-drift models (the 90th percentile Rautmann et al. model, AgDrift and XSprayDrift) in a
    landscape-context. It internally represents the landscape as point clouds of (in-field) deposition sources and
    (off-field) deposition sinks in habitats. It models spray-drift exposure trajectories from the sinks in downwind
    direction and adds deposition to the sinks if they are intersected by a trajectory. XDrift also allows to apply
    drift-filtering models, one that is based on a fixed probability density function, and one that is based on
    drift-filtering vegetation that is intersected by exposure trajectories.
    """
    # RELEASES
    VERSION = base.VersionCollection(
        base.VersionInfo("2.5.4", "2023-09-13"),
        base.VersionInfo("2.5.3", "2023-09-12"),
        base.VersionInfo("2.5.2", "2023-09-11"),
        base.VersionInfo("2.5.1", "2022-04-06"),
        base.VersionInfo("2.5.0", "2022-03-11"),
        base.VersionInfo("2.4.1", "2022-03-03"),
        base.VersionInfo("2.4.0", "2021-12-30"),
        base.VersionInfo("2.3.5", "2021-12-10"),
        base.VersionInfo("2.3.4", "2021-12-08"),
        base.VersionInfo("2.3.3", "2021-12-02"),
        base.VersionInfo("2.3.2", "2021-11-29"),
        base.VersionInfo("2.3.1", "2021-11-24"),
        base.VersionInfo("2.3.0", "2021-11-24"),
        base.VersionInfo("2.2.2", "2021-11-18"),
        base.VersionInfo("2.2.1", "2021-10-15"),
        base.VersionInfo("2.2.0", "2021-10-12"),
        base.VersionInfo("2.1.3", "2021-10-11"),
        base.VersionInfo("2.1.2", "2021-09-17"),
        base.VersionInfo("2.1.1", "2021-09-08"),
        base.VersionInfo("2.1.0", "2021-09-06"),
        base.VersionInfo("2.0.9", "2021-09-03"),
        base.VersionInfo("2.0.8", "2021-09-02"),
        base.VersionInfo("2.0.7", "2021-08-17"),
        base.VersionInfo("2.0.6", "2021-08-05"),
        base.VersionInfo("2.0.5", "2021-07-19"),
        base.VersionInfo("2.0.4", "2021-07-19"),
        base.VersionInfo("2.0.3", "2021-06-21"),
        base.VersionInfo("2.0.2", "2020-12-07"),
        base.VersionInfo("2.0.1", "2020-12-03"),
        base.VersionInfo("2.0.0", "2020-10-22"),
        base.VersionInfo("1.3.35", "2020-08-12"),
        base.VersionInfo("1.3.33", "2020-07-30"),
        base.VersionInfo("1.3.27", "2020-05-20"),
        base.VersionInfo("1.3.24", "2020-04-02"),
        base.VersionInfo("1.3.5", "2020-01-08"),
        base.VersionInfo("1.3.3", "2019-12-15"),
        base.VersionInfo("1.2.37", None),
        base.VersionInfo("1.2.35", None),
        base.VersionInfo("1.2.33", None),
        base.VersionInfo("1.2.32", None),
        base.VersionInfo("1.2.26", None),
        base.VersionInfo("1.2.25", None),
        base.VersionInfo("1.2.23", None),
        base.VersionInfo("1.2.20", None),
        base.VersionInfo("1.2.16", None),
        base.VersionInfo("1.2.15", None),
        base.VersionInfo("1.2.12", None),
        base.VersionInfo("1.2.11", None),
        base.VersionInfo("1.2.9", None),
        base.VersionInfo("1.2.8", None),
        base.VersionInfo("1.2.7", None),
        base.VersionInfo("1.1.6", None),
        base.VersionInfo("1.1.5", None),
        base.VersionInfo("1.1.4", None),
        base.VersionInfo("1.1.1", None)
    )

    # CHANGELOG
    VERSION.added("1.1.1", "components.SprayDrift component")
    VERSION.changed("1.1.4", "components.SprayDrift requires input 'SprayDriftModel'")
    VERSION.changed("1.1.5", "components.SprayDrift stores metadata of PEC")
    VERSION.changed("1.1.5", "components.SprayDrift source exposure is an input parameter again")
    VERSION.changed("1.2.7", "components.SprayDrift updated to module version 1.1")
    VERSION.changed("1.2.8", "components.SprayDrift updated to module version 1.2")
    VERSION.changed("1.2.9", "components.SprayDrift updated to module version 1.3")
    VERSION.changed("1.2.11", "components.SprayDrift updated to module version 1.4")
    VERSION.changed("1.2.12", "Rautmann crop class can be parameterized in components.SprayDrift component")
    VERSION.fixed("1.2.15", "components.SprayDrift updated to module version 1.5")
    VERSION.changed("1.2.16", "components.SprayDrift updated to module version 1.6")
    VERSION.fixed("1.2.20", "components.SprayDrift allows 16bit land-use / land-cover type codes")
    VERSION.changed("1.2.20", "components.SprayDrift updated to module version 1.7")
    VERSION.changed("1.2.23", "components.SprayDrift update to module version 1.8")
    VERSION.changed("1.2.25", "components.SprayDrift RandomSeed parameter added")
    VERSION.changed("1.2.25", "components.SprayDrift updated to module version 1.9")
    VERSION.changed("1.2.26", "components.SprayDrift updated to module version 1.10")
    VERSION.changed("1.2.32", "components.SprayDrift updated to module version 1.11")
    VERSION.changed("1.2.33", "components.SprayDrift updated to module version 1.12")
    VERSION.changed("1.2.35", "components.SprayDrift updated to module version 1.13")
    VERSION.changed("1.2.35", "components.SprayDrift MinimumDistance became parameter")
    VERSION.changed("1.2.37", "Specified HDF5 file mode in components.SprayDrift")
    VERSION.changed("1.3.3", "components.SprayDrift updated to module version 1.14")
    VERSION.changed("1.3.5", "component.SprayDrift updated to module version 1.15")
    VERSION.changed("1.3.24", "component.SprayDrift uses base function to call module")
    VERSION.changed("1.3.27", "Removed unused inputs from component.SprayDrift")
    VERSION.changed("1.3.27", "component.SprayDrift updated to module version 2.0")
    VERSION.changed("1.3.33", "component.SprayDrift checks input types strictly")
    VERSION.changed("1.3.33", "component.SprayDrift checks for physical units")
    VERSION.changed("1.3.33", "component.SprayDrift reports physical units to the data store")
    VERSION.changed("1.3.33", "component.SprayDrift checks for scales")
    VERSION.changed("1.3.35", "component.SprayDrift sets R_LIBS and R_LIBS_USER environment variables")
    VERSION.changed("2.0.0", "First independent release")
    VERSION.added("2.0.1", "Changelog and release history")
    VERSION.changed("2.0.1", "Runtime environment moved to module sub-folder")
    VERSION.changed("2.0.1", "Updated to module version 2.1")
    VERSION.added("2.0.1", "README, LICENSE, CHANGELOG, CONTRIBUTING")
    VERSION.changed("2.0.2", "Line separators in LICENSE")
    VERSION.changed("2.0.2", "Corrections in changelog and in README")
    VERSION.changed("2.0.3", "Updated the documentation and the datatype access")
    VERSION.changed("2.0.4", "Updated the module to version 2.2")
    VERSION.changed("2.0.5", "Updated the module to version 2.3")
    VERSION.changed("2.0.6", "Renamed component and module `LICENSE.txt` to `LICENSE` ")
    VERSION.fixed("2.0.6", "Spelling errors in component `README` and module `CHANGELOG` ")
    VERSION.fixed("2.0.7", "Broken link in module documentation")
    VERSION.changed("2.0.8", "Acknowledged default access mode for HDF files")
    VERSION.changed("2.0.9", "Updated the module to version 2.4")
    VERSION.changed("2.1.0", "Updated the module to version 2.5")
    VERSION.changed("2.1.1", "Updated the module to version 2.6")
    VERSION.changed("2.1.2", "Make use of generic types for class attributes")
    VERSION.changed("2.1.3", "Replaced legacy format strings by f-strings")
    VERSION.changed("2.2.0", "Updated module to version 2.7")
    VERSION.changed("2.2.0", "Switched to Google docstring style")
    VERSION.changed("2.2.1", "Set working directory for module call")
    VERSION.changed("2.2.2", "Reports element names of Exposure output if working at `base_geometry` scale")
    VERSION.changed("2.3.0", "Updated module to version 3.0")
    VERSION.changed("2.3.1", "Updated module to version 3.1")
    VERSION.changed("2.3.2", "Updated module to version 3.2")
    VERSION.changed("2.3.3", "Updated module to version 3.3")
    VERSION.changed("2.3.4", "Updated module to version 3.4")
    VERSION.changed("2.3.5", "Updated module to version 3.5")
    VERSION.changed("2.3.5", "Specifies offset of outputs")
    VERSION.changed("2.4.0", "Updated module to version 3.6")
    VERSION.changed("2.4.0", "Changed scale order of exposure output")
    VERSION.changed("2.4.1", "Mitigated weak code warnings")
    VERSION.changed("2.5.0", "Updated module to version 3.7")
    VERSION.changed("2.5.1", "Reverted to version 2.4.1")
    VERSION.added("2.5.2", "Information on runtime environment")
    VERSION.changed("2.5.3", "Extended module information for R runtime environment")
    VERSION.added("2.5.3", "Creation of repository info during documentation")
    VERSION.added("2.5.3", "Repository info to module")
    VERSION.added("2.5.3", "Repository info to R runtime environment")
    VERSION.added("2.5.4", "Scales to `EPDistanceSD` and `RandomSeed` inputs")
    VERSION.changed("2.5.4", "Report geometries of Exposure output if output scale is base_geometry")

    def __init__(self, name, observer, store):
        """
        Initializes a SprayDrift component.

        Args:
            name: The name of the component.
            observer: The default observer of the component.
            store: The default store of the component.
        """
        super(SprayDrift, self).__init__(name, observer, store)
        self._module = base.Module(
            "XSprayDrift",
            "3.6",
            "module",
            r"module\README.md",
            base.Module(
                "R",
                "4.1.2",
                "module/R-4.1.2",
                "module/R-4.1.2/README",
                None,
                True,
                "module/R-4.1.2/doc/NEWS"
            )
        )
        self._inputs = base.InputContainer(self, [
            base.Input(
                "ProcessingPath",
                (attrib.Class(str), attrib.Unit(None), attrib.Scales("global")),
                self.default_observer,
                description="The path in the file system where the component can store temporary working data. The "
                            "path will be created during the run of the component and is not allowed to previously "
                            "exist."
            ),
            base.Input(
                "SimulationStart",
                (attrib.Class(datetime.date), attrib.Unit(None), attrib.Scales("global")),
                self.default_observer,
                description="The first date for which spray-drift exposure is simulated. This should be a date before "
                            "the earliest application date in the `ApplicationDates` input."
            ),
            base.Input(
                "SimulationEnd",
                (attrib.Class(datetime.date), attrib.Unit(None), attrib.Scales("global")),
                self.default_observer,
                description="The last date (inclusive) for which spray-drift exposure is simulated. This should be a "
                            "date after the latest application date in the `ApplicationDates` input."
            ),
            base.Input(
                "Geometries",
                (attrib.Class(list[bytes]), attrib.Unit(None), attrib.Scales("space/base_geometry")),
                self.default_observer,
                description="A geospatial representation of landscape elements in Well-Known-Byte representation. "
                            "Landscape elements should include at least fields that are targets of spray-applications, "
                            "habitats that potentially receive spray-drift deposition and landscape features that "
                            "have the potential to reduce downwind spray-drift deposition. The input may also include "
                            "other landscape elements that have no relevance for spray-drift simulation."
            ),
            base.Input(
                "GeometryCrs",
                (attrib.Class(str), attrib.Unit(None), attrib.Scales("global")),
                self.default_observer,
                description="The definition of the spatial coordinate reference systems in which the landscape "
                            "elements in the `Geometries` input are represented. The coordinate system must be given "
                            "in its Well-Known-Text representation. This input will be removed in a future version of "
                            "`XSprayDrift`."
            ),
            base.Input(
                "Extent",
                (attrib.Class(tuple[float]), attrib.Unit("metre"), attrib.Scales("space/extent")),
                self.default_observer,
                description="The geographic extent for which spray-drift exposure should be simulated. This input "
                            "defines the extent of the 1-square meter `Exposure` output. The extent must be given in "
                            "coordinate reference system given in the `GeometryCrs` input and must follow the format "
                            "`x-min`, `x-max`, `y-min`, `y-max`."
            ),
            base.Input(
                "HabitatTypes",
                (attrib.Class(str), attrib.Unit(None), attrib.Scales("global")),
                self.default_observer,
                description="A list of land use and land cover classes that should be considered habitats. Only "
                            "1-square meter cells within geometries in the `Geometries` input that are of the listed "
                            "types according to the `LandUseLandCoverTypes` input will receive spray-drift exposure, "
                            "if they are located in a downwind trajectory of the exposure sources. All other square "
                            "meters that are not of a habitat type (and are not within an applied area), will report "
                            "an exposure of 0 for every day."
            ),
            base.Input(
                "FieldDistanceSD",
                (attrib.Class(float), attrib.Unit("m"), attrib.Scales("global")),
                self.default_observer,
                description="Setting the `FieldDistanceSD` to a value greater than 0 varies the distances from the "
                            "source points of exposure along the boundary of the applied geometries (see `Geometries` "
                            "input) to the receptors of exposure in the habitats (see `HabitatTypes` input) by a "
                            "normal distribution with mean 0 and the given value as standard deviation at the field "
                            "scale. Setting the input to a value of 0 results in the unaltered usage of the distances "
                            "as calculated by the geospatial operations."
            ),
            base.Input(
                "EPDistanceSD",
                (attrib.Class(float), attrib.Unit("m"), attrib.Scales("global")),
                self.default_observer,
                description="Setting the `EPDistanceSD` to a value greater than 0 varies the distances from the "
                            "source points of exposure along the boundary of the applied geometries (see `Geometries` "
                            "input) to the receptors of exposure in the habitats (see `HabitatTypes` input) by a "
                            "normal distribution with mean 0 and the given value as standard deviation at the exposure "
                            "path scale. This scale describes the variation of exposure along the field boundary, "
                            "typically in bands of 3m width. The variation at the exposure path scale is superimposed "
                            "to the variation applied at the field scale (see `FieldDistanceSD`)."
            ),
            base.Input(
                "ReportingThreshold",
                (attrib.Class(float), attrib.Unit("g/ha"), attrib.Scales("global")),
                self.default_observer,
                description="Setting the `ReportingThreshold` input to a value greater than 0 results in exposure less "
                            "than this value being reported as 0. This avoids reporting very small concentrations that "
                            "can appear as numerical artifacts, but care should be taken not to truncate relevant "
                            "exposure concentrations."
            ),
            base.Input(
                "ApplySimpleDriftFiltering",
                (attrib.Class(bool), attrib.Unit(None), attrib.Scales("global")),
                self.default_observer,
                description="The `ApplySimpleDriftFiltering` input defines whether a simple drift filtering model is "
                            "applied for the simulation of spray-drift exposure. If set to `True`, a fixed "
                            "probabilistic function is applied per 3m exposure band along the field boundary which "
                            "reduces drift deposition by a fixed amount: by 25% with 4.4% probability, by 50% with "
                            "22.2% probability, by 75% with 33.3% probability, and by 90% with 40.0% probability."
            ),
            base.Input(
                "LandUseLandCoverTypes",
                (attrib.Class(list[int]), attrib.Unit(None), attrib.Scales("space/base_geometry")),
                self.default_observer,
                description="Associates each geometry in the `Geometries` input with a land use/land cover type. The "
                            "type is used to decide whether the geometry is a habitat (see input `HabitatTypes`) and, "
                            "if `ApplySimpleDriftFiltering` is set to `True`, whether it is a drift-filtering "
                            "landscape feature."
            ),
            base.Input(
                "WindDirection",
                (attrib.Class(int), attrib.Unit("deg"), attrib.Scales("global")),
                self.default_observer,
                description="Sets a wind direction at a global scale, i.e., direction of wind is always and everywhere "
                            "the value of this input. Wind direction is given in a meteorological notation, i.e., as "
                            "the direction where the wind is blowing from. For instance, a value of `270` would "
                            "describe wind that is blowing from West to East. If you specify the `WindDirection` as "
                            "`-1`, the spray-drift component will sample a random wind-direction at an application "
                            "scale based on a uniform distribution across the windrose."
            ),
            base.Input(
                "SprayDriftModel",
                (
                    attrib.Class(str),
                    attrib.Unit(None),
                    attrib.Scales("global"),
                    attrib.InList(("XSprayDrift", "90thRautmann", "AgDrift"))
                ),
                self.default_observer,
                description="The `SprayDriftModel` input defines which model is used by the `XSprayDrift` to calculate "
                            "the fraction of drift that deposits at a given distance from the field boundary. The "
                            "`90thRautmann` model uses the deterministic values derived by the work of Rautmann et al. "
                            "and that are used during lower-tier regulatory risk assessment. They represent the 90th "
                            "percentile of drift-deposition found during a series of field trials in different types "
                            "of crops (see `RautmannClass` input). The `XSprayDrift` model is based on the same "
                            "empirical data of the Rautmann et al. field trials, but preserves variability by "
                            "representing drift-deposition as probability density functions. For each band of 3m along "
                            "the field edge, a quantile is uniformly sampled, and all sinks along the trajectory of "
                            "this band receive spray-drift deposition according to the sampled quantile and the "
                            "distance-dependent probability density function. The `AgDrift` model represents the "
                            "deposition as assumed in the US regulatory risk assessment."
            ),
            base.Input(
                "SourceExposure",
                (attrib.Class(str), attrib.Unit("g/ha"), attrib.Scales("global")),
                self.default_observer,
                description="The `SourceExposure` input specify, which spray-drift depositions are reported by the "
                            "`XSprayDrift` component for the 1-square meter cells that are located within applied "
                            "areas. A value of `NA` or `0` does not report any spray-drift deposition for these cells. "
                            "Another sensible value would be the application rate, resulting in the deposition of the "
                            "applied 1-square meter cells as being reported as the according value."
            ),
            base.Input(
                "RautmannClass",
                (
                    attrib.Class(str),
                    attrib.Unit(None),
                    attrib.Scales("global"),
                    attrib.InList(("arable", "vines", "orchards.early", "orchards.late", "hops"))
                ),
                self.default_observer,
                description="If using the `XSprayDrift` or `Rautmann90th` model as `SprayDriftModel`, the value of the "
                            "`RautmannClass` specifies which series of field trial data is used for the "
                            "distance-dependant calculation of spray-drift exposure. The `RautmannClass` should fit "
                            "the characteristics of the actual applied crops during simulation."
            ),
            base.Input(
                "AppliedFields",
                (attrib.Class(np.ndarray), attrib.Unit(None), attrib.Scales("other/application")),
                self.default_observer,
                description="The names of the applied fields. This information was used to link applications to "
                            "individual fields, but is no longer used. The `AppliedFields` input will therefore be "
                            "removed from the `XSprayDrift` component in a future version."
            ),
            base.Input(
                "ApplicationDates",
                (attrib.Class(np.ndarray), attrib.Unit(None), attrib.Scales("other/application")),
                self.default_observer,
                description="The dates when the applications take place. Dates are represented as the number of days "
                            "since the 1st January of the year 0."
            ),
            base.Input(
                "ApplicationRates",
                (attrib.Class(np.ndarray), attrib.Unit("g/ha"), attrib.Scales("other/application")),
                self.default_observer,
                description="The rates at which the substance is applied. Because the `XSprayDrift` component operates "
                            "with fractions of the application rates, regardless of their physical unit, the "
                            "`Exposure` output will have the same unit as the `ApplicationRates` input."
            ),
            base.Input(
                "TechnologyDriftReductions",
                (attrib.Class(np.ndarray), attrib.Unit("1"), attrib.Scales("other/application")),
                self.default_observer,
                description="The drift reduction by the equipment used for spray-applications is expressed as a number "
                            "between `0` and `1` that specifies by which fraction the simulated drift-deposition is "
                            "reduced prior reporting. A value of `0` results in no drift-reduction and the reporting "
                            "of depositions as output by the spray-drift model, whereas a value of `1` would indicate "
                            "that spray-drift deposition is entirely prevented by technology, resulting in the "
                            "reporting of depositions of `0`."
            ),
            base.Input(
                "AppliedAreas",
                (attrib.Class(list[bytes]), attrib.Unit(None), attrib.Scales("other/application")),
                self.default_observer,
                description="The areas that receive spray-applications, given in Well-Known-Byte representation. "
                            "Internally, the areas will be rasterized at a 1-square meter resolution and the raster "
                            "cells forming the inner boundary of the areas will be considered as individual source "
                            "points of spray-drift exposure."
            ),
            base.Input(
                "SpatialOutputScale",
                (
                    attrib.Class(str),
                    attrib.Unit(None),
                    attrib.Scales("global"),
                    attrib.InList(("1sqm", "base_geometry"))
                ),
                self.default_observer,
                description="The native spatial output scale of the `XSprayDrift` component is one square-meter. That "
                            "is spray-deposition is by default reported as a 1-square meter raster across the "
                            "landscape, as defined by the `Extent` input. However, the component is also able to "
                            "provide spray-deposition on a base_geometry scale. In this case, deposition is reported "
                            "for every geometry in the `Geometries` input by calculating the average deposition over "
                            "all 1-square meter cells within the geometry. Geometries that are not associated with a "
                            "habitat type (see `HabitatTypes` input) according to the `LandUseLandCoverTypes` input "
                            "do not receive any spray-drift depositions and a value of `0` is reported for them."
            ),
            base.Input(
                "RandomSeed",
                (attrib.Class(int), attrib.Unit(None), attrib.Scales("global")),
                self.default_observer,
                description="Allows to fix a seed for the random sampling of wind directions and deposition quantiles "
                            "if the `WindDirection` input is set tp `-1` or `XSprayDrift` is used as spray-drift model "
                            "(see `SprayDriftModel` input). Fixing the seed can help for debugging or demonstration "
                            "purposes. A value of `0` is not used as seed but results in a randomly sampled seed."
            ),
            base.Input(
                "FilteringTypes",
                (attrib.Class(list[int]), attrib.Unit(None), attrib.Scales("global")),
                self.default_observer,
                description="The `FilteringTypes` specifies types of landscape elements, as defined by the "
                            "`LandUseLandCoverTypes`, that are able to reduce downwind spray-drift depositions through "
                            "filtering, e.g., hedges. Individual trajectories of exposure, originating at source "
                            "points and pointing in downwind direction, are geometrically intersected with the "
                            "geometries of the landscape elements. If a trajectory thereby intersects with an element "
                            "having one of the filtering types as listed in the `FilteringTypes` input, "
                            "drift-filtering may occur, depending on the values of the `FilterMinWidth` and "
                            "`FilteringFraction` inputs."
            ),
            base.Input(
                "FilteringMinWidth",
                (attrib.Class(float), attrib.Unit("m"), attrib.Scales("global")),
                self.default_observer,
                description="The `FilteringMinWidth` defines a minimum length that an exposure trajectory must "
                            "intersect a filtering landscape element (see `FilteringTypes` input), before it is "
                            "actually considered for a drift-filtering effect."
            ),
            base.Input(
                "FilteringFraction",
                (attrib.Class(float), attrib.Unit("1"), attrib.Scales("global")),
                self.default_observer,
                description="The value of the `FilteringFraction` specifies the magnitude of the filter effect if "
                            "filtering takes place (see `FilteringTypes` and `FilteringMinWidth` inputs). All 1-square "
                            "meter cells along the spray-drift trajectory which are located downwind will receive a "
                            "deposition reduced according to the `FilteringFraction` value. A value of `0` thereby "
                            "results in no drift-filtering at all, a value of `1` in complete filtering, i.e., "
                            "downwind cells will receive no deposition at all. Values outside the range of `0` and `1` "
                            "are not allowed."
            ),
            base.Input(
                "MinimumDistanceToField",
                (attrib.Class(float), attrib.Unit("m"), attrib.Scales("global")),
                self.default_observer,
                description="This input defines a lower threshold for distances between sources of exposure (within "
                            "applied areas) and sinks of exposure (within habitats). If the distance between source "
                            "and sink, according to geometrical operations and possibly the application of a "
                            "probabilistic function (see `FieldDistanceSD` and `EPDistanceSD` inputs), is less than "
                            "the value of the `MinimumDistanceToField`, the distance is treated for the purpose of "
                            "calculating drift-deposition as the value of the input. The minimum distance is only "
                            "applied to sinks whose determined distance is larger than `0`."
            ),
            base.Input(
                "AgDriftBoomHeight",
                (attrib.Class(str), attrib.Unit(None), attrib.Scales("global"), attrib.InList(("low", "high"))),
                self.default_observer,
                description="Specifies the boom height for the AgDRIFT model. This input is only in use, if `AgDrift` "
                            "is used as value of the `SprayDriftModel` input."
            ),
            base.Input(
                "AgDriftDropletSize",
                (attrib.Class(str), attrib.Unit(None), attrib.Scales("global"), attrib.InList(("fine", "medium"))),
                self.default_observer,
                description="Specifies the droplet size spectrum for the AgDRIFT model. This input is only in use, if "
                            "`AgDrift` is used as value of the `SprayDriftModel` input."
            ),
            base.Input(
                "AgDriftQuantile",
                (attrib.Class(float), attrib.Unit("1"), attrib.Scales("global"), attrib.InList((.5, .9))),
                self.default_observer,
                description="Specifies the quantile for the AgDRIFT model. This input is only in use, if `AgDrift` "
                            "is used as value of the `SprayDriftModel` input."
            )
        ])
        self._outputs = base.OutputContainer(self, [base.Output("Exposure", store, self)])
        self._application_rate_unit = None
        if self.default_observer:
            self.default_observer.write_message(
                2,
                "XSprayDrift currently does not check the identity of applications",
                "Make sure that inputs of scale other/application retrieve data in the same application-order"
            )
            self.default_observer.write_message(
                3,
                "The GeometryCrs input will be removed in a future version of the XSprayDrift component",
                "The CRS will be retrieved from the metadata of the Geometries input"
            )
            self.default_observer.write_message(
                3,
                "The AppliedFields input will be removed in a future version of the XSprayDrift component",
                "It is no longer needed and will be removed without replacement"
            )

    def run(self):
        """
        Runs the component.

        Returns:
            Nothing.
        """
        processing_path = self.inputs["ProcessingPath"].read().values
        simulation_start = self.inputs["SimulationStart"].read().values
        simulation_end = self.inputs["SimulationEnd"].read().values
        simulation_length = (simulation_end - simulation_start).days + 1
        geometries = self.inputs["Geometries"].read().values
        crs = self.inputs["GeometryCrs"].read().values
        extent = self.inputs["Extent"].read().values
        raster_cols = int(round(extent[1] - extent[0]))
        raster_rows = int(round(extent[3] - extent[2]))
        x3df_path = os.path.join(processing_path, "sim.x3df")
        geom_path = os.path.join(x3df_path, "geom")
        # noinspection SpellCheckingInspection
        r_exe = os.path.join(os.path.dirname(__file__), "module", "R-4.1.2", "bin", "x64", "Rscript.exe")
        r_script = os.path.join(os.path.dirname(__file__), "module", "SDModel_XSprayDrift_x3df_2.R")
        library_path = os.path.join(os.path.dirname(__file__), "module", "R-4.1.2", "library")
        base_shapefile = os.path.join(geom_path, "base.shp")
        ppm_shapefile = os.path.join(processing_path, "ppm.shp")

        try:
            os.makedirs(geom_path)
        except FileExistsError:
            raise FileExistsError(f"Cannot run spray-drift in a path that already exists: {processing_path}")

        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromWkt(crs)
        ogr_driver = ogr.GetDriverByName("ESRI Shapefile")
        ogr_data_set = ogr_driver.CreateDataSource(base_shapefile)
        ogr_layer = ogr_data_set.CreateLayer("geom", spatial_reference, ogr.wkbPolygon)
        ogr_layer_definition = ogr_layer.GetLayerDefn()
        for i in range(len(geometries)):
            feature = ogr.Feature(ogr_layer_definition)
            feature.SetGeometry(ogr.CreateGeometryFromWkb(geometries[i]))
            ogr_layer.CreateFeature(feature)
        del ogr_layer_definition, ogr_layer, ogr_data_set, ogr_driver

        hdf5 = os.path.join(x3df_path, "arr.dat")
        f = h5py.File(hdf5, "a")
        f.create_group("/dims/time").attrs["id"] = 0
        f.create_dataset("/scales/0/simulation", (1,), np.float32)
        day = f.create_dataset("/scales/0/day", (simulation_length,), np.float32)
        day.attrs["transform"] = "Day"
        day.attrs["t_offset"] = (simulation_start - datetime.datetime.utcfromtimestamp(0).date()).days
        f.create_group("/dims/space").attrs["id"] = 1
        f.create_dataset("/scales/1/region", (1,), np.float32)
        f.create_dataset("/scales/1/base_geometry", (len(geometries),), np.float32).attrs["geometries"] = "base.shp"
        sqm = f.create_dataset("/scales/1/1sqm", (raster_cols, raster_rows), np.float32)
        sqm.attrs["transform"] = "Geographic"
        sqm.attrs["t_offset"] = [extent[0], extent[2]]
        spatial_output_scale = self.inputs["SpatialOutputScale"].read().values
        # noinspection PyTypeChecker
        f["/data/simulation/region/ppm/shapefile"] = np.full(
            (1, 1), ppm_shapefile, np.core.dtype(f"S{len(ppm_shapefile)}"))
        f["/data/simulation/region/ppm/shapefile"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/habitat_types"] = np.full(
            (1, 1),
            self.inputs["HabitatTypes"].read().values,
            np.core.dtype(f"S{len(self.inputs['HabitatTypes'].read().values)}")
        )
        f["/data/simulation/region/spray_drift/params/habitat_types"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/ep_width"] = np.full((1, 1), 3, np.float32)
        f["/data/simulation/region/spray_drift/params/ep_width"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/max_angular_deviation"] = np.full((1, 1), 0, np.float32)
        f["/data/simulation/region/spray_drift/params/max_angular_deviation"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/field_dist_sd"] = np.full((1, 1), self.inputs[
            "FieldDistanceSD"].read().values, np.float32)
        f["/data/simulation/region/spray_drift/params/field_dist_sd"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/ep_dist_sd"] = np.full((1, 1),
                                                                             self.inputs["EPDistanceSD"].read().values,
                                                                             np.float32)
        f["/data/simulation/region/spray_drift/params/ep_dist_sd"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/min_dist"] = np.full((1, 1), self.inputs[
            "MinimumDistanceToField"].read().values, np.float32)
        f["/data/simulation/region/spray_drift/params/min_dist"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/source_exposure"] = np.full(
            (1, 1),
            self.inputs["SourceExposure"].read().values,
            np.core.dtype(f"S{len(self.inputs['SourceExposure'].read().values)}")
        )
        f["/data/simulation/region/spray_drift/params/source_exposure"].attrs["set"] = True
        # noinspection PyTypeChecker
        f["/data/simulation/region/spray_drift/params/pdf_type"] = np.full((1, 1), "gamma", np.core.dtype("S5"))
        f["/data/simulation/region/spray_drift/params/pdf_type"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/crop"] = np.full(
            (1, 1),
            self.inputs["RautmannClass"].read().values,
            np.core.dtype(f"S{len(self.inputs['RautmannClass'].read().values)}")
        )
        f["/data/simulation/region/spray_drift/params/crop"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/reporting_threshold"] = np.full((1, 1), self.inputs[
            "ReportingThreshold"].read().values, np.float32)
        f["/data/simulation/region/spray_drift/params/reporting_threshold"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/apply_simple1_drift_filtering"] = np.full((1, 1), self.inputs[
            "ApplySimpleDriftFiltering"].read().values, np.bool)
        f["/data/simulation/region/spray_drift/params/apply_simple1_drift_filtering"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/model"] = np.full(
            (1, 1),
            self.inputs["SprayDriftModel"].read().values,
            np.core.dtype(f"S{len(self.inputs['SprayDriftModel'].read().values)}"))
        f["/data/simulation/region/spray_drift/params/model"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/spatial_output_scale"] = np.full(
            (1, 1), spatial_output_scale, np.core.dtype(f"S{len(spatial_output_scale)}"))
        f["/data/simulation/region/spray_drift/params/spatial_output_scale"].attrs["set"] = True
        f["/data/simulation/base_geometry/landscape/feature_type"] = np.full(
            (1, len(geometries)), self.inputs["LandUseLandCoverTypes"].read().values, np.uint16)
        f["/data/simulation/base_geometry/landscape/feature_type"].attrs["set"] = True
        f["/data/simulation/region/weather/wind_direction"] = np.full((1, 1),
                                                                      self.inputs["WindDirection"].read().values,
                                                                      np.uint16)
        f["/data/simulation/region/weather/wind_direction"].attrs["set"] = True
        if spatial_output_scale == "base_geometry":
            f.create_dataset("/data/day/base_geometry/spray_drift/exposure", (simulation_length, len(geometries)),
                             np.float32, compression="gzip", chunks=(simulation_length, 1))
        else:
            f.create_dataset(
                "/data/day/1sqm/spray_drift/exposure",
                (raster_rows, raster_cols, simulation_length),
                np.float32,
                compression="gzip",
                chunks=base.chunk_size((None, None, 1), (raster_rows, raster_cols, simulation_length))
            )
        random_seed = self.inputs["RandomSeed"].read().values
        if random_seed is None:
            random_seed = 0
        f["/data/simulation/region/spray_drift/params/random_seed"] = np.full((1, 1), random_seed, np.int)
        f["/data/simulation/region/spray_drift/params/random_seed"].attrs["set"] = True
        if len(self.inputs["FilteringTypes"].read().values) == 0:
            # noinspection PyTypeChecker
            f["/data/simulation/region/spray_drift/params/filtering_types"] = np.full((1, 1), " ", np.core.dtype("S1"))
        else:
            f["/data/simulation/region/spray_drift/params/filtering_types"] = np.full(
                (1, 1),
                self.inputs["FilteringTypes"].read().values,
                np.core.dtype(f"S{len(self.inputs['FilteringTypes'].read().values)}")
            )
        f["/data/simulation/region/spray_drift/params/filtering_types"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/filtering_min_width"] = np.full((1, 1), self.inputs[
            "FilteringMinWidth"].read().values, np.float32)
        f["/data/simulation/region/spray_drift/params/filtering_min_width"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/filtering_fraction"] = np.full((1, 1), self.inputs[
            "FilteringFraction"].read().values, np.float32)
        f["/data/simulation/region/spray_drift/params/filtering_fraction"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/boom_height"] = np.full(
            (1, 1),
            self.inputs["AgDriftBoomHeight"].read().values,
            np.core.dtype(f"S{len(self.inputs['AgDriftBoomHeight'].read().values)}")
        )
        f["/data/simulation/region/spray_drift/params/boom_height"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/droplet_size"] = np.full(
            (1, 1),
            self.inputs["AgDriftDropletSize"].read().values,
            np.core.dtype(f"S{len(self.inputs['AgDriftDropletSize'].read().values)}")
        )
        f["/data/simulation/region/spray_drift/params/droplet_size"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/ag_drift_quantile"] = np.full((1, 1), self.inputs[
            "AgDriftQuantile"].read().values, np.float32)
        f["/data/simulation/region/spray_drift/params/ag_drift_quantile"].attrs["set"] = True
        f.close()
        self.prepare_ppm_shapefile(ppm_shapefile)
        base.run_process(
            (r_exe, "--vanilla", r_script, x3df_path),
            processing_path,
            self.default_observer,
            {"R_LIBS": library_path, "R_LIBS_USER": library_path}
        )
        f = h5py.File(hdf5)
        if spatial_output_scale == "base_geometry":
            data_set = f["/data/day/base_geometry/spray_drift/exposure"]
            scales = "time/day, space/base_geometry"
            element_names = (None, self.inputs["Geometries"].describe()["element_names"][0])
            offset = (simulation_start, None)
            geometries= (None, self.inputs["Geometries"].describe()["geometries"][0])
        else:
            data_set = f["/data/day/1sqm/spray_drift/exposure"]
            scales = "space_y/1sqm, space_x/1sqm, time/day"
            element_names = None
            offset = (extent[2], extent[0], simulation_start)
            geometries = (None, None, None)
        self.outputs["Exposure"].set_values(
            np.ndarray,
            shape=data_set.shape,
            data_type=data_set.dtype,
            chunks=data_set.chunks,
            scales=scales,
            unit=self._application_rate_unit,
            element_names=element_names,
            offset=offset,
            geometries=geometries
        )
        for chunk in base.chunk_slices(data_set.shape, tuple(x * 5 for x in data_set.chunks)):
            self.outputs["Exposure"].set_values(data_set[chunk], slices=chunk, create=False, calculate_max=True)
        f.close()

    def prepare_ppm_shapefile(self, shapefile):
        """
        Prepares the application geometries.

        Args:
            shapefile: The file path of the geometries.

        Returns:
            Nothing.
        """
        crs = self.inputs["GeometryCrs"].read().values
        applied_fields = self.inputs["AppliedFields"].read().values
        application_dates = self.inputs["ApplicationDates"].read().values
        application_rates = self.inputs["ApplicationRates"].read()
        self._application_rate_unit = application_rates.unit
        technology_drift_reductions = self.inputs["TechnologyDriftReductions"].read().values
        geometries = self.inputs["AppliedAreas"].read().values
        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromWkt(crs)
        ogr_driver = ogr.GetDriverByName("ESRI Shapefile")
        ogr_data_set = ogr_driver.CreateDataSource(shapefile)
        ogr_layer = ogr_data_set.CreateLayer("geom", spatial_reference, ogr.wkbPolygon)
        ogr_layer.CreateField(ogr.FieldDefn("Field", ogr.OFTInteger))
        ogr_layer.CreateField(ogr.FieldDefn("Date", ogr.OFTDate))
        ogr_layer.CreateField(ogr.FieldDefn("Rate", ogr.OFTReal))
        ogr_layer.CreateField(ogr.FieldDefn("DriftRed", ogr.OFTReal))
        ogr_layer_definition = ogr_layer.GetLayerDefn()
        for i in range(len(geometries)):
            feature = ogr.Feature(ogr_layer_definition)
            feature.SetField("Field", int(applied_fields[i]))
            feature.SetField("Date", str(datetime.datetime.fromordinal(application_dates[i])))
            feature.SetField("Rate", float(application_rates.values[i]))
            feature.SetField("DriftRed", float(technology_drift_reductions[i]))
            feature.SetGeometry(ogr.CreateGeometryFromWkb(geometries[i]))
            ogr_layer.CreateFeature(feature)
        del ogr_layer_definition, ogr_layer, ogr_data_set, ogr_driver
