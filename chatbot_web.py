import streamlit as st
from streamlit_option_menu import option_menu
import google.generativeai as genai
import os, datetime
import math

# PENGATURAN HALAMAN & CSS ADAPTIF
st.set_page_config(
    page_title="Asisten Bisnis AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# CSS ini menggunakan variabel Streamlit (--text-color, dll.) agar bisa beradaptasi
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* --- Sidebar --- */
[data-testid="stSidebar"] {
    border-right: 1px solid var(--secondary-background-color);
    padding: 1.5rem 1rem;
}
.option-menu-container .nav-link {
    border-radius: 0.5rem !important;
    color: var(--text-color) !important;
    opacity: 0.7;
    transition: all 0.2s;
}
.option-menu-container .nav-link:hover {
    opacity: 1;
    background: var(--secondary-background-color) !important;
}
.option-menu-container .nav-link-selected {
    background-color: var(--primary-color) !important;
    color: white !important;
    opacity: 1;
}
.option-menu-container .nav-link-selected svg, .option-menu-container .nav-link:hover svg {
    fill: white !important;
}

/* --- Konten Utama --- */
h1 {
    border-bottom: 2px solid var(--primary-color);
    padding-bottom: 0.3rem;
    margin-bottom: 1.5rem;
}
[data-testid="stChatMessage"] {
    background-color: var(--secondary-background-color);
    border-radius: 0.75rem;
}
.stButton>button {
    border-radius: 0.5rem;
}

/* --- Kalkulator Adaptif --- */
.calculator-display {
    text-align: right !important;
    font-size: 2.5rem !important;
    font-weight: 600 !important;
    padding: 1rem !important;
    background-color: var(--secondary-background-color) !important;
    border-radius: 0.5rem !important;
    color: var(--text-color);
}
.stButton>button.equals-button {
    background-color: var(--primary-color) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# KONFIGURASI API
API_KEY = "AIzaSyCv1CwT5pWAF-fkj5nHjIrryu6F2gZeL9c"
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    st.error(f"Konfigurasi API gagal: {e}")
    st.stop()

# FUNGSI-FUNGSI FITUR
def fitur_konsultasi():
    st.title("💬 Konsultasi Bisnis")
    st.markdown("Ajukan pertanyaan apa pun seputar bisnis kepada Konsultan AI.")
    if "chat_session" not in st.session_state:
        chat = model.start_chat(history=[
            {"role": "user", "parts": ["Anda adalah konsultan bisnis profesional dari Indonesia."]},
            {"role": "model", "parts": ["Tentu, saya siap membantu. Silakan ajukan pertanyaan bisnis Anda."]}
        ])
        st.session_state.chat_session = chat
    for msg in st.session_state.chat_session.history:
        role = "AI" if msg.role == "model" else "Anda"
        with st.chat_message(role):
            st.markdown(msg.parts[0].text)
    if prompt := st.chat_input("Tulis pertanyaan Anda…"):
        with st.chat_message("Anda"):
            st.markdown(prompt)
        with st.spinner("AI sedang berpikir..."):
            try:
                resp = st.session_state.chat_session.send_message(prompt)
                with st.chat_message("AI"):
                    st.markdown(resp.text)
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

def fitur_rekomendasi():
    st.title("💡 Rekomendasi Bisnis")
    st.markdown("Isi formulir di bawah ini untuk mendapatkan ide bisnis yang dipersonalisasi.")
    with st.container(border=True):
        with st.form("rec_form"):
            st.subheader("Profil Calon Pebisnis")
            modal = st.text_input("Berapa modal awal yang Anda siapkan?", placeholder="Contoh: Di bawah 5 juta")
            minat = st.text_input("Apa minat atau hobi utama Anda?")
            keahlian = st.text_input("Apa keahlian spesifik yang Anda miliki?")
            waktu = st.text_input("Berapa waktu luang Anda per minggu?")
            submit = st.form_submit_button("🚀 Berikan Saya Ide!", use_container_width=True)
    if submit:
        if not all([modal, minat, keahlian, waktu]):
            st.warning("Mohon lengkapi semua kolom untuk hasil terbaik.")
        else:
            prompt = f"""
            Analisis profil calon pebisnis berikut:
            - Modal Awal: {modal}
            - Minat/Hobi: {minat}
            - Keahlian Utama: {keahlian}
            - Waktu Luang Tersedia: {waktu}
            Berikan 3 rekomendasi ide bisnis yang paling cocok, disajikan dalam format markdown. Untuk setiap ide, jelaskan secara singkat: Target Pasar, Potensi Keuntungan, dan 3 Langkah Awal untuk memulainya.
            """
            with st.spinner("AI sedang menganalisis profil Anda..."):
                try:
                    resp = model.generate_content(prompt)
                    st.divider()
                    st.subheader("✨ Berikut Rekomendasi Bisnis Untuk Anda")
                    st.markdown(resp.text)
                    st.download_button("📥 Unduh Rekomendasi", data=resp.text, file_name=f"rekomendasi_{datetime.datetime.now():%Y%m%d}.txt", mime="text/plain", use_container_width=True)
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

def fitur_catatan():
    st.title("📝 Catatan Bisnis")
    st.markdown("Simpan semua ide dan rencana bisnis Anda di sini.")
    notes_dir = "catatan_bisnis"
    os.makedirs(notes_dir, exist_ok=True)
    files = sorted([f for f in os.listdir(notes_dir) if f.endswith(".txt")], reverse=True)
    col1, col2 = st.columns([1,1])
    with col1:
        with st.container(border=True):
            st.subheader("Catatan Baru")
            with st.form("new_note", clear_on_submit=True):
                judul = st.text_input("Judul Catatan")
                isi = st.text_area("Isi Catatan", height=150)
                if st.form_submit_button("Simpan Catatan", use_container_width=True):
                    if judul and isi:
                        with open(os.path.join(notes_dir, f"{judul.replace(' ', '_')}.txt"), "w", encoding="utf-8") as f:
                            f.write(isi)
                        st.success("Catatan berhasil disimpan!")
                        st.rerun()
                    else:
                        st.warning("Judul dan isi catatan tidak boleh kosong.")
    with col2:
        with st.container(border=True):
            st.subheader("Daftar Catatan")
            if not files:
                st.info("Belum ada catatan yang tersimpan.")
            else:
                pilih = st.selectbox("Pilih catatan untuk dilihat atau dihapus", files, label_visibility="collapsed")
                if pilih:
                    with open(os.path.join(notes_dir, pilih), "r", encoding="utf-8") as f:
                        konten = f.read()
                    st.text_area("Isi:", value=konten, height=150, disabled=True)
                    if st.button(f"Hapus '{pilih}'", type="primary", use_container_width=True):
                        os.remove(os.path.join(notes_dir, pilih))
                        st.success(f"Catatan '{pilih}' dihapus.")
                        st.rerun()

def fitur_kalkulator():
    st.title("🧮 Kalkulator")
    st.markdown("Kalkulator fungsional dengan fitur hapus per karakter.")
    if 'calc_expression' not in st.session_state: st.session_state.calc_expression = "0"

    def handle_click(value):
        expr = st.session_state.calc_expression
        if expr == "Error": expr = "0"
        if value == "C" or value == "CE": st.session_state.calc_expression = "0"
        elif value == "⌫": st.session_state.calc_expression = expr[:-1] if len(expr) > 1 else "0"
        elif value == "=":
            try:
                expr_to_eval = expr.replace('×', '*').replace('÷', '/')
                result = eval(expr_to_eval)
                st.session_state.calc_expression = str(result) if not isinstance(result, float) else f"{result:.4f}".rstrip('0').rstrip('.')
            except: st.session_state.calc_expression = "Error"
        elif value in ['+', '-', '×', '÷']: st.session_state.calc_expression = f"{expr} {value} "
        else: st.session_state.calc_expression = value if expr == "0" else f"{expr}{value}"

    st.markdown(f'<div class="calculator-display">{st.session_state.calc_expression}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    button_rows = [
        ['%', 'CE', 'C', '⌫'], ['1/x', 'x²', '√x', '÷'],
        ['7', '8', '9', '×'], ['4', '5', '6', 'k'],
        ['1', '2', '3', ' p'], ['+/-', '0', '.', '=']
    ]
    key_map = {'%':'pct','CE':'ce','C':'c','⌫':'bks','1/x':'rec','x²':'sq','√x':'sqrt','÷':'div','×':'mul','-':'sub','+':'add','+/-':'neg','.':'dot','=':'eq'}

    for row in button_rows:
        cols = st.columns(4)
        for i, btn in enumerate(row):
            use_primary = (btn == '=')
            if cols[i].button(btn, use_container_width=True, key=key_map.get(btn, btn), type="primary" if use_primary else "secondary"):
                handle_click(btn)
                st.rerun()

# SIDEBAR
with st.sidebar:
    st.title("✨ Asisten Bisnis AI")
    st.markdown("---")
    menu = option_menu(
        menu_title=None,
        options=["Konsultasi", "Rekomendasi", "Catatan", "Kalkulator"],
        icons=["chat-quote-fill", "lightbulb-fill", "journal-text", "calculator-fill"],
        default_index=0
    )
    st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
    st.caption("Copyright © 2025 Sae Company. All rights reserved.")

# ROUTING HALAMAN
if menu == "Konsultasi": fitur_konsultasi()
elif menu == "Rekomendasi": fitur_rekomendasi()
elif menu == "Catatan": fitur_catatan()
elif menu == "Kalkulator": fitur_kalkulator()