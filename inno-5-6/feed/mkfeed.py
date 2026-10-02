# -*- coding: utf-8 -*-
"""ساخت دو خروجی از فایل‌های جلسه:

  ۱) JSON برای هوشینو  → feed/hooshino_paye5.json و hooshino_paye6.json
  ۲) لاتک برای معلم    → bank_paye5.tex و bank_paye6.tex (کامپایل با XeLaTeX)
"""
import io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BANK = os.path.join(ROOT, 'bank')
sys.path.insert(0, HERE)
import check_session as C

SESSIONS = {5: ['G5_S01', 'G5_S02', 'G5_S03', 'G5_S04'],
            6: ['G6_S01', 'G6_S02', 'G6_S03', 'G6_S04']}
GRADE_NAME = {5: 'پنجم', 6: 'ششم'}

FA = '۰۱۲۳۴۵۶۷۸۹'


def fa(n):
    return ''.join(FA[int(c)] if c.isdigit() else c for c in str(n))


# ---------------------------------------------------------------- سیاست AI
AI_POLICY = {
    "language": "فارسی ساده و کودکانه؛ جمله‌ی کوتاه؛ بدون اصطلاح فنیِ توضیح‌نداده.",
    "rules": [
        "هرگز پیش از دادن هر سه راهنمایی، پاسخ را نگو.",
        "هرگز دانش‌آموزان را با هم مقایسه نکن و هیچ رتبه‌ای اعلام نکن.",
        "به املا و دست‌خط امتیاز نده مگر خودِ گام همان را بخواهد.",
        "اگر دانش‌آموز چیزی خارج از درس پرسید، کوتاه پاسخ بده و به گام برگردان.",
        "اگر پاسخ نامربوط یا خالی بود، بدون قضاوت دوباره بپرس.",
        "در گام‌های pair، خطاب را دونفره کن («شما دو نفر…»).",
        "بخش آموزش (amoozesh) فقط نمایشی است: هیچ پرسشی از دانش‌آموز نپرس و منتظر پاسخ نمان؛ صفحه‌ها را به‌ترتیب نشان بده و اگر دانش‌آموز پرسید، کوتاه توضیح بده.",
        "در گام مرور (review)، پس از صفحه‌ی مرور، کارت‌های pool.review را یکی‌یکی و همراه پاسخشان نشان بده.",
        "پیش‌سنجه (preCheck) را هنگام ورود هر دانش‌آموز و پیش از بخش آموزش، جدا برای هر نفر بپرس؛ در جلسه‌ی دونفره هر نفر جداگانه پاسخ می‌دهد.",
        "قلم‌های تمرینی که group مشترک دارند، پاره‌های یک پرسش‌اند: همه را پشت‌سرهم و به ترتیب groupPart بپرس و هر پاره را جدا داوری کن.",
        "بازخورد همیشه با کاری که دانش‌آموز کرد شروع شود، نه با درست یا غلط بودنش.",
        "در گام‌هایی که answer.mode برابر fixed است، فقط با فهرست accept تطبیق بده و خلاقیت را جای پاسخ نپذیر.",
        "در گام‌هایی که answer.mode برابر ai است، فقط معیارهای criteria را بررسی کن، نه سلیقه‌ی خودت.",
        "متن aiInstruction هر گام بر این قواعد عمومی اولویت دارد.",
    ],
    "answerModes": {
        "fixed": "پاسخ معین. value پاسخ درست است و accept همه‌ی صورت‌های پذیرفتنی. فقط تطبیق کن.",
        "ai": "پاسخ باز. criteria فهرست چیزهایی است که باید در پاسخ باشد؛ همه آمد → درست، بخشی آمد → نیمه، هیچ نیامد → نادرست.",
        "none": "گام فقط نمایشی است؛ پاسخی گرفته نمی‌شود.",
    },
    "interactions": {
        "display": "فقط نمایش؛ دکمه‌ی ادامه.",
        "text": "پاسخ تایپی.",
        "image": "بارگذاری عکس.",
        "voice": "ضبط و ارسال صدا.",
    },
    "hintPolicy": "hints دقیقاً سه قلم است: ۱ تلنگر بدون لو دادن، ۲ نشان‌دادن مسیر، ۳ تقریباً پاسخ. یکی‌یکی و فقط وقتی دانش‌آموز گیر کرد.",
}


