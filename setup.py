from setuptools import setup

setup(
    name='gridspec',
    version='0.1.0',
    author="Liam Bindle",
    author_email="liam.bindle@gmail.com",
    description="A small package for working with gridspec files for offline regridding of earth system model data.",
    url="https://github.com/LiamBindle/gridspec",
    project_urls={
        "Bug Tracker": "https://github.com/LiamBindle/gridspec/issues",
    },
    py_modules=['gridspec'],
    install_requires=[
        'pygeohash',
        'netcdf4',
        'xarray',
        'numpy',
        'click',
    ],
    entry_points="""
        [console_scripts]
        gridspec-create=gridspec.cli:create
        gridspec-utils=gridspec.cli:utils
    """

)