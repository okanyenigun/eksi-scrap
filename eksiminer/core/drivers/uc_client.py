import re
import time
import subprocess
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from functools import wraps
from sys import platform
from typing import Optional, Tuple, Callable, Any
from .base_driver import DriverClient


def retry_with_progressive_fallback(
    max_retries: int = 3, enable_progressive: bool = True
):
    """
    Decorator that retries a method with progressive fallback strategies.

    Strategy:
    1. Normal retries
    2. After retries fail: refresh page and retry
    3. If still failing: reset driver and retry

    Args:
        max_retries: Maximum number of retry attempts per strategy
        enable_progressive: Enable progressive fallback (refresh -> reset)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            last_exception = None

            # Phase 1: Normal retries
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    print(f"[WARN] Attempt {attempt + 1} failed: {e}")
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(self._wait_time * (attempt + 1))

            if not enable_progressive:
                raise last_exception

            # Phase 2: Refresh page and retry
            try:
                self._store_current_url()
                self._refresh_and_restore()

                for attempt in range(max_retries):
                    try:
                        return func(self, *args, **kwargs)
                    except Exception as e:
                        print(f"[WARN] Attempt {attempt + 1} after refresh failed: {e}")
                        last_exception = e
                        if attempt < max_retries - 1:
                            time.sleep(self._wait_time * (attempt + 1))
            except Exception:
                pass

            # Phase 3: Reset driver and retry
            try:
                stored_url = self._get_stored_url()
                self._reset_and_restore(stored_url)

                for attempt in range(max_retries):
                    try:
                        return func(self, *args, **kwargs)
                    except Exception as e:
                        print(f"[WARN] Attempt {attempt + 1} after reset failed: {e}")
                        last_exception = e
                        if attempt < max_retries - 1:
                            time.sleep(self._wait_time * (attempt + 1))
            except Exception:
                pass

            raise last_exception

        return wrapper

    return decorator


class UCDriverClient(DriverClient):
    def __init__(
        self,
        headless: bool = False,
        binary_location: Optional[str] = None,
        version_main: Optional[int] = None,
        wait_time: int = 1,
    ):
        self.driver = None
        self._headless = headless
        self._binary_location = binary_location
        self._version_main = version_main
        self._wait_time = wait_time
        self.by_mapping = {
            "id": By.ID,
            "name": By.NAME,
            "class name": By.CLASS_NAME,
            "tag name": By.TAG_NAME,
            "link text": By.LINK_TEXT,
            "partial link text": By.PARTIAL_LINK_TEXT,
            "css selector": By.CSS_SELECTOR,
            "xpath": By.XPATH,
        }

        self._set_driver()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        self.close()
        return False

    def __del__(self):
        """Destructor to ensure browser cleanup on object deletion"""
        try:
            self.close()
        except Exception:
            pass

    # -------------------------- Selenium WebDriver Methods --------------------------

    @property
    def page_source(self) -> str:
        return self.driver.page_source

    def get_driver(self) -> uc.Chrome:
        if not self.driver:
            self._set_driver()
        return self.driver

    def close(self) -> None:
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"[INFO] Error closing driver: {e}")
                # Force kill Chrome processes if quit fails
                try:
                    import psutil

                    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                        try:
                            cmdline = proc.info.get("cmdline", [])
                            if cmdline and any(
                                "chrome" in str(arg).lower() for arg in cmdline
                            ):
                                if any(
                                    "chromedriver" in str(arg).lower()
                                    or "undetected" in str(arg).lower()
                                    for arg in cmdline
                                ):
                                    proc.kill()
                                    print(
                                        f"[INFO] Killed orphaned Chrome process: {proc.info['pid']}"
                                    )
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                except ImportError:
                    print("[WARN] psutil not available for process cleanup")
            finally:
                self.driver = None

    def quit(self) -> None:
        self.close()

    def refresh(self) -> None:
        self.driver.refresh()
        time.sleep(self._wait_time)

    def reset(self) -> None:
        self.close()
        time.sleep(self._wait_time * 2)  # Give more time for cleanup
        self._set_driver()
        return

    @retry_with_progressive_fallback(max_retries=3, enable_progressive=True)
    def get(
        self, url: str, by: Optional[str] = None, wait_for: Optional[str] = None
    ) -> None:
        # Check if driver is still alive
        try:
            _ = self.driver.current_url
        except Exception:
            # Driver died, recreate it
            self._set_driver()

        if wait_for:
            self.driver.get(url)
            time.sleep(self._wait_time)  # Give page time to load
            try:
                locator = (
                    self.by_mapping.get(by.lower(), By.CLASS_NAME)
                    if by
                    else By.CLASS_NAME
                )
                WebDriverWait(self.driver, self._wait_time * 10).until(
                    EC.presence_of_element_located((locator, wait_for))
                )
            except Exception as e:
                print(f"[WARN] Timeout waiting for element '{wait_for}': {e}")
        else:
            self.driver.get(url)
            time.sleep(self._wait_time * 2)  # Give page time to load

    @retry_with_progressive_fallback(max_retries=3, enable_progressive=True)
    def get_html(
        self, url: str, by: Optional[str] = None, wait_for: Optional[str] = None
    ) -> str:
        self.get(url, by=by, wait_for=wait_for)
        return self.driver.page_source

    def find_element(self, by: str, value: str):
        """Find an element by locator strategy."""
        by_locator = self.by_mapping.get(by.lower(), by)
        return self.driver.find_element(by_locator, value)

    def get_current_url(self) -> str:
        """Get the current URL."""
        return self.driver.current_url

    def scroll_to_bottom(self) -> None:
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(self._wait_time)
        return

    def wait_and_click(self, by: str, wait_for: str, timeout: int = 10) -> None:
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(
                (self.by_mapping.get(by.lower(), By.CLASS_NAME), wait_for)
            )
        )
        element.click()
        time.sleep(self._wait_time)
        return

    # -------------------------- Internal Methods --------------------------
    def _set_driver(self) -> None:
        options = uc.ChromeOptions()
        if self._binary_location:
            options.binary_location = self._binary_location

        # Set page load strategy to 'eager' to not wait for all resources
        options.page_load_strategy = "eager"

        # Critical stability options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")

        # Additional stability options to prevent crashes
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-component-extensions-with-background-pages")
        options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--force-color-profile=srgb")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--mute-audio")

        # Renderer timeout prevention
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")

        # Set user agent to avoid detection
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Auto-detect Chrome/Canary if not provided
        if not self._binary_location or not self._version_main:
            detected_path, detected_version = self.__get_chrome_path_and_version()
            if not self._binary_location:
                self._binary_location = detected_path
                options.binary_location = self._binary_location
            if not self._version_main:
                self._version_main = detected_version

        self.driver = uc.Chrome(
            options=options,
            version_main=self._version_main,
            headless=self._headless,
            browser_executable_path=self._binary_location,
            use_subprocess=False,  # Important: prevent subprocess issues
        )

        # Give Chrome more time to stabilize
        time.sleep(self._wait_time * 3)

        # Set longer timeouts to prevent hanging
        self.driver.set_page_load_timeout(60)  # Increased from 30 to 60
        self.driver.set_script_timeout(60)  # Add script timeout

        # Maximize window for better stability
        try:
            self.driver.maximize_window()
        except Exception:
            pass

    def __get_chrome_path_and_version(self) -> Tuple[str, int]:
        """Returns tuple of (path, version_main) for Chrome/Canary"""
        if platform == "darwin":
            # Try Canary first, fall back to regular Chrome
            possible_paths = [
                "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ]
            path = None
            for p in possible_paths:
                import os

                if os.path.exists(p):
                    path = p
                    print(f"Using Chrome path: {path}")
                    break
            if not path:
                raise RuntimeError("Chrome/Chrome Canary not found on macOS")
        elif platform.startswith("linux"):
            # Chrome Canary is not available for Linux, use regular Chrome
            possible_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
            ]
            path = None
            for p in possible_paths:
                if subprocess.run(["which", p], capture_output=True).returncode == 0:
                    path = p
                    break
            if not path:
                raise RuntimeError("Chrome/Chromium not found on Linux system")
        elif platform == "win32":
            path = r"C:\Users\%USERNAME%\AppData\Local\Google\Chrome SxS\Application\chrome.exe"
        else:
            raise RuntimeError("Unsupported OS")

        try:
            output = subprocess.check_output(
                [path, "--version"], stderr=subprocess.STDOUT
            )
            ver_str = output.decode().strip()
            full = re.search(r"(\d+\.\d+\.\d+\.\d+)", ver_str).group(1)
            version_main = int(full.split(".")[0])
            return path, version_main
        except Exception as e:
            raise RuntimeError(f"Failed to get version from {path}: {e}")
