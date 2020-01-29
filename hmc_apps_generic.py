# -------------------------------------------------------------------------------------
# Method to create folder (and check if folder exists)
def createFolder(sPathName=None, sPathDelimiter=None):

    from os import makedirs
    from os.path import exists

    if sPathName:
        if sPathDelimiter:
            sPathNameSel = sPathName.split(sPathDelimiter)[0]
        else:
            sPathNameSel = sPathName

        if not exists(sPathNameSel):
            makedirs(sPathNameSel)
        else:
            pass
    else:
        pass
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Method to define string
def defineString(sString='', oDictTags=None):

    if sString != '':
        if not oDictTags:
            pass
        elif oDictTags:
            for sKey, oValue in oDictTags.items():

                if isinstance(oValue, list):            # list values
                    sVarKey = oValue[0]
                    oVarValue = oValue[1]
                elif isinstance(oValue, dict):          # dict values
                    sVarKey = oValue.keys()[0]
                    oVarValue = oValue.values()[0]
                else:                                   # scalar value
                    sVarKey = sKey
                    oVarValue = oValue

                if isinstance(oVarValue, basestring):
                    sString = sString.replace(sVarKey, oVarValue)
                elif isinstance(oVarValue, int):
                    sString = sString.replace(sVarKey, str(int(oVarValue)))
                elif isinstance(oVarValue, float):
                    sString = sString.replace(sVarKey, str(float(oVarValue)))
                else:
                    sString = sString.replace(sVarKey, str(oVarValue))
    else:
        pass

    return sString
# -------------------------------------------------------------------------------------
