#!/usr/bin/env python3
"""Restore a local NuGet package into an isolated consumer and check its protocol."""

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile


def verify(package):
    package = package.resolve(strict=True)
    with zipfile.ZipFile(package) as archive:
        manifests = [name for name in archive.namelist() if name.endswith(".nuspec")]
        if len(manifests) != 1:
            raise ValueError("Expected exactly one NuGet manifest")
        manifest = ET.fromstring(archive.read(manifests[0]))
        namespace = {"n": manifest.tag.split("}")[0].lstrip("{")}
        metadata = manifest.find("n:metadata", namespace)
        package_id = metadata.findtext("n:id", namespaces=namespace)
        version = metadata.findtext("n:version", namespaces=namespace)
        if package_id != "TaskDaemon.Handler" or not version or not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z.+-]*", version):
            raise ValueError("Expected a versioned TaskDaemon.Handler package")
        if metadata.findtext("n:license", namespaces=namespace) != "MIT":
            raise ValueError("Expected MIT license metadata")
        for entry in ("lib/net8.0/TaskDaemon.Handler.dll", "README.md", "LICENSE"):
            if entry not in archive.namelist():
                raise ValueError(f"Package is missing {entry}")

    dotnet = shutil.which("dotnet")
    if dotnet is None:
        raise RuntimeError("dotnet is unavailable; install the .NET 8 SDK before checking the package")
    with tempfile.TemporaryDirectory(prefix="taskdaemon-nuget-consumer-") as directory:
        consumer = Path(directory)
        feed = consumer / "feed"
        feed.mkdir()
        shutil.copyfile(package, feed / f"{package_id}.{version}.nupkg")
        project = ET.Element("Project", Sdk="Microsoft.NET.Sdk")
        properties = ET.SubElement(project, "PropertyGroup")
        for name, value in (("OutputType", "Exe"), ("TargetFramework", "net8.0"),
                            ("ImplicitUsings", "enable"), ("Nullable", "enable")):
            ET.SubElement(properties, name).text = value
        items = ET.SubElement(project, "ItemGroup")
        ET.SubElement(items, "PackageReference", Include=package_id, Version=version)
        ET.ElementTree(project).write(consumer / "consumer.csproj", encoding="utf-8")
        config = ET.Element("configuration")
        sources = ET.SubElement(config, "packageSources")
        ET.SubElement(sources, "clear")
        ET.SubElement(sources, "add", key="local", value=str(feed))
        ET.ElementTree(config).write(consumer / "NuGet.Config", encoding="utf-8")
        shutil.copyfile(Path(__file__).parent / "ProtocolSmoke/Program.cs", consumer / "Program.cs")
        environment = dict(os.environ, DOTNET_CLI_HOME=str(consumer / ".dotnet"),
                           NUGET_PACKAGES=str(consumer / "packages"), DOTNET_NOLOGO="1",
                           DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_GENERATE_ASPNET_CERTIFICATE="false")
        result = subprocess.run(
            [dotnet, "run", "--project", str(consumer / "consumer.csproj"), "--configuration", "Release"],
            env=environment, capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0 or "C# stdio protocol smoke passed" not in result.stdout:
            raise RuntimeError(f"Package consumer failed:\n{result.stdout}\n{result.stderr}")
    print(f"NuGet package consumer verified: {package_id} {version}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Path to the .nupkg produced by dotnet pack")
    arguments = parser.parse_args()
    verify(arguments.package)
