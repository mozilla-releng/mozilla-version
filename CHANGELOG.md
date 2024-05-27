# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [3.1.0] - 2024-05-27

### Added
* 128 is the next ESR major version

## [3.0.0] - 2024-04-18

### Removed
* Support for python < 3.8

### Added
* Support for python 3.12

### Fixed
* Thunderbird `38.0.1esr` was wrongly considered both a major version and a ESR one.


## [2.3.0] - 2024-04-17

### Added
* `MobileVersion` also new properties: `is_major`, `is_stability`, `is_development`.
* `ShipItVersion`, a class that subclasses `BaseVersion`.

### Changed
* `GeckoVersion` and `MobileVersion` now inherit `ShipItVersion` (and still `BaseVersion`, indirectly).


## [2.2.0] - 2024-04-17

### Added
* `GeckoVersion` exposes new properties: `is_major`, `is_stability`, `is_development`.


## [2.1.0] - 2023-05-23

### Added
* Version classes are now exported at the top level of the `mozilla_version` module.


## [2.0.0] - 2023-04-20

### Removed
* Support for python < 3.7

### Added
* 115 is the next ESR major version

## [1.2.0] - 2022-11-25

### Changed
* `MobileVersion` allows the `X.0.0` pattern up to `major_number <= 108`.

## [1.1.0] - 2022-07-07

### Changed
* `MobileVersion` (and `FenixVersion`) now define Gecko version schemes for `major_number >= 104`.

## [1.0.1] - 2022-05-03

### Added
* 102 is the new ESR major version

## [1.0.0] - 2021-12-02

### Added
* Added `MobileVersion` as a replacement to `FenixVersion`; `FenixVersion` to be removed in a future release

## [0.5.4] - 2021-07-21

### Added
* 91 is the new ESR major version

## [0.5.3] - 2020-12-11

### Added
* added `is_release`, `is_beta`, and is_release_candidate` attrs to `MavenVersion`

## [0.5.2] - 2020-05-11

### Added
* 78 is the new ESR major number

## [0.5.1] - 2020-04-06

### Added
* `GeckoVersion.bump_version_type()` to help mergedays.

## [0.5.0] - 2019-12-18

### Added
* `FenixVersion` support for release or beta style Fenix releases.

## [0.4.1] - 2019-07-31

### Fixed
* Missing requirements in pypi packages


## [0.4.0] - 2019-07-31

### Added
* `BaseVersion.bump()`, which takes care of setting or resetting the right numbers. It's also exposed to child classes. Edge cases are taken into account
* Pre-rapid-release version numbers (like 1.5.0.1) are now supported. There are a few edge cases still unsupported (e.g.: 3.0.19-real-real)
* `VersionType.RELEASE_CANDIDATE` was added to support pre-rapid-release version numbers.

### Changed
* `VersionType.RELEASE` and `VersionType.ESR` have their integer bumped, so `VersionType.RELEASE_CANDIDATE` fits in.
* `PatternNotMatchedError` now takes several patterns
* `GeckoVersion` now raises when an "a2" version is created after [Project Dawn](https://bugzilla.mozilla.org/show_bug.cgi?id=1353821) happened.


## [0.3.4] - 2019-07-09

### Changed
* [Bug 1561617](https://bugzilla.mozilla.org/show_bug.cgi?id=1561617): part 3 - FennecVersion accepts 68.X because of the [version.txt of beta](https://hg.mozilla.org/releases/mozilla-esr68/file/59a3b58682a8a2de6bb29834d583d6e59bdf70f1/mobile/android/config/version-files/beta/version.txt).


## [0.3.3] - 2019-07-08

### Changed
* [Bug 1561617](https://bugzilla.mozilla.org/show_bug.cgi?id=1561617): part 2 - FennecVersion accepts 68.Xa1.


## [0.3.2] - 2019-06-26

### Changed
* [Bug 1561617](https://bugzilla.mozilla.org/show_bug.cgi?id=1561617): part 1 - FennecVersion doesn't accept any version >=69 and accepts 68.XbN.


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
