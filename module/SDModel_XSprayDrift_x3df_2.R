# Load libraries
library(pbapply)
library(x3df)
library(rgdal)
library(hdf5r)
library(sf)
library(data.table)
library(terra)
library(xdrift)

# General parameterization
params <- list(x3df = commandArgs(TRUE)[1])
pboptions(type = "timer")

# Open the X3df
f <- Database(params$x3df, "r+")

# Get relevant scales
simulation <- f$get_dimension("time")$get_scale("simulation")
day <- f$get_dimension("time")$get_scale("day")
region <- f$get_dimension("space")$get_scale("region")
base_geometry <- f$get_dimension("space")$get_scale("base_geometry")
scale_1sqm <- f$get_dimension("space")$get_scale("1sqm")

# Get values @ simulation/region
ppm_shapefile <-
  f$get_dataset(c(simulation, region), "ppm/shapefile")$get_values()
habitat_lulc_types <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/habitat_types")$get_values()
ep_width <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/ep_width")$get_values()
max_angular_deviation <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/max_angular_deviation")$get_values()
field_dist_sd <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/field_dist_sd")$get_values()
ep_dist_sd <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/ep_dist_sd")$get_values()
min_dist <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/min_dist")$get_values()
source_exposure <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/source_exposure")$get_values()
pdf_type <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/pdf_type")$get_values()
crop <-
  f$get_dataset(c(simulation, region), "spray_drift/params/crop")$get_values()
reporting_threshold <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/reporting_threshold")$get_values()
apply_simple1_drift_filtering <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/apply_simple1_drift_filtering")$get_values()
model_selection <-
    f$get_dataset(c(simulation, region), "spray_drift/params/model")$get_values()
spatial_output_scale <-
    f$get_dataset(c(simulation, region), "spray_drift/params/spatial_output_scale")$get_values()
random_seed <-
    f$get_dataset(c(simulation, region),
                "spray_drift/params/random_seed")$get_values()
filtering_lulc_types <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/filtering_types")$get_values()
filtering_min_width <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/filtering_min_width")$get_values()
filtering_fraction <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/filtering_fraction")$get_values()
boom_height <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/boom_height")$get_values()
droplet_size <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/droplet_size")$get_values()
ag_drift_quantile <-
  f$get_dataset(c(simulation, region),
                "spray_drift/params/ag_drift_quantile")$get_values()


# Get values @ simulation/base_geometry
lulc_type <-
  f$get_dataset(c(simulation, base_geometry), "landscape/feature_type")$get_values()

# Get values @ day/region
wind_direction <-
  f$force_scaling(c(day, region),
                  "weather/wind_direction",
                  c(SimpleDownscaling(f, c(simulation, region))))

# Set seed if specified
if (random_seed != 0) {
  set.seed(random_seed)
}

# Load PPM Shapefile
ppmsf <- readOGR(
  dsn = dirname(ppm_shapefile),
  layer = substr(basename(ppm_shapefile), 1, nchar(basename(ppm_shapefile)) - 4)
)

# Transform dates
first_day <- h5attr(day$.f, "t_offset")
ppmsf@data$tDate <- as.integer(as.Date(ppmsf@data$Date)) - first_day + 1

# Add wind directions to PPMs
ppmsf@data$Wind.dir <- wind_direction[ppmsf@data$tDate, 1]

# Random wind for applications with negative wind direction
ppmsf@data$Wind.dir[ppmsf@data$Wind.dir == 65535] <- sample(0:359, sum(ppmsf@data$Wind.dir == 65535), TRUE)

# Up-scale wind direction into 8-dir wind
ppmsf@data$Wind.dir <- cut(ppmsf@data$Wind.dir, seq(22.5, 360, 45), FALSE)
ppmsf@data$Wind.dir <- ifelse(is.na(ppmsf@data$Wind.dir), 0, ppmsf@data$Wind.dir * 45)

# Get base geometries and habitats
geometries <- base_geometry$get_geometries()
habitat_types <- as.integer(strsplit(habitat_lulc_types, ", ", TRUE)[[1]])
habitats <- st_as_sf(subset(geometries, `%in%`(lulc_type, habitat_types)))

# Get filtering parameters
filtering_types <- as.integer(strsplit(filtering_lulc_types, ", ", TRUE)[[1]])
if (!is.na(filtering_types)) {
  filter_min_width <- as.numeric(filtering_min_width)
  filter_fraction <- as.numeric(filtering_fraction)
  filterveg <- subset(geometries, `%in%`(lulc_type[1,], filtering_types))
}

# Prepare the exposure data
if (spatial_output_scale == "base_geometry") {
  exposure_ds <- f$get_dataset(c(day, base_geometry), "spray_drift/exposure")
} else {
  exposure_ds <- f$get_dataset(c(day, scale_1sqm), "spray_drift/exposure")
  origin <- h5attr(scale_1sqm$.f, "t_offset")
}

