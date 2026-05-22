import re

class TokoBuku:
    def __init__(self):
        # Database Menu Buku dengan Info Tambahan untuk UI
        # Gunakan satu kata kunci (lowercase) sebagai key untuk memudahkan pencocokan regex
        self.menu_data = {
            "novel": {"price": 95000, "emoji": "📚", "desc": "Novel fiksi best-seller terbaru"},
            "komik": {"price": 45000, "emoji": "🥷", "desc": "Komik manga Jepang terjemahan"},
            "biografi": {"price": 120000, "emoji": "✍️", "desc": "Kisah hidup tokoh inspiratif dunia"},
            "kamus": {"price": 150000, "emoji": "📖", "desc": "Kamus lengkap Inggris - Indonesia"},
            "ensiklopedia": {"price": 250000, "emoji": "🌍", "desc": "Buku pengetahuan bergambar untuk semua usia"}
        }
        
        # Regex Patterns
        self.re_number = r"\b(\d+)\b"
        # Membuat pola regex dinamis dari keys katalog buku
        menu_keys = "|".join(self.menu_data.keys())
        self.re_menu = rf"\b({menu_keys})\b"
        self.re_split = r"[,.]|\bdan\b|\b&\b" # Pemisah kalimat (koma, titik, 'dan', '&')
        
        # Regex untuk pembatalan/pengurangan belanjaan
        self.re_cancel_all = r"\b(batalkan semua|hapus semua|reset keranjang|kosongkan)\b"
        self.re_reduce = r"\b(batalkan|kurangi|tidak jadi|hapus|cancel)\b"

    def _parse_single_segment(self, text):
        """Helper untuk memproses satu potongan kalimat (misal: '2 komik')"""
        text = text.lower().strip()
        
        # 1. Cari Item Buku
        item_match = re.search(self.re_menu, text)
        if not item_match:
            return None
            
        item_key = item_match.group(1)
        
        # 2. Cari Jumlah (Default 1 buku)
        qty_match = re.search(self.re_number, text)
        qty = int(qty_match.group(1)) if qty_match else 1
        
        return {
            "item": item_key,
            "qty": qty,
            "price": self.menu_data[item_key]['price'],
            "emoji": self.menu_data[item_key]['emoji']
        }

    def detect_intent(self, text):
        text = text.lower()
        if re.search(r"\b(reset|ulang|batal semua)\b", text):
            return "RESET"
        if re.search(self.re_cancel_all, text):
            return "CANCEL_ALL"
        if re.search(self.re_reduce, text):
            return "REDUCE_ITEM"
        # Menambahkan kata 'buku', 'katalog', 'stok' agar lebih natural untuk toko buku
        if re.search(r"(menu|daftar|apa saja|jual apa|list|buku|katalog|stok)", text):
            return "ASK_MENU"
        if re.search(r"\b(selesai|bayar|checkout|cukup)\b", text):
            return "CHECKOUT"
        if re.search(r"\b(ya|yes|oke|betul|siap|baik)\b", text):
            return "YES"
        if re.search(r"\b(tidak|enggak|batal|no|salah)\b", text):
            return "NO"
        return "UNKNOWN"

    def print_menu(self):
        print("--- DAFTAR BUKU YANG TERSEDIA ---")
        for key, info in self.menu_data.items():
            print(f"{info['emoji']} {key.capitalize()} - Rp{info['price']:,} : {info['desc']}")