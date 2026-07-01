"""Allow running the package directly with `python -m chronobright`."""

from chronobright.ui.app import ChronoBrightApp


def main() -> None:
    app = ChronoBrightApp()
    app.mainloop()


if __name__ == "__main__":
    main()
