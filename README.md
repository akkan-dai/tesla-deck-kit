# tesla-deck-kit

Kenのテスラ戦略ラボ（@tesla_modelY）の動画制作ツール一式。

新しいスレッドで作業を始めるとき、これまでは7ファイルを毎回アップロードしていました。
このリポジトリを置いておくと、bashの1コマンドで環境が揃います。

## 新しいスレッドでの立ち上げ

```
curl -sL https://raw.githubusercontent.com/akkan-dai/tesla-deck-kit/main/setup.sh | bash
```

`/home/claude/w/` にテンプレートとツールが展開されます。
`raw.githubusercontent.com` はbashの許可ドメインなので、追加の設定は不要です。

## 中身

| ファイル | 役割 |
|---|---|
| `_TEMPLATE_deck_ja.html` | 日本語デッキのテンプレート |
| `_TEMPLATE_deck_en.html` | 英語デッキのテンプレート |
| `count.py` | 台本の字数と尺を計測（日本語335字/分、英語152wpm） |
| `build.py` | DATAをテンプレートに流し込む |
| `inject.py` | 画像をbase64で埋め込む |
| `verify.py` | undefined・はみ出し・英語デッキ内の日本語を検出 |
| `overlap.py` | 出典×凡例、本文×出典の重なりを検出（verify.pyが拾えない崩れ用） |
| `png.py` | 全スライドを1920×1080のPNGへ書き出し |
| `validate_json.py` | ナレーションJSONの検査（cover の有無、vo.ja / vo.en の埋まり） |
| `HANDOFF.md` | 引き継ぎプロンプト。新スレッドの1通目に貼る |
| `data_test.js` | 全30型の見本データ。型の書き方はここを見る |

## 使い方

```
python3 build.py _TEMPLATE_deck_ja.html data_jaMMDD.js deckMMDD.html
python3 inject.py deckMMDD.html /home/claude/img
python3 verify.py deckMMDD.html
python3 overlap.py deckMMDD.html
python3 png.py deckMMDD.html slides
```

## 型の一覧

すべてDATA駆動です。テンプレート側にベタ書きの内容はありません。

`hook` `specs` `specs2` `units` `ratio` `unitbig` `city` `ownbuy` `table`
`flow` `chain` `ladder` `flow2` `pricechart` `subtract` `timeline`
`three` `rows` `ps` `split` `twocol` `statement` `quote` `chart` `photo`
`concl2` `cta` `concl`

各型のDATAの書き方は `data_test.js` に1枚ずつ入っています。
型を追加・変更したら `data_test.js` にも追記し、テストデッキで確認してください。

```
python3 build.py _TEMPLATE_deck_ja.html data_test.js deck_test.html
python3 inject.py deck_test.html /home/claude/img
python3 verify.py deck_test.html && python3 overlap.py deck_test.html
python3 png.py deck_test.html slides_test
```

## 更新の記録

- 2026-09-05：全SVG図とベタ書きHTML型をDATA駆動へ書き換え。`rows` を最大7行まで対応。`overlap.py` を追加。テンプレートの日英差分は `LANG` と出典ラベルの2箇所だけになりました。
