# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HMCTools
                                 A QGIS plugin
 Create sdata to run Hydrological Model Continuum
                             -------------------
        begin                : 2017-08-21
        copyright            : (C) 2017 by Fabio Delogu
        email                : fabio.delogu@cimafoundation.org
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load HMCTools class from file HMCTools.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .hmc_tools import HMCTools
    return HMCTools(iface)
