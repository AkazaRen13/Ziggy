import tkinter as tk
import threading
import os
import sys
import random

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "Qwen2.5-1.5B-Instruct-IQ4_XS.gguf")

BG           = "#1a1a2e"
ACCENT       = "#7c6ee6"
ACCENT_LIGHT = "#a99cf0"
BUBBLE_BG    = "#16213e"
TEXT_FG      = "#e8e8f0"
HINT_FG      = "#6e6e9a"
CLEAR_BTN    = "#2a2a4a"

CIRCLE_SIZE  = 72
PADDING      = 20

_llm = None
def get_llm():
    global _llm
    if _llm is None:
        from llama_cpp import Llama
        _llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=6, n_gpu_layers=0, verbose=False)
    return _llm

def web_search(query):
    from ddgs import DDGS
    snippets = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=5):
            body = r.get("body", "").strip()
            if body:
                snippets.append(body)
    return "\n\n".join(snippets[:5]) if snippets else "No results found."

def summarise(question, context):
    prompt = (
        "<|im_start|>system\nYou are Ziggy, a concise AI search assistant. "
        "Answer in 2-4 natural sentences using only the search results. "
        "No lists, no links, plain prose.\n<|im_end|>\n"
        f"<|im_start|>user\nQuestion: {question}\n\nSearch results:\n{context[:3000]}\n<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    out = get_llm()(prompt, max_tokens=180, temperature=0.3, top_p=0.9,
                    repeat_penalty=1.1, stop=["<|im_end|>", "<|im_start|>"])
    return out["choices"][0]["text"].strip()

