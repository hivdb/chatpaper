import inspect


class RequiredSelection(Exception):
    pass


def check_selection(error_message=None):

    def func_wrapper(func):

        nonlocal error_message
        signature = inspect.signature(func)
        title = signature.parameters.get('title')
        if not error_message:
            error_message = title.default

        def call_func(*args, **kwargs):

            result = func(*args, **kwargs)

            if result is None:
                raise RequiredSelection(f"Error: {error_message}")

            return result

        return call_func

    return func_wrapper