# ================================================================ JSON
def build_json(grade):
    out = {
        "schema": "hooshino-feed/1.1",
        "grade": grade,
        "gradeName": "پایه‌ی %s ابتدایی" % GRADE_NAME[grade],
        "course": "نوآوری و هوش",
        "software": "هوشینو",
        "aiPolicy": AI_POLICY,
        "sessions": [],
    }
    for name in SESSIONS[grade]:
        S = C.load(os.path.join(HERE, 'sessions', name + '.py'))
        out["sessions"].append(S)
    return out


# ================================================================ لاتک
PRE = r"""% =====================================================================
%  مخزن محتوای «هوشینو» — درس نوآوری و هوش
%  پایه‌ی %(gname)s ابتدایی — جلسات ۱ تا ۴
%  نسخه‌ی کامل: برنامه‌ی اجرای هر جلسه + مخزن اقلام
%  کامپایل با XeLaTeX (فونت: Vazirmatn)
% =====================================================================
\documentclass[11pt,a4paper]{article}
\usepackage[a4paper,top=1.9cm,bottom=1.9cm,left=2cm,right=2cm]{geometry}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage{array}
\usepackage[most]{tcolorbox}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{graphicx}
\usepackage{amssymb}
\usepackage[hidelinks]{hyperref}
\usepackage{xepersian}

\graphicspath{{assets/png/}}

\settextfont[Scale=1.0]{Vazirmatn}
\setlatintextfont[Scale=0.92]{DejaVu Sans}
\setdigitfont[Scale=1.0]{Vazirmatn}

\definecolor{maincol}{HTML}{1F4E79}
\definecolor{morcol}{HTML}{00695C}
\definecolor{mescol}{HTML}{1F4E79}
\definecolor{tamcol}{HTML}{AD1457}
\definecolor{anscol}{HTML}{2E7D32}
\definecolor{stepcol}{HTML}{4527A0}
\definecolor{aicol}{HTML}{6A1B9A}
\definecolor{hintcol}{HTML}{B26A00}
\definecolor{tchcol}{HTML}{546E7A}
\definecolor{lightbg}{HTML}{F4F7FA}
\definecolor{stepbg}{HTML}{F3F1FB}

\newcommand{\software}{هوشینو}
\newcommand{\payeh}{پایه‌ی %(gname)s ابتدایی}
\newcommand{\en}[1]{\lr{#1}}
\newcommand{\sq}[1]{«#1»}
\newcommand{\rtlbullet}{\textcolor{maincol}{\rule[0.25ex]{0.42em}{0.42em}}}
\setlist[itemize]{label=\rtlbullet,leftmargin=1.4em,itemsep=1pt,topsep=2pt}

\newtcolorbox{jalasebox}[2]{%
  breakable, enhanced, colback=white, colframe=maincol!75,
  coltitle=white, colbacktitle=maincol,
  fonttitle=\bfseries, title={جلسه‌ی #1 \quad\textbar\quad #2},
  boxrule=0.6pt, arc=3pt, left=6pt, right=6pt, top=5pt, bottom=5pt,
  before skip=8pt, after skip=8pt}

\newtcolorbox{fasl}[1]{%
  breakable, enhanced, colback=lightbg, colframe=maincol!35,
  boxrule=0.5pt, arc=2pt, left=6pt, right=6pt, top=5pt, bottom=5pt,
  title={#1}, coltitle=maincol, fonttitle=\bfseries, colbacktitle=lightbg}

\newtcolorbox{stepbox}[1]{%
  breakable, enhanced, colback=stepbg, colframe=stepcol!45,
  boxrule=0.5pt, arc=2pt, left=6pt, right=6pt, top=5pt, bottom=5pt,
  title={#1}, coltitle=white, fonttitle=\bfseries\small, colbacktitle=stepcol}

\newcommand{\dastehead}[3]{%
  \smallskip\noindent
  \colorbox{#3!12}{\textcolor{#3}{\textbf{\,#1\,}}}\hspace{0.5em}%
  \textcolor{#3}{\small #2}\par\nopagebreak\vspace{3pt}}

\newcommand{\lbl}[2]{\noindent{\small\textbf{\textcolor{#1}{#2}}}\ }
\newcommand{\tasvir}[1]{%
  \par\nopagebreak\vspace{2pt}%
  \begin{center}\includegraphics[width=0.62\textwidth]{#1}\end{center}%
  \nopagebreak\vspace{1pt}}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[R]{\small مخزن محتوای \software{} \textbar\ \payeh}
\fancyhead[L]{\small جلسات ۱ تا ۴}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\titleformat{\section}{\Large\bfseries\color{maincol}}{\thesection.}{0.5em}{}
\titlespacing*{\section}{0pt}{14pt}{6pt}

\begin{document}

\begin{titlepage}
\centering
\vspace*{3cm}
{\Huge\bfseries\textcolor{maincol}{مخزن محتوای \software}}\\[0.8cm]
{\Huge\bfseries درس «نوآوری و هوش»}\\[1.2cm]
\rule{0.75\textwidth}{1pt}\\[0.8cm]
{\LARGE \payeh}\\[0.5cm]
{\Large جلسات ۱ تا ۴ — نسخه‌ی کامل، ویرایش ۱.۱}\\[1cm]
{\large برنامه‌ی اجرای هر جلسه، گام‌به‌گام \textbar\ مخزن ۳۰ قلمی هر جلسه}\\[1.5cm]
\rule{0.75\textwidth}{1pt}\\[1.5cm]
{\large ساختار سه‌بخشی: آموزش \textbar\ فعالیت تعاملی \textbar\ ارزیابی}\\
\vfill
{\large تاریخ: \makebox[3cm]{\dotfill}}\\[0.4cm]
{\large نام آموزشگاه: \makebox[5cm]{\dotfill}}\\[1cm]
\end{titlepage}

\section{این فایل چه چیزی دارد؟}

این نسخه، دو چیز را کنار هم می‌آورد:

\begin{fasl}{۱ — برنامه‌ی اجرای جلسه}
برای هر جلسه، \textbf{گام‌به‌گام} نوشته شده که روی صفحه‌ی \software{} چه چیزی
نمایش داده می‌شود، از دانش‌آموز چه خواسته می‌شود، پاسخ چطور داوری می‌شود، چه
راهنمایی‌هایی در چه ترتیبی داده می‌شود و معلم کجا باید دخالت کند.
همین گام‌ها عیناً همان چیزی است که به \software{} داده می‌شود.
\end{fasl}

\begin{fasl}{۲ — مخزن اقلام}
سه دسته‌ی همیشگی: \textbf{مرور} جلسه‌ی پیش، \textbf{مثال} آموزشی و
\textbf{تمرین} ارزیابی — هر کدام ۱۰ قلم. این‌ها بیش از نیاز یک جلسه‌اند تا
\software{} بتواند برای هر دانش‌آموز زیرمجموعه‌ای متناسب با عملکرد خودش بردارد.
\end{fasl}

\begin{fasl}{ویرایش ۱.۱ — چه چیزی تغییر کرد؟}
\begin{itemize}
\item \textbf{بخش آموزش فقط نمایشی است.} هیچ ورودی‌ای از دانش‌آموز نمی‌گیرد و به‌جای ۲ تا ۳ گام،
۶ تا ۷ صفحه‌ی آموزشی دارد: تعریف، مثال حل‌شده، کارت ابزار و معرفی شغل — هر صفحه با یک تصویر.
پس در آموزش مجازی یا کلاس دونفره، نیاز به توضیح معلم کم است.
\item \textbf{پیش‌سنجه.} گویه‌ی \en{K1} جلسه‌های پنجره‌ی مشاغل از بخش آموزش بیرون آمد و پیش از
شروع آموزش، جدا از هر دانش‌آموز پرسیده می‌شود (بیرون از ۶۰ دقیقه).
\item \textbf{مرور و مثال، کارت آموزشی‌اند.} اقلام مرور با پاسخشان و اقلام مثال به‌صورت مثال حل‌شده نمایش داده می‌شوند.
\item \textbf{پرسش‌های چندجای‌خالی شکسته شد.} هر پرسشی که چند پاسخ جدا می‌خواست (چند گویه، چند مورد برای دسته‌بندی،
چند جمله) در ارزیابی و مخزن تمرین به چند پرسش جداگانه تبدیل شد؛ پاره‌های یک پرسش شناسه‌ی گروه مشترک دارند.
\end{itemize}
\end{fasl}

\begin{fasl}{دو حالت پاسخ}
هر پرسش یکی از این دو حالت را دارد و \software{} باید بداند با کدام روبه‌روست:

\smallskip\noindent
\textbf{\textcolor{anscol}{پاسخ معین}} — یک پاسخ درست دارد. فهرست
\sq{پذیرفتنی} همه‌ی صورت‌های قابل قبول را می‌آورد و \software{} فقط تطبیق می‌دهد.

\smallskip\noindent
\textbf{\textcolor{aicol}{پاسخ باز}} — پاسخ ثابت ندارد. به‌جای پاسخ،
\sq{معیارها} نوشته شده؛ \software{} بررسی می‌کند کدام معیارها در پاسخ آمده است:
همه‌ی معیارها آمد یعنی \textbf{درست}؛ بخشی آمد یعنی \textbf{نیمه}؛ هیچ‌کدام نیامد یعنی \textbf{نادرست}.
\end{fasl}

\begin{fasl}{راهنمایی سه‌سطحی}
هر پرسش سه راهنمایی دارد و فقط وقتی داده می‌شود که دانش‌آموز گیر کند:
\textbf{۱)} تلنگر، بدون لو دادن چیزی. \textbf{۲)} نشان‌دادن مسیر فکر.
\textbf{۳)} تقریباً پاسخ، تا خودش خط آخر را بردارد.
\software{} هرگز پیش از این سه، پاسخ را نمی‌گوید.
\end{fasl}

\begin{fasl}{یادداشت معلم}
هرجا \textbf{\textcolor{tchcol}{یادداشت معلم}} آمده، متنی است که فقط شما
می‌بینید — به دانش‌آموز نمایش داده نمی‌شود.
\end{fasl}

"""


