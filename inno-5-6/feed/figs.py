# -*- coding: utf-8 -*-
"""کتابخانه‌ی کوچک ساخت تصویرهای SVG آموزشی، هم‌سبک با تصویرهای موجود مخزن.

همه‌ی تصویرها پهنای ۹۰۰ دارند، پس‌زمینه‌ی روشن، نوار بالای سرمه‌ای و تیتر
راست‌چین. رنگ‌ها همان رنگ‌های تصویرهای قبلی‌اند تا مخزن یک‌دست بماند.
"""
from xml.sax.saxutils import escape

from figs_icons import ICONS

FONT = 'Vazirmatn, Tahoma, sans-serif'
BG = '#F2F5FF'
NAVY = '#2D3A8C'
INK = '#1E2761'
TXT = '#3C4A5E'
MUTED = '#8C97AB'
LINE = '#D7DEF2'
TEAL = '#06BEB6'
YELLOW = '#FFC93C'
CORAL = '#FF6B6B'
PURPLE = '#8E7CE8'
GREEN = '#2E9E5B'
CREAM = '#FFF6DC'
MINT = '#DDF6F4'
SOFT = '#E8ECFB'
WHITE = '#FFFFFF'
BROWN = '#B07A3B'
BLUE = '#3D7BE0'

FA = '۰۱۲۳۴۵۶۷۸۹'

# فهرست تصویرها: شناسه → تابع سازنده
REG = {}


def fig(iid):
    def deco(fn):
        REG[iid] = fn
        return fn
    return deco


def fa(n):
    return ''.join(FA[int(c)] if c.isdigit() else c for c in str(n))


def tint(color):
    """رنگ روشنِ هم‌خانواده برای پس‌زمینه‌ی کارت."""
    return {TEAL: MINT, YELLOW: CREAM, CORAL: '#FFE9E9', PURPLE: '#EEEBFC',
            NAVY: SOFT, GREEN: '#E3F4EA', BROWN: '#F5EBDD', BLUE: '#E4EEFC'
            }.get(color, '#F7F9FF')


