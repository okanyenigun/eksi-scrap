from .base_driver import BaseBrowser
from .drivers.uc_driver import UCDriver


def get_browser_driver(name: str = "uc", headless: bool = False, binary_location: str = None) -> BaseBrowser:
    if name == "uc":
        return UCDriver(headless=headless, binary_location=binary_location)

    raise NotImplementedError(f"Browser driver '{name}' not implemented")