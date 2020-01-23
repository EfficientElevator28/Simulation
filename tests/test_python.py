"""
Author: Daniel Nichols

Simple test to make sure python works
"""
from sys import version_info
from utils_for_tests import error


def test_is_python3():
    if version_info[0] < 3:
        error("Python version <3")


def run_tests():
    test_is_python3()


if __name__ == "__main__":
    run_tests()
