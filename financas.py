import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

# ─────────────────────────────────────────
#  BANCO DE DADOS
# ─────────────────────────────────────────
DB_NAME = "financas.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entradas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria TEXT NOT NULL,
            data TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def salvar_entrada(descricao, valor, data):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO entradas (descricao, valor, data) VALUES (?, ?, ?)",
                 (descricao, valor, data))
    conn.commit()
    conn.close()

def salvar_gasto(descricao, valor, categoria, data):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT INTO gastos (descricao, valor, categoria, data) VALUES (?, ?, ?, ?)",
                 (descricao, valor, categoria, data))
    conn.commit()
    conn.close()

def buscar_entradas(mes, ano):
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute(
        "SELECT id, descricao, valor, data FROM entradas WHERE strftime('%m', data)=? AND strftime('%Y', data)=?",
        (f"{mes:02d}", str(ano))
    ).fetchall()
    conn.close()
    return rows

def buscar_gastos(mes, ano):
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute(
        "SELECT id, descricao, valor, categoria, data FROM gastos WHERE strftime('%m', data)=? AND strftime('%Y', data)=?",
        (f"{mes:02d}", str(ano))
    ).fetchall()
    conn.close()
    return rows

def excluir_entrada(id_):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM entradas WHERE id=?", (id_,))
    conn.commit()
    conn.close()

def excluir_gasto(id_):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("DELETE FROM gastos WHERE id=?", (id_,))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
#  CORES & ESTILO
# ─────────────────────────────────────────
CORES = {
    "bg":        "#0F1117",
    "card":      "#1A1D27",
    "borda":     "#2A2D3E",
    "verde":     "#00E676",
    "vermelho":  "#FF5252",
    "azul":      "#448AFF",
    "texto":     "#E8EAF6",
    "subtexto":  "#7986CB",
    "amarelo":   "#FFD740",
}

CATEGORIAS = [
    "🍔 Alimentação",
    "🚌 Transporte",
    "🏠 Moradia",
    "💊 Saúde",
    "📚 Educação",
    "🎬 Lazer",
    "👗 Vestuário",
    "💡 Contas",
    "📦 Outros",
]

CORES_CATEGORIA = [
    "#FF6B6B", "#FFE66D", "#A8E6CF",
    "#88D8B0", "#FFEAA7", "#DDA0DD",
    "#98D8C8", "#F7DC6F", "#AED6F1",
]

