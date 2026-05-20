import sys

class DocVQAException(Exception):
    """
    Base class for exceptions in this project.
    """
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = self._get_detailed_error_message(error_message, error_detail)

    def _get_detailed_error_message(self, error_message, error_detail: sys):
        _, _, exc_tb = error_detail.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename
        error_message = "Error occurred in python script name [{0}] line number [{1}] error message [{2}]".format(
            file_name, exc_tb.tb_lineno, str(error_message)
        )
        return error_message

    def __str__(self):
        return self.error_message

class OCRError(DocVQAException):
    """Raised when an OCR operation fails."""
    pass

class APIError(DocVQAException):
    """Raised when an external API call fails."""
    pass

class DataLoadingError(DocVQAException):
    """Raised when the dataset fails to load."""
    pass

class EmbeddingError(DocVQAException):
    """Raised when embedding generation fails."""
    pass
