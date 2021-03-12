from gridspec.gnom_cube_sphere.gcs_gridspec import GnomonicCubedSphereGridspec

cs_size = 24
gs = GnomonicCubedSphereGridspec(cs_size, stretch_factor=2, target_lat=40, target_lon=260)
gs.save()
