"""Inspect the original public unsigned archive, never a device report or signed IPA.

Only image-relative code offsets are used. No ASLR addresses, device identifiers,
crash report, signing credentials, or provisioning profiles are inputs/outputs.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile


ARCHIVE_SHA256 = "102dd223c67436ab4a85849f5e695242b82fb9970972947fe148039dbe46d76c"
LIBRARY_UUID = "17dc9a94-2103-381d-9cdb-435759ebbd9b"
OFFSETS = (0x38B2E4, 0x38A184, 0x90B04)


def main():
    source, output = map(Path, sys.argv[1:])
    output.mkdir(parents=True, exist_ok=True)
    archives = list(source.rglob("NEBULA-NativeVPN-Unsigned.xcarchive.tar.gz"))
    if len(archives) != 1:
        raise SystemExit("Expected exactly one original archive")
    archive = archives[0]
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != ARCHIVE_SHA256:
        raise SystemExit("Original archive hash mismatch; refusing symbol substitution")

    def run(name, args, required=True):
        result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output / name).write_text(result.stdout, encoding="utf-8")
        if required and result.returncode:
            raise SystemExit(f"{name} failed ({result.returncode})")
        return result.stdout

    run("xcode.txt", ["xcodebuild", "-version"])
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        base = "NEBULA-NativeVPN-Unsigned.xcarchive/"
        binary_member = base + "Products/Applications/sing-box.app/Frameworks/Library.framework/Library"
        dwarf_member = base + "dSYMs/Library.framework.dSYM/Contents/Resources/DWARF/Library"
        binary, dwarf = root / "Library", root / "Library.dwarf"
        with tarfile.open(archive) as tar:
            # Copy just two explicitly named regular files; no archive paths are extracted.
            for member, destination in ((binary_member, binary), (dwarf_member, dwarf)):
                info = tar.getmember(member)
                if not info.isfile():
                    raise SystemExit("Unexpected non-file archive member")
                destination.write_bytes(tar.extractfile(info).read())
        for name, path in (("binary", binary), ("dsym", dwarf)):
            uuids = run(f"{name}-uuid.txt", ["xcrun", "dwarfdump", "--uuid", str(path)])
            if LIBRARY_UUID not in uuids.lower():
                raise SystemExit(f"{name} UUID mismatch")
        (output / "provenance.json").write_text(json.dumps({
            "sourceRun": 43436217497,
            "sourceCommit": "5743a8412714bf96a7cd32b9e2237fd34f4d2d7e",
            "archiveSHA256": digest,
            "librarySHA256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "dwarfSHA256": hashlib.sha256(dwarf.read_bytes()).hexdigest(),
            "uuid": LIBRARY_UUID,
            "imageTextVMAddress": "0x0",
            "imageRelativeOffsets": [hex(n) for n in OFFSETS],
        }, indent=2) + "\n", encoding="utf-8")
        run("symbolication.txt", ["xcrun", "atos", "-arch", "arm64", "-o", str(dwarf),
                                   *[hex(n) for n in OFFSETS]])
        # Return addresses may map to the next source line; inspect the preceding ARM64 instruction too.
        run("preceding-instruction-symbolication.txt", ["xcrun", "atos", "-arch", "arm64", "-o", str(dwarf),
                                                        *[hex(n - 4) for n in OFFSETS]])
        run("library-symbols.txt", ["xcrun", "nm", "-n", str(binary)])
        run("dwarf-symbols.txt", ["xcrun", "nm", "-n", str(dwarf)])
        commands = ["xcrun", "lldb", "--batch", "--no-lldbinit", "-o", f'target create "{binary}"',
                    "-o", f'target symbols add "{dwarf}"']
        for address in OFFSETS:
            commands += ["-o", f"image lookup -v -a {hex(address)}",
                         "-o", f"disassemble -s {hex(address - 128)} -e {hex(address + 64)}"]
        run("lldb-lookup-disassembly.txt", commands)
        run("load-commands.txt", ["xcrun", "otool", "-l", str(binary)])
        print((output / "symbolication.txt").read_text())
        print("Original binary and dSYM UUID verified; no rebuild, signing, or execution performed.")


if __name__ == "__main__":
    main()
