import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CDAPack",
    version="0.0.2",
    author="Aditya Vasudevan",
    author_email="aditya2499@gmail.com",
    description="A Climate Data Analysis package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adivas24/NCPOR",
    packages=setuptools.find_packages(),
    install_requires = [ 'cython','geopandas','xarray','cartopy', 'matplotlib','scipy','numpy', 'pandas', 'shapely','python-dateutil', 'netCDF4','rasterio']
    ,classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPL",
        "Operating System :: OS Independent",
    ],
)