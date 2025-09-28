# chatbot.py (Versi Asisten Bisnis Fungsional)

import google.generativeai as genai
import os
import datetime

#1. KONFIGURASI API
API_KEY_ANDA = "AIzaSyCv1CwT5pWAF-fkj5nHjIrryu6F2gZeL9c" 

try:
    genai.configure(api_key=API_KEY_ANDA)
except Exception as e:
    print(f"Konfigurasi API gagal. Pastikan API Key valid. Error: {e}")
    exit()

#2. INISIALISASI MODEL (SATU KALI SAJA)
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    print(f"Gagal membuat model Gemini. Error: {e}")
    exit()

#3. DEFINISI FUNGSI UNTUK SETIAP FITUR
def fitur_konsultasi():
    """Fitur tanya jawab bebas dengan AI sebagai konsultan bisnis."""
    print("\n--- Mode Konsultasi Bisnis ---")
    print("Anda bisa bertanya apa saja seputar bisnis. Ketik 'kembali' untuk ke menu utama.")
    
    # Memberi peran pada AI
    chat = model.start_chat(history=[
        {
            "role": "user",
            "parts": ["Mulai sekarang, Anda adalah seorang konsultan bisnis profesional dari Indonesia. Berikan jawaban yang strategis, praktis, dan mudah dipahami."]
        },
        {
            "role": "model",
            "parts": ["Baik, saya siap membantu. Silakan ajukan pertanyaan bisnis Anda."]
        }
    ])
    
    while True:
        user_input = input("Anda: ")
        if user_input.lower() == 'kembali':
            break

        try:
            response = chat.send_message(user_input)
            print(f"Konsultan AI: {response.text}\n")
        except Exception as e:
            print(f"Terjadi kesalahan saat mengirim pesan: {e}")
            break
            
    print("\nKembali ke menu utama...")

def fitur_rekomendasi():
    """Memberikan rekomendasi bisnis berdasarkan jawaban pengguna."""
    print("\n--- Mode Rekomendasi Bisnis ---")
    print("Jawab beberapa pertanyaan berikut untuk mendapatkan rekomendasi bisnis dari AI.")

    pertanyaan = [
        "Berapa modal awal yang Anda siapkan? (misal: di bawah 5 juta, 5-20 juta, di atas 20 juta)",
        "Apa minat, hobi, atau passion Anda? (misal: kopi, fashion, menulis, otomotif)",
        "Apa keahlian spesifik yang Anda miliki? (misal: memasak, desain grafis, marketing digital)",
        "Berapa banyak waktu luang yang bisa Anda alokasikan per minggu? (misal: 5-10 jam, 10-20 jam, penuh waktu)"
    ]
    
    jawaban = {}
    for p in pertanyaan:
        jawaban[p] = input(f"{p}\n> ")

    # Format jawaban menjadi satu prompt
    prompt_detail = "Analisis data berikut dan berikan 3 rekomendasi bisnis yang paling cocok untuk saya.\n"
    prompt_detail += f"- Modal: {jawaban[pertanyaan[0]]}\n"
    prompt_detail += f"- Minat/Hobi: {jawaban[pertanyaan[1]]}\n"
    prompt_detail += f"- Keahlian: {jawaban[pertanyaan[2]]}\n"
    prompt_detail += f"- Waktu Luang: {jawaban[pertanyaan[3]]}\n"
    prompt_detail += "Untuk setiap rekomendasi, berikan analisis singkat (target pasar, potensi keuntungan, langkah awal) dalam format yang jelas dan terstruktur."

    print("\nAI sedang berpikir... Mohon tunggu sebentar.")
    try:
        response = model.generate_content(prompt_detail)
        rekomendasi_ai = response.text
        print("\n--- Rekomendasi Bisnis dari AI ---")
        print(rekomendasi_ai)

        simpan = input("\nApakah Anda ingin menyimpan rekomendasi ini? (y/n): ").lower()
        if simpan == 'y':
            nama_file = f"rekomendasi_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(nama_file, 'w', encoding='utf-8') as f:
                f.write(rekomendasi_ai)
            print(f"Rekomendasi disimpan sebagai '{nama_file}'")
    except Exception as e:
        print(f"Terjadi kesalahan saat menghasilkan rekomendasi: {e}")

    print("\nKembali ke menu utama...")

