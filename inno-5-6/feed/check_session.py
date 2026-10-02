# -*- coding: utf-8 -*-
"""بررسی یک فایل جلسه در برابر قرارداد hooshino-session/1.1.

    python3 check_session.py sessions/G5_S01.py
"""
import importlib.util, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))

INTERACTIONS = {'display', 'text', 'image', 'voice'}
MODES = {'class', 'solo', 'pair'}
PART_KINDS = ['amoozesh', 'taamol', 'arzyabi']
STEP_KINDS = {'review', 'teach', 'example', 'activity', 'practice',
              'reflect', 'mission', 'wrap', 'precheck'}
SCHEMA = 'hooshino-session/1.1'
ANSWER_MODES = {'fixed', 'ai', 'none'}
PRACTICE_TYPES = {'چندگزینه‌ای', 'کوتاه‌پاسخ', 'بله یا خیر', 'بازنویسی',
                  'دسته‌بندی', 'عملی', 'استدلالی', 'طراحی', 'داوری',
                  'محاسبه', 'تطبیق', 'پیش‌بینی'}

# مواد مجاز (جلسات ۳۱ و ۳۲ چاپگر هم دارند، ولی اینجا ۱ تا ۴ است)
MAVAD_OK = {'کاغذ و مداد و مدادرنگی', 'کاغذ و مداد', 'تبلت شخصی با هوشینو',
            'هدفون و میکروفون', 'نمایشگر کلاسی'}

LATIN_DIGIT = re.compile(r'[0-9]')
PERSIAN = re.compile(u'[؀-ۿ]')

# ترکیب‌هایی که نیم‌فاصله می‌خواهند — با مرز واژه، وگرنه «سومی » هم گیر می‌افتد
ZWNJ_TRAPS = [
    re.compile(u'(?:^|\\s)(?:می|نمی)\\s'),
    re.compile(u'\\s(?:ها|های|هایی|تر|ترین)(?:\\s|$)'),
]

FORBIDDEN = [
    (u'پارسال', u'ارجاع به پایه‌ی قبل'),
    (u'سال گذشته یاد', u'ارجاع به پایه‌ی قبل'),
    (u'نرم‌افزار هوشمند کلاس', u'جای‌نگهدار قدیمی نام نرم‌افزار'),
]


