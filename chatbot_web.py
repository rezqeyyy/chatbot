import streamlit as st
from streamlit_option_menu import option_menu
import google.generativeai as genai
import os, datetime, math, json, re
from supabase import create_client, Client

# --------------------------------------------------
# PENGATURAN HALAMAN & CSS
# --------------------------------------------------
st.set_page_config(
    page_title="Asisten Bisnis AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_custom_css():
    st.markdown("""
<style>
/* ===== FONT & TAMPILAN DASAR ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    padding: 1rem;
    display: flex;
    flex-direction: column;
}
/* Mengatur agar menu mengisi ruang & footer menempel di bawah */
.option-menu-container {
    flex-grow: 1;
}

/* ===== KONTEN UTAMA ===== */
.block-container {
    padding: 2rem;
}
h1 {
    font-size: 2.25rem;
    font-weight: 700;
}

/* ===== TAMPILAN CHAT YANG LEBIH RAPI ===== */
.chat-wrapper {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
.message-container {
    display: flex;
    align-items: flex-end;
    gap: 10px;
}
.message-container.user { justify-content: flex-end; }
.message-container.ai { justify-content: flex-start; }
.avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: #4B5563; /* Warna avatar disesuaikan */
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: white;
}
.text-container {
    display: flex;
    flex-direction: column;
}
.message-container.user .text-container { align-items: flex-end; }
.message-container.ai .text-container { align-items: flex-start; }
.sender-name {
    font-size: 0.8rem;
    color: #9CA3AF;
    margin: 0 0.75rem 0.2rem;
}
.chat-bubble {
    padding: 0.8rem 1.2rem;
    line-height: 1.6;
    display: inline-block;
    max-width: 100%;
    position: relative;
    background: #374151; /* Warna bubble yang serasi */
    color: #F9FAFB;
    border-radius: 1rem;
}
/* Menghilangkan "ekor" untuk desain yang lebih simpel */
.chat-bubble.ai::before, .chat-bubble.user::after {
    content: none;
}
</style>
    """, unsafe_allow_html=True)

load_custom_css()

# --------------------------------------------------
# KONFIGURASI API & KONEKSI
# --------------------------------------------------
GEMINI_API_KEY = "AIzaSyCv1CwT5pWAF-fkj5nHjIrryu6F2gZeL9c" #
SUPABASE_URL = "https://mmacplzzdrpezpfremul.supabase.co" #
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1tYWNwbHp6ZHJwZXpwZnJlbXVsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxNDYzMDUsImV4cCI6MjA3NDcyMjMwNX0.h7HMd8xYBz7RnxE1-G5RmowX_-Gn1u_l7NVEFDVwrOg" #

try:
    genai.configure(api_key=GEMINI_API_KEY) #
    model = genai.GenerativeModel("gemini-2.5-flash") #
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) #
except Exception as e:
    st.error(f"Konfigurasi API gagal: {e}")
    st.stop()

# --- PEMULIHAN SESI LOGIN ---
if 'user' not in st.session_state: st.session_state.user = None
if st.session_state.user:
    try:
        supabase.auth.set_session(st.session_state.user.session.access_token, st.session_state.user.session.refresh_token) #
    except Exception:
        st.session_state.user = None

# --- FUNGSI-FUNGSI FITUR ---

