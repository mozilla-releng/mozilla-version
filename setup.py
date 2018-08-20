import os
import re
from setuptools import setup, find_packages


project_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(project_dir, 'version.txt')) as f:
    version = f.read().rstrip()

# We allow commented lines in this file
with open(os.path.join(project_dir, 'requirements.txt')) as f:
    requirements_raw = f.read()

try:
    requirements_without_escaped_end_of_lines = bytes(requirements_raw, 'utf-8').decode('unicode_escape')
except TypeError:
    requirements_without_escaped_end_of_lines = requirements_raw.decode('string_escape') # python2

requirements_with_hashes = requirements_without_escaped_end_of_lines.split('\n')
requirements_without_comments = [
    line for line in requirements_with_hashes if line and not line.startswith('#')
]
requirements_without_hashes = [
    re.sub(r'--hash=\S+', '', line)
    for line in requirements_without_comments
]

setup(
    name='mozilla-version',
    version=version,
    description="""Process Firefox versions numbers. Tells whether they are valid or not, whether \
they are nightlies or regular releases, whether this version precedes that other.
    """,
    author='Mozilla Release Engineering',
    author_email='release+python@mozilla.com',
    url='https://github.com/mozilla-releng/mozilla-version',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license='MPL2',
    install_requires=requirements_without_hashes,
    classifiers=(
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ),
)