ASSETS = os.path.join(BANK, 'assets', 'png')
_IMG_CACHE = None


def _has_image(iid):
    """آیا تصویر این شناسه واقعاً ساخته شده است؟

    اقلام مرور هرگز تصویر نگرفتند و بعضی تمرین‌ها هم تصویرپذیر نبودند،
    پس درج کورکورانه‌ی \\tasvir باعث خطای کامپایل می‌شود.
    """
    global _IMG_CACHE
    if _IMG_CACHE is None:
        try:
            _IMG_CACHE = {f[:-4] for f in os.listdir(ASSETS) if f.endswith('.png')}
        except OSError:
            _IMG_CACHE = set()
    return iid in _IMG_CACHE


def esc(s):
    return (s or '').replace('\n', '\\par\\noindent ')


def unit_tex(u, out, show_id=True):
    """یک گام یا قلم مخزن را به لاتک تبدیل می‌کند."""
    sc = u['screen']
    a = u.get('answer') or {}
    am = a.get('mode')

    if show_id:
        out.append('\\lbl{stepcol}{\\en{%s}}\\textbf{%s}\\par\n'
                   % (u['id'], sc.get('title', '')))
    else:
        out.append('\\noindent\\textbf{%s}\\par\n' % sc.get('title', ''))

    out.append('\\noindent{\\small\\textcolor{tchcol}{صفحه:}}\\ %s\\par\n'
               % esc(sc.get('body', '')))
    if sc.get('bullets'):
        out.append('\\begin{itemize}\n')
        for b in sc['bullets']:
            out.append('\\item %s\n' % b)
        out.append('\\end{itemize}\n')
    if sc.get('image') and _has_image(sc['image']):
        out.append('\\tasvir{%s}\n' % sc['image'])

    if u.get('ask'):
        out.append('\\lbl{maincol}{پرسش:}%s\\par\n' % esc(u['ask']))

    if am == 'fixed':
        out.append('\\lbl{anscol}{پاسخ معین:}%s\\par\n' % esc(a.get('value', '')))
        if a.get('accept'):
            out.append('\\noindent{\\small\\textcolor{anscol}{پذیرفتنی:}\\ %s}\\par\n'
                       % '؛ '.join(a['accept']))
    elif am == 'ai':
        out.append('\\lbl{aicol}{پاسخ باز — معیارها:}\\par\n')
        out.append('\\begin{itemize}\n')
        for c in a.get('criteria', []):
            out.append('\\item %s\n' % c)
        out.append('\\end{itemize}\n')
        if a.get('sample'):
            out.append('\\noindent{\\small\\textcolor{aicol}{نمونه‌ی پاسخ خوب:}\\ %s}\\par\n'
                       % esc(a['sample']))

    if u.get('hints'):
        out.append('\\lbl{hintcol}{راهنمایی:}\\par\n')
        out.append('\\begin{enumerate}[leftmargin=1.6em,itemsep=0pt,topsep=1pt]\n')
        for h in u['hints']:
            out.append('\\item %s\n' % h)
        out.append('\\end{enumerate}\n')

    fb = u.get('feedback') or {}
    parts = []
    for k, lab in (('correct', 'درست'), ('partial', 'نیمه'), ('incorrect', 'نادرست')):
        if fb.get(k):
            parts.append('\\textbf{%s:} %s' % (lab, fb[k]))
    if parts:
        out.append('\\noindent{\\small\\textcolor{anscol}{بازخورد —}\\ %s}\\par\n'
                   % '\\ \\textbar\\ '.join(parts))

    for ce in u.get('commonErrors', []):
        out.append('\\noindent{\\small\\textcolor{tamcol}{خطای رایج:}\\ %s '
                   '\\textcolor{tamcol}{\\textbar}\\ \\textcolor{anscol}{پاسخ:}\\ %s}\\par\n'
                   % (ce['error'], ce['reply']))

    if u.get('teacherNote'):
        out.append('\\noindent{\\small\\textcolor{tchcol}{\\textbf{یادداشت معلم:}\\ %s}}\\par\n'
                   % esc(u['teacherNote']))
    out.append('\\vspace{5pt}\n')


