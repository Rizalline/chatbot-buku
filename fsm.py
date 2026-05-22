import re
from enum import Enum, auto
# Pastikan nama class dan file engine sesuai dengan kode Anda sebelumnya
from engine import TokoBuku as NLPEngine 

class State(Enum):
    IDLE = auto()
    ORDERING = auto()
    CONFIRMATION = auto()
    PAYMENT = auto()

class BookFSM:
    def __init__(self):
        self.state = State.IDLE
        self.nlp = NLPEngine()
        self.cart = []
        self.response = ""

    def get_response(self):
        return self.response

    def calculate_total(self):
        return sum(item['price'] * item['qty'] for item in self.cart)

    def get_menu_text(self):
        # typo diperbaiki: .item() menjadi .items()
        teks_menu = "**📚 Daftar Katalog Buku **\n"
        for key, data in self.nlp.menu_data.items():
            teks_menu += f"- {data['emoji']} **{key.capitalize()}** (Rp {data['price']:,}): *{data['desc']}*\n"
        teks_menu += "\nSilakan ketik pesanan Anda (contoh: *'Pesan 2 novel, 1 komik'*)."
        return teks_menu

    def reduce_cart(self, item_to_reduce, qty_to_remove):
        # typo diperbaiki: false menjadi False
        found = False
        message = ""

        for item in self.cart:
            if item['item'] == item_to_reduce:
                item['qty'] -= qty_to_remove
                found = True
                # Perbaikan Logika: Jika qty kurang dari atau sama dengan 0, hapus item dari keranjang
                if item['qty'] <= 0:
                    # typo diperbaiki: self.cart.remove(item_to_reduce) salah karena item_to_reduce hanyalah string string key, harusnya me-remove objek item tersebut
                    self.cart.remove(item)
                    message = f"❌ **{item_to_reduce.capitalize()}** telah dihapus dari keranjang."
                else:
                    message = f"📉 **{item_to_reduce.capitalize()}** dikurangi {qty_to_remove}. Sisa di keranjang: {item['qty']}."
                break
                
        if not found:
            message = f"Gagal: **{item_to_reduce.capitalize()}** tidak ditemukan di keranjang Anda."
        return message

    def step(self, user_input=""):
        user_input = user_input.strip()
        intent = self.nlp.detect_intent(user_input)
        
        # GLOBAL RESET SYSTEM
        # Menyesuaikan dengan intent 'RESET' dari code NLPEngine Anda sebelumnya
        if intent == "RESET" or intent == "RESET_SYSTEM":
            self.__init__()
            self.response = "Sistem di-reset total. Halo! Mau cari buku apa hari ini?"
            return

        # STATE LOGIC: IDLE
        if self.state == State.IDLE:
            self.state = State.ORDERING
            self.response = "Halo! Selamat datang di Toko Buku. Mau pesan buku apa hari ini? Ketik 'menu' atau 'katalog' untuk melihat pilihan."
            return # Menggunakan return agar tidak langsung mengeksekusi state selanjutnya di loop yang sama

        # STATE LOGIC: ORDERING
        elif self.state == State.ORDERING:
            # FITUR: Tanya Menu
            if intent == "ASK_MENU":
                self.response = self.get_menu_text()
                
            # FITUR: Batalkan Semua
            elif intent == "CANCEL_ALL":
                self.cart = []
                self.response = "Keranjang belanja Anda telah dikosongkan. Mau pesan buku yang lain?"
                
            # FITUR: Kurangi/Batalkan Item Tertentu
            elif intent == "REDUCE_ITEM":
                # Menggunakan method _parse_single_segment / parse_orders sesuai ketersediaan di NLPEngine
                # Di sini saya asumsikan parse_orders mengembalikan list of dict
                items_to_remove = self._parse_multiple_segments(user_input) 
                if items_to_remove:
                    results = []
                    for itm in items_to_remove:
                        res = self.reduce_cart(itm['item'], itm['qty'])
                        results.append(res)
                    self.response = "\n".join(results)
                else:
                    self.response = "Buku apa yang ingin dikurangi? Contoh: *'batalkan 1 novel'*."

            # FITUR: Checkout Keranjang
            elif intent == "CHECKOUT":
                if not self.cart:
                    self.response = "Keranjang belanja Anda masih kosong."
                else:
                    self.state = State.CONFIRMATION
                    # Menampilkan detail keranjang sebelum total belanjaan
                    detail_keranjang = "\n".join([f"- {i['emoji']} {i['item'].capitalize()} x{i['qty']}" for i in self.cart])
                    self.response = f"Isi keranjang Anda:\n{detail_keranjang}\n\nTotal: **Rp {self.calculate_total():,}**. Apakah data pesanan sudah benar dan lanjut ke pembayaran? (Ya/Tidak)"

            else:
                # Logika Penambahan Pesanan
                new_orders = self._parse_multiple_segments(user_input)
                if new_orders:
                    for order in new_orders:
                        # Cek jika item sudah ada, tambah qty saja
                        existing = next((i for i in self.cart if i['item'] == order['item']), None)
                        if existing:
                            existing['qty'] += order['qty']
                        else:
                            # Ambil info harga & emoji dari menu_data
                            menu_info = self.nlp.menu_data[order['item']]
                            order.update({"price": menu_info['price'], "emoji": menu_info['emoji']})
                            self.cart.append(order)
                    self.response = "✅ Buku berhasil ditambahkan ke keranjang. Ada lagi? (Ketik 'bayar' atau 'checkout' jika sudah selesai)"
                else:
                    self.response = "Maaf, saya tidak mengerti buku apa yang Anda maksud. Coba ketik: *'pesan 2 novel'* atau *'lihat katalog'*."

        # STATE LOGIC: CONFIRMATION
        elif self.state == State.CONFIRMATION:
            if intent == "YES":
                self.state = State.PAYMENT
                self.step() # Auto-step langsung ke STATE PAYMENT
            elif intent == "NO":
                self.state = State.ORDERING
                self.response = "Siap, silakan lanjut memilih atau mengubah pesanan buku Anda."
            else:
                self.response = "Mohon konfirmasi dengan menjawab 'Ya' atau 'Tidak'."

        # STATE LOGIC: PAYMENT
        elif self.state == State.PAYMENT:
            total = self.calculate_total()
            self.response = f"🙏 Terima kasih! Pembayaran sebesar **Rp {total:,}** telah kami terima. E-book / Buku pesanan Anda sedang diproses dan siap dikirim!"
            self.cart = [] # Mengosongkan keranjang setelah sukses transaksi
            self.state = State.IDLE

    def _parse_multiple_segments(self, text):
        """
        Helper tambahan untuk memecah teks input (misal: '2 novel dan 1 komik') 
        menjadi list pesanan menggunakan function _parse_single_segment dari NLPEngine.
        """
        segments = re.split(self.nlp.re_split, text)
        orders = []
        for seg in segments:
            parsed = self.nlp._parse_single_segment(seg)
            if parsed:
                orders.append(parsed)
        return orders

    