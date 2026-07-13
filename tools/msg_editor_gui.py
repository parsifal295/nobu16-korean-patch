#!/usr/bin/env python3
from __future__ import annotations

import argparse
import traceback
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    HAVE_TK = True
except ModuleNotFoundError:
    tk = None
    filedialog = None
    messagebox = None
    ttk = None
    HAVE_TK = False

import nobu16_msg_model as model


if HAVE_TK:
    TkBase = tk.Tk
else:
    class TkBase:
        pass


class MsgEditorApp(TkBase):
    def __init__(self, csv_path: Path | None, input_bin: Path | None) -> None:
        if not HAVE_TK:
            raise RuntimeError("tkinter is not available")
        super().__init__()
        self.title("NOBU16 MSG Editor")
        self.geometry("1500x860")
        self.minsize(1200, 700)

        self.csv_path: Path | None = csv_path
        self.catalog: model.Catalog | None = None
        self.entries: list[model.Entry] = []
        self.by_id: dict[int, model.Entry] = {}
        self.current_id: int | None = None

        self.search_var = tk.StringVar(value="")
        self.todo_only_var = tk.BooleanVar(value=False)
        self.allow_shorter_var = tk.BooleanVar(value=True)
        self.ascii_only_var = tk.BooleanVar(value=False)
        self.strict_original_var = tk.BooleanVar(value=True)
        self.input_bin_var = tk.StringVar(value=str(input_bin) if input_bin else "")
        self.output_bin_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready")
        self.stats_var = tk.StringVar(value="files=0 total=0 translated=0 todo=0")
        self.csv_var = tk.StringVar(value=str(csv_path) if csv_path else "")

        self._build_ui()
        self.bind("<Control-s>", self._on_ctrl_s)
        self.bind("<Control-f>", self._on_ctrl_f)

        if self.csv_path:
            self.load_csv(self.csv_path)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=8)
        root.pack(fill="both", expand=True)

        top = ttk.LabelFrame(root, text="Project")
        top.pack(fill="x", pady=(0, 8))

        ttk.Label(top, text="CSV").grid(row=0, column=0, padx=4, pady=4, sticky="w")
        ttk.Entry(top, textvariable=self.csv_var).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(top, text="Open CSV", command=self.open_csv_dialog).grid(row=0, column=2, padx=4, pady=4)
        ttk.Button(top, text="Reload", command=self.reload_csv).grid(row=0, column=3, padx=4, pady=4)
        ttk.Button(top, text="Save CSV", command=self.save_csv).grid(row=0, column=4, padx=4, pady=4)
        ttk.Button(top, text="Save As", command=self.save_csv_as).grid(row=0, column=5, padx=4, pady=4)

        ttk.Label(top, textvariable=self.stats_var).grid(row=1, column=1, padx=4, pady=(0, 4), sticky="w")
        ttk.Label(top, textvariable=self.status_var).grid(row=1, column=2, columnspan=4, padx=4, pady=(0, 4), sticky="w")

        top.columnconfigure(1, weight=1)

        middle = ttk.PanedWindow(root, orient="horizontal")
        middle.pack(fill="both", expand=True, pady=(0, 8))

        left = ttk.Frame(middle)
        right = ttk.Frame(middle)
        middle.add(left, weight=3)
        middle.add(right, weight=2)

        filter_box = ttk.LabelFrame(left, text="List")
        filter_box.pack(fill="both", expand=True)

        filter_row = ttk.Frame(filter_box)
        filter_row.pack(fill="x", padx=6, pady=6)
        ttk.Label(filter_row, text="Search").pack(side="left")
        self.search_entry = ttk.Entry(filter_row, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(6, 6))
        self.search_entry.bind("<Return>", lambda _e: self.refresh_tree())
        ttk.Checkbutton(filter_row, text="Todo only", variable=self.todo_only_var, command=self.refresh_tree).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(filter_row, text="Refresh", command=self.refresh_tree).pack(side="left")

        columns = ("id", "file", "enc", "offset", "alloc", "orig", "ko", "status")
        self.tree = ttk.Treeview(filter_box, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("id", text="id")
        self.tree.heading("file", text="file")
        self.tree.heading("enc", text="enc")
        self.tree.heading("offset", text="offset")
        self.tree.heading("alloc", text="alloc")
        self.tree.heading("orig", text="original_en")
        self.tree.heading("ko", text="translated_ko")
        self.tree.heading("status", text="status")

        self.tree.column("id", width=60, stretch=False, anchor="e")
        self.tree.column("file", width=140, stretch=False)
        self.tree.column("enc", width=90, stretch=False)
        self.tree.column("offset", width=100, stretch=False, anchor="e")
        self.tree.column("alloc", width=80, stretch=False, anchor="e")
        self.tree.column("orig", width=360, stretch=True)
        self.tree.column("ko", width=360, stretch=True)
        self.tree.column("status", width=90, stretch=False)
        self.tree.tag_configure("todo", foreground="#666666")

        yscroll = ttk.Scrollbar(filter_box, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(filter_box, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.pack(fill="both", expand=True, padx=6, pady=(0, 0))
        yscroll.pack(side="right", fill="y")
        xscroll.pack(fill="x", padx=6, pady=(0, 6))
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

        edit_box = ttk.LabelFrame(right, text="Editor")
        edit_box.pack(fill="both", expand=True)

        meta = ttk.Frame(edit_box)
        meta.pack(fill="x", padx=6, pady=6)
        self.meta_var = tk.StringVar(value="id=-")
        ttk.Label(meta, textvariable=self.meta_var).pack(side="left")

        ttk.Label(edit_box, text="Original").pack(anchor="w", padx=6)
        self.original_text = tk.Text(edit_box, height=8, wrap="word", state="disabled")
        self.original_text.pack(fill="x", padx=6, pady=(0, 6))

        ttk.Label(edit_box, text="Translated").pack(anchor="w", padx=6)
        self.translated_text = tk.Text(edit_box, height=8, wrap="word")
        self.translated_text.pack(fill="x", padx=6, pady=(0, 6))

        ttk.Label(edit_box, text="Notes").pack(anchor="w", padx=6)
        self.notes_entry = ttk.Entry(edit_box)
        self.notes_entry.pack(fill="x", padx=6, pady=(0, 8))

        row_actions = ttk.Frame(edit_box)
        row_actions.pack(fill="x", padx=6, pady=(0, 8))
        ttk.Button(row_actions, text="Apply Row", command=self.apply_row).pack(side="left")
        ttk.Button(row_actions, text="Clear Row", command=self.clear_row).pack(side="left", padx=(6, 0))
        ttk.Button(row_actions, text="Find Next Todo", command=self.find_next_todo).pack(side="left", padx=(6, 0))

        patch_box = ttk.LabelFrame(root, text="Validate / Inject")
        patch_box.pack(fill="x")

        ttk.Label(patch_box, text="Input bin").grid(row=0, column=0, padx=4, pady=4, sticky="w")
        ttk.Entry(patch_box, textvariable=self.input_bin_var).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(patch_box, text="Browse", command=self.pick_input_bin).grid(row=0, column=2, padx=4, pady=4)

        ttk.Label(patch_box, text="Output bin").grid(row=1, column=0, padx=4, pady=4, sticky="w")
        ttk.Entry(patch_box, textvariable=self.output_bin_var).grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        ttk.Button(patch_box, text="Browse", command=self.pick_output_bin).grid(row=1, column=2, padx=4, pady=4)

        opts = ttk.Frame(patch_box)
        opts.grid(row=0, column=3, rowspan=2, padx=8, pady=4, sticky="w")
        ttk.Checkbutton(opts, text="allow-shorter", variable=self.allow_shorter_var).pack(anchor="w")
        ttk.Checkbutton(opts, text="ascii-only", variable=self.ascii_only_var).pack(anchor="w")
        ttk.Checkbutton(opts, text="strict-original", variable=self.strict_original_var).pack(anchor="w")

        ttk.Button(patch_box, text="Validate", command=self.validate_all).grid(row=0, column=4, padx=8, pady=4)
        ttk.Button(patch_box, text="Inject", command=self.inject_bin).grid(row=1, column=4, padx=8, pady=4)

        patch_box.columnconfigure(1, weight=1)

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)
        self.update_idletasks()

    def _set_original_text(self, text: str) -> None:
        self.original_text.configure(state="normal")
        self.original_text.delete("1.0", "end")
        self.original_text.insert("1.0", text)
        self.original_text.configure(state="disabled")

    def _get_translated_text(self) -> str:
        return self.translated_text.get("1.0", "end-1c")

    def _set_translated_text(self, text: str) -> None:
        self.translated_text.delete("1.0", "end")
        self.translated_text.insert("1.0", text)

    def _get_selected_tree_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            return None
        try:
            return int(selected[0])
        except Exception:
            return None

    def _select_tree_id(self, entry_id: int) -> None:
        iid = str(entry_id)
        if iid in self.tree.get_children(""):
            self.tree.selection_set(iid)
            self.tree.focus(iid)
            self.tree.see(iid)

    def _on_ctrl_s(self, _event: tk.Event[tk.Misc]) -> str:
        self.save_csv()
        return "break"

    def _on_ctrl_f(self, _event: tk.Event[tk.Misc]) -> str:
        self.search_entry.focus_set()
        self.search_entry.selection_range(0, "end")
        return "break"

    def load_csv(self, path: Path) -> None:
        try:
            cat = model.load_catalog(path)
        except Exception as ex:
            messagebox.showerror("Load CSV failed", f"{path}\n\n{ex}")
            return
        self.csv_path = path
        self.catalog = cat
        self.csv_var.set(str(path))
        self.entries = cat.entries
        self.by_id = {e.id: e for e in cat.entries}
        self.current_id = None
        self.refresh_tree()
        self.refresh_stats()
        self._set_status(f"Loaded {path}")
        if self.entries:
            self._select_tree_id(self.entries[0].id)

    def reload_csv(self) -> None:
        if not self.csv_path:
            messagebox.showwarning("Reload", "CSV is not selected.")
            return
        self.load_csv(self.csv_path)

    def open_csv_dialog(self) -> None:
        path = filedialog.askopenfilename(
            title="Open catalog CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=str(self.csv_path.parent) if self.csv_path else None,
        )
        if not path:
            return
        self.load_csv(Path(path))

    def refresh_stats(self) -> None:
        total = len(self.entries)
        translated = sum(1 for e in self.entries if e.translated_ko.strip())
        todo = total - translated
        files = len({e.file for e in self.entries})
        self.stats_var.set(f"files={files} total={total} translated={translated} todo={todo}")

    def refresh_tree(self) -> None:
        selected_id = self._get_selected_tree_id()
        for iid in self.tree.get_children(""):
            self.tree.delete(iid)

        q = self.search_var.get().strip().lower()
        todo_only = self.todo_only_var.get()
        first_id: int | None = None

        for e in self.entries:
            if todo_only and e.translated_ko.strip():
                continue
            if q:
                hay = f"{e.id} {e.file} {e.encoding} {e.original_en} {e.translated_ko} {e.notes}".lower()
                if q not in hay:
                    continue
            if first_id is None:
                first_id = e.id
            tags = ("todo",) if not e.translated_ko.strip() else ()
            self.tree.insert(
                "",
                "end",
                iid=str(e.id),
                values=(
                    e.id,
                    Path(e.file).name,
                    e.encoding,
                    f"0x{e.offset:X}",
                    e.allocated_bytes,
                    e.original_en,
                    e.translated_ko,
                    e.status,
                ),
                tags=tags,
            )

        if selected_id is not None:
            self._select_tree_id(selected_id)
        elif first_id is not None:
            self._select_tree_id(first_id)

    def on_select_row(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        entry_id = self._get_selected_tree_id()
        if entry_id is None:
            return
        e = self.by_id.get(entry_id)
        if e is None:
            return
        self.current_id = entry_id
        self.meta_var.set(
            f"id={e.id}  file={Path(e.file).name}  enc={e.encoding}  "
            f"offset=0x{e.offset:X}  alloc={e.allocated_bytes}  align={e.align}  status={e.status}"
        )
        self._set_original_text(e.original_en)
        self._set_translated_text(e.translated_ko)
        self.notes_entry.delete(0, "end")
        self.notes_entry.insert(0, e.notes)

    def _require_current_entry(self) -> model.Entry | None:
        if self.current_id is None:
            messagebox.showwarning("Editor", "Select a row first.")
            return None
        e = self.by_id.get(self.current_id)
        if e is None:
            messagebox.showwarning("Editor", "Selected row is not available.")
            return None
        return e

    def apply_row(self) -> None:
        e = self._require_current_entry()
        if e is None:
            return

        text = self._get_translated_text()
        notes = self.notes_entry.get()
        try:
            enc = model.encode_text(
                text,
                e.encoding,
                ascii_only_run=self.ascii_only_var.get(),
            )
        except Exception as ex:
            messagebox.showerror("Encoding error", str(ex))
            return
        if len(enc) > e.allocated_bytes:
            messagebox.showerror(
                "Length error",
                f"id={e.id} encoded bytes {len(enc)} > allocated {e.allocated_bytes}",
            )
            return

        e.translated_ko = text
        e.notes = notes
        e.status = "translated" if text.strip() else "todo"
        self.refresh_stats()
        self.refresh_tree()
        self._select_tree_id(e.id)
        self._set_status(f"Applied row id={e.id} ({len(enc)}/{e.allocated_bytes} bytes)")

    def clear_row(self) -> None:
        e = self._require_current_entry()
        if e is None:
            return
        e.translated_ko = ""
        e.status = "todo"
        self._set_translated_text("")
        self.refresh_stats()
        self.refresh_tree()
        self._select_tree_id(e.id)
        self._set_status(f"Cleared row id={e.id}")

    def find_next_todo(self) -> None:
        if not self.entries:
            return
        start_idx = 0
        if self.current_id is not None:
            for i, e in enumerate(self.entries):
                if e.id == self.current_id:
                    start_idx = i + 1
                    break
        for i in range(start_idx, len(self.entries)):
            if not self.entries[i].translated_ko.strip():
                self._select_tree_id(self.entries[i].id)
                return
        for i in range(0, start_idx):
            if not self.entries[i].translated_ko.strip():
                self._select_tree_id(self.entries[i].id)
                return
        messagebox.showinfo("Todo", "No todo rows found.")

    def save_csv(self) -> None:
        if not self.csv_path:
            self.save_csv_as()
            return
        if self.catalog is None:
            messagebox.showwarning("Save CSV", "No catalog loaded.")
            return
        try:
            model.save_catalog(self.csv_path, self.catalog)
        except Exception as ex:
            messagebox.showerror("Save CSV failed", str(ex))
            return
        self._set_status(f"Saved {self.csv_path}")

    def save_csv_as(self) -> None:
        base_dir = str(self.csv_path.parent) if self.csv_path else "."
        initial_file = self.csv_path.name if self.csv_path else "msggame_runs.edited.csv"
        path = filedialog.asksaveasfilename(
            title="Save CSV as",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=base_dir,
            initialfile=initial_file,
        )
        if not path:
            return
        self.csv_path = Path(path)
        self.csv_var.set(path)
        self.save_csv()

    def pick_input_bin(self) -> None:
        path = filedialog.askopenfilename(
            title="Select input bin",
            filetypes=[("BIN files", "*.bin"), ("All files", "*.*")],
            initialdir=str(Path(self.input_bin_var.get()).parent) if self.input_bin_var.get() else None,
        )
        if path:
            self.input_bin_var.set(path)

    def pick_output_bin(self) -> None:
        initial = self.output_bin_var.get()
        path = filedialog.asksaveasfilename(
            title="Select output bin",
            defaultextension=".bin",
            filetypes=[("BIN files", "*.bin"), ("All files", "*.*")],
            initialdir=str(Path(initial).parent) if initial else None,
            initialfile=Path(initial).name if initial else "msggame.patched.bin",
        )
        if path:
            self.output_bin_var.set(path)

    def _report_dialog(self, title: str, lines: list[str]) -> None:
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("980x560")
        text = tk.Text(win, wrap="none")
        ysb = ttk.Scrollbar(win, orient="vertical", command=text.yview)
        xsb = ttk.Scrollbar(win, orient="horizontal", command=text.xview)
        text.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        text.pack(fill="both", expand=True, side="left")
        ysb.pack(fill="y", side="right")
        xsb.pack(fill="x", side="bottom")
        text.insert("1.0", "\n".join(lines))
        text.configure(state="disabled")

    def validate_all(self) -> None:
        if not self.entries:
            messagebox.showwarning("Validate", "No CSV loaded.")
            return
        errors, warnings, targets = model.validate_entries(
            self.entries,
            exact_length=not self.allow_shorter_var.get(),
            ascii_only_run=self.ascii_only_var.get(),
        )
        self.refresh_stats()
        msg = f"targets={targets} errors={len(errors)} warnings={len(warnings)}"
        self._set_status(f"Validate: {msg}")
        if not errors and not warnings:
            messagebox.showinfo("Validate", msg)
            return
        lines = [msg, ""]
        if warnings:
            lines.append("[WARN]")
            lines.extend(warnings)
            lines.append("")
        if errors:
            lines.append("[ERR]")
            lines.extend(errors)
        self._report_dialog("Validate Report", lines)

    def inject_bin(self) -> None:
        if not self.entries:
            messagebox.showwarning("Inject", "No CSV loaded.")
            return

        input_bin = self.input_bin_var.get().strip()
        output_bin = self.output_bin_var.get().strip()
        if not input_bin:
            messagebox.showwarning("Inject", "Input bin is required.")
            return
        if not output_bin:
            messagebox.showwarning("Inject", "Output bin is required.")
            return
        in_path = Path(input_bin)
        out_path = Path(output_bin)
        if not in_path.exists():
            messagebox.showerror("Inject", f"Input bin not found:\n{in_path}")
            return

        # If catalog spans multiple files, patch rows that match input file name.
        name_matches = [e for e in self.entries if Path(e.file).name.lower() == in_path.name.lower()]
        if name_matches:
            patch_entries = name_matches
        else:
            patch_entries = self.entries

        errors, warnings, targets = model.validate_entries(
            patch_entries,
            exact_length=not self.allow_shorter_var.get(),
            ascii_only_run=self.ascii_only_var.get(),
        )
        if errors:
            self._report_dialog("Inject blocked (validate errors)", errors)
            self._set_status(f"Inject blocked: errors={len(errors)}")
            return
        if warnings:
            proceed = messagebox.askyesno(
                "Inject warning",
                f"warnings={len(warnings)} detected. Continue inject?",
            )
            if not proceed:
                return

        try:
            patched, skipped = model.inject_single_file(
                src_bin=in_path,
                out_bin=out_path,
                entries=patch_entries,
                strict_original=self.strict_original_var.get(),
                exact_length=not self.allow_shorter_var.get(),
                ascii_only_run=self.ascii_only_var.get(),
            )
        except Exception as ex:
            detail = "".join(traceback.format_exception_only(type(ex), ex)).strip()
            messagebox.showerror("Inject failed", detail)
            self._set_status("Inject failed")
            return

        self._set_status(
            f"Inject done: targets={targets} patched={patched} skipped={skipped} output={out_path}"
        )
        messagebox.showinfo(
            "Inject complete",
            f"targets={targets}\npatched={patched}\nskipped={skipped}\noutput={out_path}",
        )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="GUI msg editor for NOBU16 catalog/run CSV")
    p.add_argument("--csv", help="catalog or run CSV path")
    p.add_argument("--input-bin", help="input *.bin path for single-file inject")
    return p


def main() -> int:
    args = build_parser().parse_args()
    if not HAVE_TK:
        raise SystemExit(
            "tkinter is not installed in this Python environment. "
            "Install python3-tk (Linux) or use a Python build with Tk support (Windows)."
        )
    csv_path = Path(args.csv) if args.csv else None
    input_bin = Path(args.input_bin) if args.input_bin else None
    app = MsgEditorApp(csv_path=csv_path, input_bin=input_bin)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
