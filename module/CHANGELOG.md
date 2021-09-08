# CHANGELOG
This list contains all additions, changes and fixes for the XSprayDrift module.

## [2.6] - 2021-09-08
### Added
### Changed
### Fixed
- Error in determination of in-region exposure

## [2.5] - 2021-09-06
### Added
### Changed
- Suppressed unnecessary display of outputs  
### Fixed

## [2.4] - 2021-09-03
### Added
### Changed
- Renamed some datasets in HDF5 input file 
### Fixed

## [2.3] - 2021-07-19
### Added
### Changed
### Fixed
- Error introduced during last re-factory


## [2.2] - 2021-07-19
### Added
### Changed
- Code style refactoring of R script
- Minor changes in changelog

### Fixed


## [2.1] - 2020-12-02
### Added
- README, LICENSE, CHANGELOG and CONTRIBUTION
### Changed
### Fixed


## [2.0] - 2020-05-20
### Added
### Changed
- Updated to `xdrift` R package 1.0.9999
### Fixed


## [1.15] - 2020-01-08
### Added
### Changed
- Fewer messages from module
### Fixed


## [1.14] - 2019-12-15
### Added
### Changed
- Updated to allow preliminary AgDRIFT implementation
### Fixed


## [1.13]
### Added
- Simulates drift filtering by vegetation
### Changed
### Fixed


## [1.12]
### Added
### Changed
- R package updated
### Fixed


## [1.11]
### Added
### Changed
### Fixed
- Script updated to fix spatial offset issues


## [1.10]
### Added
### Changed
- R script refactored
### Fixed


## [1.9]
### Added
- Random seed parameter
### Changed
### Fixed


## [1.8]
### Added
### Changed
- Updated module's R packages, including `xdrift` (now v0.1.1)
### Fixed


## [1.7]
### Added
- New optional spatial output scale of base geometry
### Changed
### Fixed


## [1.6]
### Added
### Changed
- Uses new input format for applications, including pre-simulated spatial extents of applications
- R runtime environment updated to 3.5.3 
### Fixed


## [1.5]
### Added
### Changed
### Fixed
- Now ignores fields that are not applied due to buffer / margin


## [1.4]
### Added
### Changed
### Fixed
- Now ignores simulated spray-drift outside considered area


## [1.3]
### Added
### Changed
### Fixed
- Multiple applications on a day can no longer clear out each other


## [1.2]
### Added
### Changed
### Fixed
- No longer stops execution if no habitat within 50 m of field


## [1.1]
### Added
### Changed
- Now uses inclusive simulation time boundaries

### Fixed
- No longer produces warnings if no habitat affected

## [1.0]
### Added
- First release of the XSprayDrift module

### Changed
### Fixed