def fitur_konsultasi():
    st.title("💬 Konsultasi Bisnis")
    st.markdown("Ajukan pertanyaan apa pun seputar bisnis kepada Konsultan AI.")

    # Inisialisasi session state jika belum ada
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "ai", "name": "Konsultan AI", "content": "Tentu, saya siap membantu. Silakan ajukan pertanyaan bisnis Anda."}
        ]

    # 1. Tampilkan semua pesan yang sudah ada di session state
    st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        role = message["role"]
        avatar_char = "🤖" if role == "ai" else "🧑‍💻"
        
        container_html = f'<div class="message-container {role}">'
        avatar_html = f'<div class="avatar">{avatar_char}</div>'
        text_html = f'<div class="text-container"><div class="sender-name">{message["name"]}</div><div class="chat-bubble {role}">{message["content"]}</div></div>'

        if role == 'ai':
            st.markdown(container_html + avatar_html + text_html + '</div>', unsafe_allow_html=True)
        else: # role == 'user'
            st.markdown(container_html + text_html + avatar_html + '</div>', unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Tangani input baru dari pengguna
    if prompt := st.chat_input("Tulis pertanyaan Anda…"):
        # Tambahkan pesan pengguna ke state dan LANGSUNG RERUN
        st.session_state.messages.append({"role": "user", "name": "Anda", "content": prompt})
        st.rerun()

    # 3. Logika untuk AI merespons (dijalankan setelah rerun)
    # Cek apakah pesan terakhir adalah dari pengguna, jika iya, maka AI perlu merespons
    if st.session_state.messages[-1]["role"] == "user":
        with st.spinner("AI sedang berpikir..."):
            try:
                # Ambil prompt dari pesan terakhir
                user_prompt = st.session_state.messages[-1]["content"]
                response = model.generate_content(user_prompt)
                ai_response = response.text
            except Exception as e:
                ai_response = f"Terjadi kesalahan: {e}"
        
        # Tambahkan respons AI ke state dan RERUN lagi untuk menampilkannya
        st.session_state.messages.append({"role": "ai", "name": "Konsultan AI", "content": ai_response})
        st.rerun()
        
def fitur_rekomendasi():
    st.title("💡 Rekomendasi Bisnis") #
    st.markdown("Isi formulir di bawah ini untuk mendapatkan ide bisnis yang dipersonalisasi.") #
    with st.container(border=True): #
        with st.form("rec_form"): #
            st.subheader("Profil Calon Pebisnis") #
            modal = st.text_input("Berapa modal awal yang Anda siapkan?", placeholder="Contoh: Di bawah 5 juta") #
            minat = st.text_input("Apa minat atau hobi utama Anda?") #
            keahlian = st.text_input("Apa keahlian spesifik yang Anda miliki?") #
            waktu = st.text_input("Berapa waktu luang Anda per minggu?") #
            submit = st.form_submit_button("🚀 Berikan Saya Ide!", use_container_width=True) #
    if submit: #
        if not all([modal, minat, keahlian, waktu]): #
            st.warning("Mohon lengkapi semua kolom untuk hasil terbaik.") #
        else:
            prompt_data = {"modal": modal, "minat": minat, "keahlian": keahlian, "waktu": waktu} #
            prompt = f"Analisis profil {prompt_data} dan berikan 3 ide bisnis singkat." #
            with st.spinner("AI sedang menganalisis profil Anda..."): #
                try:
                    resp = model.generate_content(prompt) #
                    rekomendasi_ai = resp.text #
                    st.divider() #
                    st.subheader("✨ Berikut Rekomendasi Bisnis Untuk Anda") #
                    st.markdown(rekomendasi_ai) #
                    if st.session_state.get('user'): #
                        if st.button("Simpan Rekomendasi ke Akun"): #
                            user_id = st.session_state.user.user.id #
                            supabase.table('recommendations').insert({
                                "user_id": user_id,
                                "prompt_data": json.dumps(prompt_data),
                                "recommendation_text": rekomendasi_ai
                            }).execute() #
                            st.success("Rekomendasi berhasil disimpan!") #
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}") #

def fitur_catatan():
    st.title("📝 Catatan Bisnis") #
    if not st.session_state.get('user'): #
        st.warning("Anda harus login untuk membuat dan melihat catatan bisnis Anda.") #
        st.info("Login atau buat akun baru melalui menu di sidebar.") #
        return
    user_id = st.session_state.user.user.id #
    notes = supabase.table('notes').select('*').eq('user_id', user_id).order('created_at', desc=True).execute().data #
    col1, col2 = st.columns([1,1]) #
    with col1: #
        with st.container(border=True): #
            st.subheader("Catatan Baru") #
            with st.form("new_note", clear_on_submit=True): #
                judul = st.text_input("Judul Catatan") #
                isi = st.text_area("Isi Catatan", height=150) #
                if st.form_submit_button("Simpan Catatan", use_container_width=True, type="primary"): #
                    if judul and isi: #
                        supabase.table('notes').insert({"title": judul, "content": isi, "user_id": user_id}).execute() #
                        st.success("Catatan berhasil disimpan!") #
                        st.rerun() #
                    else:
                        st.warning("Judul dan isi catatan tidak boleh kosong.") #
    with col2: #
        with st.container(border=True): #
            st.subheader("Daftar Catatan") #
            if not notes: #
                st.info("Belum ada catatan yang tersimpan.") #
            else:
                note_titles = [note['title'] for note in notes] #
                pilih = st.selectbox("Pilih catatan", note_titles, label_visibility="collapsed") #
                if pilih: #
                    selected_note = next((note for note in notes if note['title'] == pilih), None) #
                    st.text_area("Isi:", value=selected_note['content'], height=150, disabled=True) #
                    if st.button(f"Hapus '{pilih}'", use_container_width=True): #
                        supabase.table('notes').delete().eq('id', selected_note['id']).execute() #
                        st.success(f"Catatan '{pilih}' dihapus.") #
                        st.rerun() #