class Fig(object):
    def __init__(self, title, sub=None, h=420, w=900):
        self.w, self.h = w, h
        self.el = []
        self.rect(0, 0, w, h, 0, BG)
        self.rect(0, 0, w, 10, 0, NAVY)
        self.text(w - 30, 56, title, 27, INK, 700, 'start')
        if sub:
            self.text(w - 30, 84, sub, 17, MUTED, 400, 'start')

    # ------------------------------------------------------------ پایه
    def rect(self, x, y, w, h, rx=12, fill=WHITE, stroke=None, sw=2, dash=None):
        s = '<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s"' % (
            x, y, w, h, rx, fill)
        if stroke:
            s += ' stroke="%s" stroke-width="%g"' % (stroke, sw)
        if dash:
            s += ' stroke-dasharray="%s"' % dash
        self.el.append(s + '/>')

    def circle(self, cx, cy, r, fill=WHITE, stroke=None, sw=2, dash=None):
        s = '<circle cx="%g" cy="%g" r="%g" fill="%s"' % (cx, cy, r, fill)
        if stroke:
            s += ' stroke="%s" stroke-width="%g"' % (stroke, sw)
        if dash:
            s += ' stroke-dasharray="%s"' % dash
        self.el.append(s + '/>')

    def line(self, x1, y1, x2, y2, stroke=MUTED, sw=2.5, dash=None, cap='round'):
        s = ('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="%g" '
             'stroke-linecap="%s"' % (x1, y1, x2, y2, stroke, sw, cap))
        if dash:
            s += ' stroke-dasharray="%s"' % dash
        self.el.append(s + '/>')

    def path(self, d, fill='none', stroke=MUTED, sw=2.5, dash=None):
        s = '<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linecap="round" stroke-linejoin="round"' % (
            d, fill, stroke, sw)
        if dash:
            s += ' stroke-dasharray="%s"' % dash
        self.el.append(s + '/>')

    def poly(self, pts, fill, stroke=None, sw=2):
        s = '<polygon points="%s" fill="%s"' % (
            ' '.join('%g,%g' % p for p in pts), fill)
        if stroke:
            s += ' stroke="%s" stroke-width="%g" stroke-linejoin="round"' % (stroke, sw)
        self.el.append(s + '/>')

    def text(self, x, y, s, size=17, fill=TXT, weight=400, anchor='middle'):
        self.el.append(
            '<text x="%g" y="%g" font-family="%s" font-size="%g" fill="%s" '
            'font-weight="%s" text-anchor="%s" direction="rtl">%s</text>'
            % (x, y, FONT, size, fill, weight, anchor, escape(str(s))))

    def lines(self, x, y, rows, size=17, fill=TXT, weight=400, anchor='middle', gap=None):
        gap = gap or size * 1.55
        for i, r in enumerate(rows):
            self.text(x, y + i * gap, r, size, fill, weight, anchor)

    def icon(self, name, cx, cy, size=60, color=NAVY):
        vb, inner = ICONS[name]
        vw, vh = [float(v) for v in vb.split()[2:]]
        w = size * vw / max(vw, vh)
        h = size * vh / max(vw, vh)
        self.el.append('<svg x="%g" y="%g" width="%g" height="%g" viewBox="%s" fill="%s">%s</svg>'
                       % (cx - w / 2, cy - h / 2, w, h, vb, color, inner))

    # ------------------------------------------------------------ ترکیبی
    def arrow(self, x1, y1, x2, y2, color=MUTED, sw=3, head=11, dash=None):
        import math
        a = math.atan2(y2 - y1, x2 - x1)
        bx, by = x2 - head * math.cos(a), y2 - head * math.sin(a)
        self.line(x1, y1, bx, by, color, sw, dash)
        p1 = (x2, y2)
        p2 = (bx + head * 0.6 * math.sin(a), by - head * 0.6 * math.cos(a))
        p3 = (bx - head * 0.6 * math.sin(a), by + head * 0.6 * math.cos(a))
        self.poly([p1, p2, p3], color)

    def card(self, x, y, w, h, color, label=None, icon=None, num=None,
             sub=None, head=34, icon_size=64, label_size=16):
        """کارت با سربرگ رنگی (همان کارت‌های تصویرهای قبلی)."""
        self.rect(x, y, w, h, 18, WHITE, LINE, 2)
        self.rect(x, y, w, head, 18, color)
        self.rect(x, y + head / 2, w, head / 2, 0, color)
        if num is not None:
            self.circle(x + w - 20, y + head / 2, 12, WHITE)
            self.text(x + w - 20, y + head / 2 + 6, fa(num), 15, color, 700)
        body_top = y + head
        if icon:
            cy = body_top + (h - head) * (0.36 if (label or sub) else 0.5)
            self.icon(icon, x + w / 2, cy, icon_size, color)
        if label:
            ly = body_top + (h - head) * (0.74 if icon else 0.45)
            if isinstance(label, (list, tuple)):
                self.lines(x + w / 2, ly, label, label_size, TXT, 600)
            else:
                self.text(x + w / 2, ly, label, label_size, TXT, 600)
        if sub:
            sy = body_top + (h - head) * 0.9
            self.text(x + w / 2, sy, sub, 13.5, MUTED, 400)

    def head_card(self, x, y, w, h, color, title, rows=(), size=16, icon=None):
        """کارت ستونی با تیتر داخل سربرگ و چند سطر متن."""
        self.rect(x, y, w, h, 16, WHITE, LINE, 2)
        self.rect(x, y, w, 46, 16, color)
        self.rect(x, y + 23, w, 23, 0, color)
        self.text(x + w / 2, y + 30, title, 18, WHITE, 700)
        top = y + 46
        if icon:
            self.icon(icon, x + w / 2, top + 44, 50, color)
            top += 88
        for i, r in enumerate(rows):
            self.text(x + w / 2, top + 34 + i * size * 1.75, r, size, TXT, 500)

    def token(self, x, y, s, color=TEAL, size=110, dashed=False, fs=40, fill=WHITE):
        if dashed:
            self.rect(x, y, size, size, 16, CREAM, color, 3, '7 6')
        else:
            self.rect(x, y, size, size, 16, fill, LINE, 2)
        self.text(x + size / 2, y + size / 2 + fs * 0.36, s, fs, color, 700)

    def pill(self, x, y, w, h, label, color, icon=None, label_size=16, fill=WHITE):
        self.rect(x, y, w, h, h / 2 if h < 90 else 26, fill, color, 3)
        if icon:
            self.icon(icon, x + w / 2, y + h * 0.36, 40, color)
            if isinstance(label, (list, tuple)):
                self.lines(x + w / 2, y + h * 0.72, label, label_size, TXT, 600)
            else:
                self.text(x + w / 2, y + h * 0.74, label, label_size, TXT, 600)
        else:
            if isinstance(label, (list, tuple)):
                n = len(label)
                y0 = y + h / 2 - (n - 1) * label_size * 0.78 + label_size * 0.36
                self.lines(x + w / 2, y0, label, label_size, TXT, 600)
            else:
                self.text(x + w / 2, y + h / 2 + label_size * 0.36, label, label_size, TXT, 600)

    def bubble(self, x, y, w, h, rows, color=TEAL, tail='right', size=17, fill=WHITE, weight=600):
        """حباب گفت‌وگو؛ دم حباب پایین سمت راست یا چپ."""
        self.rect(x, y, w, h, 18, fill, color, 3)
        tx = x + w - 46 if tail == 'right' else x + 46
        d = 14 if tail == 'right' else -14
        self.poly([(tx - 12, y + h - 1.5), (tx + 12, y + h - 1.5), (tx + d * 1.6, y + h + 22)],
                  fill, None)
        self.line(tx + 12 * (1 if tail == 'right' else -1), y + h, tx + d * 1.6, y + h + 22, color, 3)
        self.line(tx - 12 * (1 if tail == 'right' else -1), y + h, tx + d * 1.6, y + h + 22, color, 3)
        if isinstance(rows, str):
            rows = [rows]
        n = len(rows)
        y0 = y + h / 2 - (n - 1) * size * 0.8 + size * 0.36
        self.lines(x + w / 2, y0, rows, size, TXT, weight, gap=size * 1.6)

    def badge(self, cx, cy, ok=True, r=20):
        c = GREEN if ok else CORAL
        self.circle(cx, cy, r, c)
        self.icon('check' if ok else 'xmark', cx, cy, r * 1.05, WHITE)

    def note(self, s, y=None, size=18, fill=TXT, weight=400):
        self.text(self.w / 2, y or self.h - 30, s, size, fill, weight)

    def tag(self, x, y, s, color, size=14, pad=14, w=None):
        w = w or (len(s) * size * 0.55 + pad * 2)
        self.rect(x - w / 2, y - size, w, size * 1.9, size * 0.95, color)
        self.text(x, y + size * 0.36 - 1, s, size, WHITE, 700)
        return w

    def svg(self):
        head = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
                'viewBox="0 0 %d %d" font-family="%s">' % (self.w, self.h, self.w, self.h, FONT))
        return head + '\n' + '\n'.join(self.el) + '\n</svg>\n'
