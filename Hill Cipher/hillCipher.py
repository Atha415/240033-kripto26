import numpy as np

MOD = 26


def bersihkan_teks(teks):
    return ''.join(c for c in teks.upper() if c.isalpha())


def teks_ke_angka(teks):
    return [ord(c) - ord('A') for c in teks]


def angka_ke_teks(angka):
    return ''.join(chr(int(a) % MOD + ord('A')) for a in angka)


def invers_modulo(a, m=MOD):
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


def determinan_matriks(matriks):
    det = int(round(np.linalg.det(matriks)))
    return det % MOD


def invers_matriks_modulo(matriks, m=MOD):
    n = matriks.shape[0]
    det = determinan_matriks(matriks)
    det_inv = invers_modulo(det, m)

    if det_inv is None:
        raise ValueError(
            f"Matriks kunci tidak memiliki invers modulo {m} "
            f"(determinan = {det}, gcd(det, {m}) != 1)."
        )

    kofaktor = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            minor = np.delete(np.delete(matriks, i, axis=0), j, axis=1)
            kofaktor[i][j] = ((-1) ** (i + j)) * round(np.linalg.det(minor))

    adjoin = kofaktor.T
    invers = (det_inv * adjoin) % m
    return invers.astype(int)


def baca_matriks_dari_input(n, nama="kunci"):
    print(f"Masukkan matriks {nama} berukuran {n}x{n} (baris demi baris, " f"nilai dipisah spasi):")
    matriks = []
    for i in range(n):
        while True:
            baris = input(f"Baris {i + 1}: ").strip().split()
            try:
                baris = [int(x) for x in baris]
                if len(baris) != n:
                    print(f"Jumlah nilai harus {n}, coba lagi.")
                    continue
                matriks.append(baris)
                break
            except ValueError:
                print("Masukkan hanya angka, coba lagi.")
    return np.array(matriks)


def enkripsi(plaintext, kunci):
    n = kunci.shape[0]
    teks = bersihkan_teks(plaintext)

    while len(teks) % n != 0:
        teks += 'X'

    angka = teks_ke_angka(teks)
    hasil = []

    for i in range(0, len(angka), n):
        blok = np.array(angka[i:i + n])
        blok_terenkripsi = np.dot(kunci, blok) % MOD
        hasil.extend(blok_terenkripsi)

    return angka_ke_teks(hasil)

def dekripsi(ciphertext, kunci):
    n = kunci.shape[0]
    teks = bersihkan_teks(ciphertext)

    if len(teks) % n != 0:
        raise ValueError("Panjang ciphertext harus kelipatan ukuran kunci.")

    kunci_invers = invers_matriks_modulo(kunci)
    angka = teks_ke_angka(teks)
    hasil = []

    for i in range(0, len(angka), n):
        blok = np.array(angka[i:i + n])
        blok_terdekripsi = np.dot(kunci_invers, blok) % MOD
        hasil.extend(blok_terdekripsi)

    return angka_ke_teks(hasil)

def cari_kunci(plaintext, ciphertext, n):
    p_bersih = bersihkan_teks(plaintext)
    c_bersih = bersihkan_teks(ciphertext)

    if len(p_bersih) != len(c_bersih):
        raise ValueError(
            "Panjang plaintext dan ciphertext (setelah huruf non-alfabet " "dibuang) harus sama.")

    if len(p_bersih) < n * n:
        raise ValueError(
            f"Butuh minimal {n * n} karakter plaintext & ciphertext "
            f"untuk kunci berukuran {n}x{n}."
        )

    jumlah_blok = len(p_bersih) // n
    p_blok = [teks_ke_angka(p_bersih[i * n:(i + 1) * n]) for i in range(jumlah_blok)]
    c_blok = [teks_ke_angka(c_bersih[i * n:(i + 1) * n]) for i in range(jumlah_blok)]

    panjang_terpakai = jumlah_blok * n
    p_terpakai = p_bersih[:panjang_terpakai]
    c_terpakai = c_bersih[:panjang_terpakai]

    from itertools import combinations

    for kombinasi in combinations(range(jumlah_blok), n):
        P = np.array([p_blok[i] for i in kombinasi]).T
        C = np.array([c_blok[i] for i in kombinasi]).T

        det = determinan_matriks(P)
        if invers_modulo(det) is None:
            continue 

        P_invers = invers_matriks_modulo(P)
        K = (np.dot(C, P_invers) % MOD).astype(int)

        hasil_cek = enkripsi(p_terpakai, K)
        if hasil_cek == c_terpakai:
            return K

    raise ValueError(
        "Tidak ditemukan kombinasi blok yang menghasilkan matriks kunci "
        "valid dan konsisten dengan seluruh teks. Coba berikan pasangan "
        "plaintext-ciphertext yang lebih panjang."
    )

def cetak_matriks(matriks, nama="Matriks"):
    print(f"{nama}:")
    for baris in matriks:
        print(' '.join(str(int(x)).rjust(3) for x in baris))