def load(path):
    spec = importlib.util.spec_from_file_location('sess', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.SESSION


def strings(obj, acc=None, skip=('teacherNote', 'key', 'aiInstruction')):
    """همه‌ی رشته‌های دانش‌آموزبین (یادداشت معلم و کلید را رد می‌کند)."""
    if acc is None:
        acc = []
    if isinstance(obj, str):
        acc.append(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in skip:
                continue
            strings(v, acc, skip)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            strings(v, acc, skip)
    return acc


def check_unit(u, where, errs, warns, need_hints=True):
    """بررسی یک گام یا یک قلم مخزن."""
    for f in ('id', 'screen', 'answer'):
        if f not in u:
            errs.append('%s: missing field %r' % (where, f))
            return
    sc = u['screen']
    if not sc.get('title'):
        errs.append('%s: screen.title missing' % where)
    if not sc.get('body'):
        errs.append('%s: screen.body missing' % where)
    else:
        wc = len(sc['body'].split())
        if wc > 55:
            warns.append('%s: screen.body %d words (>55)' % (where, wc))
        if re.search(u'معلم (می|نشان|می‌گوید)', sc['body']):
            errs.append('%s: screen.body is teacher-voice, must address the student' % where)
    if len(sc.get('bullets') or []) > 4:
        warns.append('%s: more than 4 bullets' % where)

    it = u.get('interaction')
    if it not in INTERACTIONS:
        errs.append('%s: bad interaction %r' % (where, it))
    md = u.get('mode')
    if md not in MODES:
        errs.append('%s: bad mode %r' % (where, md))

    a = u['answer']
    am = a.get('mode')
    if am not in ANSWER_MODES:
        errs.append('%s: bad answer.mode %r' % (where, am))
    elif am == 'fixed':
        if not a.get('value'):
            errs.append('%s: fixed answer needs value' % where)
        if not a.get('accept'):
            errs.append('%s: fixed answer needs accept[]' % where)
        if not a.get('aiInstruction'):
            errs.append('%s: fixed answer needs aiInstruction' % where)
    elif am == 'ai':
        if not a.get('criteria'):
            errs.append('%s: ai answer needs criteria[]' % where)
        elif len(a['criteria']) < 1:
            errs.append('%s: ai answer needs at least one criterion' % where)
        if not a.get('aiInstruction'):
            errs.append('%s: ai answer needs aiInstruction' % where)
        if not a.get('sample'):
            warns.append('%s: ai answer has no sample' % where)
        for c in a.get('criteria', []):
            if len(c.split()) < 3:
                warns.append('%s: criterion too vague: %r' % (where, c))

    if am == 'none':
        if it != 'display':
            errs.append('%s: answer.mode none but interaction is %r' % (where, it))
        if u.get('hints'):
            errs.append('%s: display step must have empty hints' % where)
        if u.get('ask') is not None:
            errs.append('%s: display step must have ask=None' % where)
    else:
        if not u.get('ask'):
            errs.append('%s: needs ask' % where)
        if need_hints:
            h = u.get('hints') or []
            if len(h) != 3:
                errs.append('%s: needs exactly 3 hints, got %d' % (where, len(h)))
        fb = u.get('feedback') or {}
        for k in ('correct', 'incorrect'):
            if not fb.get(k):
                errs.append('%s: feedback.%s missing' % (where, k))
        # «نیمه» برای پاسخ باز همیشه لازم است؛ برای پاسخ معین فقط وقتی
        # پاسخ چندتکه‌ای است (چندگزینه‌ای و بله/خیر حالت نیمه ندارند).
        if am == 'ai' and not fb.get('partial'):
            errs.append('%s: feedback.partial missing (required for ai answers)' % where)

    for ce in u.get('commonErrors', []):
        if not ce.get('error') or not ce.get('reply'):
            errs.append('%s: commonErrors entry incomplete' % where)


def check(path):
    errs, warns = [], []
    S = load(path)

    if S.get('schema') != SCHEMA:
        errs.append('bad schema tag (want %s)' % SCHEMA)
    g, n = S.get('grade'), S.get('session')
    if g not in (5, 6):
        errs.append('bad grade %r' % g)
    if n not in (1, 2, 3, 4):
        errs.append('bad session %r' % n)
    if not S.get('title'):
        errs.append('missing title')

    meta = S.get('meta') or {}
    for f in ('goal', 'concepts', 'mission', 'curriculumLink', 'materials',
              'output', 'teacherTip', 'minutes'):
        if not meta.get(f):
            errs.append('meta.%s missing' % f)
    if meta.get('minutes') != 60:
        errs.append('meta.minutes must be 60')
    for m in meta.get('materials', []):
        if m not in MAVAD_OK:
            errs.append('material not in whitelist: %r' % m)

    parts = S.get('parts') or []
    if [p.get('kind') for p in parts] != PART_KINDS:
        errs.append('parts must be exactly %s in order' % PART_KINDS)
    total = 0
    for p in parts:
        mins = p.get('minutes') or 0
        total += mins
        steps = p.get('steps') or []
        if not steps:
            errs.append('part %s has no steps' % p.get('kind'))
        ssum = sum(s.get('minutes') or 0 for s in steps)
        if ssum != mins:
            errs.append('part %s: step minutes %d != part minutes %d'
                        % (p.get('kind'), ssum, mins))
        for i, s in enumerate(steps, 1):
            where = '%s/%s' % (p.get('kind'), s.get('id', '?'))
            if s.get('seq') != i:
                errs.append('%s: seq should be %d' % (where, i))
            if s.get('kind') not in STEP_KINDS:
                errs.append('%s: bad step kind %r' % (where, s.get('kind')))
            check_unit(s, where, errs, warns)
            # بخش آموزش فقط نمایشی است: هیچ ورودی‌ای از دانش‌آموز نمی‌گیرد
            if p.get('kind') == 'amoozesh' and s.get('interaction') != 'display':
                errs.append('%s: amoozesh steps must be display-only (no student input)' % where)
            if p.get('kind') == 'amoozesh' and not (s.get('screen') or {}).get('image'):
                warns.append('%s: amoozesh step has no image' % where)
        # مرور ۵ دقیقه‌ای در جلسات ۲ به بعد
        if p.get('kind') == 'amoozesh' and n and n > 1:
            s0 = steps[0] if steps else {}
            if s0.get('kind') != 'review':
                errs.append('session %d: first amoozesh step must be a review' % n)
            elif s0.get('minutes') != 5:
                errs.append('session %d: review step must be 5 minutes' % n)
    if total != 60:
        errs.append('parts total %d minutes, must be 60' % total)

    # --- پیش‌سنجه: گام‌های فردی پیش از بخش آموزش، بیرون از ۶۰ دقیقه
    pre = S.get('preCheck')
    if pre is None:
        errs.append('preCheck missing (use [] when there is none)')
    for i, s in enumerate(pre or [], 1):
        where = 'preCheck/%s' % s.get('id', '?')
        check_unit(s, where, errs, warns)
        if s.get('kind') != 'precheck':
            errs.append('%s: kind must be precheck' % where)
        if s.get('minutes') != 0:
            errs.append('%s: precheck minutes must be 0 (outside the 60)' % where)
        if s.get('seq') != i:
            errs.append('%s: seq should be %d' % (where, i))

    pool = S.get('pool') or {}
    exp_review = 0 if n == 1 else 10
    for kind, want in (('review', exp_review), ('example', 10)):
        got = len(pool.get(kind) or [])
        if got != want:
            errs.append('pool.%s has %d items, want %d' % (kind, got, want))
    # تمرین‌ها: ۱۰ «گروه»؛ پرسشی که چند جای خالی داشت به چند قلم جدا شکسته شده
    groups = {}
    for it in pool.get('practice') or []:
        groups.setdefault(it.get('group') or it.get('id'), []).append(it)
    if len(groups) != 10:
        errs.append('pool.practice has %d groups, want 10' % len(groups))
    for gid, items in groups.items():
        if len({it.get('level') for it in items}) != 1:
            errs.append('practice group %s: mixed levels' % gid)
        if len(items) > 1:
            parts_ = sorted(it.get('groupPart') for it in items)
            if parts_ != list(range(1, len(items) + 1)):
                errs.append('practice group %s: bad groupPart numbering' % gid)
            for it in items:
                if it.get('groupSize') != len(items):
                    errs.append('practice %s: groupSize should be %d' % (it.get('id'), len(items)))
    for kind in ('review', 'example'):
        for it in pool.get(kind) or []:
            if it.get('interaction') != 'display':
                errs.append('pool.%s/%s: teaching items must be display-only' % (kind, it.get('id')))
    seqs = [it.get('seq') for it in pool.get('practice') or []]
    if seqs != list(range(1, len(seqs) + 1)):
        errs.append('pool.practice seq must run 1..%d' % len(seqs))
    for kind in ('review', 'example', 'practice'):
        for it in pool.get(kind) or []:
            where = 'pool.%s/%s' % (kind, it.get('id', '?'))
            check_unit(it, where, errs, warns,
                       need_hints=(it.get('answer', {}).get('mode') != 'none'))
            if not re.match(r'^G[56]-S0[1-4]-[REP]\d\d(-\d)?$', it.get('id', '')):
                errs.append('%s: bad id format' % where)
            if not it.get('key'):
                warns.append('%s: no teacher key' % where)
    lv = [items[0].get('level') for items in groups.values()]
    if sorted(lv) != [1, 1, 1, 2, 2, 2, 2, 3, 3, 3]:
        errs.append('practice levels must be 3x1, 4x2, 3x3 — got %r' % sorted(lv))
    for it in pool.get('practice') or []:
        if it.get('type') not in PRACTICE_TYPES:
            errs.append('practice %s: bad type %r' % (it.get('id'), it.get('type')))

    dev = S.get('device') or {}
    for f in ('work', 'challenge', 'record', 'home'):
        if not dev.get(f):
            errs.append('device.%s missing' % f)
    if set((dev.get('challenge') or {}).keys()) != {'1', '2', '3'}:
        errs.append('device.challenge needs levels 1,2,3')

    # --- متن ---
    for s in strings(S):
        if PERSIAN.search(s) and LATIN_DIGIT.search(s):
            warns.append('latin digit in persian text: %s' % s[:60])
        for rx in ZWNJ_TRAPS:
            m = rx.search(s)
            if m:
                warns.append('possible missing ZWNJ (%s): %s'
                             % (m.group(0).strip(), s[:60]))
                break
    alls = strings(S, skip=())
    for frag, why in FORBIDDEN:
        for s in alls:
            if frag in s:
                errs.append('forbidden (%s): %s' % (why, s[:60]))
                break

    return S, errs, warns


if __name__ == '__main__':
    p = sys.argv[1]
    S, errs, warns = check(p)
    nsteps = sum(len(x.get('steps') or []) for x in S.get('parts') or [])
    npool = sum(len(v) for v in (S.get('pool') or {}).values())
    print('%s — grade %s session %s | %d steps, %d pool items'
          % (os.path.basename(p), S.get('grade'), S.get('session'), nsteps, npool))
    for w in warns:
        print('WARN  ' + w)
    for e in errs:
        print('ERROR ' + e)
    print('OK' if not errs else 'FAILED (%d errors)' % len(errs))
    sys.exit(1 if errs else 0)
