#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_json.py <tesla.json>
ナレーションJSONを、動画自動生成が通る形式かどうか検査する。
基準は 2026-09-01-tesla.json の構造。"""
import sys, io, json, re

d = json.load(io.open(sys.argv[1], encoding="utf-8"))
errs, warns = [], []

if set(d.keys()) != {"meta", "slides"}:
    errs.append("最上位は meta と slides の2つだけです（現在: %s）" % ", ".join(sorted(d.keys())))

m = d.get("meta", {})
for k in ("project", "title", "cover", "runtime"):
    v = m.get(k)
    if not isinstance(v, dict):
        errs.append("meta.%s がありません。{\"ja\":…, \"en\":…} の形で入れてください" % k); continue
    for lang in ("ja", "en"):
        if not (v.get(lang) or "").strip():
            errs.append("meta.%s.%s が空です" % (k, lang))
if not (m.get("date") or "").strip():
    errs.append("meta.date が空です")

ids = [s.get("id") for s in d.get("slides", [])]
cov = m.get("cover", {})
for lang in ("ja", "en"):
    c = cov.get(lang)
    if c and c not in ids:
        errs.append("meta.cover.%s が指すスライド %s が存在しません" % (lang, c))

for s in d.get("slides", []):
    sid = s.get("id", "?")
    extra = set(s.keys()) - {"id", "vo", "only"}
    if extra:
        errs.append("%s: 余分なキー %s（id / vo / only だけにしてください）" % (sid, ", ".join(sorted(extra))))
    vo = s.get("vo", {})
    ja, en = (vo.get("ja") or ""), (vo.get("en") or "")
    if not ja.strip():
        errs.append("%s: vo.ja が空です" % sid)
    if "\n" in ja or "\n" in en:
        errs.append("%s: vo に改行が入っています。1行に連結してください" % sid)
    if s.get("only") == "ja":
        if en.strip():
            warns.append("%s: only=ja なのに vo.en に本文があります" % sid)
        continue
    if not en.strip():
        errs.append("%s: vo.en が空です（only:\"ja\" もありません）" % sid)

n_en = len([s for s in d.get("slides", []) if s.get("only") != "ja"])
print("slides: ja=%d en=%d  cover=%s/%s" % (len(ids), n_en, cov.get("ja"), cov.get("en")))
print("-" * 50)
for e in errs: print("ERROR  " + e)
for w in warns: print("WARN   " + w)
if not errs and not warns:
    print("OK  自動生成が通る形式です")
print("-" * 50)
sys.exit(1 if errs else 0)