def cari_kunci_verbose(plaintext, ciphertext, n):
    from itertools import combinations

    p_bersih = bersihkan_teks(plaintext)
    c_bersih = bersihkan_teks(ciphertext)

    if len(p_bersih) != len(c_bersih):
        raise ValueError(
            "Panjang plaintext dan ciphertext (setelah huruf non-alfabet "
            "dibuang) harus sama."
        )
    if len(p_bersih) < n * n:
        raise ValueError(
            f"Butuh minimal {n * n} karakter plaintext & ciphertext "
            f"untuk kunci berukuran {n}x{n}."
        )

    p_angka_full = teks_ke_angka(p_bersih)
    c_angka_full = teks_ke_angka(c_bersih)

    print(f"\nDiketahui:")
    print(f"  Pt = {p_bersih}  ; Ct = {c_bersih}  ; m = {n}")
    print(f"\n{p_bersih} -> {tuple(p_angka_full)}")
    print(f"{c_bersih} -> {tuple(c_angka_full)}")

    jumlah_blok = len(p_bersih) // n
    p_blok = [p_angka_full[i * n:(i + 1) * n] for i in range(jumlah_blok)]
    c_blok = [c_angka_full[i * n:(i + 1) * n] for i in range(jumlah_blok)]

    panjang_terpakai = jumlah_blok * n
    p_terpakai = p_bersih[:panjang_terpakai]
    c_terpakai = c_bersih[:panjang_terpakai]

    for kombinasi in combinations(range(jumlah_blok), n):
        P = np.array([p_blok[i] for i in kombinasi]).T
        C = np.array([c_blok[i] for i in kombinasi]).T

        det = determinan_matriks(P)
        det_inv = invers_modulo(det)
        if det_inv is None:
            continue

        blok_terpakai = ', '.join(str(tuple(p_blok[i])) for i in kombinasi)
        print(f"\nBlok yang dipakai: {blok_terpakai}")
        cetak_matriks(P, "P")
        cetak_matriks(C, "C")
        print(f"det(P) = {det} (mod {MOD})   invers det = {det_inv}")

        n_ = P.shape[0]
        kofaktor = np.zeros((n_, n_))
        for i in range(n_):
            for j in range(n_):
                minor = np.delete(np.delete(P, i, axis=0), j, axis=1)
                kofaktor[i][j] = ((-1) ** (i + j)) * round(np.linalg.det(minor))
        adjoin = kofaktor.T
        cetak_matriks(adjoin, "adj(P)")

        hasil_sebelum_mod = np.dot(C, adjoin)
        cetak_matriks(hasil_sebelum_mod, "C x adj(P) (sebelum mod)")

        P_invers = (det_inv * adjoin) % MOD
        K = (np.dot(C, P_invers) % MOD).astype(int)
        print(f"\nK = C . P^-1 (mod {MOD}) =")
        cetak_matriks(K, "K")

        hasil_cek = enkripsi(p_terpakai, K)
        if hasil_cek == c_terpakai:
            print(f"\nVerifikasi: enkripsi '{p_terpakai}' dengan K -> {hasil_cek} " f"(cocok dengan ciphertext)")
            return K
        else:
            print("(Kunci ini tidak konsisten dengan seluruh teks, mencoba kombinasi lain...)")

    raise ValueError(
        "Tidak ditemukan kombinasi blok yang menghasilkan matriks kunci "
        "valid dan konsisten dengan seluruh teks. Coba berikan pasangan "
        "plaintext-ciphertext yang lebih panjang."
    )


def menu_enkripsi():
    print("\n--- ENKRIPSI ---")
    plaintext = input("Masukkan plaintext: ")
    n = int(input("Ukuran matriks kunci (n): "))
    kunci = baca_matriks_dari_input(n, "kunci")

    try:
        hasil = enkripsi(plaintext, kunci)
        print(f"\nCiphertext hasil enkripsi: {hasil}")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")


def menu_dekripsi():
    print("\n--- DEKRIPSI ---")
    ciphertext = input("Masukkan ciphertext: ")
    n = int(input("Ukuran matriks kunci (n): "))
    kunci = baca_matriks_dari_input(n, "kunci")

    try:
        hasil = dekripsi(ciphertext, kunci)
        print(f"\nPlaintext hasil dekripsi: {hasil}")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")


def menu_cari_kunci():
    print("\n--- MENCARI KUNCI ---")
    plaintext = input("Masukkan plaintext (yang diketahui): ")
    ciphertext = input("Masukkan ciphertext (pasangannya): ")
    n = int(input("Ukuran matriks kunci (n): "))

    try:
        kunci = cari_kunci(plaintext, ciphertext, n)
        cetak_matriks(kunci, "\nMatriks kunci yang ditemukan")
        verifikasi = enkripsi(plaintext, kunci)
        print(f"\nVerifikasi: enkripsi plaintext dengan kunci ini -> {verifikasi}")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")


def main():
    while True:
        print("\n===== PROGRAM HILL CIPHER =====")
        print("1. Enkripsi")
        print("2. Dekripsi")
        print("3. Cari Kunci")
        print("4. Keluar")
        pilihan = input("Pilih menu (1-4): ").strip()

        if pilihan == '1':
            menu_enkripsi()
        elif pilihan == '2':
            menu_dekripsi()
        elif pilihan == '3':
            menu_cari_kunci()
        elif pilihan == '4':
            print("Program selesai. Terima kasih!")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")


if __name__ == "__main__":
    main()