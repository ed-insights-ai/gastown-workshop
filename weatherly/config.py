"""Configuration constants and Config dataclass for weatherly.

Module-level constants are the application defaults. The Config dataclass
provides runtime configuration, typically populated from CLI arguments.
"""

from dataclasses import dataclass

API_BASE_URL: str = "https://wttr.in"
DEFAULT_FORMAT: str = "j1"
DEFAULT_UNITS: str = "fahrenheit"
REQUEST_TIMEOUT: int = 10


@dataclass
class Config:
    api_base_url: str = API_BASE_URL
    location: str = "auto"
    units: str = DEFAULT_UNITS
    format: str = DEFAULT_FORMAT
    request_timeout: int = REQUEST_TIMEOUT