def fitur_catatan():
    """Fitur untuk membuat, membaca, dan menghapus catatan bisnis."""
    notes_dir = "catatan_bisnis"
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)

    while True:
        print("\n--- Mode Catatan Bisnis ---")
        print("1. Buat Catatan Baru")
        print("2. Baca Semua Catatan")
        print("3. Hapus Catatan")
        print("4. Kembali ke Menu Utama")
        pilihan_catatan = input("Pilih opsi (1-4): ")

        if pilihan_catatan == '1':
            judul = input("Masukkan judul catatan: ")
            konten = input("Tulis isi catatan Anda (tekan Enter untuk menyimpan):\n")
            nama_file = os.path.join(notes_dir, f"{judul.replace(' ', '_')}.txt")
            with open(nama_file, 'w', encoding='utf-8') as f:
                f.write(konten)
            print(f"Catatan '{judul}' berhasil disimpan.")
        
        elif pilihan_catatan == '2':
            print("\n--- Daftar Catatan ---")
            files = [f for f in os.listdir(notes_dir) if f.endswith('.txt')]
            if not files:
                print("Belum ada catatan.")
            else:
                for i, file_name in enumerate(files):
                    print(f"{i + 1}. {file_name.replace('.txt', '').replace('_', ' ')}")
                try:
                    pilih_baca = int(input("Pilih nomor catatan untuk dibaca (atau 0 untuk kembali): "))
                    if 0 < pilih_baca <= len(files):
                        with open(os.path.join(notes_dir, files[pilih_baca - 1]), 'r', encoding='utf-8') as f:
                            print("\n--- Isi Catatan ---")
                            print(f.read())
                except ValueError:
                    print("Input tidak valid.")
        
        elif pilihan_catatan == '3':
            print("\n--- Hapus Catatan ---")
            files = [f for f in os.listdir(notes_dir) if f.endswith('.txt')]
            if not files:
                print("Belum ada catatan untuk dihapus.")
            else:
                for i, file_name in enumerate(files):
                    print(f"{i + 1}. {file_name.replace('.txt', '').replace('_', ' ')}")
                try:
                    pilih_hapus = int(input("Pilih nomor catatan untuk dihapus (atau 0 untuk kembali): "))
                    if 0 < pilih_hapus <= len(files):
                        file_to_delete = os.path.join(notes_dir, files[pilih_hapus - 1])
                        konfirmasi = input(f"Anda yakin ingin menghapus '{files[pilih_hapus - 1]}'? (y/n): ").lower()
                        if konfirmasi == 'y':
                            os.remove(file_to_delete)
                            print("Catatan berhasil dihapus.")
                except ValueError:
                    print("Input tidak valid.")
        
        elif pilihan_catatan == '4':
            break
        else:
            print("Pilihan tidak valid.")

    print("\nKembali ke menu utama...")

def fitur_kalkulator():
    """Kalkulator sederhana untuk perhitungan cepat."""
    print("\n--- Mode Kalkulator ---")
    print("Masukkan perhitungan (contoh: 50000 * 0.2) atau ketik 'kembali' untuk keluar.")
    
    while True:
        ekspresi = input("> ")
        if ekspresi.lower() == 'kembali':
            break
        try:
            # Peringatan: eval() bisa berisiko jika input tidak terkontrol.
            # Namun, untuk aplikasi lokal sederhana ini, risikonya minimal.
            hasil = eval(ekspresi)
            print(f"Hasil: {hasil}")
        except Exception as e:
            print(f"Ekspresi tidak valid. Error: {e}")
            
    print("\nKembali ke menu utama...")

#4. LOOP MENU UTAMA
while True:
    print("\n=====================================")
    print(" Selamat Datang di Asisten Bisnis AI")
    print("=====================================")
    print("Pilih fitur:")
    print("1. Konsultasi Bisnis")
    print("2. Rekomendasi Bisnis")
    print("3. Catatan Bisnis")
    print("4. Kalkulator")
    print("5. Keluar")

    pilihan = input("Masukkan pilihan Anda (1-5): ")

    if pilihan == '1':
        fitur_konsultasi()
    elif pilihan == '2':
        fitur_rekomendasi()
    elif pilihan == '3':
        fitur_catatan()
    elif pilihan == '4':
        fitur_kalkulator()
    elif pilihan == '5':
        print("Terima kasih telah menggunakan asisten bisnis. Sampai jumpa!")
        break
    else:
        print("Pilihan tidak valid. Silakan masukkan angka antara 1 sampai 5.")