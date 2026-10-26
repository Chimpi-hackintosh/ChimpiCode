"""Explicit WiX components from an existing frozen Windows staging tree."""
import hashlib
import shutil
import tempfile
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from .builds import BuildError, command

WIX = "http://wixtoolset.org/schemas/v4/wxs"
UI = WIX + "/ui"
UPGRADE_NAMESPACE = uuid.UUID("5a6b0c30-8462-4bac-a07a-9674aba77494")
ET.register_namespace("", WIX)
ET.register_namespace("ui", UI)


def element(parent, tag, **attrs):
    return ET.SubElement(parent, "{" + WIX + "}" + tag, attrs)


def identifier(prefix, value):
    return prefix + hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def write_wxs(staging, output, name="ChimpiCode", version="1.0.0", language="en"):
    staging = Path(staging).resolve()
    if not (staging / f"{name}.exe").is_file():
        raise FileNotFoundError(staging / f"{name}.exe")
    pt = language == "pt-BR"
    root = ET.Element("{" + WIX + "}Wix")
    product = element(root, "Package", Name=name, Manufacturer="SnoopyOS Company", Version=version,
                      Language="1046" if pt else "1033", Scope="perMachine", InstallerVersion="500",
                      UpgradeCode=str(uuid.uuid5(UPGRADE_NAMESPACE, name)).upper())
    element(product, "MajorUpgrade", DowngradeErrorMessage=("Uma versão mais recente já está instalada." if pt else "A newer version is already installed."),
            Schedule="afterInstallInitialize", IgnoreLanguage="yes")
    element(product, "MediaTemplate", EmbedCab="yes", CompressionLevel="high")
    element(product, "Property", Id="ARPNOMODIFY", Value="1")
    programs = element(product, "StandardDirectory", Id="ProgramFiles64Folder")
    manufacturer = element(programs, "Directory", Id="ManufacturerFolder", Name="SnoopyOS Company")
    install = element(manufacturer, "Directory", Id="INSTALLFOLDER", Name=name)
    directories = {".": install}
    refs = []
    exe_id = None
    for file in sorted(staging.rglob("*")):
        if not file.is_file():
            continue
        if file.suffix.lower() in {".py", ".pyw"}:
            raise ValueError(f"Source file in staging: {file}")
        relative = file.relative_to(staging)
        current = Path(".")
        for part in relative.parent.parts:
            parent_key = current.as_posix()
            current = current / part
            key = current.as_posix()
            if key not in directories:
                directories[key] = element(directories[parent_key], "Directory", Id=identifier("D_", key), Name=part)
        key = relative.as_posix()
        component_id = identifier("C_", key)
        component = element(directories[relative.parent.as_posix()], "Component", Id=component_id,
                            Guid=str(uuid.uuid5(UPGRADE_NAMESPACE, name + "/" + key)).upper(), Bitness="always64")
        file_id = identifier("F_", key)
        element(component, "File", Id=file_id, Source=str(file), KeyPath="yes")
        refs.append(component_id)
        if key == name + ".exe":
            exe_id = file_id
    menu = element(product, "StandardDirectory", Id="ProgramMenuFolder")
    folder = element(menu, "Directory", Id="AppMenuFolder", Name=name)
    shortcuts = element(folder, "Component", Id="StartMenuShortcuts", Guid=str(uuid.uuid5(UPGRADE_NAMESPACE, name + "/shortcuts")), Bitness="always64")
    element(shortcuts, "Shortcut", Id="StartMenuShortcut", Name=name, Target=f"[#{exe_id}]", WorkingDirectory="INSTALLFOLDER")
    element(shortcuts, "RemoveFolder", Id="RemoveStartMenuFolder", On="uninstall")
    element(shortcuts, "RegistryValue", Root="HKLM", Key=f"Software\\SnoopyOS Company\\{name}",
            Name="Installed", Type="integer", Value="1", KeyPath="yes")
    feature = element(product, "Feature", Id="MainFeature", Title=name, Level="1", AllowAbsent="no")
    if name == "ChimpiCode" and (staging / "from.cmd").is_file():
        cli = element(install, "Component", Id="CommandLineEnvironment", Bitness="always64",
                      Guid=str(uuid.uuid5(UPGRADE_NAMESPACE, name + "/cli-path")))
        element(cli, "RegistryValue", Root="HKLM", Key="Software\\SnoopyOS Company\\ChimpiCode",
                Name="CommandLineInstalled", Type="integer", Value="1", KeyPath="yes")
        element(cli, "Environment", Id="ChimpiCodeCommandPath", Name="PATH", Value="[INSTALLFOLDER]",
                Action="set", Part="last", System="yes", Permanent="no")
        element(feature, "ComponentRef", Id="CommandLineEnvironment")
    for ref in refs + ["StartMenuShortcuts"]:
        element(feature, "ComponentRef", Id=ref)
    desktop = element(product, "StandardDirectory", Id="DesktopFolder")
    desktop_component = element(desktop, "Component", Id="DesktopShortcutComponent", Guid=str(uuid.uuid5(UPGRADE_NAMESPACE, name + "/desktop")), Bitness="always64")
    element(desktop_component, "Shortcut", Id="DesktopShortcut", Name=name, Target=f"[#{exe_id}]", WorkingDirectory="INSTALLFOLDER")
    element(desktop_component, "RegistryValue", Root="HKLM", Key=f"Software\\SnoopyOS Company\\{name}",
            Name="DesktopShortcut", Type="integer", Value="1", KeyPath="yes")
    extra = element(product, "Feature", Id="DesktopFeature", Title="Atalho na área de trabalho" if pt else "Desktop shortcut", Level="2")
    element(extra, "ComponentRef", Id="DesktopShortcutComponent")
    element(product, "Property", Id="INSTALLLEVEL", Value="1")
    # Only display a license agreement when this package actually includes one.
    # ChimpiCode's MIT license is copied into its staging tree by the app build.
    license_file = staging / "LICENSE"
    if license_file.is_file():
        license_rtf = Path(output).with_suffix(".rtf")
        escaped = []
        for char in license_file.read_text(encoding="utf-8"):
            if char in "\\{}":
                escaped.append("\\" + char)
            elif char == "\n":
                escaped.append("\\par\n")
            elif ord(char) > 127:
                for index in range(0, len(char.encode("utf-16-le")), 2):
                    unit = int.from_bytes(char.encode("utf-16-le")[index:index+2], "little", signed=True)
                    escaped.append(f"\\u{unit}?")
            else:
                escaped.append(char)
        license_rtf.write_text("{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Arial;}}\\f0\\fs18 " + "".join(escaped) + "}", encoding="ascii")
        element(product, "WixVariable", Id="WixUILicenseRtf", Value=str(license_rtf.resolve()))
        ET.SubElement(product, "{" + UI + "}WixUI", {"Id": "WixUI_FeatureTree"})
    element(product, "UIRef", Id="WixUI_ErrorProgressText")
    ET.indent(root)
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)
    return len(refs)


def build_msi(staging, output, name="ChimpiCode", version="1.0.0", language="en"):
    wix = shutil.which("wix")
    if not wix:
        raise BuildError("wix_missing")
    with tempfile.TemporaryDirectory(prefix="chimpicode-wix-") as temporary:
        source = Path(temporary) / "Package.wxs"
        write_wxs(staging, source, name, version, language)
        culture = "pt-br" if language == "pt-BR" else "en-us"
        result = command([wix, "build", source, "-arch", "x64", "-ext", "WixToolset.UI.wixext",
                          "-culture", culture, "-o", output], timeout=600)
        if not result.ok:
            raise RuntimeError(result.output)
    return Path(output)
