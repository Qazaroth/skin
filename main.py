#!/usr/bin/env python3
"""Skin Terminal Client - Main Entry Point"""

VERSION = "1.1.0"  # <-- Change this to update the version across the app

import config
from app import SkinApp

if __name__ == "__main__":
    cfg = config.load()
    app = SkinApp(version=VERSION, base_url=cfg["base_url"])
    app.run()