# ─────────────────────────────────────────
#  JANELA DE ENTRADA
# ─────────────────────────────────────────
class JanelaEntrada(tk.Toplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.callback = callback
        self.title("Nova Entrada")
        self.configure(bg=CORES["bg"])
        self.resizable(False, False)
        self.geometry("400x320")
        self._centralizar()
        self._build()

    def _centralizar(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 200
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 160
        self.geometry(f"+{x}+{y}")

    def _build(self):
        tk.Label(self, text="💰  NOVA ENTRADA", font=("Courier", 14, "bold"),
                 bg=CORES["bg"], fg=CORES["verde"]).pack(pady=(20, 10))

        frame = tk.Frame(self, bg=CORES["card"], padx=24, pady=16)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        def campo(label, var, row, placeholder=""):
            tk.Label(frame, text=label, bg=CORES["card"], fg=CORES["subtexto"],
                     font=("Courier", 9)).grid(row=row, column=0, sticky="w", pady=4)
            e = tk.Entry(frame, textvariable=var, bg=CORES["borda"], fg=CORES["texto"],
                         insertbackground=CORES["verde"], font=("Courier", 11),
                         relief="flat", bd=4, width=22)
            e.grid(row=row, column=1, padx=(10, 0), pady=4)
            return e

        self.desc_var  = tk.StringVar()
        self.valor_var = tk.StringVar()
        self.data_var  = tk.StringVar(value=datetime.date.today().strftime("%d/%m/%Y"))

        campo("Descrição :", self.desc_var,  0)
        campo("Valor (R$):", self.valor_var, 1)
        campo("Data      :", self.data_var,  2)

        tk.Button(frame, text="✔  SALVAR", font=("Courier", 11, "bold"),
                  bg=CORES["verde"], fg=CORES["bg"], relief="flat", bd=0,
                  padx=20, pady=8, cursor="hand2",
                  command=self._salvar).grid(row=3, column=0, columnspan=2, pady=16)

    def _salvar(self):
        desc  = self.desc_var.get().strip()
        valor = self.valor_var.get().strip()
        data  = self.data_var.get().strip()
        if not desc or not valor:
            messagebox.showwarning("Atenção", "Preencha todos os campos!", parent=self)
            return
        try:
            valor_f = float(valor.replace(",", "."))
            dt = datetime.datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Valor ou data inválidos!\nData: dd/mm/aaaa", parent=self)
            return
        salvar_entrada(desc, valor_f, dt)
        self.callback()
        self.destroy()

# ─────────────────────────────────────────
#  JANELA DE GASTO
# ─────────────────────────────────────────
class JanelaGasto(tk.Toplevel):
    def __init__(self, master, callback):
        super().__init__(master)
        self.callback = callback
        self.title("Novo Gasto")
        self.configure(bg=CORES["bg"])
        self.resizable(False, False)
        self.geometry("420x360")
        self._centralizar()
        self._build()

    def _centralizar(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 210
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 180
        self.geometry(f"+{x}+{y}")

    def _build(self):
        tk.Label(self, text="💸  NOVO GASTO", font=("Courier", 14, "bold"),
                 bg=CORES["bg"], fg=CORES["vermelho"]).pack(pady=(20, 10))

        frame = tk.Frame(self, bg=CORES["card"], padx=24, pady=16)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        def label(txt, row):
            tk.Label(frame, text=txt, bg=CORES["card"], fg=CORES["subtexto"],
                     font=("Courier", 9)).grid(row=row, column=0, sticky="w", pady=4)

        self.desc_var  = tk.StringVar()
        self.valor_var = tk.StringVar()
        self.data_var  = tk.StringVar(value=datetime.date.today().strftime("%d/%m/%Y"))
        self.cat_var   = tk.StringVar(value=CATEGORIAS[0])

        label("Descrição  :", 0)
        tk.Entry(frame, textvariable=self.desc_var, bg=CORES["borda"], fg=CORES["texto"],
                 insertbackground=CORES["vermelho"], font=("Courier", 11),
                 relief="flat", bd=4, width=22).grid(row=0, column=1, padx=(10,0), pady=4)

        label("Valor (R$) :", 1)
        tk.Entry(frame, textvariable=self.valor_var, bg=CORES["borda"], fg=CORES["texto"],
                 insertbackground=CORES["vermelho"], font=("Courier", 11),
                 relief="flat", bd=4, width=22).grid(row=1, column=1, padx=(10,0), pady=4)

        label("Categoria  :", 2)
        cat_menu = ttk.Combobox(frame, textvariable=self.cat_var, values=CATEGORIAS,
                                font=("Courier", 10), width=20, state="readonly")
        cat_menu.grid(row=2, column=1, padx=(10,0), pady=4)

        label("Data       :", 3)
        tk.Entry(frame, textvariable=self.data_var, bg=CORES["borda"], fg=CORES["texto"],
                 insertbackground=CORES["vermelho"], font=("Courier", 11),
                 relief="flat", bd=4, width=22).grid(row=3, column=1, padx=(10,0), pady=4)

        tk.Button(frame, text="✔  SALVAR", font=("Courier", 11, "bold"),
                  bg=CORES["vermelho"], fg="white", relief="flat", bd=0,
                  padx=20, pady=8, cursor="hand2",
                  command=self._salvar).grid(row=4, column=0, columnspan=2, pady=16)

    def _salvar(self):
        desc  = self.desc_var.get().strip()
        valor = self.valor_var.get().strip()
        cat   = self.cat_var.get()
        data  = self.data_var.get().strip()
        if not desc or not valor:
            messagebox.showwarning("Atenção", "Preencha todos os campos!", parent=self)
            return
        try:
            valor_f = float(valor.replace(",", "."))
            dt = datetime.datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro", "Valor ou data inválidos!\nData: dd/mm/aaaa", parent=self)
            return
        salvar_gasto(desc, valor_f, cat, dt)
        self.callback()
        self.destroy()

# ─────────────────────────────────────────
#  APP PRINCIPAL
# ─────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("💼 Controle Financeiro")
        self.configure(bg=CORES["bg"])
        self.geometry("920x680")
        self.minsize(800, 580)
        init_db()
        self._build()
        self.atualizar()

    def _build(self):
        # ── Cabeçalho ──
        header = tk.Frame(self, bg=CORES["card"], height=64)
        header.pack(fill="x")
        tk.Label(header, text="💼  CONTROLE FINANCEIRO", font=("Courier", 16, "bold"),
                 bg=CORES["card"], fg=CORES["texto"]).pack(side="left", padx=24, pady=14)

        # Filtro mês/ano
        filtro = tk.Frame(header, bg=CORES["card"])
        filtro.pack(side="right", padx=20)
        hoje = datetime.date.today()
        meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
        self.mes_var = tk.IntVar(value=hoje.month)
        self.ano_var = tk.IntVar(value=hoje.year)

        tk.Label(filtro, text="Mês:", bg=CORES["card"], fg=CORES["subtexto"],
                 font=("Courier", 9)).pack(side="left")
        mes_cb = ttk.Combobox(filtro, textvariable=self.mes_var,
                              values=list(range(1, 13)), width=3,
                              font=("Courier", 10), state="readonly")
        mes_cb.pack(side="left", padx=4)

        tk.Label(filtro, text="Ano:", bg=CORES["card"], fg=CORES["subtexto"],
                 font=("Courier", 9)).pack(side="left", padx=(8,0))
        anos = list(range(2020, hoje.year + 2))
        ano_cb = ttk.Combobox(filtro, textvariable=self.ano_var,
                              values=anos, width=5,
                              font=("Courier", 10), state="readonly")
        ano_cb.pack(side="left", padx=4)

        tk.Button(filtro, text="🔍", font=("Courier", 10), bg=CORES["azul"],
                  fg="white", relief="flat", padx=6, cursor="hand2",
                  command=self.atualizar).pack(side="left", padx=4)

        # ── Botões principais ──
        btn_frame = tk.Frame(self, bg=CORES["bg"])
        btn_frame.pack(pady=16)

        tk.Button(btn_frame, text="＋  NOVA ENTRADA", font=("Courier", 12, "bold"),
                  bg=CORES["verde"], fg=CORES["bg"], relief="flat", bd=0,
                  padx=28, pady=12, cursor="hand2",
                  command=lambda: JanelaEntrada(self, self.atualizar)
                  ).pack(side="left", padx=12)

        tk.Button(btn_frame, text="－  NOVO GASTO", font=("Courier", 12, "bold"),
                  bg=CORES["vermelho"], fg="white", relief="flat", bd=0,
                  padx=28, pady=12, cursor="hand2",
                  command=lambda: JanelaGasto(self, self.atualizar)
                  ).pack(side="left", padx=12)

        tk.Button(btn_frame, text="🗑  EXCLUIR", font=("Courier", 12, "bold"),
                  bg=CORES["amarelo"], fg=CORES["bg"], relief="flat", bd=0,
                  padx=28, pady=12, cursor="hand2",
                  command=self._excluir_selecionado
                  ).pack(side="left", padx=12)

        # ── Cards de resumo ──
        self.cards_frame = tk.Frame(self, bg=CORES["bg"])
        self.cards_frame.pack(fill="x", padx=24)

        # ── Área principal (tabela + gráfico) ──
        main = tk.Frame(self, bg=CORES["bg"])
        main.pack(fill="both", expand=True, padx=24, pady=8)

        # Tabela
        tabela_frame = tk.Frame(main, bg=CORES["card"], padx=8, pady=8)
        tabela_frame.pack(side="left", fill="both", expand=True)
        tk.Label(tabela_frame, text="📋 Lançamentos", font=("Courier", 10, "bold"),
                 bg=CORES["card"], fg=CORES["subtexto"]).pack(anchor="w", padx=4)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
            background=CORES["card"], fieldbackground=CORES["card"],
            foreground=CORES["texto"], rowheight=26, font=("Courier", 9))
        style.configure("Treeview.Heading",
            background=CORES["borda"], foreground=CORES["subtexto"],
            font=("Courier", 9, "bold"))
        style.map("Treeview", background=[("selected", CORES["azul"])])

        cols = ("Tipo", "Descrição", "Categoria", "Valor", "Data")
        self.tree = ttk.Treeview(tabela_frame, columns=cols, show="headings", height=14)
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.column("Tipo",      width=70,  anchor="center")
        self.tree.column("Descrição", width=160)
        self.tree.column("Categoria", width=130)
        self.tree.column("Valor",     width=90,  anchor="e")
        self.tree.column("Data",      width=90,  anchor="center")

        scroll = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Gráfico
        self.grafico_frame = tk.Frame(main, bg=CORES["card"], width=300)
        self.grafico_frame.pack(side="right", fill="y", padx=(12,0))
        self.grafico_frame.pack_propagate(False)
        tk.Label(self.grafico_frame, text="📊 Gastos por Categoria",
                 font=("Courier", 10, "bold"), bg=CORES["card"],
                 fg=CORES["subtexto"]).pack(anchor="w", padx=8, pady=4)
        self.canvas_widget = None

    def _excluir_selecionado(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um item na tabela para excluir!")
            return

        item = selecionado[0]
        tags = self.tree.item(item, "tags")

        # Extrair id e tipo das tags
        id_ = None
        tipo = None
        for tag in tags:
            if tag.startswith("id:"):
                id_ = int(tag.split(":")[1])
            if tag.startswith("tipo:"):
                tipo = tag.split(":")[1]

        if id_ is None or tipo is None:
            messagebox.showerror("Erro", "Não foi possível identificar o registro.")
            return

        valores = self.tree.item(item, "values")
        confirmado = messagebox.askyesno(
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir?\n\n"
            f"Tipo: {valores[0]}\n"
            f"Descrição: {valores[1]}\n"
            f"Valor: {valores[3]}\n"
            f"Data: {valores[4]}"
        )
        if not confirmado:
            return

        if tipo == "entrada":
            excluir_entrada(id_)
        else:
            excluir_gasto(id_)

        self.atualizar()

    def _card(self, parent, titulo, valor, cor):
        f = tk.Frame(parent, bg=CORES["card"], padx=16, pady=10)
        f.pack(side="left", expand=True, fill="x", padx=6)
        tk.Label(f, text=titulo, font=("Courier", 8), bg=CORES["card"],
                 fg=CORES["subtexto"]).pack(anchor="w")
        tk.Label(f, text=f"R$ {valor:,.2f}", font=("Courier", 14, "bold"),
                 bg=CORES["card"], fg=cor).pack(anchor="w")

    def atualizar(self):
        mes = self.mes_var.get()
        ano = self.ano_var.get()

        entradas = buscar_entradas(mes, ano)
        gastos   = buscar_gastos(mes, ano)

        # Cards
        for w in self.cards_frame.winfo_children():
            w.destroy()

        total_ent  = sum(e[2] for e in entradas)   # e = (id, descricao, valor, data)
        total_gas  = sum(g[2] for g in gastos)     # g = (id, descricao, valor, categoria, data)
        saldo      = total_ent - total_gas
        cor_saldo  = CORES["verde"] if saldo >= 0 else CORES["vermelho"]

        self._card(self.cards_frame, "ENTRADAS",  total_ent, CORES["verde"])
        self._card(self.cards_frame, "GASTOS",    total_gas, CORES["vermelho"])
        self._card(self.cards_frame, "SALDO",     saldo,     cor_saldo)

        # Tabela
        for row in self.tree.get_children():
            self.tree.delete(row)
        for e in entradas:
            # e = (id, descricao, valor, data)
            dt = datetime.datetime.strptime(e[3], "%Y-%m-%d").strftime("%d/%m/%Y")
            self.tree.insert("", "end",
                             values=("Entrada", e[1], "—", f"R$ {e[2]:,.2f}", dt),
                             tags=("entrada", f"id:{e[0]}", "tipo:entrada"))
        for g in gastos:
            # g = (id, descricao, valor, categoria, data)
            dt = datetime.datetime.strptime(g[4], "%Y-%m-%d").strftime("%d/%m/%Y")
            self.tree.insert("", "end",
                             values=("Gasto", g[1], g[3], f"R$ {g[2]:,.2f}", dt),
                             tags=("gasto", f"id:{g[0]}", "tipo:gasto"))
        self.tree.tag_configure("entrada", foreground=CORES["verde"])
        self.tree.tag_configure("gasto",   foreground=CORES["vermelho"])

        # Gráfico
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()

        por_cat = defaultdict(float)
        for g in gastos:
            # g = (id, descricao, valor, categoria, data)
            por_cat[g[3]] += g[2]

        if por_cat:
            labels = list(por_cat.keys())
            values = list(por_cat.values())
            cores_usadas = CORES_CATEGORIA[:len(labels)]

            fig, ax = plt.subplots(figsize=(3.2, 3.2),
                                   facecolor=CORES["card"])
            ax.set_facecolor(CORES["card"])
            wedges, texts, autotexts = ax.pie(
                values, labels=None, colors=cores_usadas,
                autopct="%1.0f%%", startangle=140,
                pctdistance=0.75,
                wedgeprops=dict(width=0.6, edgecolor=CORES["card"], linewidth=2)
            )
            for at in autotexts:
                at.set_color("white")
                at.set_fontsize(7)
                at.set_fontfamily("monospace")

            patches = [mpatches.Patch(color=cores_usadas[i],
                                      label=f"{labels[i].split(' ',1)[-1]}: R${values[i]:,.0f}")
                       for i in range(len(labels))]
            ax.legend(handles=patches, loc="lower center", bbox_to_anchor=(0.5, -0.32),
                      fontsize=6.5, frameon=False, labelcolor=CORES["texto"],
                      ncol=2)
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
            self.canvas_widget = canvas
            plt.close(fig)
        else:
            lbl = tk.Label(self.grafico_frame, text="Nenhum gasto\nregistrado este mês.",
                           font=("Courier", 10), bg=CORES["card"], fg=CORES["subtexto"])
            lbl.pack(expand=True)
            self.canvas_widget = lbl

# ─────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
