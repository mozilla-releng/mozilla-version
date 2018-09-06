# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [0.2.1] - 2018-09-06

### Fixed
* Unpinned dependencies when installing mozilla-version as a library (via setup.py)


## [0.2.0] - 2018-08-10

### Changed
* `FirefoxVersion` was moved from `mozilla_version.firefox` to `mozilla_version.gecko`
* `FirefoxVersion()` doesn't parse strings anymore. `FirefoxVersion.parse(string)` should be called instead.
* `FirefoxVersion()` allows to build version numbers by specifying raw values directly

### Added
* In `mozilla_version.gecko`: `ThunderbirdVersion`, `FennecVersion`, `DeveditionVersion`, and `GeckoVersion`. The latter being a class that has generic support of the others (+ `FirefoxVersion`)
* Known edge cases that were ever shipped to Balrog. For instance: Firefox 38.0.5b1.


## [0.1.2] - 2018-06-28

### Fixed
* Added `enum34` package for python < 3.4


## [0.1.1] - 2018-06-28

### Fixed
* Missing requirements file in package

### Added
* Python 2.7 support, needed by mozilla-central


## [0.1.0] - 2018-06-27
Initial release
