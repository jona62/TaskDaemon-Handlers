#!/usr/bin/env python3
"""Check package versions and the immutable source tag before publication."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tomllib
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


def package_versions():
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    java = ET.parse(ROOT / "java/pom.xml").getroot()
    csharp = ET.parse(ROOT / "csharp/TaskDaemon/TaskDaemon.Handler.csproj").getroot()
    cpp = re.search(r"project\(taskdaemon-cpp VERSION ([0-9.]+)", (ROOT / "cpp/CMakeLists.txt").read_text())
    if cpp is None:
        raise ValueError("C++ package version is missing")
    versions = {
        "python": tomllib.loads((ROOT / "python/pyproject.toml").read_text())["project"]["version"],
        "npm": json.loads((ROOT / "nodejs/package.json").read_text())["version"],
        "rust": tomllib.loads((ROOT / "rust/Cargo.toml").read_text())["package"]["version"],
        "nuget": csharp.findtext("PropertyGroup/Version"),
        "maven": java.findtext("m:version", namespaces=ns),
        "cpp": cpp.group(1),
        "vcpkg": json.loads((ROOT / "cpp/packaging/vcpkg/taskdaemon-handler/vcpkg.json").read_text())["version"],
    }
    return versions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("--require-tag", action="store_true")
    args = parser.parse_args()
    if re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", args.version) is None:
        parser.error("version must be a stable semantic version, for example 0.1.2")
    try:
        mismatches = {name: version for name, version in package_versions().items() if version != args.version}
        if mismatches:
            raise ValueError(f"package versions differ from {args.version}: {mismatches}")
        if args.require_tag:
            tag = "v" + args.version
            if os.environ.get("GITHUB_REF") != "refs/tags/" + tag:
                raise ValueError(f"publishing requires selecting tag {tag}, rather than a branch")
            tagged = subprocess.check_output(["git", "rev-parse", tag + "^{commit}"], cwd=ROOT, text=True).strip()
            head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
            if tagged != head:
                raise ValueError("checkout does not match the release tag")
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    print(f"All package versions match {args.version}; source checks passed.")


if __name__ == "__main__":
    main()
