import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cdapack",
    version="0.0.6",
    author="Aditya Vasudevan",
    author_email="aditya2499@gmail.com",
    #entry_points = {"console_scripts": ['cdapack = cdapack.driver:main']},
    #scripts = ['cdapack.py'],
    entry_points = {
        'console_scripts': ['cdapack=cdapack.gui_functions:main'],
    },
    description="A Climate Data Analysis package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adivas24/NCPOR",
    packages=setuptools.find_packages(),
    install_requires = [
    'cython',
    'geopandas',
    'xarray',
    'cartopy',
    'matplotlib',
    'scipy',
    'numpy',
    'pandas',
    'shapely',
    'python-dateutil',
    'netCDF4',
    'rasterio'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)