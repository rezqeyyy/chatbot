# chatbot.py (Versi Final Disesuaikan)

import google.generativeai as genai

API_KEY_ANDA = "AIzaSyCv1CwT5pWAF-fkj5nHjIrryu6F2gZeL9c" 

try:
    genai.configure(api_key=API_KEY_ANDA)
except Exception as e:
    print(f"Konfigurasi gagal. Pastikan API Key valid. Error: {e}")
    exit()

model = genai.GenerativeModel('gemini-2.5-flash')
chat = model.start_chat(history=[])

print("--- Chatbot Gemini Dimulai ---")
print("Ketik 'keluar' untuk mengakhiri chat.")
print("-" * 30)


while True:
    user_input = input("Anda: ")

    if user_input.lower() == 'keluar':
        print("\n--- Chatbot Berakhir ---")
        break

    try:
        response = chat.send_message(user_input)
        print(f"Dara Cantik: {response.text}\n")
    except Exception as e:
        print(f"Terjadi kesalahan saat mengirim pesan: {e}")
        break