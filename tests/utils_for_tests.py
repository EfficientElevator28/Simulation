"""
Author: Daniel Nichols
utilities for testers.
"""
import sys


def error(message=""):
    print("[Failed] -- " + str(message), sys.stderr)