def search_and_answer(question):
    try:
        return summarise(question, web_search(question))
    except Exception as e:
        return f"Error: {e}"


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        self.cwin = tk.Toplevel(self.root)
        self.cwin.overrideredirect(True)
        self.cwin.attributes("-topmost", True)
        self.cwin.attributes("-transparentcolor", "magenta")
        self.cwin.config(bg="magenta")
        self.cwin.geometry(f"{CIRCLE_SIZE}x{CIRCLE_SIZE}+{sw-CIRCLE_SIZE-PADDING}+{sh-CIRCLE_SIZE-PADDING-48}")

        self.canvas = tk.Canvas(self.cwin, width=CIRCLE_SIZE, height=CIRCLE_SIZE,
                                bg="magenta", highlightthickness=0)
        self.canvas.pack()

        self._press_x = 0
        self._press_y = 0
        self._moved = False
        self.canvas.bind("<ButtonPress-1>",   self._press)
        self.canvas.bind("<B1-Motion>",       self._motion)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.canvas.bind("<Button-3>", self._right_click)

        self.bwin = tk.Toplevel(self.root)
        self.bwin.overrideredirect(True)
        self.bwin.attributes("-topmost", True)
        self.bwin.config(bg=BG)
        self.bwin.withdraw()
        self._build_bubble()

        self.bubble_open = False
        self._state = "idle"
        self._anim_job = None

        # start idle animation loop
        self._idle_loop()

        self.root.mainloop()

    def _right_click(self, e):
        menu = tk.Menu(self.root, tearoff=0, bg="#1a1a2e", fg="#e8e8f0",
                       activebackground="#7c6ee6", activeforeground="white",
                       font=("Segoe UI", 10), bd=0)
        menu.add_command(label="Quit Ziggy", command=self.root.quit)
        menu.tk_popup(e.x_root, e.y_root)

    # ── animation ─────────────────────────────────────────────────────────────

    def _idle_loop(self):
        if self._state != "idle":
            self._anim_job = self.root.after(500, self._idle_loop)
            return

        roll = random.random()

        if roll < 0.25:
            self._blink()
        elif roll < 0.40:
            self._look_side()
        elif roll < 0.50:
            self._surprised()
        elif roll < 0.58:
            self._squint()
        elif roll < 0.65:
            self._uwu()
        elif roll < 0.72:
            self._wink()
        else:
            self._draw_face("idle")

        delay = random.randint(1800, 4000)
        self._anim_job = self.root.after(delay, self._idle_loop)

    def _blink(self):
        self._draw_face("blink")
        self.root.after(120, lambda: self._draw_face("idle") if self._state == "idle" else None)

    def _look_side(self):
        side = random.choice(["look_left", "look_right"])
        self._draw_face(side)
        self.root.after(700, lambda: self._draw_face("idle") if self._state == "idle" else None)

    def _surprised(self):
        self._draw_face("surprised")
        self.root.after(600, lambda: self._draw_face("idle") if self._state == "idle" else None)

    def _squint(self):
        self._draw_face("squint")
        self.root.after(800, lambda: self._draw_face("idle") if self._state == "idle" else None)

    def _uwu(self):
        self._draw_face("uwu")
        self.root.after(900, lambda: self._draw_face("idle") if self._state == "idle" else None)

    def _wink(self):
        self._draw_face("wink")
        self.root.after(600, lambda: self._draw_face("idle") if self._state == "idle" else None)

    def _set_state(self, s):
        self._state = s
        self._draw_face(s)

    # ── face drawing ──────────────────────────────────────────────────────────

    def _draw_face(self, face):
        c = self.canvas
        c.delete("all")

        # outer glow
        c.create_oval(1, 1, CIRCLE_SIZE-1, CIRCLE_SIZE-1,
                      fill="", outline=ACCENT_LIGHT, width=1)
        # body
        c.create_oval(3, 3, CIRCLE_SIZE-3, CIRCLE_SIZE-3,
                      fill=BG, outline=ACCENT, width=2)

        cx = CIRCLE_SIZE // 2  # 36

        if face == "idle":
            self._eye(c, 18, 24, 9, 9)
            self._eye(c, 43, 24, 9, 9)
            c.create_arc(20, 42, 52, 56, start=0, extent=-25,
                         style=tk.ARC, outline=ACCENT_LIGHT, width=2)

        elif face == "blink":
            # closed eyes = horizontal lines
            c.create_line(16, 29, 28, 29, fill=ACCENT_LIGHT, width=2)
            c.create_line(42, 29, 54, 29, fill=ACCENT_LIGHT, width=2)
            c.create_arc(20, 42, 52, 56, start=0, extent=-25,
                         style=tk.ARC, outline=ACCENT_LIGHT, width=2)

        elif face == "look_left":
            self._eye(c, 14, 24, 9, 9)
            self._eye(c, 39, 24, 9, 9)
            c.create_arc(20, 42, 52, 56, start=0, extent=-25,
                         style=tk.ARC, outline=ACCENT_LIGHT, width=2)

        elif face == "look_right":
            self._eye(c, 22, 24, 9, 9)
            self._eye(c, 47, 24, 9, 9)
            c.create_arc(20, 42, 52, 56, start=0, extent=-25,
                         style=tk.ARC, outline=ACCENT_LIGHT, width=2)

        elif face == "surprised":
            # wide round eyes, O mouth
            self._eye(c, 16, 20, 12, 12)
            self._eye(c, 42, 20, 12, 12)
            c.create_oval(28, 43, 42, 55, fill="", outline=ACCENT_LIGHT, width=2)

        elif face == "squint":
            # half-closed eyes
            c.create_arc(16, 22, 28, 34, start=0, extent=180,
                         style=tk.ARC, outline=ACCENT_LIGHT, width=2)
            c.create_arc(42, 22, 54, 34, start=0, extent=180,
                         style=tk.ARC, outline=ACCENT_LIGHT, width=2)
            c.create_arc(20, 42, 52, 54, start=0, extent=-20,
                         style=tk.ARC, outline=ACCENT_LIGHT, width=2)

        elif face == "uwu":
            # >< eyes
            c.create_line(16, 22, 28, 34, fill=ACCENT_LIGHT, width=2)
            c.create_line(28, 22, 16, 34, fill=ACCENT_LIGHT, width=2)
            c.create_line(42, 22, 54, 34, fill=ACCENT_LIGHT, width=2)
            c.create_line(54, 22, 42, 34, fill=ACCENT_LIGHT, width=2)
            # w mouth
            c.create_line(20, 46, 27, 52, 35, 46, 43, 52, 50, 46,
                          fill=ACCENT_LIGHT, width=2)

        elif face == "wink":
            self._eye(c, 18, 24, 9, 9)
            # right eye wink line
            c.create_line(42, 29, 54, 29, fill=ACCENT_LIGHT, width=2)
            c.create_arc(20, 42, 52, 56, start=0, extent=-30,
                         style=tk.ARC, outline=ACCENT_LIGHT, width=2)

        elif face == "thinking":
            # look up-left
            self._eye(c, 14, 20, 9, 9)
            self._eye(c, 39, 20, 9, 9)
            # flat mouth
            c.create_line(22, 48, 48, 48, fill=ACCENT_LIGHT, width=2)
            # thought dots
            c.create_oval(50, 16, 56, 22, fill=ACCENT_LIGHT, outline="")
            c.create_oval(56, 10, 60, 14, fill=ACCENT_LIGHT, outline="")
            c.create_oval(61,  5, 64,  8, fill=ACCENT_LIGHT, outline="")

        elif face == "happy":
            self._eye(c, 18, 22, 9, 11)
            self._eye(c, 43, 22, 9, 11)
            c.create_arc(17, 38, 53, 56, start=0, extent=-35,
                         style=tk.ARC, outline=ACCENT_LIGHT, width=2)

    def _eye(self, c, x, y, w, h):
        c.create_oval(x-1, y-1, x+w+1, y+h+1, fill="#2a1a5a", outline="")
        c.create_oval(x,   y,   x+w,   y+h,   fill=ACCENT_LIGHT, outline="")
        # pupil shine
        c.create_oval(x+2, y+2, x+5, y+5, fill="white", outline="")

    # ── drag / click ──────────────────────────────────────────────────────────

    def _press(self, e):
        self._press_x = e.x
        self._press_y = e.y
        self._moved = False

    def _motion(self, e):
        dx = e.x - self._press_x
        dy = e.y - self._press_y
        if abs(dx) > 4 or abs(dy) > 4:
            self._moved = True
        if self._moved:
            x = self.cwin.winfo_x() + dx
            y = self.cwin.winfo_y() + dy
            self.cwin.geometry(f"+{x}+{y}")
            if self.bubble_open:
                self._place_bubble()

    def _release(self, e):
        if not self._moved:
            if self.bubble_open:
                self._hide_bubble()
            else:
                self._show_bubble()

    # ── bubble ────────────────────────────────────────────────────────────────

    def _build_bubble(self):
        self.bwin.config(bg=BG)

        header = tk.Frame(self.bwin, bg=ACCENT, height=36)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="✦ Ziggy", bg=ACCENT, fg="white",
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=12, pady=6)
        close_btn = tk.Label(header, text="✕", bg=ACCENT, fg="white",
                             font=("Segoe UI", 10), cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=10)
        close_btn.bind("<Button-1>", lambda e: self._hide_bubble())

        body = tk.Frame(self.bwin, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        search_row = tk.Frame(body, bg=BG)
        search_row.pack(fill=tk.X, pady=(0, 8))

        ef = tk.Frame(search_row, bg="#0f0f25",
                      highlightbackground=ACCENT, highlightthickness=1)
        ef.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.evar = tk.StringVar()
        self.entry = tk.Entry(ef, textvariable=self.evar,
                              bg="#0f0f25", fg=TEXT_FG, insertbackground=ACCENT_LIGHT,
                              relief=tk.FLAT, bd=0, font=("Segoe UI", 11))
        self.entry.pack(fill=tk.X, ipady=8, ipadx=10)
        self.entry.bind("<Return>", self._submit)
        self.entry.bind("<FocusIn>",
            lambda e: (self.evar.set(""), self.entry.config(fg=TEXT_FG))
            if self.evar.get() == "Ask anything…" else None)
        self.entry.bind("<FocusOut>",
            lambda e: (self.evar.set("Ask anything…"), self.entry.config(fg=HINT_FG))
            if not self.evar.get() else None)

        clr = tk.Label(search_row, text="⌫", bg=CLEAR_BTN, fg=HINT_FG,
                       font=("Segoe UI", 11), cursor="hand2", padx=8, pady=6)
        clr.pack(side=tk.LEFT, padx=(4, 4))
        clr.bind("<Button-1>", self._clear)

        btn = tk.Label(search_row, text="⌕", bg=ACCENT, fg="white",
                       font=("Segoe UI", 13, "bold"), cursor="hand2", padx=10, pady=6)
        btn.pack(side=tk.LEFT)
        btn.bind("<Button-1>", self._submit)

        self.status = tk.Label(body, text="", bg=BG, fg=HINT_FG,
                               font=("Segoe UI", 8), anchor="w")
        self.status.pack(fill=tk.X)

        af = tk.Frame(body, bg="#0f0f25",
                      highlightbackground="#2a2a4a", highlightthickness=1)
        af.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

        self.answer = tk.Text(af, bg="#0f0f25", fg=TEXT_FG,
                              font=("Segoe UI", 10), relief=tk.FLAT, bd=0,
                              wrap=tk.WORD, width=38, height=3,
                              state=tk.DISABLED, cursor="arrow",
                              highlightthickness=0, padx=10, pady=8,
                              spacing1=2, spacing3=3)
        self.answer.pack(fill=tk.BOTH, expand=True)

        self.evar.set("Ask anything…")
        self.entry.config(fg=HINT_FG)

    def _clear(self, *_):
        self.evar.set("")
        self.entry.config(fg=TEXT_FG)
        self.entry.focus_set()

    def _place_bubble(self):
        sw = self.root.winfo_screenwidth()
        cx = self.cwin.winfo_x()
        cy = self.cwin.winfo_y()
        bw = 400
        bx = cx - bw - 10 if cx + bw + CIRCLE_SIZE + 10 > sw else cx + CIRCLE_SIZE + 10
        self.bwin.geometry(f"{bw}x220+{bx}+{cy-20}")

    def _show_bubble(self):
        self._place_bubble()
        self.bwin.deiconify()
        self.bubble_open = True
        self.entry.focus_set()

    def _hide_bubble(self):
        self.bwin.withdraw()
        self.bubble_open = False

    def _submit(self, *_):
        q = self.evar.get().strip()
        if not q or q == "Ask anything…":
            return
        self._set_state("thinking")
        self.status.config(text="⟳  Searching the web…")
        self._set_answer("")
        threading.Thread(target=self._run, args=(q,), daemon=True).start()

    def _run(self, q):
        ans = search_and_answer(q)
        self.root.after(0, self._done, ans)

    def _done(self, ans):
        self._set_state("happy")
        self.status.config(text="✦ Ziggy")
        self._set_answer(ans)
        lines = max(3, min(10, len(ans) // 55 + ans.count('\n') + 1))
        self.answer.config(height=lines)
        bw = 400
        bh = 130 + lines * 22
        sw = self.root.winfo_screenwidth()
        cx = self.cwin.winfo_x()
        cy = self.cwin.winfo_y()
        bx = cx - bw - 10 if cx + bw + CIRCLE_SIZE + 10 > sw else cx + CIRCLE_SIZE + 10
        self.bwin.geometry(f"{bw}x{bh}+{bx}+{cy-20}")
        self.root.after(3000, lambda: self._set_state("idle"))

    def _set_answer(self, text):
        self.answer.config(state=tk.NORMAL)
        self.answer.delete("1.0", tk.END)
        self.answer.insert(tk.END, text)
        self.answer.config(state=tk.DISABLED)


if __name__ == "__main__":
    App()