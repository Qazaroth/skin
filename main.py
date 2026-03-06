#!/usr/bin/env python3
"""Skin Terminal Client - Main Entry Point"""

VERSION = "1.2.0"  # <-- Change this to update the version across the app

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import config
from app import SkinApp

if __name__ == "__main__":
    cfg = config.load()
    app = SkinApp(version=VERSION, base_url=cfg["base_url"])
    app.run()