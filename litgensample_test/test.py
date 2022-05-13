import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path

import litgensample


def main():
    print(litgensample.add(3, 4))


if __name__ == "__main__":
    main()