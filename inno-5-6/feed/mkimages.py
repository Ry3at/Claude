# -*- coding: utf-8 -*-
"""ساخت تصویرهای تازه‌ی بخش آموزش (و چند تصویر کمکی) — SVG و PNG.

    python3 feed/mkimages.py            # همه
    python3 feed/mkimages.py G5-S01-A03 # فقط یکی

PNG با rsvg-convert در دو برابر اندازه ساخته می‌شود (مثل تصویرهای قبلی).
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from figs import *  # noqa

ROOT = os.path.dirname(HERE)
SVG_DIR = os.path.join(ROOT, 'bank', 'assets', 'svg')
PNG_DIR = os.path.join(ROOT, 'bank', 'assets', 'png')

# ===================================================================== الگوهای مشترک
def three_parts(title):
    f = Fig(title, 'هر جلسه همین سه بخش را دارد', h=420)
    data = [(TEAL, 'book', 'آموزش', '۱۵ دقیقه — یاد می‌گیری'),
            (YELLOW, 'puzzle', 'فعالیت تعاملی', '۳۵ دقیقه — بازی و ساختن'),
            (CORAL, 'medal', 'ارزیابی', '۱۰ دقیقه — چالش و نشان')]
    x = 602
    for i, (c, ic, lab, sub) in enumerate(data):
        f.card(x, 120, 268, 220, c, lab, ic, i + 1, sub)
        if i < 2:
            f.arrow(x - 4, 230, x - 14, 230, MUTED)
        x -= 286
    f.note('نشان را با تمام‌کردن مأموریت می‌گیری، نه با بهترین بودن.', 385)
    return f


def recap(title, items, sub='جلسه‌ی پیش در یک نگاه'):
    """چهار کارت مرور: (رنگ، نماد، برچسب دوسطری)."""
    f = Fig(title, sub, h=400)
    x = 672
    for i, (c, ic, lab) in enumerate(items):
        f.card(x, 120, 198, 230, c, lab, ic, i + 1, label_size=15, icon_size=58)
        x -= 214
    return f


def toolcard(name, ic, color, answers, sub='کارت ابزار — چهار پرسش'):
    f = Fig('ابزار امروز: ' + name, sub, h=470)
    f.rect(650, 120, 220, 320, 22, WHITE, color, 3)
    f.circle(760, 230, 70, tint(color))
    f.icon(ic, 760, 230, 80, color)
    f.text(760, 350, name, 22, INK, 700)
    f.text(760, 385, 'ماژول داخل هوشینو', 14, MUTED)
    qs = ['چه کاری می‌کند؟', 'از کجا بلد است؟', 'کجا اشتباه می‌کند؟', 'کجا نباید به‌جای من تصمیم بگیرد؟']
    cols = [TEAL, YELLOW, CORAL, PURPLE]
    for i in range(4):
        y = 120 + i * 82
        f.rect(30, y, 600, 70, 14, WHITE, LINE, 2)
        f.rect(586, y, 44, 70, 14, cols[i])
        f.rect(586, y, 14, 70, 0, cols[i])
        f.text(608, y + 43, fa(i + 1), 20, WHITE, 700)
        f.text(570, y + 28, qs[i], 15, cols[i] if cols[i] != YELLOW else BROWN, 700, 'start')
        f.text(570, y + 54, answers[i], 15.5, TXT, 500, 'start')
    return f


def flow(title, sub, steps, h=400, note=None, w_card=190, y=120, ch=210):
    """کارت‌های پشت‌سرهم از راست به چپ با پیکان."""
    f = Fig(title, sub, h=h)
    n = len(steps)
    gap = (840 - n * w_card) / (n - 1) if n > 1 else 0
    x = 870 - w_card
    for i, (c, ic, lab) in enumerate(steps):
        f.card(x, y, w_card, ch, c, lab, ic, i + 1, label_size=15, icon_size=56)
        if i < n - 1:
            f.arrow(x - 4, y + ch / 2 + 17, x - gap + 6, y + ch / 2 + 17, MUTED)
        x -= w_card + gap
    if note:
        f.note(note, h - 32)
    return f


def compare_rows(title, sub, rows, h=430, labels=('درخواست', 'پاسخ')):
    """دو ردیف مقایسه: (رنگ، برچسب ردیف، متن چپ، متن راست، درست؟)."""
    f = Fig(title, sub, h=h)
    y = 125
    rh = (h - 160) / len(rows) - 14
    for (c, lab, req, ans, ok) in rows:
        f.rect(30, y, 840, rh, 18, WHITE, c, 3)
        f.tag(800, y + 36, lab, c, 15, w=110)
        f.bubble(470, y + 52, 300, rh - 84, req, c, 'right', 16)
        f.icon('robot', 420, y + rh / 2 + 4, 52, NAVY)
        f.arrow(462, y + rh / 2 + 4, 450, y + rh / 2 + 4, MUTED)
        f.arrow(392, y + rh / 2 + 4, 380, y + rh / 2 + 4, MUTED)
        f.rect(60, y + 40, 310, rh - 70, 14, tint(c))
        f.lines(215, y + rh / 2 - (len(ans) - 1) * 13 + 6, ans, 15.5, TXT, 600, gap=26)
        f.badge(60, y + 40, ok, 17)
        y += rh + 14
    return f


# ===================================================================== پایه‌ی پنجم — جلسه‌ی ۱
@fig('G5-S01-A02')
def _():
    return three_parts('یک جلسه، سه بخش')


@fig('G5-S01-A03')
def _():
    f = Fig('الگو یعنی قاعده', 'بعدی چه رنگی است؟', h=400)
    cols = [CORAL, BLUE, CORAL, BLUE]
    x = 760
    for c in cols:
        f.circle(x, 200, 48, c)
        x -= 130
    f.rect(x - 52, 148, 104, 104, 18, CREAM, YELLOW, 3, '7 6')
    f.text(x, 218, '؟', 50, YELLOW, 700)
    f.rect(170, 290, 560, 56, 28, WHITE, TEAL, 3)
    f.text(450, 326, 'قاعده: یکی در میان قرمز و آبی  ←  بعدی قرمز است', 18, TXT, 600)
    f.note('اگر قاعده را پیدا کنی، بعدی را می‌دانی — بدون شانس.', 382, 16, MUTED)
    return f


@fig('G5-S01-A04')
def _():
    f = Fig('مثال حل‌شده: ۲، ۴، ۶، ...', 'به فاصله‌ی بین عددها نگاه کن', h=420)
    vals = ['۲', '۴', '۶']
    cols = [TEAL, YELLOW, CORAL]
    xs = [700, 540, 380, 220]
    for i, v in enumerate(vals):
        f.token(xs[i], 180, v, cols[i], 120)
    f.rect(xs[3], 180, 120, 120, 16, '#E3F4EA', GREEN, 3)
    f.text(xs[3] + 60, 256, '۸', 46, GREEN, 700)
    for i in range(3):
        a, b = xs[i] + 60, xs[i + 1] + 60
        f.path('M %g 172 Q %g 112 %g 172' % (a, (a + b) / 2, b + 8), stroke=PURPLE, sw=3)
        f.poly([(b + 8, 174), (b + 2, 160), (b + 18, 164)], PURPLE)
        f.tag((a + b) / 2, 130, '\u200e+۲', PURPLE, 16, w=56)
    f.rect(170, 330, 560, 54, 27, WHITE, GREEN, 3)
    f.text(450, 364, 'قاعده: هر بار دو تا اضافه می‌شود ← بعدی ۸', 18, TXT, 600)
    return f


@fig('G5-S01-A05')
def _():
    f = Fig('الگو یا شانس؟', 'آزمون ساده: می‌توانی قاعده‌اش را بنویسی؟', h=470)
    rows = [(['۵', '۵', '۵', '۵'], True, 'الگو', 'قاعده: همیشه ۵'),
            (['۷', '۲', '۹', '۱'], False, 'شانس', 'هیچ قاعده‌ای بعدی را نمی‌گوید')]
    y = 120
    for vals, ok, lab, why in rows:
        c = GREEN if ok else CORAL
        f.rect(30, y, 840, 140, 20, WHITE, c, 3)
        x = 760
        for v in vals:
            f.token(x - 45, y + 25, v, c, 90, fs=36)
            x -= 105
        f.badge(300, y + 50, ok, 24)
        f.text(260, y + 58, lab, 24, c, 700, 'start')
        f.text(300, y + 105, why, 16, TXT, 500, 'start')
        y += 160
    f.note('تکرار یک عدد هم الگوست؛ چون قاعده دارد.', 450, 16, MUTED)
    return f


@fig('G5-S01-A06')
def _():
    f = Fig('ذهن ما الگوباز است', 'حتی در ابرها صورت می‌بینیم!', h=420)
    f.icon('cloud', 300, 235, 260, '#C6CFE4')
    f.circle(265, 235, 11, INK)
    f.circle(335, 235, 11, INK)
    f.path('M 262 270 Q 300 300 338 270', stroke=INK, sw=6)
    f.icon('brain', 700, 210, 110, PURPLE)
    f.bubble(560, 285, 280, 70, 'یک صورت می‌بینم!', PURPLE, 'right', 18)
    f.arrow(610, 215, 470, 230, MUTED, dash='8 7')
    f.note('همین الگویابی هم ما را باهوش می‌کند و هم گاهی گولمان می‌زند.', 395, 16, MUTED)
    return f


# ===================================================================== پایه‌ی پنجم — جلسه‌ی ۲
@fig('G5-S02-A01')
def _():
    return recap('مرور: الگو و پیش‌بینی', [
        (TEAL, 'headphones', ['سه قرار', 'هدفون، صدا، نوبت']),
        (YELLOW, 'bulb', ['الگو یعنی', 'قاعده‌ی بعدی']),
        (CORAL, 'shuffle', ['۷ ، ۲ ، ۹ ، ۱', 'شانس است']),
        (PURPLE, 'question', ['ماشین چطور', 'حدس می‌زند؟'])])


@fig('G5-S02-A02')
def _():
    return toolcard('تصویرخوان', 'eye', TEAL, [
        'تصویر را می‌بیند و توصیف می‌کند؛ شباهت‌ها را می‌گوید.',
        'از دیدن تعداد خیلی زیادی تصویر و توضیحشان.',
        'حدسش را جای دیدن می‌گوید؛ گاهی چیز ناشبیه را شبیه می‌بیند.',
        'اینکه دو چیز واقعاً یکی‌اند یا نه را خودم بررسی می‌کنم.'])


@fig('G5-S02-A03')
def _():
    f = Fig('تصویرخوان چطور نگاه می‌کند؟', 'او معنا را نمی‌فهمد؛ رنگ و لبه و شکل را مقایسه می‌کند', h=430)
    f.rect(660, 130, 210, 210, 18, WHITE, NAVY, 3)
    f.icon('cat', 765, 235, 140, '#E08A3C')
    f.text(765, 370, 'تصویر', 16, MUTED, 600)
    f.arrow(645, 235, 590, 235, MUTED)
    chips = [(TEAL, 'palette', 'رنگ: نارنجی'), (YELLOW, 'pencil', 'لبه‌ها: خط‌های تیز'),
             (PURPLE, 'square', 'شکل: گوش مثلثی')]
    y = 120
    for c, ic, lab in chips:
        f.rect(300, y, 280, 62, 31, WHITE, c, 3)
        f.icon(ic, 545, y + 31, 30, c)
        f.text(510, y + 38, lab, 17, TXT, 600, 'start')
        y += 76
    f.rect(300, y, 280, 62, 31, '#FFE9E9', CORAL, 3, '7 6')
    f.badge(545, y + 31, False, 17)
    f.text(510, y + 38, 'معنا: «این گربه است»', 17, TXT, 600, 'start')
    f.arrow(290, 235, 240, 235, MUTED)
    f.icon('robot', 150, 225, 100, NAVY)
    f.text(150, 310, 'مقایسه با', 15, MUTED)
    f.text(150, 334, 'تصویرهای دیگر', 15, MUTED)
    return f


@fig('G5-S02-A04')
def _():
    f = Fig('شبیه از نگاه ماشین', 'برای ما دو چیز متفاوت؛ برای تصویرخوان شبیه', h=430)
    # پرتقال
    f.circle(690, 230, 80, '#FF9F1C')
    f.path('M 690 150 Q 700 128 724 126', stroke=GREEN, sw=6)
    f.circle(668, 205, 14, '#FFC266')
    f.text(690, 345, 'پرتقال', 18, TXT, 700)
    # توپ
    f.circle(450, 230, 80, '#F27A1A')
    f.path('M 370 230 L 530 230', stroke=INK, sw=4)
    f.path('M 450 150 L 450 310', stroke=INK, sw=4)
    f.path('M 393 173 Q 430 230 393 287', stroke=INK, sw=4)
    f.path('M 507 173 Q 470 230 507 287', stroke=INK, sw=4)
    f.text(450, 345, 'توپ بسکتبال', 18, TXT, 700)
    f.icon('robot', 170, 250, 90, NAVY)
    f.bubble(70, 120, 200, 70, 'شبیه هم‌اند!', NAVY, 'left', 18)
    f.rect(170, 372, 560, 40, 20, WHITE, LINE, 2)
    f.text(450, 398, 'رنگ و شکلشان نزدیک است، ولی معنایشان کاملاً فرق دارد.', 15.5, TXT, 600)
    return f


@fig('G5-S02-A05')
def _():
    f = Fig('شغل امروز: کارشناس کشاورزی دقیق', 'از روی داده تصمیم می‌گیرد کجا آب بدهد', h=440)
    data = [(BLUE, 'drop', ['حسگر خاک', 'رطوبت هر قطعه']),
            (TEAL, 'eye', ['تصویر هوایی', 'رنگ مزرعه از بالا']),
            (YELLOW, 'cloud', ['پیش‌بینی هوا', 'باران می‌آید؟'])]
    y = 112
    for c, ic, lab in data:
        f.rect(560, y, 310, 90, 18, WHITE, c, 3)
        f.circle(825, y + 45, 30, tint(c))
        f.icon(ic, 825, y + 45, 34, c)
        f.lines(700, y + 38, lab, 16, TXT, 600, gap=26)
        f.arrow(552, y + 45, 400, 250, MUTED)
        y += 106
    f.rect(70, 160, 320, 190, 22, WHITE, GREEN, 3)
    f.icon('tractor', 230, 225, 90, GREEN)
    f.text(230, 300, 'تصمیم:', 17, MUTED, 600)
    f.text(230, 330, 'کجا آب بدهیم؟', 20, INK, 700)
    return f


@fig('G5-S02-A06')
def _():
    f = Fig('مثال حل‌شده: نقشه‌ی رطوبت', 'رنگ هر قطعه، رطوبت خاک آن را نشان می‌دهد', h=460)
    names = ['الف', 'ب', 'پ', 'ت', 'ث', 'ج']
    cols = ['#3D7BE0', '#5B91E6', '#3D7BE0', '#5B91E6', '#B07A3B', '#3D7BE0']
    pct = ['۷۰٪', '۶۲٪', '۶۸٪', '۶۵٪', '۱۸٪', '۷۲٪']
    for i in range(6):
        r, c = divmod(i, 3)
        x = 820 - (c + 1) * 150
        y = 120 + r * 140
        dry = (i == 4)
        f.rect(x, y, 140, 125, 14, cols[i], CORAL if dry else WHITE, 5 if dry else 2)
        f.text(x + 70, y + 45, names[i], 22, WHITE, 700)
        f.text(x + 70, y + 92, pct[i], 26, WHITE, 700)
    # راهنما
    f.rect(40, 125, 300, 120, 16, WHITE, LINE, 2)
    f.text(190, 155, 'راهنمای رنگ', 16, INK, 700)
    f.rect(270, 175, 36, 24, 6, '#3D7BE0')
    f.text(255, 193, 'آبی: خاک مرطوب', 15, TXT, 500, 'start')
    f.rect(270, 210, 36, 24, 6, '#B07A3B')
    f.text(255, 228, 'قهوه‌ای: خاک خشک', 15, TXT, 500, 'start')
    f.rect(40, 265, 300, 140, 16, '#FFE9E9', CORAL, 3)
    f.icon('drop', 190, 300, 36, BLUE)
    f.lines(190, 345, ['قطعه‌ی «ث» الگو را می‌شکند:', 'خشک است و آب لازم دارد.'], 15.5, TXT, 600, gap=26)
    f.note('داده را بخوان، نه اینکه کدام قطعه سبزتر به نظر می‌رسد.', 438, 16, MUTED)
    return f


@fig('G5-S02-A07')
def _():
    f = Fig('هر دو دنبال الگو', 'تصویرخوان و کارشناس کشاورزی یک کار مشترک دارند', h=420)
    f.card(650, 120, 220, 200, TEAL, ['کارشناس کشاورزی', 'در نقشه‌ی رطوبت'], 'seedling', label_size=15)
    f.card(30, 120, 220, 200, NAVY, ['تصویرخوان', 'در رنگ و شکل تصویر'], 'robot', label_size=15)
    f.circle(450, 220, 80, WHITE, YELLOW, 4)
    f.icon('search', 450, 200, 50, YELLOW)
    f.text(450, 262, 'الگو', 22, INK, 700)
    f.arrow(640, 220, 540, 220, MUTED)
    f.arrow(260, 220, 360, 220, MUTED)
    f.rect(130, 345, 640, 50, 25, '#FFE9E9', CORAL, 2)
    f.text(450, 377, 'تصمیم اشتباه ← آب هدر می‌رود یا زمین تشنه خشک می‌ماند', 16, TXT, 600)
    return f


# ===================================================================== پایه‌ی پنجم — جلسه‌ی ۳
@fig('G5-S03-A01')
def _():
    return recap('مرور: الگو در تصویر', [
        (TEAL, 'eye', ['تصویرخوان', 'رنگ، لبه، شکل']),
        (GREEN, 'tractor', ['کشاورزی دقیق', 'تصمیم با داده']),
        (YELLOW, 'file', ['کارت شغل ۱', 'تا جلسه‌ی ۳۱']),
        (PURPLE, 'medal', ['نشان', 'چشم الگویاب'])])


@fig('G5-S03-A02')
def _():
    return toolcard('دستیار گفت‌وگو', 'chat', PURPLE, [
        'با تو گفت‌وگو می‌کند و به پرسش‌هایت پاسخ می‌دهد.',
        'از دیدن مقدار خیلی زیادی نوشته؛ واژه‌ی بعدی را حدس می‌زند.',
        'پاسخ نادرست را با لحن کاملاً مطمئن می‌گوید.',
        'هر ادعایش را پیش از استفاده خودم بررسی می‌کنم.'])


@fig('G5-S03-A03')
def _():
    f = Fig('مثال: مطمئن ولی غلط', 'لحن، جمله را درست نمی‌کند', h=440)
    f.bubble(470, 110, 400, 80, '«ماه از زمین بزرگ‌تر است!»', PURPLE, 'right', 20)
    f.tag(560, 230, 'لحن: کاملاً مطمئن', PURPLE, 15, w=170)
    f.tag(770, 230, 'محتوا: نادرست', CORAL, 15, w=150)
    # زمین و ماه به مقیاس
    f.circle(250, 250, 120, '#3D7BE0')
    f.path('M 170 200 Q 210 170 250 210 Q 280 240 240 270 Q 200 290 180 260 Z', fill='#2E9E5B', stroke='#2E9E5B', sw=2)
    f.path('M 280 300 Q 320 280 340 310 Q 320 340 290 330 Z', fill='#2E9E5B', stroke='#2E9E5B', sw=2)
    f.text(250, 398, 'زمین', 18, TXT, 700)
    f.circle(480, 330, 33, '#C6CFE4')
    f.circle(470, 320, 6, '#A9B4CF')
    f.circle(492, 342, 5, '#A9B4CF')
    f.text(480, 398, 'ماه', 18, TXT, 700)
    f.rect(580, 280, 290, 110, 16, WHITE, LINE, 2)
    f.lines(725, 318, ['واقعیت: ماه خیلی کوچک‌تر است؛', 'پهنایش حدود یک‌چهارمِ زمین.'], 15.5, TXT, 600, gap=28)
    return f


@fig('G5-S03-A04')
def _():
    f = Fig('لحن و درستی، دو چیز جدا', 'هر جمله را از دو سو بسنج', h=480)
    f.text(615, 140, 'درست', 20, GREEN, 700)
    f.text(285, 140, 'نادرست', 20, CORAL, 700)
    f.text(835, 230, 'مطمئن', 18, PURPLE, 700)
    f.text(835, 375, 'نامطمئن', 18, MUTED, 700)
    cells = [(470, 160, '«آب در صد درجه می‌جوشد.»', GREEN, False),
             (140, 160, '«ماه از زمین بزرگ‌تر است.»', CORAL, True),
             (470, 305, '«فکر کنم تهران پایتخت است.»', GREEN, False),
             (140, 305, '«شاید شترمرغ پرواز کند.»', CORAL, False)]
    for x, y, s, c, hot in cells:
        f.rect(x, y, 300, 130, 18, '#FFE9E9' if hot else WHITE, CORAL if hot else LINE, 4 if hot else 2)
        f.text(x + 150, y + 72, s, 16.5, TXT, 600)
    f.tag(290, 300, 'خطرناک‌ترین خانه', CORAL, 14, w=150)
    f.note('لحن می‌گوید «چطور گفته شد»؛ درستی می‌گوید «با واقعیت جور است یا نه».', 462, 15.5, MUTED)
    return f


@fig('G5-S03-A05')
def _():
    f = flow('چرا همیشه مطمئن حرف می‌زند؟', 'دستیار گفت‌وگو جمله را این‌طور می‌سازد', [
        (TEAL, 'book', ['نوشته‌های', 'خیلی زیاد']),
        (YELLOW, 'gear', ['حدس واژه‌ی', 'محتمل بعدی']),
        (PURPLE, 'chat', ['جمله‌ی روان', 'و مطمئن'])], h=440, w_card=220, ch=200)
    f.rect(170, 345, 560, 60, 30, '#FFE9E9', CORAL, 2, '7 6')
    f.badge(700, 375, False, 16)
    f.text(670, 381, 'بخش جداگانه برای «مطمئن نیستم» ندارد — دروغ هم نمی‌گوید.', 15, TXT, 600, 'start')
    return f


@fig('G5-S03-A06')
def _():
    return flow('محتوا را چطور بسنجیم؟', 'سه قدم کارآگاهی', [
        (CORAL, 'hand', ['لحن را', 'کنار بگذار']),
        (YELLOW, 'brain', ['خودم درباره‌اش', 'چه می‌دانم؟']),
        (TEAL, 'book', ['با یک منبع', 'معتبر بسنج']),
        (GREEN, 'check', ['حالا', 'داوری کن'])], h=400,
        note='هدف بی‌اعتمادی به همه‌چیز نیست؛ هر جمله را جدا بسنج.', w_card=180)


# ===================================================================== پایه‌ی پنجم — جلسه‌ی ۴
@fig('G5-S04-A01')
def _():
    return recap('مرور: لحن و درستی', [
        (PURPLE, 'chat', ['دستیار', 'گفت‌وگو']),
        (CORAL, 'xmark', ['مطمئن', 'ولی غلط']),
        (BLUE, 'moon', ['ماه کوچک‌تر', 'از زمین است']),
        (YELLOW, 'medal', ['نشان', 'کارآگاه لحن'])])


@fig('G5-S04-A02')
def _():
    f = Fig('درخواست چیست؟', 'ابزار فقط واژه‌های تو را می‌گیرد، نه فکرت را', h=430)
    f.icon('user', 770, 290, 110, NAVY)
    f.bubble(600, 110, 270, 90, ['در ذهن من:', 'دوچرخه‌ی قرمز کنار درخت'], YELLOW, 'right', 15.5, CREAM)
    f.rect(330, 255, 300, 64, 32, WHITE, TEAL, 3)
    f.text(480, 295, '«این تصویر چیست؟»', 18, TXT, 700)
    f.arrow(660, 287, 640, 287, MUTED)
    f.arrow(320, 287, 245, 287, TEAL)
    f.icon('robot', 170, 285, 100, NAVY)
    f.text(170, 370, 'فقط همین واژه‌ها', 15, MUTED, 600)
    f.text(170, 394, 'به او رسید', 15, MUTED, 600)
    f.text(480, 360, 'آنچه در ذهن توست، تا ننویسی‌اش نمی‌رسد.', 15.5, CORAL, 600)
    return f


@fig('G5-S04-A03')
def _():
    f = Fig('نشانه، حدس را باریک می‌کند', 'هر نشانه، پاسخ‌های ممکن را کمتر می‌کند', h=470)
    f.poly([(140, 120), (760, 120), (520, 330), (380, 330)], '#E8ECFB', LINE, 2)
    ics = [('cat', '#E08A3C'), ('dog', BROWN), ('tree', GREEN), ('home', NAVY), ('sun', YELLOW),
           ('car' if False else 'tractor', CORAL), ('star', PURPLE), ('drop', BLUE)]
    x = 690
    for ic, c in ics:
        f.icon(ic, x, 160, 40, c)
        x -= 66
    f.text(450, 220, 'درخواست مبهم: خیلی پاسخ ممکن', 15, MUTED, 600)
    tags = [('+ رنگ: نارنجی', TEAL), ('+ شکل: گوش مثلثی', YELLOW), ('+ مکان: روی دیوار', PURPLE)]
    y = 255
    for s, c in tags:
        f.tag(450, y, s, c, 14, w=180)
        y += 32
    f.arrow(450, 335, 450, 360, MUTED)
    f.circle(450, 405, 40, WHITE, GREEN, 3)
    f.icon('cat', 450, 405, 46, '#E08A3C')
    f.text(560, 412, 'یک پاسخ دقیق', 17, GREEN, 700, 'end')
    return f


@fig('G5-S04-A04')
def _():
    return compare_rows('مثال حل‌شده: از مبهم به دقیق', 'یک تصویر، دو درخواست', [
        (CORAL, 'مبهم', '«این تصویر چیست؟»', ['«یک عکس از بیرون.»', 'کلی و به‌دردنخور'], False),
        (TEAL, 'دقیق', ['«رنگ دوچرخه، حیوان روی', 'زین و درخت کنارش را بگو.»'],
         ['«دوچرخه‌ی قرمز، گربه‌ی', 'خاکستری روی زین، کنار درخت سیب.»'], True)], h=470)


@fig('G5-S04-A05')
def _():
    f = Fig('دقیق یعنی طولانی نیست', 'نشانه‌های واقعی این چهارتا هستند', h=470)
    data = [(TEAL, 'palette', 'رنگ'), (YELLOW, 'square', 'شکل'), (PURPLE, 'ruler', 'اندازه'), (CORAL, 'compass', 'مکان')]
    x = 690
    for c, ic, lab in data:
        f.card(x, 110, 180, 140, c, lab, ic, label_size=17, icon_size=44)
        x -= 220
    f.rect(30, 275, 840, 76, 18, '#FFE9E9', CORAL, 2)
    f.badge(830, 313, False, 18)
    f.text(800, 306, '«لطفاً خیلی خیلی دقیق نگاه کن و بگو چیه.»', 16.5, TXT, 600, 'start')
    f.text(800, 334, 'بلند و مؤدبانه است، ولی هیچ نشانه‌ای ندارد.', 14.5, MUTED, 500, 'start')
    f.rect(30, 365, 840, 76, 18, '#E3F4EA', GREEN, 2)
    f.badge(830, 403, True, 18)
    f.text(800, 396, '«دنبال دایره‌ی تیره‌ی کوچک در گوشه‌ی بالا بگرد.»', 16.5, TXT, 600, 'start')
    f.text(800, 424, 'کوتاه است، ولی چهار نشانه دارد: شکل، رنگ، اندازه، مکان.', 14.5, MUTED, 500, 'start')
    return f


@fig('G5-S04-A06')
def _():
    f = flow('شغل امروز: پزشک تصویربرداری', 'کار روزانه‌ی پزشک و کارشناس تصویربرداری پزشکی', [
        (TEAL, 'monitor', ['خواندن', 'تصویر پزشکی']),
        (YELLOW, 'search', ['پیدا کردن', 'نشانه‌ی دقیق']),
        (PURPLE, 'chat', ['توضیح ساده', 'به بیمار'])], h=420, w_card=220,
        note='پیش از نگاه‌کردن، می‌داند دنبال چه نشانه‌ای بگردد.')
    return f


@fig('G5-S04-A07')
def _():
    f = Fig('مثال: نشانه‌ها را بشمار', 'در این درخواست چند نشانه هست؟', h=420)
    segs = [('دنبال یک لکه‌ی', None), ('تیره', TEAL), ('و', None), ('گرد', YELLOW),
            ('در', None), ('گوشه‌ی بالای تصویر', PURPLE), ('بگرد.', None)]
    x = 860
    for s, c in segs:
        w = len(s) * 11.5 + 30
        if c:
            f.rect(x - w, 140, w, 56, 14, tint(c), c, 3)
            f.text(x - w / 2, 176, s, 20, TXT, 700)
        else:
            f.text(x - w / 2, 176, s, 20, TXT, 500)
        x -= w + 8
    labels = [(TEAL, 'رنگ', 'تیره'), (YELLOW, 'شکل', 'گرد'), (PURPLE, 'مکان', 'گوشه‌ی بالا')]
    x = 640
    for c, a, b in labels:
        f.card(x, 235, 180, 120, c, b, None, None, None, head=34, label_size=19)
        f.text(x + 90, 262, a, 16, WHITE, 700)
        x -= 210
    f.note('سه نشانه ← تصویرخوان می‌داند دقیقاً کجا را نگاه کند.', 395, 16, MUTED)
    return f


def build(ids=None):
    os.makedirs(SVG_DIR, exist_ok=True)
    os.makedirs(PNG_DIR, exist_ok=True)
    for iid, fn in sorted(REG.items()):
        if ids and iid not in ids:
            continue
        f = fn()
        sp = os.path.join(SVG_DIR, iid + '.svg')
        with open(sp, 'w', encoding='utf-8') as fh:
            fh.write(f.svg())
        pp = os.path.join(PNG_DIR, iid + '.png')
        subprocess.check_call(['rsvg-convert', '-z', '2', sp, '-o', pp])
    print('images:', len(ids) if ids else len(REG))


if __name__ == '__main__':
    import mkimages_g6  # noqa: F401  (تصویرهای پایه‌ی ششم)
    build(sys.argv[1:] or None)