# Consider each application individually
exposure <- pblapply(
  1:nrow(ppmsf),
  function(i) {
    applied_geom <- st_as_sf(ppmsf[i,])
    applied_geom_bbox <- matrix(st_bbox(applied_geom), ncol = 2)
    lroi_bbox <- applied_geom_bbox + matrix(c(-50, -50, 50, 50), 2, 2)
    if (spatial_output_scale == "1sqm") {
      lroi_bbox <- lroi_bbox + `%%`(matrix(origin, 2, 2), 1) - `%%`(lroi_bbox, 1)
    }
    lroi_bbox <- matrix(
      c(
        max(lroi_bbox[1, 1], geometries@bbox[1, 1]),
        max(lroi_bbox[2, 1], geometries@bbox[2, 1]),
        min(lroi_bbox[1, 2], geometries@bbox[1, 2]),
        min(lroi_bbox[2, 2], geometries@bbox[2, 2])
      ), 2, 2)
    lroi_bbox_geom <- st_sfc(
      st_polygon(list(cbind(lroi_bbox[1, c(1, 2, 2, 1, 1)], lroi_bbox[2, c(1, 1, 2, 2, 1)]))),
      crs = st_crs(applied_geom)
    )
    inner_buffer <- st_buffer(applied_geom, -2)
    if (!is.null(nrow(inner_buffer))) {
      lroi_habitats <- st_intersection(habitats$geometry, lroi_bbox_geom)
      if (length(lroi_habitats) > 0) {
        r <- rast(
          xmin = lroi_bbox[1,1],
          xmax = lroi_bbox[1,2],
          ymin = lroi_bbox[2,1],
          ymax = lroi_bbox[2,2],
          crs = geometries@proj4string@projargs,
          resolution = 1
        )
        r <- rasterize(vect(lroi_habitats), r, 2)
        r <- rasterize(vect(applied_geom), r, 1, update = TRUE)
        local_roi <- data.table(id = 1:ncell(r), lulc = c(r[]))[!is.nan(lulc)]
        local_roi[, c("x", "y") := .(xFromCell(r, id), yFromCell(r, id))]
        local_roi[, ep := bands(x, y, applied_geom$Wind.dir, ep_width, "meteorological")]
        dist <- local_roi[
          , .(x, y, dist = mindwdist(x, y, applied_geom$Wind.dir, which(lulc == 1), max_angular_deviation)), ep]

        # Distance variability at the field scale
        dist_var_field <- rnorm(1, sd = field_dist_sd)

        # Distance variability at the EP scale
        dist_var <- dist[, .(offset = rnorm(1, sd = ep_dist_sd) + dist_var_field), ep]

        setkey(dist, ep)
        setkey(dist_var, ep)
        dist <- dist_var[dist]
        dist[dist > 0, dist := ifelse(dist + offset > min_dist, dist + offset, min_dist)]
        if (model_selection == "90thRautmann") {
          suppressWarnings(
            exposure_appl <- dist[
              ,
              .(
                x,
                y,
                exposure = rautmann90(
                  dist,
                  target.exposure = as.numeric(source_exposure),
                  crop = crop
                ) * ifelse(
                  apply_simple1_drift_filtering == "TRUE",
                  1 - sample(c(.25, .5, .75, .9), 1, prob = c(.1, .5, .75, .9)),
                  1
                ) * applied_geom$Rate * (1 - applied_geom$DriftRed)
              ),
              ep
            ]
          )
        } else {
          if (model_selection == "AgDRIFT") {
              exposure_appl <- dist[
                ,
                .(
                  x,
                  y,
                  exposure = agdrift.g(
                    dist,
                    droplet_size,
                    round(ag_drift_quantile, 5),
                    boom_height,
                    as.numeric(source_exposure)
                  ) * ifelse(
                    apply_simple1_drift_filtering == "TRUE",
                    1 - sample(c(.25, .5, .75, .9), 1, prob = c(.1, .5, .75, .9)),
                    1
                  ) * applied_geom$Rate * (1 - applied_geom$DriftRed)
                ),
                ep
              ]
          } else {
            if (model_selection == "XSprayDrift") {
              suppressWarnings(
                exposure_appl <- dist[
                  ,
                  .(
                    x,
                    y,
                    exposure = xspraydrift(
                      dist,
                      target.exposure = as.numeric(source_exposure),
                      crop = crop,
                      pdf.type = pdf_type
                    ) * ifelse(
                      apply_simple1_drift_filtering == "TRUE",
                      1 - sample(c(.25, .5, .75, .9), 1, prob = c(.1, .5, .75, .9)),
                      1
                    ) * applied_geom$Rate * (1 - applied_geom$DriftRed)
                  ),
                  ep
                ]
              )
            } else {
              stop(paste("Unknown spray-drift model:", model_selection))
            }
          }
        }

        # Filter values
        exposure_appl <- exposure_appl[exposure >= reporting_threshold]

        # Drift filtering by vegetation
        if (!is.na(filtering_types)) {
          setkeyv(exposure_appl, c("x", "y"))
          setkeyv(dist, c("x", "y"))
          exposure_appl <- dist[exposure_appl][dist > 0]
          exposure_appl[, id := 1:.N]
          eplines <- st_sf(
            geom = st_sfc(
              lapply(split(exposure_appl, by = "id"), function(x) {
                st_linestring(
                  cbind(
                    c(x[, x], x[, sinpi(applied_geom$Wind.dir / 180) * dist + x]),
                    c(x[, y], x[, cospi(applied_geom$Wind.dir / 180) * dist + y])
                  )
                )
              }),
              crs = st_crs(applied_geom)
            ),
            ID = exposure_appl[, id]
          )
          vegintersects <- st_intersection(eplines, filterveg)
          vegintersecttable <- data.table(
            id = vegintersects$ID,
            length = as.numeric(st_length(vegintersects))
          )[, .(vegwidth = sum(length)), keyby = id]
          setkey(exposure_appl, id)
          exposure_appl <- vegintersecttable[exposure_appl]
          exposure_appl[vegwidth >= filter_min_width, exposure := exposure * (1 - filter_fraction)]
        }

        # Save results
        if(spatial_output_scale == "base_geometry") {
          if (nrow(exposure_appl) > 0)
            data.table(
              x = exposure_appl[, x],
              y = exposure_appl[, y],
              t = applied_geom$tDate,
              exposure = exposure_appl[, exposure]
            )
          else
            NULL
        } else {
          if (nrow(exposure_appl) > 0) {
            idx <- exposure_appl[, scale_1sqm$t(cbind(x + 1, y + 1))]
            exposure_appl[, c("i", "j") := .(idx[, 1], idx[, 2])]
            exposure_appl <- exposure_appl[
              `between`(i, 1, exposure_ds$.f$dims[2]) & `between`(j, 1, exposure_ds$.f$dims[3])]
            ll <- exposure_appl[, cbind(min(i), min(j))]
            ru <- exposure_appl[, cbind(max(i), max(j))]
            exposure <- exposure_ds$.f$read(
              list(applied_geom$tDate, ll[1,1]:(ru[1,1] - ll[1,1] + 1), ll[1,2]:(ru[1,2] - ll[1,2] + 1)))
            coords <- cbind(1, exposure_appl[, i], exposure_appl[, j])
            coords[,2] <- coords[,2] - ll[1,1] + 1
            coords[,3] <- coords[,3] - ll[1,2] + 1
            exposure[coords] <- exposure[coords] + exposure_appl[, exposure]
            exposure_ds$.f$write(
              list(applied_geom$tDate, ll[1,1]:(ru[1,1] - ll[1,1] + 1), ll[1,2]:(ru[1,2] - ll[1,2] + 1)),
              exposure
            )
          }
        }
      }
    }
  }
)

