import biipyc
ffi, C = biipyc.link_clib("%BLOCKNAME_C%/simple_dynlibs/sum.h")
print "Complex calc in c is %d" % C.sum(4, 5)
