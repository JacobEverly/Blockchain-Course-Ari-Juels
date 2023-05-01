import random
import hashlib

def sha256_2_string(string_to_hash):
    """ Returns the SHA256^2 hash of a given string input
    in hexadecimal format.

    Args:
        string_to_hash (str): Input string to hash twice

    Returns:
        str: Output of double-SHA256 encoded as hexadecimal string.
    """
    # First, convert the input string to bytes
    input_bytes = string_to_hash.encode('utf-8')

    # Compute the first SHA256 hash
    first_hash = hashlib.sha256(input_bytes).digest()

    # Compute the second SHA256 hash on the output of the first hash
    second_hash = hashlib.sha256(first_hash).digest()

    # Return the output as a hexadecimal string
    return second_hash.hex()


def encode_as_str(list_to_encode, sep = "|"):
    """ Encodes a list as a string with given separator.

    Args:
        list_to_encode (:obj:`list` of :obj:`Object`): List of objects to convert to strings.
        sep (str, optional): Separator to join objects with.
    """
    return sep.join([str(x) for x in list_to_encode])

def nonempty_intersection(list1, list2):
    """ Returns true iff two lists have a nonempty intersection. """
    return len(list(set(list1) & set(list2))) > 0


def remove_empties(list):
    return [x for x in list if x != ""]

def run_async(func):
    """
        ( source: http://code.activestate.com/recipes/576684-simple-threading-decorator/ )
        run_async(func)
            function decorator, intended to make "func" run in a separate
            thread (asynchronously).
            Returns the created Thread object

            E.g.:
            @run_async
            def task1():
                do_something

            @run_async
            def task2():
                do_something_too

            t1 = task1()
            t2 = task2()
            ...
            t1.join()
            t2.join()
    """
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target = func, args = args, kwargs = kwargs)
        func_hl.start()
        return func_hl

    return async_func