PART_LABEL = {'amoozesh': ('آموزش', 'morcol'),
              'taamol': ('فعالیت تعاملی', 'mescol'),
              'arzyabi': ('ارزیابی', 'tamcol')}
IX = {'display': 'نمایش', 'text': 'پاسخ تایپی', 'image': 'بارگذاری عکس',
      'voice': 'ضبط صدا'}
MX = {'class': 'کل کلاس', 'solo': 'فردی', 'pair': 'دونفره'}


def build_tex(grade):
    out = [PRE.replace('%(gname)s', GRADE_NAME[grade])]
    for name in SESSIONS[grade]:
        S = C.load(os.path.join(HERE, 'sessions', name + '.py'))
        n, meta = S['session'], S['meta']
        out.append('\\section{جلسه‌ی %s — %s}\n' % (fa(n), S['title']))
        out.append('\\begin{jalasebox}{%s}{%s}\n' % (fa(n), S['title']))

        # --- شناسنامه‌ی جلسه ---
        out.append('\\dastehead{شناسنامه‌ی جلسه}{هدف، مفاهیم، مأموریت و مواد}{maincol}\n')
        out.append('\\lbl{maincol}{هدف:}%s\\par\n' % meta['goal'])
        out.append('\\lbl{maincol}{مفاهیم:}%s\\par\n' % '، '.join(meta['concepts']))
        out.append('\\lbl{maincol}{مأموریت:}%s \\textbar\\ \\textbf{نشان:} %s\\par\n'
                   % (meta['mission']['name'], meta['mission']['badge']))
        cl = meta['curriculumLink']
        out.append('\\lbl{maincol}{پیوند با برنامه‌ی درسی \\textbar\\ %s:}%s\\par\n'
                   % (cl['area'], cl['text']))
        if meta.get('tool'):
            out.append('\\lbl{tamcol}{ابزار امروز — %s:}%s\\par\n'
                       % (meta['tool']['name'], meta['tool']['note']))
        else:
            out.append('\\lbl{tamcol}{ابزار امروز:}ابزار تازه‌ای باز نمی‌شود.\\par\n')
        if meta.get('toolNote'):
            out.append('\\noindent{\\small %s}\\par\n' % meta['toolNote'])
        out.append('\\lbl{maincol}{مواد:}%s\\par\n' % '، '.join(meta['materials']))
        out.append('\\lbl{maincol}{خروجی:}%s\\par\n' % meta['output'])
        out.append('\\noindent{\\small\\textcolor{tchcol}{\\textbf{نکته‌ی معلم:}\\ %s}}\\par\n'
                   % meta['teacherTip'])
        out.append('\\vspace{4pt}\n')

        # --- پیش‌سنجه ---
        if S.get('preCheck'):
            out.append('\\dastehead{پیش‌سنجه}{پیش از بخش آموزش، جدا برای هر دانش‌آموز — بیرون از ۶۰ دقیقه}{tamcol}\n')
            for s in S['preCheck']:
                out.append('\\begin{stepbox}{پیش‌سنجه \\textbar\\ فردی \\textbar\\ پاسخ تایپی}\n')
                unit_tex(s, out)
                out.append('\\end{stepbox}\n')

        # --- برنامه‌ی اجرا ---
        out.append('\\dastehead{برنامه‌ی اجرای جلسه}{گام‌به‌گام، همان چیزی که به \\software{} داده می‌شود}{stepcol}\n')
        for p in S['parts']:
            lab, colr = PART_LABEL[p['kind']]
            out.append('\\dastehead{%s — %s دقیقه}{}{%s}\n'
                       % (lab, fa(p['minutes']), colr))
            for s in p['steps']:
                title = ('گام %s \\textbar\\ %s دقیقه \\textbar\\ %s \\textbar\\ %s'
                         % (fa(s['seq']), fa(s['minutes']),
                            MX.get(s['mode'], s['mode']),
                            IX.get(s['interaction'], s['interaction'])))
                out.append('\\begin{stepbox}{%s}\n' % title)
                unit_tex(s, out)
                out.append('\\end{stepbox}\n')

        # --- روی دستگاه شخصی ---
        dev = S['device']
        out.append('\\dastehead{روی دستگاه شخصی}{کار فردی، چالش سه‌سطحی و تمرین خانه}{mescol}\n')
        out.append('\\lbl{mescol}{کار:}%s\\par\n' % dev['work'])
        out.append('\\lbl{mescol}{چالش سه‌سطحی:}\\par\n')
        out.append('\\begin{itemize}\n')
        for lv in ('1', '2', '3'):
            out.append('\\item \\textbf{سطح %s:} %s\n' % (fa(lv), dev['challenge'][lv]))
        out.append('\\end{itemize}\n')
        out.append('\\lbl{mescol}{ثبت در پروفایل:}%s\\par\n' % dev['record'])
        out.append('\\lbl{mescol}{تمرین خانه:}%s\\par\\vspace{4pt}\n' % dev['home'])

        # --- مخزن ---
        pool = S['pool']
        if pool['review']:
            out.append('\\dastehead{مخزن — مرور جلسه‌ی پیش}{۱۰ کارت مرور با پاسخ \\textbar\\ ۵ دقیقه‌ی نخست آموزش}{morcol}\n')
            for it in pool['review']:
                unit_tex(it, out)
        else:
            out.append('\\dastehead{مخزن — مرور جلسه‌ی پیش}{ندارد — نخستین جلسه‌ی سال است}{morcol}\n')
        out.append('\\dastehead{مخزن — مثال آموزشی}{۱۰ مثال حل‌شده‌ی نمایشی \\textbar\\ بخش آموزش}{mescol}\n')
        for it in pool['example']:
            unit_tex(it, out)
        ngr = len({it.get('group') or it['id'] for it in pool['practice']})
        out.append('\\dastehead{مخزن — تمرین ارزیابی}{%s پرسش در %s قلم جدا \\textbar\\ بخش ارزیابی}{tamcol}\n'
                   % (fa(ngr), fa(len(pool['practice']))))
        for it in pool['practice']:
            extra = ''
            if it.get('group'):
                extra = ' \\textbar\\ پاره‌ی %s از %s پرسش \\en{%s}' % (
                    fa(it['groupPart']), fa(it['groupSize']), it['group'])
            out.append('\\noindent{\\small\\textcolor{tamcol}{سطح %s \\textbar\\ %s%s}}\\par\n'
                       % (fa(it['level']), it['type'], extra))
            unit_tex(it, out)

        out.append('\\end{jalasebox}\n\n')

    out.append('\\end{document}\n')
    # نمادهایی که قلم Vazirmatn ندارد
    return (''.join(out).replace('←', '\\ensuremath{\\leftarrow}')
            .replace('✓', '\\ensuremath{\\checkmark}'))


