"""Class definition of the SprayDrift component."""
from osgeo import ogr, osr
import datetime
import h5py
import numpy as np
import os
import base
import attrib


class SprayDrift(base.Component):
    """A Landscape Model component that simulates spray-drift using XDrift."""
    # RELEASES
    VERSION = base.VersionCollection(
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

    def __init__(self, name, observer, store):
        """
        Initializes a SprayDrift component.

        Args:
            name: The name of the component.
            observer: The default observer of the component.
            store: The default store of the component.
        """
        super(SprayDrift, self).__init__(name, observer, store)
        self._module = base.Module("XSprayDrift", "2.7", r"module\README.md")
        self._inputs = base.InputContainer(self, [
            base.Input(
                "ProcessingPath",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer),
            base.Input(
                "SimulationStart",
                (attrib.Class(datetime.date, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "SimulationEnd",
                (attrib.Class(datetime.date, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "Geometries",
                (
                    attrib.Class(list[bytes], 1),
                    attrib.Unit(None, 1),
                    attrib.Scales("space/base_geometry", 1)
                ),
                self.default_observer
            ),
            base.Input(
                "GeometryCrs",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "Extent",
                (attrib.Class(tuple[float], 1), attrib.Unit("metre", 1), attrib.Scales("space/extent", 1)),
                self.default_observer
            ),
            base.Input(
                "HabitatTypes",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "FieldDistanceSD",
                (attrib.Class(float, 1), attrib.Unit("m", 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input("EPDistanceSD", (attrib.Class(float, 1), attrib.Unit("m", 1)), self.default_observer),
            base.Input(
                "ReportingThreshold",
                (attrib.Class(float, 1), attrib.Unit("g/ha", 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "ApplySimpleDriftFiltering",
                (attrib.Class(bool, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "LandUseLandCoverTypes",
                (
                    attrib.Class(list[int], 1),
                    attrib.Unit(None, 1),
                    attrib.Scales("space/base_geometry", 1)
                ),
                self.default_observer
            ),
            base.Input(
                "WindDirection",
                (attrib.Class(int, 1), attrib.Unit("deg", 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "SprayDriftModel",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "SourceExposure",
                (attrib.Class(str, 1), attrib.Unit("g/ha", 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "RautmannClass",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "AppliedFields",
                (attrib.Class(np.ndarray, 1), attrib.Unit(None, 1), attrib.Scales("other/application", 1)),
                self.default_observer
            ),
            base.Input(
                "ApplicationDates",
                (attrib.Class(np.ndarray, 1), attrib.Unit(None, 1), attrib.Scales("other/application", 1)),
                self.default_observer
            ),
            base.Input(
                "ApplicationRates",
                (attrib.Class(np.ndarray, 1), attrib.Unit("g/ha", 1), attrib.Scales("other/application", 1)),
                self.default_observer
            ),
            base.Input(
                "TechnologyDriftReductions",
                (attrib.Class(np.ndarray, 1), attrib.Unit("1", 1), attrib.Scales("other/application", 1)),
                self.default_observer
            ),
            base.Input(
                "AppliedAreas",
                (attrib.Class(list[bytes], 1), attrib.Unit(None, 1), attrib.Scales("other/application", 1)),
                self.default_observer
            ),
            base.Input(
                "SpatialOutputScale",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input("RandomSeed", (attrib.Class(int, 1), attrib.Unit(None, 1)), self.default_observer),
            base.Input(
                "FilteringTypes",
                (attrib.Class(list[int], 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "FilteringMinWidth",
                (attrib.Class(float, 1), attrib.Unit("m", 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "FilteringFraction",
                (attrib.Class(float, 1), attrib.Unit("1", 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "MinimumDistanceToField",
                (attrib.Class(float, 1), attrib.Unit("m", 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "AgDriftBoomHeight",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "AgDriftDropletSize",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer
            ),
            base.Input(
                "AgDriftQuantile",
                (attrib.Class(float, 1), attrib.Unit("1", 1), attrib.Scales("global", 1)),
                self.default_observer
            )
        ])
        self._outputs = base.OutputContainer(self, [base.Output("Exposure", store, self)])
        self._application_rate_unit = None

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
        r_exe = os.path.join(os.path.dirname(__file__), "module", "R-3.5.3", "bin", "x64", "Rscript.exe")
        r_script = os.path.join(os.path.dirname(__file__), "module", "SDModel_XSprayDrift_x3df_2.R")
        library_path = os.path.join(os.path.dirname(__file__), "module", "R-3.5.3", "library")
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
            (1, 1), ppm_shapefile, np.dtype(f"S{len(ppm_shapefile)}"))
        f["/data/simulation/region/ppm/shapefile"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/habitat_types"] = np.full(
            (1, 1),
            self.inputs["HabitatTypes"].read().values,
            np.dtype(f"S{len(self.inputs['HabitatTypes'].read().values)}")
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
            np.dtype(f"S{len(self.inputs['SourceExposure'].read().values)}")
        )
        f["/data/simulation/region/spray_drift/params/source_exposure"].attrs["set"] = True
        # noinspection PyTypeChecker
        f["/data/simulation/region/spray_drift/params/pdf_type"] = np.full((1, 1), "gamma", np.dtype("S5"))
        f["/data/simulation/region/spray_drift/params/pdf_type"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/crop"] = np.full(
            (1, 1),
            self.inputs["RautmannClass"].read().values,
            np.dtype(f"S{len(self.inputs['RautmannClass'].read().values)}")
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
            np.dtype(f"S{len(self.inputs['SprayDriftModel'].read().values)}"))
        f["/data/simulation/region/spray_drift/params/model"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/spatial_output_scale"] = np.full(
            (1, 1), spatial_output_scale, np.dtype(f"S{len(spatial_output_scale)}"))
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
            f.create_dataset("/data/day/1sqm/spray_drift/exposure", (simulation_length, raster_cols, raster_rows),
                             np.float32, compression="gzip",
                             chunks=base.chunk_size((1, None, None), (simulation_length, raster_cols, raster_rows)))
        random_seed = self.inputs["RandomSeed"].read().values
        if random_seed is None:
            random_seed = 0
        f["/data/simulation/region/spray_drift/params/random_seed"] = np.full((1, 1), random_seed, np.int)
        f["/data/simulation/region/spray_drift/params/random_seed"].attrs["set"] = True
        if len(self.inputs["FilteringTypes"].read().values) == 0:
            # noinspection PyTypeChecker
            f["/data/simulation/region/spray_drift/params/filtering_types"] = np.full((1, 1), " ", np.dtype("S1"))
        else:
            f["/data/simulation/region/spray_drift/params/filtering_types"] = np.full(
                (1, 1),
                self.inputs["FilteringTypes"].read().values,
                np.dtype(f"S{len(self.inputs['FilteringTypes'].read().values)}")
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
            np.dtype(f"S{len(self.inputs['AgDriftBoomHeight'].read().values)}")
        )
        f["/data/simulation/region/spray_drift/params/boom_height"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/droplet_size"] = np.full(
            (1, 1),
            self.inputs["AgDriftDropletSize"].read().values,
            np.dtype(f"S{len(self.inputs['AgDriftDropletSize'].read().values)}")
        )
        f["/data/simulation/region/spray_drift/params/droplet_size"].attrs["set"] = True
        f["/data/simulation/region/spray_drift/params/ag_drift_quantile"] = np.full((1, 1), self.inputs[
            "AgDriftQuantile"].read().values, np.float32)
        f["/data/simulation/region/spray_drift/params/ag_drift_quantile"].attrs["set"] = True
        f.close()
        self.prepare_ppm_shapefile(ppm_shapefile)
        base.run_process(
            (r_exe, "--vanilla", r_script, x3df_path),
            None,
            self.default_observer,
            {"R_LIBS": library_path, "R_LIBS_USER": library_path}
        )
        f = h5py.File(hdf5)
        if spatial_output_scale == "base_geometry":
            data_set = f["/data/day/base_geometry/spray_drift/exposure"]
            scales = "time/day, space/base_geometry"
        else:
            data_set = f["/data/day/1sqm/spray_drift/exposure"]
            scales = "time/day, space_x/1sqm, space_y/1sqm"
        self.outputs["Exposure"].set_values(
            np.ndarray,
            shape=data_set.shape,
            data_type=data_set.dtype,
            chunks=data_set.chunks,
            scales=scales,
            unit=self._application_rate_unit
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
