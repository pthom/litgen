import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

import numpy as np
import litgensample


def main():
    print(litgensample.add(3, 4))

    a = np.zeros((10), np.uint8)
    # print(f"{a=}")
    # litgensample.add_inside_array(a, 0)
    # print(f"{a=}")
    # litgensample.add_inside_array(a, 5)
    # print(f"{a=}")

    litgensample.mul_inside_array(a, 10)
    print(a)

if __name__ == "__main__":
    main()