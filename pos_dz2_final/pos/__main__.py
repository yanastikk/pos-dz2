import sys

from .application import Gradebook
from .bootstrap import build_container
from .demo import run_demo
from .infrastructure import ConsoleApp, ConsoleIO


def main():
    container = build_container()
    if "--demo" in sys.argv:
        run_demo(container.resolve(Gradebook), container.resolve(ConsoleIO))
    else:
        container.resolve(ConsoleApp).run()


# запускаем main только как программу
if __name__ == "__main__":
    main()
