from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    """Wrap every DRF error response in a single ``{"errors": {...}}`` envelope."""
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    data = response.data
    if isinstance(data, dict):
        errors = data
    elif isinstance(data, list):
        errors = {"non_field_errors": data}
    else:
        errors = {"detail": [data]}

    response.data = {"errors": errors}
    return response
