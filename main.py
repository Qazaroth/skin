#!/usr/bin/env python3
"""Skin Terminal Client - Main Entry Point"""

VERSION = "1.0.0"  # <-- Change this to update the version across the app

from app import SkinApp

if __name__ == "__main__":
    app = SkinApp(version=VERSION)
    app.run()