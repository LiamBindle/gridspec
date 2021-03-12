from gridspec.misc.datafile_ops import join_datafiles


join_datafiles("C12.GCHP.SpeciesConc.20180101_1200z", gridspec_file='c12_gridspec.nc',
               tile_dim='nf',
               rename_dict={'extradim1': 'lev'},
               coord_attrs_dict={'lev': dict(standard_name="model_layer", units="layer")},
               transpose=('time', 'lev', 'nf', 'Ydim', 'Xdim')
)