# mozilla-version

[![Build Status](https://travis-ci.org/mozilla-releng/mozilla-version.svg?branch=master)](https://travis-ci.org/mozilla-releng/mozilla-version) [![Coverage Status](https://coveralls.io/repos/github/mozilla-releng/mozilla-version/badge.svg?branch=master)](https://coveralls.io/github/mozilla-releng/mozilla-version?branch=master)[![Documentation Status](https://readthedocs.org/projects/mozilla-version/badge/?version=latest)](https://mozilla-version.readthedocs.io/en/latest/?badge=latest)


Process Mozilla's version numbers. Support main products like Firefox desktop, Fennec, Fenix, and Thunderbird. Tell whether version numbers are valid or not, whether they are nightlies or regular releases, whether this version precedes that other.

## Rationale

Mozilla's build and release pipelines deal with version numbers. This has naturally grown into many scripts living at various places. Most of them reimplemented the same logic that determined whether a version was of which type. In theory, it's a simple problem that could (and was) solved with a regular expression. Although, as a human group, Mozilla hasn't been 100% consistent in giving version numbers to its products. Thus, the regular expression had to grow and we had to update each place that dealt with such exceptions.

Hence, `mozilla-version` is an attempt to become the source of truth when a piece of software has to deal with version numbers. It was build to take existing exceptions into account while enforcing new versions to comply with known schemes.

## Documentation

Want to use `mozilla-version`? Here's how: https://mozilla-version.readthedocs.io/en/latest/

## Get the code

Just install it from pip:

```sh
pip install mozilla-version
```


## Hack on the code
```sh
virtualenv venv         # create the virtualenv in ./venv
. venv/bin/activate    # activate it
git clone https://github.com/mozilla-releng/mozilla-version
cd mozilla-version
pip install mozilla-version
```


## Design choices


### Object-oriented programming

`mozilla-version` uses classes to represent version numbers. For readers wondering: the original author is not a big fan of OOP and usually tries to not use this paradigm. Although, version handling turns out to be simpler when consumers of `mozilla-version` get objects. For instance:

```py
# Functional programming
version_string = "84.0b3"
if is_version_beta(version_string) and get_beta_number(version_string) >= 2:
    do_something()

# OOP
version = FirefoxVersion.parse("84.0b3")
if version.is_beta and version.beta_number >= 2:
    do_something()
```

In the latter case, data gets parsed once and the `if` statement is closer to a regular English sentence. Another example:

```py
# Functional programming
from functools import cmp_to_key

version_strings = ["84.0b3", "100.0.1", "84.0a1", "84.0"]
sorted_versions = sorted(version_strings, key=cmp_to_key(compare_versions))
# compare_version() would be a function provided by the mozilla-version library.
# Signature would look like this: compare_versions(version_a, version_b)
#
# cmp_to_key() comes from https://docs.python.org/3/howto/sorting.html#the-old-way-using-the-cmp-parameter

# OOP
version_strings = ["84.0b3", "100.0.1", "84.0a1", "84.0"]
versions = [FirefoxVersion.parse(string) for string in version_strings]
sorted_version = sorted(versions)
```

Once again, `compare_versions()` would have to parse both versions every time it's called. We could memoize intermediary results but it doesn't help in writing a straightforward `sorted()` call.

One major drawback of OOP is the complexity of the class hierarchy. Remembering side effects of a parent's function call can be hard to remember and debug. Luckily, the problem around version numbers is restricted enough to likely not be a problem in the future.


### About sanity-checks

Like mentioned in the rationale, this problem cannot be solved with a regular expression anymore. `mozilla-version` checks whether a version number is valid thanks to 2 passes.

The first one is a regular expression. Its purpose to take out strings that are obviously neither version numbers, nor roughly matching the expected scheme. It's not meant to be strict.

The second pass ensures data is 100% valid. This is done at the end of the `__init__()` call. Therefore, a consumer of say `FirefoxVersion()` is guaranteed to deal with a valid version number the constructor succeeds (which is the implicit rule of a constructor, by the way). Speaking of `__init__()`, mozilla-version relies on `attrs` which implicitly defines constructors for us. Hence, the second pass is processed in `__attrs_post_init__()`.


### About edge case handling

Edge cases are handled in the second pass. This means: the first pass needs to be broad enough to let edge cases pass through.

They are explicitly called out in each class as `_RELEASED_EDGE_CASES`. They were found on:
 * https://archive.mozilla.org/pub/firefox/releases/
 * https://product-details.mozilla.org/1.0/all.json


### About testing

Version numbers are a very simple problem to unit test. This library has 100% coverage and unit tests are small enough to be extended. Cases are usually written in a simple way where version under tests are plain strings. Then, the test itself parses each string. It's really meant to favor case addition. Feel free to add any edge cases you have in mind.
