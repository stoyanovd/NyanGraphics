import signal


class TimedOutExc(Exception):
    """
    Raised when a timeout happens
    """


def timeout(dt):
    """
    Return a decorator that raises a TimedOutExc exception
    after dt seconds, if the decorated function did not return.
    """

    def decorate(f):
        def handler(signum, frame):
            raise TimedOutExc()

        def new_f(*args, **kwargs):
            old_handler = signal.signal(signal.SIGALRM, handler)
            signal.setitimer(signal.ITIMER_REAL, dt)

            result = f(*args, **kwargs)  # f() always returns, in this scheme

            signal.signal(signal.SIGALRM, old_handler)  # Old signal handler is restored
            signal.alarm(0)  # Alarm removed

            return result

        new_f.__name__ = f.__name__
        return new_f

    return decorate

# @timeout(10)
# def function_that_takes_a_long_time():
#     try:
#         # ... long, parallel calculation ...
