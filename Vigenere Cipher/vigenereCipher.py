def bersihkan_teks(teks):
    return ''.join(c.upper() for c in teks if c.isalpha())

def buat_keystream(teks, key):
    key = bersihkan_teks(key)
    keystream = ''
    for i in range(len(teks)):
        keystream += key[i % len(key)]
    return keystream

def vigenere_enkripsi(plaintext, key):
    plaintext = bersihkan_teks(plaintext)
    keystream = buat_keystream(plaintext, key)
    ciphertext = ''
    for p, k in zip(plaintext, keystream):
        angka_p = ord(p) - ord('A')
        angka_k = ord(k) - ord('A')
        c = (angka_p + angka_k) % 26
        ciphertext += chr(c + ord('A'))
    return ciphertext

def vigenere_dekripsi(ciphertext, key):
    ciphertext = bersihkan_teks(ciphertext)
    keystream = buat_keystream(ciphertext, key)
    plaintext = ''
    for c, k in zip(ciphertext, keystream):
        angka_c = ord(c) - ord('A')
        angka_k = ord(k) - ord('A')
        p = (angka_c - angka_k) % 26
        plaintext += chr(p + ord('A'))
    return plaintext


if __name__ == '__main__':
    print("=== Vigenere Cipher ===")
    print("1. Enkripsi")
    print("2. Dekripsi")
    pilihan = input("Pilih menu (1/2) : ")

    if pilihan == '1':
        plaintext = input("Masukkan plaintext : ")
        key = input("Masukkan key        : ")
        hasil = vigenere_enkripsi(plaintext, key)
        print("\nHasil Enkripsi   :", hasil)

    elif pilihan == '2':
        ciphertext = input("Masukkan ciphertext : ")
        key = input("Masukkan key         : ")
        hasil = vigenere_dekripsi(ciphertext, key)
        print("\nHasil Dekripsi   :", hasil)

    else:
        print("Pilihan tidak valid.")