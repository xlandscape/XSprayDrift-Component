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
base.documentation.write_repository_info(
    os.path.join(root_folder, "..", "variant", "XSprayDrift"),
    os.path.join(root_folder, "..", "variant", "XSprayDrift", "repository.json"),
    os.path.join(root_folder, "..", "..", "..", "versions.json"),
    "component"
)
