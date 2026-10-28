#!/usr/bin/env python3
"""Install or verify the pinned local WASM runtime from the npm registry."""
import argparse
import base64
import hashlib
import io
from pathlib import Path
import tarfile
import urllib.request

VERSION = "1.30.0"
URL = f"https://registry.npmjs.org/onnxruntime-web/-/onnxruntime-web-{VERSION}.tgz"
INTEGRITY = "sha512-q0y+JrrtukXSzsBWEMccVfqX25LRmosXHF+CaRJmg8pZClzcV7svNc4rKY3jL02Vb7QmRMDs1SigqR4CXAfKYQ=="
FILES = {
    "package/dist/ort.wasm.min.js": "ort.min.js",
    "package/dist/ort-wasm-simd-threaded.mjs": "ort-wasm-simd-threaded.mjs",
    "package/dist/ort-wasm-simd-threaded.wasm": "ort-wasm-simd-threaded.wasm",
    "package/package.json": "package.json",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--package", type=Path, help="Tarball npm local; también se verifica su integridad")
    args = parser.parse_args()
    if args.package:
        payload = args.package.read_bytes()
    else:
        with urllib.request.urlopen(URL, timeout=90) as response:
            payload = response.read()
    actual = "sha512-" + base64.b64encode(hashlib.sha512(payload).digest()).decode()
    if actual != INTEGRITY:
        raise SystemExit("Integridad del paquete distinta a la versión fijada; instalación cancelada.")
    destination = Path(__file__).resolve().parent / "vendor/onnxruntime-web"
    if not args.verify_only:
        destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        for member, filename in FILES.items():
            stream = archive.extractfile(member)
            if stream is None:
                raise SystemExit(f"Falta el archivo esperado: {member}")
            data = stream.read()
            target = destination / filename
            if args.verify_only:
                if not target.is_file() or target.read_bytes() != data:
                    raise SystemExit(f"El runtime local no coincide: {target}")
            else:
                target.write_bytes(data)
    license_data = (Path(__file__).resolve().parent / "recursos/ONNXRuntime-LICENSE.txt").read_bytes()
    license_target = destination / "LICENSE.txt"
    if args.verify_only:
        if not license_target.is_file() or license_target.read_bytes() != license_data:
            raise SystemExit("La licencia MIT local no coincide con la copia conservada.")
    else:
        license_target.write_bytes(license_data)
    print(f"ONNX Runtime Web {VERSION}: {'verificado' if args.verify_only else 'instalado'}; integridad SHA-512 correcta.")


if __name__ == "__main__":
    main()
