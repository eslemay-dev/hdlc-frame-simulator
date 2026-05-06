#!/usr/bin/env python3
"""
HDLC Benzeri Cerceve Olusturma ve Dogrulama Sistemi
Tkinter GUI - Trinket.io uyumlu
"""

import tkinter as tk
from tkinter import ttk, messagebox

FLAG = "01111110"

# ─────────────────────────────────────────
# CRC Hesaplama
# ─────────────────────────────────────────

def crc_remainder(data_bits, polynomial):
    poly_len = len(polynomial)
    padded = list(data_bits + "0" * (poly_len - 1))
    for i in range(len(data_bits)):
        if padded[i] == "1":
            for j in range(poly_len):
                padded[i + j] = str(int(padded[i + j]) ^ int(polynomial[j]))
    return "".join(padded[-(poly_len - 1):])


def crc_check(data_with_crc, polynomial):
    remainder = crc_remainder(data_with_crc, polynomial)
    return all(b == "0" for b in remainder)


# ─────────────────────────────────────────
# Bit Stuffing / Destuffing
# ─────────────────────────────────────────

def bit_stuffing(data):
    result = []
    count = 0
    for bit in data:
        result.append(bit)
        if bit == "1":
            count += 1
            if count == 5:
                result.append("0")
                count = 0
        else:
            count = 0
    return "".join(result)


def bit_destuffing(data):
    result = []
    count = 0
    i = 0
    while i < len(data):
        bit = data[i]
        result.append(bit)
        if bit == "1":
            count += 1
            if count == 5:
                if i + 1 < len(data) and data[i + 1] == "0":
                    i += 1
                count = 0
        else:
            count = 0
        i += 1
    return "".join(result)


# ─────────────────────────────────────────
# Yardimci: Giriş Dogrulama
# ─────────────────────────────────────────

def validate_bits(s, label):
    if not s:
        return f"{label} bos birakilamaz!"
    if not all(c in "01" for c in s):
        return f"{label} sadece 0 ve 1 icermelidir!"
    return None


def validate_poly(s):
    err = validate_bits(s, "Polinom")
    if err:
        return err
    if s[0] != "1":
        return "Polinom '1' ile baslamalidir!"
    if len(s) < 2:
        return "Polinom en az 2 bit olmalidir!"
    return None


# ─────────────────────────────────────────
# Ana GUI Sinifi
# ─────────────────────────────────────────

class HDLCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HDLC Benzeri Cerceve Sistemi")
        self.root.resizable(False, False)

        # Renkler
        self.bg        = "#1e1e2e"
        self.panel_bg  = "#2a2a3e"
        self.entry_bg  = "#313145"
        self.fg        = "#cdd6f4"
        self.fg_dim    = "#a6adc8"
        self.accent    = "#89b4fa"
        self.green     = "#a6e3a1"
        self.red       = "#f38ba8"
        self.yellow    = "#f9e2af"
        self.teal      = "#94e2d5"
        self.mauve     = "#cba6f7"

        self.root.configure(bg=self.bg)
        self._build_ui()

    # ── UI İnşa ──────────────────────────

    def _build_ui(self):
        # Başlık
        title_frame = tk.Frame(self.root, bg=self.bg)
        title_frame.pack(fill="x", padx=20, pady=(18, 4))

        tk.Label(title_frame, text="HDLC Benzeri Çerçeve Sistemi",
                 font=("Courier", 17, "bold"), bg=self.bg, fg=self.accent
                 ).pack(side="left")

        # Polinom satırı
        poly_frame = tk.Frame(self.root, bg=self.panel_bg, bd=0)
        poly_frame.pack(fill="x", padx=20, pady=(6, 0), ipady=10)

        tk.Label(poly_frame, text="CRC Polinomu:",
                 font=("Courier", 11), bg=self.panel_bg, fg=self.fg_dim
                 ).pack(side="left", padx=(14, 6))

        self.poly_var = tk.StringVar(value="10011")
        tk.Entry(poly_frame, textvariable=self.poly_var, width=14,
                 font=("Courier", 12), bg=self.entry_bg, fg=self.yellow,
                 insertbackground=self.fg, relief="flat", bd=4
                 ).pack(side="left")

        tk.Label(poly_frame, text="(örn: 10011)",
                 font=("Courier", 10), bg=self.panel_bg, fg=self.fg_dim
                 ).pack(side="left", padx=8)

        # Notebook (Sekmeler)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",       background=self.bg,       borderwidth=0)
        style.configure("TNotebook.Tab",   background=self.panel_bg, foreground=self.fg_dim,
                        font=("Courier", 11, "bold"), padding=[16, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", self.entry_bg)],
                  foreground=[("selected", self.accent)])
        style.configure("TFrame", background=self.bg)

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=20, pady=10)

        send_tab = ttk.Frame(nb)
        recv_tab = ttk.Frame(nb)
        nb.add(send_tab, text=" 📤  SEND ")
        nb.add(recv_tab, text=" 📥  RECEIVE ")

        self._build_send_tab(send_tab)
        self._build_recv_tab(recv_tab)

    def _labeled_entry(self, parent, label, var, hint=""):
        row = tk.Frame(parent, bg=self.bg)
        row.pack(fill="x", padx=18, pady=(10, 0))
        tk.Label(row, text=label, font=("Courier", 10), bg=self.bg, fg=self.fg_dim
                 ).pack(anchor="w")
        e = tk.Entry(row, textvariable=var, width=60,
                     font=("Courier", 12), bg=self.entry_bg, fg=self.teal,
                     insertbackground=self.fg, relief="flat", bd=4)
        e.pack(fill="x", pady=(2, 0))
        if hint:
            tk.Label(row, text=hint, font=("Courier", 9), bg=self.bg, fg=self.fg_dim
                     ).pack(anchor="w")

    def _log_box(self, parent):
        frame = tk.Frame(parent, bg=self.panel_bg, bd=0)
        frame.pack(fill="both", expand=True, padx=18, pady=10)
        sb = tk.Scrollbar(frame)
        sb.pack(side="right", fill="y")
        txt = tk.Text(frame, height=16, font=("Courier", 11),
                      bg=self.panel_bg, fg=self.fg, insertbackground=self.fg,
                      relief="flat", bd=6, wrap="word",
                      yscrollcommand=sb.set, state="disabled")
        txt.pack(fill="both", expand=True)
        sb.config(command=txt.yview)

        # Renk etiketleri
        txt.tag_config("head",   foreground=self.accent,  font=("Courier", 12, "bold"))
        txt.tag_config("label",  foreground=self.fg_dim,  font=("Courier", 11))
        txt.tag_config("value",  foreground=self.teal,    font=("Courier", 11, "bold"))
        txt.tag_config("ok",     foreground=self.green,   font=("Courier", 11, "bold"))
        txt.tag_config("err",    foreground=self.red,     font=("Courier", 11, "bold"))
        txt.tag_config("warn",   foreground=self.yellow,  font=("Courier", 11))
        txt.tag_config("mauve",  foreground=self.mauve,   font=("Courier", 11, "bold"))
        txt.tag_config("sep",    foreground="#444466")
        return txt

    def _write(self, txt, *parts):
        """parts: (text, tag) çiftleri"""
        txt.config(state="normal")
        for text, tag in parts:
            txt.insert("end", text, tag)
        txt.config(state="disabled")
        txt.see("end")

    def _clear(self, txt):
        txt.config(state="normal")
        txt.delete("1.0", "end")
        txt.config(state="disabled")

    # ── SEND sekmesi ─────────────────────

    def _build_send_tab(self, tab):
        inner = tk.Frame(tab, bg=self.bg)
        inner.pack(fill="both", expand=True)

        self.payload_var = tk.StringVar(value="1101011111")
        self._labeled_entry(inner, "Payload (bit dizisi):", self.payload_var,
                            "örn: 1101011111")

        btn_row = tk.Frame(inner, bg=self.bg)
        btn_row.pack(padx=18, pady=10, anchor="w")
        tk.Button(btn_row, text="  Çerçeve Oluştur  ", command=self._do_send,
                  font=("Courier", 11, "bold"), bg=self.accent, fg="#1e1e2e",
                  activebackground=self.teal, relief="flat", bd=0, cursor="hand2",
                  padx=8, pady=5).pack(side="left")

        self.send_frame_var = tk.StringVar()
        copy_row = tk.Frame(inner, bg=self.bg)
        copy_row.pack(fill="x", padx=18, pady=(0, 4))
        tk.Label(copy_row, text="Oluşturulan Frame:", font=("Courier", 10),
                 bg=self.bg, fg=self.fg_dim).pack(side="left")
        tk.Button(copy_row, text="Panoya Kopyala", command=self._copy_frame,
                  font=("Courier", 10), bg=self.panel_bg, fg=self.fg_dim,
                  activebackground=self.entry_bg, relief="flat", cursor="hand2",
                  padx=6, pady=2).pack(side="left", padx=8)

        frame_entry = tk.Entry(inner, textvariable=self.send_frame_var, width=80,
                               font=("Courier", 10), bg=self.entry_bg, fg=self.mauve,
                               insertbackground=self.fg, relief="flat", bd=4,
                               state="readonly")
        frame_entry.pack(fill="x", padx=18, pady=(0, 6))

        self.send_log = self._log_box(inner)

    def _copy_frame(self):
        frame = self.send_frame_var.get()
        if frame:
            self.root.clipboard_clear()
            self.root.clipboard_append(frame)
            messagebox.showinfo("Kopyalandı", "Frame panoya kopyalandı!\nReceive sekmesine yapıştırabilirsiniz.")

    def _do_send(self):
        poly    = self.poly_var.get().strip()
        payload = self.payload_var.get().strip()
        txt     = self.send_log
        self._clear(txt)

        err = validate_poly(poly)
        if err:
            self._write(txt, ("HATA: " + err + "\n", "err"))
            return
        err = validate_bits(payload, "Payload")
        if err:
            self._write(txt, ("HATA: " + err + "\n", "err"))
            return

        sep = "─" * 52 + "\n"

        self._write(txt,
            ("\n📤  SEND MODU\n", "head"),
            (sep, "sep"),
            ("  Payload          : ", "label"), (payload + "\n", "value"),
            ("  CRC Polinomu     : ", "label"), (poly    + "\n", "value"),
            (sep, "sep"),
        )

        remainder    = crc_remainder(payload, poly)
        data_with_crc = payload + remainder
        stuffed      = bit_stuffing(data_with_crc)
        frame        = FLAG + stuffed + FLAG

        self._write(txt,
            ("\n  [1] CRC Remainder : ", "label"), (remainder     + "\n", "mauve"),
            ("  [2] Payload + CRC : ", "label"), (data_with_crc + "\n", "value"),
            ("  [3] Bit Stuffed   : ", "label"), (stuffed       + "\n", "value"),
            ("  [4] Frame         : ", "label"), (frame         + "\n", "mauve"),
            ("\n  ✅  Gönderilecek Frame hazır!\n", "ok"),
        )

        self._write(txt,
            (sep, "sep"),
            ("  FLAG: ", "warn"), (FLAG, "value"),
            ("   |   ", "sep"),
            ("Veri(stuffed): ", "warn"), (stuffed, "value"),
            ("   |   ", "sep"),
            ("FLAG: ", "warn"), (FLAG + "\n", "value"),
        )

        self.send_frame_var.set(frame)

    # ── RECEIVE sekmesi ──────────────────

    def _build_recv_tab(self, tab):
        inner = tk.Frame(tab, bg=self.bg)
        inner.pack(fill="both", expand=True)

        self.frame_var = tk.StringVar()
        self._labeled_entry(inner, "Alınan Frame (bit dizisi):", self.frame_var,
                            "Send modundaki 'Oluşturulan Frame'i buraya yapıştırın")

        btn_row = tk.Frame(inner, bg=self.bg)
        btn_row.pack(padx=18, pady=10, anchor="w")
        tk.Button(btn_row, text="  Frame'i Doğrula  ", command=self._do_receive,
                  font=("Courier", 11, "bold"), bg=self.green, fg="#1e1e2e",
                  activebackground=self.teal, relief="flat", bd=0, cursor="hand2",
                  padx=8, pady=5).pack(side="left")

        self.recv_log = self._log_box(inner)

    def _do_receive(self):
        poly  = self.poly_var.get().strip()
        frame = self.frame_var.get().strip()
        txt   = self.recv_log
        self._clear(txt)

        err = validate_poly(poly)
        if err:
            self._write(txt, ("HATA: " + err + "\n", "err"))
            return
        err = validate_bits(frame, "Frame")
        if err:
            self._write(txt, ("HATA: " + err + "\n", "err"))
            return

        sep = "─" * 52 + "\n"

        self._write(txt,
            ("\n📥  RECEIVE MODU\n", "head"),
            (sep, "sep"),
            ("  Alınan Frame     : ", "label"), (frame + "\n", "value"),
            ("  CRC Polinomu     : ", "label"), (poly  + "\n", "value"),
            (sep, "sep"),
        )

        # Flag kontrolü
        if not (frame.startswith(FLAG) and frame.endswith(FLAG)):
            self._write(txt,
                ("\n  [1] Flag kontrolü : ", "label"),
                ("❌  Başlangıç veya bitiş flag'i geçersiz!\n", "err"),
            )
            return

        self._write(txt,
            ("\n  [1] Flag kontrolü : ", "label"),
            ("✅  Doğru (01111110 ... 01111110)\n", "ok"),
        )

        inner_bits = frame[len(FLAG):-len(FLAG)]
        destuffed  = bit_destuffing(inner_bits)
        crc_len    = len(poly) - 1
        payload    = destuffed[:-crc_len]
        recv_crc   = destuffed[-crc_len:]
        valid      = crc_check(destuffed, poly)

        self._write(txt,
            ("  [2] İç bit akışı  : ", "label"), (inner_bits + "\n", "value"),
            ("  [3] Bit Destuffed : ", "label"), (destuffed  + "\n", "value"),
            ("\n  [4] CRC Kontrolü\n", "label"),
            ("      Payload       : ", "label"), (payload  + "\n", "mauve"),
            ("      Alınan CRC    : ", "label"), (recv_crc + "\n", "mauve"),
            ("      CRC Geçerli   : ", "label"),
        )

        if valid:
            self._write(txt, ("✅  Evet\n", "ok"))
        else:
            self._write(txt, ("❌  Hayır\n", "err"))

        self._write(txt, ("\n" + sep, "sep"), ("  SONUÇ\n", "head"))

        if valid:
            self._write(txt,
                ("  Payload          : ", "label"), (payload + "\n", "value"),
                ("  Hata var mı?     : ", "label"), ("Hayır ✅  Veri bütünlüğü sağlandı!\n", "ok"),
            )
        else:
            self._write(txt,
                ("  Payload          : ", "label"), (payload + "\n", "value"),
                ("  Hata var mı?     : ", "label"), ("Evet ❌   Veri bozulmuş olabilir!\n", "err"),
            )


# ─────────────────────────────────────────
# Baslatma
# ─────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = HDLCApp(root)
    root.mainloop()