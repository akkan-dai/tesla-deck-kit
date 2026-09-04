#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""台本MDの字数と尺を出す。日本語=335字/分（350/320も併記）、英語=152wpm。"""
import sys, re, io

def is_en(t):
    j = len(re.findall(r"[\u3040-\u30ff\u4e00-\u9fff]", t))
    return j < len(t) * 0.05

def mmss(sec):
    return "%d:%02d" % (int(sec) // 60, int(sec) % 60)

def main(path):
    raw = io.open(path, encoding="utf-8").read()
    lines = raw.split("\n")
    blocks, cur, curid = [], [], None
    for ln in lines:
        m = re.match(r"^\s*\[?(S\d+)\]?\s", ln) or re.match(r"^#+\s*\[?(S\d+)\]?", ln)
        if m:
            if curid: blocks.append((curid, "\n".join(cur)))
            curid, cur = m.group(1), []
            continue
        if curid is not None: cur.append(ln)
    if curid: blocks.append((curid, "\n".join(cur)))

    def clean(t):
        t = re.sub(r"^\s*[#>|\-*].*$", "", t, flags=re.M)   # 見出し・表・箇条書き行を除外
        t = re.sub(r"`[^`]*`", "", t)
        return t

    en = is_en(raw)
    total = 0
    print("%-5s %8s %8s" % ("ID", "count", "sec@335" if not en else "sec@152wpm"))
    print("-" * 26)
    for bid, body in blocks:
        b = clean(body)
        if en:
            n = len(re.findall(r"[A-Za-z0-9'’\-]+", b))
            sec = n / 152.0 * 60
        else:
            n = len(re.sub(r"\s", "", re.sub(r"[A-Za-z0-9\.,\!\?:;\(\)\[\]/%$–—\"'’]", "", b)))
            n = len(re.sub(r"\s", "", b))
            sec = n / 335.0 * 60
        total += n
        print("%-5s %8d %8s" % (bid, n, mmss(sec)))
    print("-" * 26)
    if en:
        print("合計 %d語 / %s (152wpm)" % (total, mmss(total / 152.0 * 60)))
    else:
        print("合計 %d字" % total)
        for r in (320, 335, 350):
            print("  %d字/分 -> %s" % (r, mmss(total / float(r) * 60)))

if __name__ == "__main__":
    main(sys.argv[1])
