"""
Library Features:

Name:          hmc_tools_settings
Author(s):     Fabio Delogu (fabio.delogu@cimafoundation.org)
Date:          '20170907'
Version:       '1.0.0'
"""
# -------------------------------------------------------------------------------------
# TAG(S) NOTE:
# DataFile: $domain.$var.txt
# DataType: raster, vector, table
# DataView: True, False
# DataFormat: i, f, None
# DataWorkFlow: IN, OUT, IN/OUT
# DataLevel: Optional, Mandatory, NotDef
# DataUndef: -1, -9999, None
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Dictionary to set variable(s) information for section finder tool
oDictVars_Alg_SectionFinder = \
    {'CHANNELS_NETWORK':
         {'DataName': 'CHANNELS_NETWORK', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.choice.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Mandatory',
          'DataValue': None, 'DataFormat': 'i', 'DataUndef': -1},
     'POINT':
         {'DataName': 'POINT', 'DataView': True, 'DataType': 'vector',
          'DataFile': None, 'DataWorkFlow': 'IN', 'DataLevel': 'Mandatory',
          'DataValue': None, 'DataFormat': None, 'DataUndef': None},
     'SECTION_IMPORTED_TABLE':
         {'DataName': 'SECTION_IMPORTED_TABLE', 'DataView': True, 'DataType': 'table',
          'DataFile': None, 'DataWorkFlow': 'IN', 'DataLevel': 'Optional',
          'DataValue': None, 'DataFormat': None, 'DataUndef': None},
     'SECTION':
         {'DataName': 'SECTION', 'DataView': True, 'DataType': 'table',
          'DataFile': None, 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': None, 'DataUndef': None},
     }
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Dictionary to set variable(s) information for parameters algorithm
oDictVars_Alg_Parameter = \
    {'DEM':
         {'DataName': 'DEM', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.dem.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Mandatory',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'WATERMARK':
         {'DataName': 'WATERMARK', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.watermark.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Optional',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'PARAMETERS':
         {'DataName': 'PARAMETERS', 'DataView': False, 'DataType': 'table',
          'DataFile': '$domain.parameters.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Optional',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'UC':
         {'DataName': 'UC', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.uc.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'UH':
         {'DataName': 'UH', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.uh.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'CF':
         {'DataName': 'CF', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.cf.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'CT':
         {'DataName': 'CT', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.ct.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     }
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Dictionary to set variable(s) information for watermark algorithm
oDictVars_Alg_WaterMark = \
    {'DEM':
         {'DataName': 'DEM', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.dem.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Mandatory',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'FLOW_DIRECTIONS':
         {'DataName': 'FLOW_DIRECTIONS', 'DataView': False, 'DataType': 'raster',
          'DataFile': '$domain.pnt.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Mandatory',
          'DataValue': None, 'DataFormat': 'i', 'DataUndef': 0},
     'CHANNELS_NETWORK':
         {'DataName': 'CHANNELS_NETWORK', 'DataView': False, 'DataType': 'raster',
          'DataFile': '$domain.choice.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Mandatory',
          'DataValue': None, 'DataFormat': 'i', 'DataUndef': -1},
     'PARTIAL_DISTANCE':
         {'DataName': 'PARTIAL_DISTANCE', 'DataView': False, 'DataType': 'raster',
          'DataFile': '$domain.pdistance.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Mandatory',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'UH':
         {'DataName': 'UH', 'DataView': False, 'DataType': 'raster',
          'DataFile': '$domain.uh.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Optional',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'UC':
         {'DataName': 'UC', 'DataView': False, 'DataType': 'raster',
          'DataFile': '$domain.uc.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Optional',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'SECTIONS':
         {'DataName': 'SECTIONS', 'DataView': False, 'DataType': 'table',
          'DataFile': '$domain.info_section.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Mandatory',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'CORRIVATION_TIME.$section':
         {'DataName': 'CORRIVATION_TIME.$section', 'DataView': False, 'DataType': 'raster',
          'DataFile': '$domain.ctime.$section.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'MASK.$section':
         {'DataName': 'MASK.$section', 'DataView': False, 'DataType': 'raster',
          'DataFile': '$domain.mask.$section.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'i', 'DataUndef': -9999},
     'DEM_MASKED.$section':
         {'DataName': 'DEM_MASKED.$section', 'DataView': False, 'DataType': 'raster',
          'DataFile': '$domain.dem.$section.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'WATERMARK':
         {'DataName': 'WATERMARK', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.watermark.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'i', 'DataUndef': -9999},
     }
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Dictionary to set variable(s) information for land algorithm
oDictVars_Alg_Land = \
    {'DEM':
         {'DataName': 'DEM', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.dem.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Mandatory',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'CN':
         {'DataName': 'CN', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.cn.txt', 'DataWorkFlow': 'IN', 'DataLevel': 'Mandatory',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'LATITUDE':
         {'DataName': 'LATITUDE', 'DataView': False, 'DataType': 'raster',
          'DataFile': '$domain.lat.txt',  'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'LONGITUDE':
         {'DataName': 'LONGITUDE', 'DataView': False, 'DataType': 'raster',
          'DataFile': '$domain.lon.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'MASK':
         {'DataName': 'MASK', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.mask.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'i', 'DataUndef': 0},
     'CELLAREA':
         {'DataName': 'CELLAREA', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.cellarea.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'FLOW_DIRECTIONS':
         {'DataName': 'FLOW_DIRECTIONS', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.pnt.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'i', 'DataUndef': 0},
     'DRAINAGE_AREA':
         {'DataName': 'DRAINAGE_AREA', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.area.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'i', 'DataUndef': -9999},
     'CHANNELS_NETWORK':
         {'DataName': 'CHANNELS_NETWORK', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.choice.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'i', 'DataUndef': -1},
     'PARTIAL_DISTANCE':
        {'DataName': 'PARTIAL_DISTANCE', 'DataView': True, 'DataType': 'raster',
         'DataFile': '$domain.pdistance.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
         'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'WT_ALPHA':
         {'DataName': 'WT_ALPHA', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.alpha.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'WT_BETA':
         {'DataName': 'WT_BETA', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.beta.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': 0},
     'COEFF_RESOLUTION':
         {'DataName': 'COEFF_RESOLUTION', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.coeffres.txt', 'DataWorkFlow': 'OUT', 'DataLevel': 'NotDef',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': 1.0},
     }
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Dictionary to set variable(s) information for preprocess algorithm
oDictVars_Alg_PreProcess = \
    {'DEM':
         {'DataName': 'DEM', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.dem.txt', 'DataWorkFlow': 'IN/OUT', 'DataLevel': 'Mandatory',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     'CN':
         {'DataName': 'CN', 'DataView': True, 'DataType': 'raster',
          'DataFile': '$domain.cn.txt', 'DataWorkFlow': 'IN/OUT', 'DataLevel': 'Mandatory',
          'DataValue': None, 'DataFormat': 'f', 'DataUndef': -9999},
     }
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Form section header definition
oFormSectionHeader = ['sec_idx_x', 'sec_idx_y', 'sec_domain',
                      'sec_name', 'sec_hydro_code', 'sec_area',
                      'sec_thr_alert', 'sec_thr_alarm',
                      'sec_geo_x', 'sec_geo_y', 'sec_data']
# -------------------------------------------------------------------------------------
