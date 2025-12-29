from __future__ import annotations

import json
import tkinter as tk
from tkinter import messagebox

from storage.config import AppConfig
from features.sticker_selector import StickerSelectorClient
from windows.ui_theme import FONT_MONO, FONT_UI, apply_window_icon, ttk


class StickerSettingsWindow(tk.Toplevel):
    def __init__(self, master, cfg: AppConfig, on_apply_cfg):
        super().__init__(master)
        apply_window_icon(self)
        self.title("StickerSelector 设置")
        self.geometry("1100x700")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.cfg = cfg
        self.on_apply_cfg = on_apply_cfg

        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        main = ttk.Frame(root)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(main)
        right.pack(side="right", fill="both", expand=True, padx=(12, 0))

        self._build_left(left)
        self._build_right(right)

        bottom = ttk.Frame(root)
        bottom.pack(fill="x", pady=(10, 0))
        ttk.Button(bottom, text="保存并应用", command=self.save_apply).pack(side="left")
        ttk.Button(bottom, text="取消", command=self._on_close).pack(side="left", padx=8)

    def _build_left(self, parent):
        box = ttk.Labelframe(parent, text="StickerSelector 设置", padding=10)
        box.pack(fill="x")

        self.sticker_enabled_var = tk.BooleanVar(
            value=bool(self.cfg.sticker_selector_enabled)
        )
        ttk.Checkbutton(
            box, text="启用 StickerSelector", variable=self.sticker_enabled_var
        ).pack(anchor="w")

        row_api = ttk.Frame(box)
        row_api.pack(fill="x", pady=4)
        ttk.Label(row_api, text="API 地址", width=12).pack(side="left")
        self.sticker_api_var = tk.StringVar(value=self.cfg.sticker_selector_api)
        ttk.Entry(row_api, textvariable=self.sticker_api_var).pack(
            side="left", fill="x", expand=True
        )
        ttk.Label(row_api, text="示例：http://127.0.0.1:8000").pack(
            side="left", padx=8
        )

        row_k = ttk.Frame(box)
        row_k.pack(fill="x", pady=4)
        ttk.Label(row_k, text="默认返回数量", width=12).pack(side="left")
        self.sticker_k_var = tk.StringVar(value=str(self.cfg.sticker_selector_k or 3))
        ttk.Spinbox(row_k, from_=1, to=6, textvariable=self.sticker_k_var, width=6).pack(
            side="left"
        )
        ttk.Label(row_k, text="最多6条；随机模式建议 >1").pack(side="left", padx=8)

        row_series = ttk.Frame(box)
        row_series.pack(fill="x", pady=4)
        ttk.Label(row_series, text="series 过滤", width=12).pack(side="left")
        self.sticker_series_var = tk.StringVar(value=self.cfg.sticker_selector_series)
        ttk.Entry(row_series, textvariable=self.sticker_series_var, width=12).pack(
            side="left"
        )
        ttk.Label(row_series, text="可留空").pack(side="left", padx=8)

        row_order = ttk.Frame(box)
        row_order.pack(fill="x", pady=4)
        ttk.Label(row_order, text="order 排序", width=12).pack(side="left")
        order_val = (self.cfg.sticker_selector_order or "desc").strip() or "desc"
        self.sticker_order_var = tk.StringVar(value=order_val)
        order_box = ttk.Combobox(
            row_order,
            textvariable=self.sticker_order_var,
            values=["desc", "asc"],
            width=8,
            state="readonly",
        )
        order_box.pack(side="left")
        ttk.Label(row_order, text="raw 排序方向").pack(side="left", padx=8)

        row_mode = ttk.Frame(box)
        row_mode.pack(fill="x", pady=4)
        ttk.Label(row_mode, text="选择模式", width=12).pack(side="left")
        mode_value = "random" if self.cfg.sticker_selector_random else "best"
        self.sticker_mode_var = tk.StringVar(value=mode_value)
        ttk.Radiobutton(
            row_mode,
            text="随机（k>1）",
            value="random",
            variable=self.sticker_mode_var,
        ).pack(side="left")
        ttk.Radiobutton(
            row_mode, text="最高匹配", value="best", variable=self.sticker_mode_var
        ).pack(side="left", padx=10)

        row_embed = ttk.Frame(box)
        row_embed.pack(fill="x", pady=4)
        ttk.Label(row_embed, text="embed_raw 阈值", width=12).pack(side="left")
        self.sticker_embed_raw_var = tk.StringVar(
            value=str(self.cfg.sticker_selector_embed_raw_min or 0.0)
        )
        ttk.Entry(row_embed, textvariable=self.sticker_embed_raw_var, width=10).pack(
            side="left"
        )
        ttk.Label(row_embed, text="仅混合模型生效；低于阈值不发送").pack(
            side="left", padx=8
        )

        prompt_box = ttk.Labelframe(parent, text="AI 表情包提示词", padding=10)
        prompt_box.pack(fill="both", expand=True, pady=(10, 0))
        split_preview = (
            (self.cfg.split_delimiter or "<<<NEXT>>>").strip() or "<<<NEXT>>>"
        )
        hint = (
            f"让 AI 在需要时输出 <<<标签1 标签2>>> 形式提示词；"
            f"也可用分隔符 {split_preview} 拆分文本与表情包提示。"
        )
        ttk.Label(prompt_box, text=hint, wraplength=460).pack(anchor="w")
        self.sticker_prompt_text = tk.Text(
            prompt_box, height=6, wrap="word", font=FONT_UI
        )
        self.sticker_prompt_text.pack(fill="both", expand=True, pady=(6, 4))
        self.sticker_prompt_text.insert("1.0", self.cfg.sticker_selector_prompt or "")
        ttk.Button(
            prompt_box, text="填充示例模板", command=self.fill_sticker_prompt
        ).pack(anchor="e")

    def _build_right(self, parent):
        test_box = ttk.Labelframe(parent, text="接口测试（最多6张）", padding=10)
        test_box.pack(fill="both", expand=True)

        test_tag_row = ttk.Frame(test_box)
        test_tag_row.pack(fill="x", pady=2)
        ttk.Label(test_tag_row, text="描述词", width=10).pack(side="left")
        self.test_tags_var = tk.StringVar(value="可爱 小猫 开心")
        ttk.Entry(test_tag_row, textvariable=self.test_tags_var).pack(
            side="left", fill="x", expand=True
        )

        info_row = ttk.Frame(test_box)
        info_row.pack(fill="x", pady=2)
        ttk.Label(
            info_row, text="（使用上方设置的 API / 返回数量 / series / order 进行测试）"
        ).pack(side="left")

        btn_row = ttk.Frame(test_box)
        btn_row.pack(fill="x", pady=(6, 4))
        ttk.Button(btn_row, text="发送测试", command=self._test_sticker_api).pack(
            side="right"
        )

        self.sticker_test_output = tk.Text(
            test_box, height=18, wrap="word", font=FONT_MONO, state="disabled"
        )
        self.sticker_test_output.pack(fill="both", expand=True)

    def fill_sticker_prompt(self):
        split = (self.cfg.split_delimiter or "<<<NEXT>>>").strip() or "<<<NEXT>>>"
        template = (
            "当需要用表情包回复时，请输出单独一条 <<<标签1 标签2 标签3>>>，标签用空格分隔，不要加其它解释。\n"
            f"如果需要同时回复文本和表情包，请用分隔符 {split} 把文本和表情包提示分开。\n"
            "输出X条 <<< >>> 则为X个表情包逐个发送。详细表情包规则请根据人格设定里的来。\n"
            "表情包示例：<<<可爱 小猫 开心兴奋>>> 标签越多表情包越准确，请最少使用2个标签\n"
        )
        self.sticker_prompt_text.delete("1.0", tk.END)
        self.sticker_prompt_text.insert("1.0", template)

    def _set_sticker_test_result(self, text: str):
        self.sticker_test_output.configure(state="normal")
        self.sticker_test_output.delete("1.0", tk.END)
        self.sticker_test_output.insert("1.0", text)
        self.sticker_test_output.configure(state="disabled")

    def _open_sticker_item_detail(self, item, meta):
        win = tk.Toplevel(self)
        win.title("Sticker 详情")
        win.geometry("640x520")

        top = ttk.Frame(win, padding=8)
        top.pack(fill="both", expand=True)

        left = ttk.Frame(top)
        left.pack(side="left", fill="both", expand=True)
        right = ttk.Frame(top)
        right.pack(side="right", fill="y")

        url = item.get("url") if isinstance(item, dict) else None
        full_url = None
        if url:
            base = (self.sticker_api_var.get() or "").strip()
            if url.startswith("http://") or url.startswith("https://"):
                full_url = url
            elif base:
                full_url = base.rstrip("/") + "/" + url.lstrip("/")

        img_label = ttk.Label(left)
        img_label.pack(fill="both", expand=True)

        try:
            from io import BytesIO
            from PIL import Image, ImageTk  # type: ignore
            import requests
        except Exception:
            img_label.configure(text="无法预览图片（缺少 Pillow 或 requests）")
            return

        win._detail_img_refs = []
        win._detail_frames = None
        win._detail_anim_handle = None
        win._detail_last_size = (0, 0)

        raw_data = None
        if full_url:
            try:
                r = requests.get(full_url, stream=True, timeout=5)
                r.raise_for_status()
                raw_data = r.content
            except Exception:
                img_label.configure(text="图片加载失败")
                raw_data = None
        else:
            img_label.configure(text="无图片 URL")

        def _cancel_anim():
            try:
                if getattr(win, "_detail_anim_handle", None):
                    try:
                        img_label.after_cancel(win._detail_anim_handle)
                    except Exception:
                        try:
                            win.after_cancel(win._detail_anim_handle)
                        except Exception:
                            pass
            except Exception:
                pass
            win._detail_anim_handle = None
            win._detail_running = False

        def _on_close_win():
            try:
                _cancel_anim()
            except Exception:
                pass
            try:
                win.destroy()
            except Exception:
                pass

        win.protocol("WM_DELETE_WINDOW", _on_close_win)
        win.bind(
            "<Destroy>",
            lambda e: _cancel_anim() if getattr(e, "widget", None) is win else None,
        )

        def _update_preview(event=None):
            if not raw_data:
                return
            try:
                from io import BytesIO

                img_full = Image.open(BytesIO(raw_data))
            except Exception:
                return

            try:
                w = max(64, left.winfo_width() - 16)
                h = max(64, left.winfo_height() - 16)
                max_size = (w, h)

                is_animated = (
                    getattr(img_full, "is_animated", False)
                    or getattr(img_full, "n_frames", 1) > 1
                )

                if win._detail_last_size == max_size and win._detail_frames is not None:
                    if isinstance(win._detail_frames, list):
                        if win._detail_anim_handle is None:
                            win._detail_running = True

                            def animate(i=0):
                                if not win._detail_running:
                                    return
                                try:
                                    img_label.configure(image=win._detail_frames[i])
                                    win._detail_anim_handle = img_label.after(
                                        120, animate, (i + 1) % len(win._detail_frames)
                                    )
                                except Exception:
                                    win._detail_anim_handle = None

                            animate()
                    else:
                        img_label.configure(image=win._detail_frames)
                    return

                _cancel_anim()
                win._detail_frames = None

                if is_animated:
                    frames = []
                    for f in range(getattr(img_full, "n_frames", 1)):
                        img_full.seek(f)
                        fr = img_full.convert("RGBA")
                        fr.thumbnail(max_size, Image.LANCZOS)
                        frames.append(ImageTk.PhotoImage(fr))
                    win._detail_img_refs.clear()
                    win._detail_img_refs.append(frames)
                    win._detail_frames = frames
                    win._detail_last_size = max_size

                    win._detail_running = True

                    def animate(i=0):
                        if not win._detail_running:
                            return
                        try:
                            img_label.configure(image=win._detail_frames[i])
                            win._detail_anim_handle = img_label.after(
                                120, animate, (i + 1) % len(win._detail_frames)
                            )
                        except Exception:
                            win._detail_anim_handle = None

                    animate()
                else:
                    img = img_full.convert("RGBA")
                    img.thumbnail(max_size, Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    win._detail_img_refs.clear()
                    win._detail_img_refs.append(photo)
                    win._detail_frames = photo
                    win._detail_last_size = max_size
                    img_label.configure(image=photo)
            except Exception:
                pass

        left.bind("<Configure>", _update_preview)
        _update_preview()

        meta_frame = ttk.Frame(right, padding=8)
        meta_frame.pack(fill="y")
        ttk.Label(meta_frame, text="元数据", font=(None, 12, "bold")).pack(anchor="w")
        if isinstance(item, dict):
            for k in ("id", "series", "fit_rate", "raw", "embed_raw", "match_rate"):
                if k in item:
                    ttk.Label(meta_frame, text=f"{k}: {item.get(k)}").pack(anchor="w")
            tags = item.get("tags")
            if isinstance(tags, list):
                ttk.Label(meta_frame, text=f"tags: {', '.join(tags)}").pack(anchor="w")

        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=6)
        ttk.Label(right, text="返回 meta", font=(None, 11, "bold")).pack(anchor="w")
        txt = tk.Text(right, height=12, width=36, font=FONT_MONO)
        txt.pack(fill="y")
        try:
            txt.insert("1.0", json.dumps(meta or {}, indent=2, ensure_ascii=False))
        except Exception:
            txt.insert("1.0", str(meta or {}))
        txt.configure(state="disabled")

    def _test_sticker_api(self):
        api = (self.sticker_api_var.get() or "").strip()
        if not api:
            messagebox.showerror("错误", "请先填写 API 地址")
            return

        tags = (self.test_tags_var.get() or "").strip()
        if not tags:
            messagebox.showerror("错误", "请填写描述词")
            return

        try:
            k_val = int((self.sticker_k_var.get() or "").strip())
        except Exception:  # noqa: BLE001
            messagebox.showerror("错误", "返回数量需要是数字")
            return

        series = (self.sticker_series_var.get() or "").strip()
        order = (self.sticker_order_var.get() or "").strip() or "desc"
        client = StickerSelectorClient(api, max_k=6)
        k_final = client.normalize_k(k_val)
        res = client.select(tags, k_final, series, order)

        if res.error:
            self._set_sticker_test_result(f"❌ 失败：{res.error}")
            return

        self.sticker_test_output.configure(state="normal")
        self.sticker_test_output.delete("1.0", tk.END)
        self._sticker_test_buttons = []

        if not getattr(res, "items", None):
            self.sticker_test_output.insert(tk.END, "无 items 返回\n")
        else:
            btn_row = ttk.Frame(self.sticker_test_output)
            for idx, item in enumerate(res.items, start=1):
                raw = item.get("raw") if isinstance(item, dict) else None
                embed_raw = item.get("embed_raw") if isinstance(item, dict) else None
                fit = item.get("fit_rate") if isinstance(item, dict) else None
                if raw is not None:
                    if embed_raw is not None:
                        btn_text = f"#{idx} raw {raw:.3f} / e {embed_raw:.3f}"
                    else:
                        btn_text = f"#{idx} raw {raw:.3f}"
                elif fit is not None:
                    btn_text = f"#{idx} 符合度 {fit:.2f}"
                else:
                    btn_text = f"#{idx} 详情"
                btn = ttk.Button(
                    btn_row,
                    text=btn_text,
                    command=lambda it=item, m=res.meta: self._open_sticker_item_detail(
                        it, m
                    ),
                )
                btn.pack(side="left", padx=6)
                self._sticker_test_buttons.append(btn)
            self._sticker_test_button_row = btn_row
            self.sticker_test_output.window_create(tk.END, window=btn_row)
            self.sticker_test_output.insert(tk.END, "\n")

        self.sticker_test_output.configure(state="disabled")

    def save_apply(self):
        try:
            self.cfg.sticker_selector_k = int((self.sticker_k_var.get() or "").strip())
        except Exception:  # noqa: BLE001
            messagebox.showerror("错误", "默认返回数量不是数字")
            return

        try:
            embed_raw_min = float((self.sticker_embed_raw_var.get() or "").strip() or 0)
        except Exception:  # noqa: BLE001
            messagebox.showerror("错误", "embed_raw 阈值不是数字")
            return

        self.cfg.sticker_selector_enabled = bool(self.sticker_enabled_var.get())
        self.cfg.sticker_selector_api = (self.sticker_api_var.get() or "").strip()
        self.cfg.sticker_selector_series = (self.sticker_series_var.get() or "").strip()
        self.cfg.sticker_selector_order = (self.sticker_order_var.get() or "").strip() or "desc"
        self.cfg.sticker_selector_random = (
            self.sticker_mode_var.get() or "best"
        ) == "random"
        self.cfg.sticker_selector_embed_raw_min = embed_raw_min
        self.cfg.sticker_selector_prompt = self.sticker_prompt_text.get(
            "1.0", tk.END
        ).rstrip("\n")

        self.cfg.save(self.cfg.config_path)
        if self.on_apply_cfg:
            self.on_apply_cfg(self.cfg)

        self.destroy()

    def _on_close(self):
        self.destroy()
