import unittest
from biicode.common.edition.parsing.cpp.drl_parser import DRLCPPParser
from biicode.common.model.blob import Blob
from biicode.common.test import testfileutils
from nose_parameterized import parameterized  # @UnresolvedImport


class GeomCPPParserTest(unittest.TestCase):
    @parameterized.expand([
        ('eigen/src/LU/arch/Inverse_SSE.h', ),
        ('eigen/src/Geometry/Translation.h', ),
        ('eigen/src/Geometry/Scaling.h', ),
        ('eigen/src/Geometry/Homogeneous.h', ),
        ('eigen/src/Geometry/AlignedBox.h', ),
        ('eigen/src/Core/Matrix.h', ),
        ('eigen/src/Core/Product.h', ),
        ('eigen/src/Core/arch/AltiVec/PacketMath.h', ),
        ('eigen/src/Core/BandMatrix.h', ),
        ('eigen/src/Core/Matrix.h', ),
        ('eigen/src/Core/products/GeneralMatrixVector.h', ),
        ('eigen/src/Core/products/SelfadjointRank2Update.h', ),
        ('eigen/src/Core/util/Constants.h', ),
    ])
    def test_parse(self, header_file):
        BlobH = Blob(testfileutils.read(header_file))
        parserH = DRLCPPParser()
        parserH.parse(BlobH.bytes)