def fitur_kalkulator():
    st.title("🧮 Kalkulator Minimalis") #
    st.markdown("Masukkan perhitungan di bawah dan tekan 'Hitung'. Gunakan `*` untuk kali dan `/` untuk bagi.") #
    if 'calc_result' not in st.session_state: st.session_state.calc_result = "0" #
    st.markdown(f'<div class="calculator-display">{st.session_state.calc_result}</div>', unsafe_allow_html=True) #
    with st.form("calculator_form"): #
        expression = st.text_input("Ekspresi matematika", label_visibility="collapsed",
                                   placeholder="Contoh: (150000 + 50000) * 2") #
        submitted = st.form_submit_button("Hitung", use_container_width=True) #
    if submitted: #
        try:
            expr_to_eval = expression.replace('x', '*').replace('×', '*').replace(':', '/') #
            if not re.match(r"^[0-9+\-*/().\s]*$", expr_to_eval): #
                raise ValueError("Input mengandung karakter yang tidak diizinkan.") #
            result = eval(expr_to_eval) #
            st.session_state.calc_result = str(result) #
            st.rerun() #
        except Exception as e:
            st.session_state.calc_result = "Error" #
            st.error(f"Ekspresi tidak valid: {e}") #
            st.rerun() #

# ------------- SIDEBAR & MENU -------------
with st.sidebar: #
    st.markdown('<div class="user-block">', unsafe_allow_html=True) #
    if st.session_state.get('user'): #
        email = st.session_state.user.user.email #
        st.markdown(f"""
            <div class="user-info">
                <div class="user-avatar">{email[0].upper()}</div>
                <div class="user-email">{email}</div>
            </div>
        """, unsafe_allow_html=True) #
    else:
        st.title("✨ Asisten Bisnis AI") #
        with st.expander("🔐 Login / Buat Akun"): #
            tab1, tab2 = st.tabs(["Login", "Buat Akun"]) #
            with tab1: #
                with st.form("login_form", clear_on_submit=True): #
                    email = st.text_input("Email") #
                    password = st.text_input("Password", type="password") #
                    if st.form_submit_button("Login", use_container_width=True, type="primary"): #
                        try:
                            st.session_state['user'] = supabase.auth.sign_in_with_password({"email": email, "password": password}) #
                            st.rerun() #
                        except Exception as e:
                            st.error(f"Login gagal: {e}") #
            with tab2: #
                with st.form("signup_form", clear_on_submit=True): #
                    email = st.text_input("Email Baru") #
                    password = st.text_input("Buat Password", type="password") #
                    if st.form_submit_button("Buat Akun", use_container_width=True): #
                        try:
                            supabase.auth.sign_up({"email": email, "password": password}) #
                            st.session_state['user'] = supabase.auth.sign_in_with_password({"email": email, "password": password}) #
                            st.rerun() #
                        except Exception as e:
                            st.error(f"Gagal membuat akun: {e}") #
    st.markdown('</div>', unsafe_allow_html=True) #

    menu = option_menu( #
        menu_title="",
        options=["Konsultasi", "Rekomendasi", "Catatan", "Kalkulator"],
        icons=["chat-quote-fill", "lightbulb-fill", "journal-text", "calculator-fill"],
        default_index=0
    )

    if st.session_state.get('user'): #
        if st.button("Logout", use_container_width=True): #
            st.session_state.user = None #
            st.session_state.chat_session = None #
            st.session_state.display_history = [] #
            st.rerun() #
    st.caption("© 2025 | Ditenagai oleh Google Gemini") #

# ------------- ROUTE -------------
if menu == "Konsultasi": #
    fitur_konsultasi()
elif menu == "Rekomendasi": #
    fitur_rekomendasi()
elif menu == "Catatan": #
    fitur_catatan()
elif menu == "Kalkulator": #
    fitur_kalkulator()

