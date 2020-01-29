#!/bin/sh -e

# FlowDirections production
f2py -c module_flow_directions.f90 -m hmc_apps_dataland_flowdirections

# DrainageArea production
f2py -c module_drainage_area.f90 -m hmc_apps_dataland_drainagearea

# ChannelsNetwork production
f2py -c module_channels_network.f90 -m hmc_apps_dataland_channelsnetwork

# WatertableSlopes production
f2py -c module_watertable_slopes.f90 -m hmc_apps_dataland_watertableslopes

# CoefficientResolution production
f2py -c module_coeff_resolution.f90 -m hmc_apps_dataland_coeffresolution

# CorrivationTime production
f2py -c module_corrivation_time.f90 -m hmc_apps_dataland_corrivationtime



