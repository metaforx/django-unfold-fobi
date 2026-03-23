"""
Compatibility patch for django-fobi DRF integration with newer versions of DRF.
This patches the missing set_value function that was removed in DRF 3.15+.
"""

import rest_framework.fields as drf_fields

# set_value was removed in DRF 3.15+, but fobi still needs it
# This is a compatibility shim
if not hasattr(drf_fields, "set_value"):

    def set_value(dictionary, keys, value):
        """
        Set a value in a nested dictionary given a list of keys.
        This is a compatibility shim for the removed set_value function.
        """
        if not keys:
            return
        for key in keys[:-1]:
            dictionary = dictionary.setdefault(key, {})
        dictionary[keys[-1]] = value

    # Patch it directly into the module
    drf_fields.set_value = set_value

    # Also make it available for direct import
    __all__ = ["set_value"]
