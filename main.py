import streamlit as st
from fsm import BookFSM # Pastikan nama file FSM Anda adalah fsm.py

# --- KONFIGURASI HALAMAN ---
# Judul dipersingkat sesuai permintaan
st.set_page_config(page_title="Bot Toko Buku", page_icon="📚", layout="wide")

# --- TAMBAHKAN CSS KUSTOM ---
st.markdown("""
<style>
.stMetric {
    background-color: #f0f2f6;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
}
.stChatMessage { padding: 10px; }
</style>
""", unsafe_allow_html=True)

# --- INISIALISASI SESSION STATE ---
if 'bot' not in st.session_state:
    st.session_state.bot = BookFSM() 
    st.session_state.bot.step()
    st.session_state.history = [{"role": "assistant", "content": st.session_state.bot.get_response()}]

# --- HEADER WEB ---
st.title("📚 Bot Toko Buku")
st.markdown("---")

# --- LAYOUT UTAMA DENGAN TAB ---
tab1, tab2 = st.tabs(["💬 Chat Pembelian", "📋 Katalog Buku"])

# === TAB 1: CHATBOT ===
with tab1:
    col_chat, col_info = st.columns([2, 1])
    
    # Kolom Kanan: Keranjang & Informasi
    with col_info:
        st.subheader("Keranjang")
        if st.session_state.bot.cart:
            total = 0
            for i, item in enumerate(st.session_state.bot.cart):
                subtotal = item['price'] * item['qty']
                total += subtotal
                st.markdown(f"**{i+1}. {item['emoji']} {item['item'].capitalize()}**")
                st.caption(f"{item['qty']} x Rp {item['price']:,} = Rp {subtotal:,}")
            
            st.divider()
            st.metric("Total Tagihan", f"Rp {total:,}")
            
            # Tombol Kosongkan Keranjang
            if st.button("Kosongkan Keranjang"):
                st.session_state.bot.cart = []
                st.rerun()
        else:
            st.info("Keranjang masih kosong.")
        
        st.markdown("---")
        st.caption(f"Status Bot: '{st.session_state.bot.state.name}'")
        
        if st.button("Reset Sistem"):
            st.session_state.clear()
            st.rerun()

    # Kolom Kiri: Chat UI
    with col_chat:
        # Container untuk history chat agar input tetap di bawah
        chat_container = st.container(height=500)
        
        # Render Chat History
        with chat_container:
            for msg in st.session_state.history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        # Input User
        if prompt := st.chat_input("Contoh: Pesan 2 novel dan 1 komik... "):
            # 1. Tampilkan input user
            st.session_state.history.append({"role": "user", "content": prompt})
            
            # 2. Proses di FSM
            st.session_state.bot.step(prompt)
            bot_reply = st.session_state.bot.get_response()
            
            # 3. Simpan respon bot
            st.session_state.history.append({"role": "assistant", "content": bot_reply})
            
            # 4. Rerun (Muat ulang UI)
            st.rerun()

# === TAB 2: MENU UI ===
with tab2:
    st.header("Katalog Buku Tersedia")
    st.markdown("Temukan berbagai buku menarik untuk membuka jendela dunia Anda.")
    
    # Ambil data menu dari nlp engine bot
    menu_items = st.session_state.bot.nlp.menu_data
    
    # Buat Grid Layout (2 kolom)
    cols = st.columns(2)
    
    # Loop items untuk ditampilkan
    for index, (key, data) in enumerate(menu_items.items()):
        # Logika selang-seling kolom
        with cols[index % 2]:
            st.container()
            # Tampilan Card Sederhana
            st.markdown(f"### {data['emoji']} {key.capitalize()}")
            st.markdown(f"*{data['desc']}*")
            st.metric(label="Harga", value=f"Rp {data['price']:,}")
            st.markdown("---")