if __name__ == '__main__':
    for grade in (5, 6):
        j = build_json(grade)
        p = os.path.join(HERE, 'hooshino_paye%d.json' % grade)
        io.open(p, 'w', encoding='utf-8').write(
            json.dumps(j, ensure_ascii=False, indent=2))
        nst = sum(len(x['steps']) for s in j['sessions'] for x in s['parts'])
        npl = sum(len(v) for s in j['sessions'] for v in s['pool'].values())
        print('grade %d JSON: %d sessions, %d steps, %d pool items, %d KB'
              % (grade, len(j['sessions']), nst, npl, os.path.getsize(p) // 1024))

        tex = build_tex(grade)
        tp = os.path.join(BANK, 'bank_paye%d.tex' % grade)
        io.open(tp, 'w', encoding='utf-8').write(tex)
        print('           TEX: %d KB' % (os.path.getsize(tp) // 1024))


# ================================================================ CSV
def build_csv(grade, path):
    """نمای تخت برای واردکردن سریع و بازبینی در اکسل.

    ستون‌های تودرتو (معیارها، راهنمایی‌ها، بازخورد) با «|» جدا می‌شوند؛
    نسخه‌ی کامل و ساختاریافته در JSON است.
    """
    import csv
    rows = []
    for name in SESSIONS[grade]:
        S = C.load(os.path.join(HERE, 'sessions', name + '.py'))
        n, title = S['session'], S['title']

        def emit(u, where, kind, level='', typ=''):
            a = u.get('answer') or {}
            fb = u.get('feedback') or {}
            sc = u['screen']
            rows.append([
                u['id'], grade, n, title, where, kind, level, typ,
                u.get('mode', ''), u.get('interaction', ''),
                u.get('minutes', ''),
                sc.get('title', ''), sc.get('body', ''),
                ' | '.join(sc.get('bullets') or []),
                u.get('ask') or '',
                a.get('mode', ''),
                a.get('value', ''),
                ' | '.join(a.get('accept') or []),
                ' | '.join(a.get('criteria') or []),
                a.get('sample', ''),
                a.get('aiInstruction', ''),
                ' | '.join(u.get('hints') or []),
                fb.get('correct', ''), fb.get('partial', ''), fb.get('incorrect', ''),
                ' | '.join('%s => %s' % (c['error'], c['reply'])
                           for c in u.get('commonErrors') or []),
                u.get('teacherNote', ''),
                'assets/svg/%s.svg' % sc['image'] if sc.get('image') and _has_image(sc['image']) else '',
                'assets/png/%s.png' % sc['image'] if sc.get('image') and _has_image(sc['image']) else '',
                u.get('group', ''), u.get('groupPart', ''), u.get('itemCode', ''),
            ])

        for s in S.get('preCheck') or []:
            emit(s, 'precheck', s.get('kind', ''))
        for p in S['parts']:
            for s in p['steps']:
                emit(s, p['kind'], s.get('kind', ''))
        for k in ('review', 'example', 'practice'):
            for it in S['pool'][k]:
                emit(it, 'pool', k, it.get('level', ''), it.get('type', ''))

    with io.open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['id', 'grade', 'session', 'session_title', 'where', 'kind',
                    'level', 'type', 'mode', 'interaction', 'minutes',
                    'screen_title', 'screen_body', 'screen_bullets', 'ask',
                    'answer_mode', 'answer_value', 'answer_accept',
                    'answer_criteria', 'answer_sample', 'ai_instruction',
                    'hints', 'fb_correct', 'fb_partial', 'fb_incorrect',
                    'common_errors', 'teacher_note', 'image_svg', 'image_png',
                    'group', 'group_part', 'item_code'])
        w.writerows(rows)
    return len(rows)


for _g in (5, 6):
    _n = build_csv(_g, os.path.join(BANK, 'bank_paye%d.csv' % _g))
    print('grade %d CSV: %d rows' % (_g, _n))
