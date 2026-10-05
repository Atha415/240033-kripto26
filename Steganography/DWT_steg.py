
'''
cara pakai:
    encode:
    python stegoDWT.py encode -c foto/foto.png -t kriptografi -o stego.png
    python stegoDWT.py encode -c foto/cover.png -f foto/rahasia.png -o stego.png

    decode:
    python stegoDWT.py decode -s stego.png
    python stegoDWT.py decode -s stego2.png -o rahasia.png 

    
'''
import argparse
import os
import struct

import numpy as np
import pywt
from PIL import Image

DELTA = 20          # step kuantisasi QIM (makin besar = makin tahan noise, makin terlihat)
WAVELET = "haar"
MAGIC = b"DWT1"     # penanda data valid



# ---------- util bit ----------
def bytes_to_bits(data: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8))


def bits_to_bytes(bits: np.ndarray) -> bytes:
    return np.packbits(bits.astype(np.uint8)).tobytes()


# ---------- QIM ----------
def qim_embed(coef: np.ndarray, bits: np.ndarray) -> np.ndarray:
    off = bits * (DELTA / 2.0)
    return np.round((coef - off) / DELTA) * DELTA + off


def qim_extract(coef: np.ndarray) -> np.ndarray:
    d0 = np.abs(coef - np.round(coef / DELTA) * DELTA)
    d1 = np.abs(coef - (np.round((coef - DELTA / 2) / DELTA) * DELTA + DELTA / 2))
    return (d1 < d0).astype(np.uint8)


# ---------- DWT helper ----------
def subbands(channel: np.ndarray):
    """DWT 1 level -> (cA, (cH, cV, cD))"""
    return pywt.dwt2(channel.astype(np.float64), WAVELET)


def capacity_bits(shape) -> int:
    h, w, _ = shape
    return 3 * 3 * (h // 2) * (w // 2)  


def load_cover(path: str) -> np.ndarray:
    img = np.array(Image.open(path).convert("RGB"))
    h, w, _ = img.shape
    img = img[: h - h % 2, : w - w % 2]
    return np.clip(img, 10, 245)


# ---------- ENCODE ----------
def encode(cover_path, out_path, text=None, file_path=None):
    if text is not None:
        kind, name, payload = 0, b"", text.encode("utf-8")
    else:
        kind = 1
        name = os.path.basename(file_path).encode("utf-8")[:255]
        with open(file_path, "rb") as f:
            payload = f.read()

    header = MAGIC + struct.pack(">BBI", kind, len(name), len(payload))
    bits = bytes_to_bits(header + name + payload)

    cover = load_cover(cover_path)
    cap = capacity_bits(cover.shape)
    if len(bits) > cap:
        raise ValueError(f"Data terlalu besar: butuh {len(bits)} bit, kapasitas {cap} bit")
    print(f"[i] Data: {len(bits)} bit | Kapasitas cover: {cap} bit ({len(bits)/cap:.1%})")

    # siapkan semua koefisien (3 channel x 3 subband), embed berurutan
    stego = np.zeros_like(cover, dtype=np.float64)
    pos = 0
    for ch in range(3):
        cA, (cH, cV, cD) = subbands(cover[:, :, ch])
        bands = [cH, cV, cD]
        for i, band in enumerate(bands):
            n = band.size
            chunk = bits[pos:pos + n]
            pos += len(chunk)
            if len(chunk):
                flat = band.flatten()
                flat[: len(chunk)] = qim_embed(flat[: len(chunk)], chunk)
                bands[i] = flat.reshape(band.shape)
        stego[:, :, ch] = pywt.idwt2((cA, tuple(bands)), WAVELET)

    stego = np.clip(np.round(stego), 0, 255).astype(np.uint8)
    Image.fromarray(stego).save(out_path, format="PNG")

    mse = np.mean((cover.astype(float) - stego.astype(float)) ** 2)
    psnr = 10 * np.log10(255 ** 2 / mse) if mse > 0 else float("inf")
    print(f"[+] Stego image disimpan: {out_path} | PSNR = {psnr:.2f} dB")


# ---------- DECODE ----------
def extract_bits(stego: np.ndarray, n_bits: int) -> np.ndarray:
    out = []
    for ch in range(3):
        _, (cH, cV, cD) = subbands(stego[:, :, ch])
        for band in (cH, cV, cD):
            out.append(qim_extract(band.flatten()))
            if sum(len(o) for o in out) >= n_bits:
                return np.concatenate(out)[:n_bits]
    return np.concatenate(out)[:n_bits]


def decode(stego_path, out_path=None):
    img = np.array(Image.open(stego_path).convert("RGB"))
    h, w, _ = img.shape
    img = img[: h - h % 2, : w - w % 2]

    head_len = 4 + 6
    head = bits_to_bytes(extract_bits(img, head_len * 8))
    if head[:4] != MAGIC:
        raise ValueError("Tidak ditemukan pesan tersembunyi (header tidak valid)")
    kind, name_len, data_len = struct.unpack(">BBI", head[4:10])

    total = head_len + name_len + data_len
    raw = bits_to_bytes(extract_bits(img, total * 8))
    name = raw[head_len:head_len + name_len].decode("utf-8", errors="replace")
    payload = raw[head_len + name_len:total]

    if kind == 0:
        print("[+] Pesan tersembunyi:\n" + payload.decode("utf-8", errors="replace"))
    else:
        out = out_path or ("extracted_" + name)
        with open(out, "wb") as f:
            f.write(payload)
        print(f"[+] File '{name}' ({len(payload)} byte) disimpan ke: {out}")


# ---------- CLI ----------
def main():
    p = argparse.ArgumentParser(description="Steganografi DWT (Haar) + QIM")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("encode", help="sembunyikan pesan/file")
    e.add_argument("-c", "--cover", required=True, help="cover image")
    e.add_argument("-o", "--output", default="stego.png", help="output stego (PNG)")
    g = e.add_mutually_exclusive_group(required=True)
    g.add_argument("-t", "--text", help="pesan teks")
    g.add_argument("-f", "--file", help="file/gambar rahasia")

    d = sub.add_parser("decode", help="ekstrak pesan/file")
    d.add_argument("-s", "--stego", required=True, help="stego image")
    d.add_argument("-o", "--output", help="nama file output (jika payload berupa file)")

    a = p.parse_args()
    if a.cmd == "encode":
        encode(a.cover, a.output, text=a.text, file_path=a.file)
    else:
        decode(a.stego, a.output)


if __name__ == "__main__":
    main()