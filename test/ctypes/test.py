import ctypes
so = ctypes.cdll.LoadLibrary
lib = ctypes.cdll.LoadLibrary("./libpycall.so")
new_lib = ctypes.cdll.LoadLibrary("./libpycall.so")
class StructPointer(ctypes.Structure):
    _fields_ = [("list", ctypes.c_int * 10)]
lib.init()
lib.write(1)
lib.write(1)
lib.read.restype = ctypes.POINTER(StructPointer)
p = lib.read()
for i in p.contents.list:
    print(i)
new_lib.init()
new_lib.write(2)


new_lib.read.restype = ctypes.POINTER(StructPointer)
p = new_lib.read()
for i in p.contents.list:
    print(i)