if (spatial_output_scale == "base_geometry") {
  exposure <- rbindlist(exposure)
  exposure <- exposure[exposure > 0, .(exposure = sum(exposure)), .(x, y, t)]
  idx <- exposure[, scale_1sqm$t(cbind(x + 1, y + 1))]
  exposure <- data.table(x = idx[, 1], y = idx[, 2], t = exposure[, t], exposure = exposure[, exposure])
  setkeyv(exposure, c("x", "y"))
  result <- pbsapply(1:length(lulc_type), function(i) {
    if (`%in%`(lulc_type[i], habitat_types)) {
      habitat <- geometries[i,]
      if (habitat@bbox[1,2] - habitat@bbox[1,1] > 1 & habitat@bbox[2,2] - habitat@bbox[2,1] > 1) {
        r <- rast(
            xmin = habitat@bbox[1,1],
            xmax = habitat@bbox[1,2],
            ymin = habitat@bbox[2,1],
            ymax = habitat@bbox[2,2],
            crs = geometries@proj4string@projargs,
            resolution = 1
        )
        r <- rasterize(vect(habitat), r, 0)
        dt <- data.table(id = 1:ncell(r), lulc = c(r[]))[!is.nan(lulc)]
        dt[, c("x", "y") := list(xFromCell(r, id), yFromCell(r, id))]
        idx <- dt[, scale_1sqm$t(cbind(x + 1, y + 1))]
        dt <- data.table(x = idx[, 1], y = idx[, 2])
        setkeyv(dt, c("x", "y"))
        habitat_exposure <- exposure[dt]
        if (habitat_exposure[exposure > 0, .N] > 0) {
          habitat_exposure <- habitat_exposure[!is.na(t), sum(exposure) / dt[, .N], t]
          sapply(1:nrow(habitat_exposure), function(j) {
            exposure_ds$.f[i,habitat_exposure[j,t]] <- habitat_exposure[j, V1]
          })
        }
      }
    }
    TRUE
  })
}

# Clean up
result <- f$close()
