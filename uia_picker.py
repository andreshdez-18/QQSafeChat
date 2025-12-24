from __future__ import annotations
import win32api
import win32gui
import win32con
import uiautomation as auto
from typing import Optional, Callable
from models import BoundControl


class HighlightRect:
    def __init__(self):
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = "HighlightRect_UiaChatbot"
        wc.hInstance = win32api.GetModuleHandle(None)

        try:
            self.class_atom = win32gui.RegisterClass(wc)
        except win32gui.error:
            self.class_atom = win32gui.GetClassInfo(wc.hInstance, wc.lpszClassName)[0]

        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_LAYERED
            | win32con.WS_EX_TRANSPARENT
            | win32con.WS_EX_TOPMOST,
            self.class_atom,
            None,
            win32con.WS_POPUP,
            0,
            0,
            0,
            0,
            0,
            0,
            wc.hInstance,
            None,
        )
        win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 255, win32con.LWA_ALPHA)

    def wnd_proc(self, hwnd, msg, w, l):
        if msg == win32con.WM_PAINT:
            hdc, ps = win32gui.BeginPaint(hwnd)
            pen = win32gui.CreatePen(win32con.PS_SOLID, 2, win32api.RGB(0, 200, 255))
            old = win32gui.SelectObject(hdc, pen)
            l2, t2, r2, b2 = win32gui.GetClientRect(hwnd)
            win32gui.Rectangle(hdc, l2, t2, r2, b2)
            win32gui.SelectObject(hdc, old)
            win32gui.DeleteObject(pen)
            win32gui.EndPaint(hwnd, ps)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, w, l)

    def show_rect(self, rect):
        win32gui.SetWindowPos(
            self.hwnd,
            win32con.HWND_TOPMOST,
            int(rect.left),
            int(rect.top),
            int(rect.right - rect.left),
            int(rect.bottom - rect.top),
            win32con.SWP_SHOWWINDOW,
        )
        win32gui.InvalidateRect(self.hwnd, None, True)

    def hide(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)


def control_from_point_safe(x: int, y: int, tk_hwnd: int):
    hwnd = win32gui.WindowFromPoint((x, y))

    if hwnd == tk_hwnd or win32gui.IsChild(tk_hwnd, hwnd):
        return None
    try:
        return auto.ControlFromPoint(x, y)
    except Exception:
        return None


def build_bound_control(ctrl, expected_type: str) -> Optional[BoundControl]:
    try:
        r = ctrl.BoundingRectangle
        cx = int((r.left + r.right) / 2)
        cy = int((r.top + r.bottom) / 2)
        return BoundControl(
            expected_type=expected_type,
            center_x=cx,
            center_y=cy,
            name=getattr(ctrl, "Name", "") or "",
            framework=getattr(ctrl, "FrameworkId", "") or "",
            automation_id=getattr(ctrl, "AutomationId", "") or "",
            class_name=getattr(ctrl, "ClassName", "") or "",
        )
    except Exception:
        return None


def reacquire(bound: BoundControl, tk_hwnd: int):
    offsets = [
        (0, 0),
        (8, 0),
        (-8, 0),
        (0, 8),
        (0, -8),
        (15, 0),
        (-15, 0),
        (0, 15),
        (0, -15),
    ]
    for dx, dy in offsets:
        ctrl = control_from_point_safe(
            bound.center_x + dx, bound.center_y + dy, tk_hwnd
        )
        if not ctrl:
            continue
        try:
            if ctrl.ControlTypeName == bound.expected_type:
                return ctrl
        except Exception:
            continue
    return None
