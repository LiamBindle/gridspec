from gridspec.misc.datafile_ops import split_datafile

split_datafile("../sample_data/GCHP.SpeciesConc.20180101_1200z.nc4", tile_dim='nf', gridspec_file='c24_gridspec.nc', directory="./")