import biipyc2

ffi, link_lib = biipyc2.link_clib("%BLOCKNAME_C%/csparse/cs.h")
a = ffi.new("cs *")
print "Wrong pointer, result %f" % link_lib.cs_norm(a)
