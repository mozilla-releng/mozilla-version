# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).


## [0.3.2] - 2019-06-26

### Changed
* [Bug 1561617](https://bugzilla.mozilla.org/show_bug.cgi?id=1561617): FennecVersion doesn't accept any version >=69 and accepts 68.XbN.


## [0.3.1] - 2018-11-12

### Changed
* `BalrogVersion`, `GeckoVersion` and derivatives are now hashable.

### Added
* `mozilla_version.version.BaseVersion` to expose semver-like numbers.
* `mozilla_version.maven.MavenVersion` to handle Maven version and more precisely the ones like `0.30.0-SNAPSHOT`.


## [0.3.0] - 2018-09-20

### Changed
* `VersionType.ESR` is now greater than `VersionType.RELEASE`. This facilitates filtering on mixed-list of releases.

### Added
* `mozilla_version.gecko.GeckoSnapVersion` to handle Ubuntu Snap packages.

### Fixed
* `GeckoVersion._compare()` doesn't cast other to `FirefoxVersion` anymore.


## [0.2.2] - 2018-09-07

### Fixed
* Added requirements.txt.in in package so setup.py works


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
