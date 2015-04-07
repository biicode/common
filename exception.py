class BiiException(Exception):
    '''Base class for all bii custom exceptions'''
    pass


class ConfigurationFileError(BiiException):
    '''Risen when trying to read a missformatted file'''
    pass


class BiiSerializationException(BiiException):
    pass


class PublishException(BiiException):
    pass


class UpToDatePublishException(PublishException):
    pass


class InvalidNameException(BiiException):
    pass


########  Remote related exceptions ########

class BiiServiceException(BiiException):
    pass


##########  3xx Redirect Codes ##############

class BiiRequestRedirectionException(BiiServiceException):  # Generic 300
    pass


########## 4xx Request Errors ################

class BiiRequestErrorException(BiiServiceException):  # Generic 400
    pass


class AuthenticationException(BiiRequestErrorException):  # 401
    pass


class NotActivatedUser(AuthenticationException):  # 421
    pass


class ForbiddenException(BiiRequestErrorException):  # 403
    pass


class NotFoundException(BiiRequestErrorException):  # 404
    pass


########## 5xx Server Errors ################

class ServerInternalErrorException(BiiServiceException):  # Generic 500
    pass


# Store exceptions
class BiiStoreException(BiiException):
    pass


class AlreadyInStoreException(BiiStoreException):
    pass


class NotInStoreException(BiiStoreException):
    pass
