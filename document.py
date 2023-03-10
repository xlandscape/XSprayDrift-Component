"""
Script for documenting the code of the XSprayDrift component.
"""
import os
import base.documentation
import XSprayDrift

root_folder = os.path.abspath(os.path.join(os.path.dirname(base.__file__), ".."))
base.documentation.write_changelog(
    "XSprayDrift component",
    XSprayDrift.SprayDrift.VERSION,
    os.path.join(root_folder, "..", "variant", "XSprayDrift", "CHANGELOG.md")
)
