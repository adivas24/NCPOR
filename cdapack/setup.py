import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cdapack",
    version="0.0.4",
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
    'cython>=0.29.11',
    'geopandas>=0.5.0',
    'xarray>=0.12.2',
    'cartopy>=0.17.0',
    'matplotlib>= 3.1.1',
    'scipy>=1.3.0',
    'numpy>=1.16.4',
    'pandas>=0.24.2',
    'shapely>=1.6.4.post2',
    'python-dateutil>=2.8.0',
    'netCDF4>=1.5.1.2',
    'rasterio>=1.0.24'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
)