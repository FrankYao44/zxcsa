import ctypes
so = ctypes.cdll.LoadLibrary
lib = ctypes.cdll.LoadLibrary("./libpycall.so")
lib.init()
lib.write(1)
class StructPointer(ctypes.Structure):
    _fields_ = [("list", ctypes.c_int * 10)]

lib.read.restype = ctypes.POINTER(StructPointer)
p = lib.read()
for i in p.contents.list:
    print(i)
