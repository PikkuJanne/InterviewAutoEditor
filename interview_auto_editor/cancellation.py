"""Cooperative cancellation shared by the application and bounded local IO."""
from contextlib import contextmanager
from contextvars import ContextVar


class Cancelled(KeyboardInterrupt):
    """No partial run may be presented as a completed result."""


_check = ContextVar('iae_cancel', default=lambda: False)


def checkpoint():
    if _check.get()():
        raise Cancelled()


@contextmanager
def scope(check):
    token = _check.set(check)
    try:
        checkpoint()
        yield
    finally:
        _check.reset(token)
