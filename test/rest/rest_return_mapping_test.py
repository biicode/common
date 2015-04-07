import unittest
from biicode.common.rest.rest_return_mapping import getExceptionFromHttpError
from biicode.common.rest.rest_return_mapping import getHttpCodeFromException
from biicode.common.exception import NotFoundException
from biicode.common.exception import ServerInternalErrorException
from biicode.common.exception import BiiRequestErrorException


class RestMappingTest(unittest.TestCase):
    def test_get_exception_from_http_error(self):
        self.assertEquals(getExceptionFromHttpError(404), NotFoundException)
        self.assertEquals(getExceptionFromHttpError(409), BiiRequestErrorException)
        self.assertEquals(getExceptionFromHttpError(509), ServerInternalErrorException)
        self.assertEquals(getExceptionFromHttpError("500"), ServerInternalErrorException)
        self.assertIsNone(getExceptionFromHttpError(605))

    def test_get_http_code_from_exception(self):
        self.assertEquals(getHttpCodeFromException(NotFoundException()), 404)
