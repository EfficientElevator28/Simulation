import sys
from simulator import Simulator


def step():
    return True


def main(argc, argv):
    s = Simulator(name="basic_simulator", step_func=step)

    s.run(timestep=1, new_thread=False)


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
