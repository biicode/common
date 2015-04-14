from biicode.common.exception import (AuthenticationException, NotFoundException,
                                      ServerInternalErrorException, BiiRequestRedirectionException,
                                      BiiRequestErrorException, ForbiddenException,
                                      BiiException, PublishException)

EXCEPTION_CODES = {500: ServerInternalErrorException,
                   520: BiiException,
                   521: PublishException,
                   400: BiiRequestErrorException,
                   401: AuthenticationException,
                   403: ForbiddenException,
                   404: NotFoundException,
                   300: BiiRequestRedirectionException,
                   200: None}


def getExceptionFromHttpError(error_code):
    try:
        if error_code in EXCEPTION_CODES:
            return EXCEPTION_CODES[error_code]
        else:
            return EXCEPTION_CODES[_base_error(error_code)]
    except KeyError:
        return None


def _base_error(error_code):
    return int(str(error_code)[0] + "00")


def getHttpCodeFromException(exception):
    for code, ex in EXCEPTION_CODES.iteritems():
        if exception.__class__ == ex:
            return code
    return 500
