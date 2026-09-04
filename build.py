#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build.py <template.html> <data_xx.js> <out.html>
テンプレート内の `const DATA = { ... };` を data ファイルの中身で丸ごと置き換える。"""
import sys, io, re

tpl_p, data_p, out_p = sys.argv[1], sys.argv[2], sys.argv[3]
tpl = io.open(tpl_p, encoding="utf-8").read()
data = io.open(data_p, encoding="utf-8").read().strip()

if not data.startswith("const DATA"):
    print("!! data ファイルは `const DATA = {` で始めてください"); sys.exit(1)

i = tpl.find("const DATA")
if i < 0:
    print("!! テンプレートに const DATA が見つかりません"); sys.exit(1)
# const DATA ブロックの終端 = 直後の </script> の手前にある `};`
j = tpl.find("</script>", i)
if j < 0:
    print("!! </script> が見つかりません"); sys.exit(1)
k = tpl.rfind("};", i, j)
if k < 0:
    print("!! DATA の終端 }; が見つかりません"); sys.exit(1)

out = tpl[:i] + data.rstrip() + "\n" + tpl[k + 2:]
io.open(out_p, "w", encoding="utf-8").write(out)

n = len(re.findall(r"\{\s*id:\"S\d+\"", data))
print("built: %s  (slides in DATA: %d, %d bytes)" % (out_p, n, len(out)))
