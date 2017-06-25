# -*- coding: UTF-8 -*-

from types import MethodType

def _AddStrongReference(self, obj):
    self._strong_ref_max_id += 1
    obj._strong_ref_obj_id = self._strong_ref_max_id
    self._strong_ref_refs[obj._strong_ref_obj_id] = obj

def _ReleaseStrongReference(self, obj):
    if hasattr(obj, "_strong_ref_obj_id") \
            and (obj._strong_ref_obj_id in self._strong_ref_refs):
        del self._strong_ref_refs[obj._strong_ref_obj_id]

    else:
        raise RuntimeError("Cannot release strong reference: object not referenced")

def strongref(cls):
    setattr(cls, "_strong_ref_obj_id", 0)
    setattr(cls, "_strong_ref_refs", {})
    setattr(cls, "_strong_ref_max_id", 0)
    setattr(cls, "_AddStrongReference", MethodType(_AddStrongReference, cls))
    setattr(cls, "_ReleaseStrongReference", MethodType(_ReleaseStrongReference, cls))

    return cls
