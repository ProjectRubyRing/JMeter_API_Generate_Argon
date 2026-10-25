# -*- coding: utf-8 -*-
"""
Sheet 1: 目次・概要 (Table of Contents & Architecture Overview)
"""
from generate_guide_table_helpers import *

def build_sheet1(ws):
    ws.title = "目次・概要"
    ws.views.sheetView[0].showGridLines = True
    ws.sheet_properties.tabColor = "1F1F1F"

    # Set column widths
    col_widths = {
        "A": 8.0,
        "B": 24.0,
        "C": 38.0,
        "D": 28.0,
        "E": 36.0,
        "F": 26.0
    }
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width

    # Header Banner
    add_header_banner(
        ws,
        "JMeter シナリオ構築 実践マニュアル（自動生成JMX カスタマイズ完全ガイド）",
        "対象: Apache JMeter 5.6.3 | 自動生成された JMX (api_test.jmx) をベースに実運用シナリオへ組み上げるための完全ガイド"
    )

    r = 4
    # Section 1
    r = add_section(ws, r, "1. 本マニュアルの位置づけと自動生成JMXの活用方針")
    callout_text = (
        "【自動生成JMXと実運用シナリオの役割分担】\n"
        "・本ツール（jmeter_api_tool）が自動生成する JMX（api_test.jmx）は、Excel / CSV / OpenAPI 定義から各 API の呼出設定、"
        "共通変数、HTTPヘッダ、Cookie管理、基本アサーション、結果出力リスナーを網羅した完全な土台を提供します。\n"
        "・しかし、実際の性能試験・業務シナリオテストでは、「ログイン応答のトークンを引き継ぐ」「CSVからテストデータを順次投入する」"
        "「特定処理だけを何回も反復する」「ランダムIDでDB排他ロックを回避する」といった業務フロー特有の動的制御（シナリオ化）が必要です。\n"
        "・本書は、自動生成された JMX をベースにして、JMeter GUI（画面）から最小限の作業で確実に業務シナリオを組み上げるための完全手順を詳しく解説します。\n"
        "・なお、自動生成された api_test.jmx には、本マニュアルで解説する主要部品（CSVデータセット設定、乱数生成、JSON抽出、Debug Sampler 等）が"
        "あらかじめ「[任意]」要素として組み込まれています。既存部品のパラメータ修正、または新規部品の追加のどちらでも柔軟に対応できます。"
    )
    r = add_callout(ws, r, callout_text)

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 2
    r = add_section(ws, r, "2. 4大シナリオパターンと対応シート案内")
    headers_s2 = ["No", "シナリオパターン", "主な業務ユースケース", "使用する主要なJMeter部品", "適用先・反映箇所", "詳細参照シート"]
    r = add_table_header(ws, r, headers_s2)

    patterns = [
        (
            "①",
            "API間の依存関係\n（値の動的受け渡し・相関）",
            "・ログインAPIで認証トークンを取得し、後続の全業務APIヘッダへ設定\n"
            "・前APIで新規作成・採番されたID（注文番号等）を後続の詳細・更新APIへ設定\n"
            "・一覧取得APIの検索結果から特定のアイテムIDを抽出して次APIへ引き渡す",
            "JSON Extractor（JSON抽出）\n"
            "Regular Expression Extractor（正規表現抽出）\n"
            "Boundary Extractor（境界抽出）",
            "後続サンプラーの:\n"
            "・URLパス (${ID})\n"
            "・クエリ (${PARAM})\n"
            "・HTTPヘッダ (${TOKEN})\n"
            "・リクエスト本文 (${BODY})",
            "「①API依存関係・値受け渡し」シート"
        ),
        (
            "②",
            "POST入力データの\nCSV順次読込・利用\n（データ駆動テスト・DDT）",
            "・大量の異なる会員アカウント（ID/PW）による一斉ログイン試験\n"
            "・CSVファイルに用意した複数件の登録データ（氏名・住所・金額）を1行ずつPOST\n"
            "・APIごとに異なるペイロードパターンを外出しCSVから流し込むデータ駆動試験",
            "CSV Data Set Config（CSVデータセット設定）\n"
            "HTTP Request Sampler (Body Data タブ)\n"
            "HTTP Header Manager (Content-Type)",
            "サンプラーの:\n"
            "・Body Data 欄（JSON/XML本文）\n"
            "・Parameters 欄（Formデータ）\n"
            "・CSVファイル配置 (data/*.csv)",
            "「②CSVデータ順次POST利用」シート"
        ),
        (
            "③",
            "数値IDの\nランダム動的生成\n（キャッシュ・排他回避）",
            "・DBの同一レコード更新競合（デッドロック・ロック待ち）を回避するための分散アクセス\n"
            "・APIキャッシュ（RedisやCDN）のヒットを回避し、バックエンドDBへの実負荷を検証\n"
            "・1000〜9999など特定範囲の注文ID、ユーザID、商品コードを毎回ランダムに生成・送信",
            "Random Variable（ランダム変数 設定エレメント）\n"
            "組み込み関数: ${__Random(最小,最大,変数名)}\n"
            "ユニーク値関数: ${__UUID()}, ${__RandomString()}",
            "サンプラーの:\n"
            "・URLパス (${RND_ID})\n"
            "・クエリパラメータ\n"
            "・リクエスト本文内の数値フィールド",
            "「③数値IDのランダム生成」シート"
        ),
        (
            "④",
            "特定APIのみの\n複数回ループ実行\n（反復制御・ポーリング）",
            "・「1回ログイン → 商品検索・詳細閲覧を5回反復 → 1回ログアウト」といった典型シナリオ\n"
            "・非同期処理（バッチ処理・帳票出力）の完了ステータスを一定間隔で最大N回ポーリング\n"
            "・1回のシナリオ実行の中で、特定APIだけを意図的に重み付けで高頻度に呼び出す負荷モデル",
            "Loop Controller（ループコントローラ）\n"
            "While Controller（条件付きループ）\n"
            "Flow Control Action（タイマ・思考時間）\n"
            "組み込みカウンタ: ${__jm__コントローラ名__idx}",
            "Thread Group 配下の:\n"
            "・ループ対象サンプラーの階層移動\n"
            "・ループ内タイマ（待機時間）\n"
            "・ページング変数 (${PAGE})",
            "「④特定APIのループ実行」シート"
        ),
        (
            "複合",
            "4大パターンの統合と\nシナリオ設計原則\n（トラブルシューティング）",
            "・①〜④の全パターンを組み合わせた完全なエンドツーエンド業務シナリオのツリー構造設計\n"
            "・JMeter特有の親子関係（スコープ）による変数の有効範囲と予期せぬ不具合の完全防止\n"
            "・CLI実行時（-JTHREADS, -JLOOPS）の総リクエスト数計算式と実務トラブル10選の対処法",
            "Test Plan (全体設定)\n"
            "Thread Group (スレッドグループ)\n"
            "Debug Sampler (デバッグ部品)\n"
            "View Results Tree (結果ツリー)",
            "JMX全体の階層構造設計\n"
            "変数のライフサイクル管理\n"
            "トラブルシューティング10選",
            "「複合シナリオ・設計原則」シート"
        )
    ]

    for idx, row_data in enumerate(patterns):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["center", "left", "left", "left", "left", "center"],
            bold_cols=[1, 2, 6]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 3
    r = add_section(ws, r, "3. JMeter GUI 画面操作とシナリオ設計の5大原則")
    headers_s3 = ["No", "設計原則・操作ルール", "JMeter GUI での具体的アクション", "動作仕様・採用理由", "設定不備時のトラブル・リスク"]
    r = add_table_header(ws, r, headers_s3)

    principles = [
        (
            "1",
            "要素の追加方法と\nツリーの親子関係",
            "追加元となる親要素（Thread Group や対象サンプラー）を右クリック → [追加 (Add)] → 各カテゴリから要素を選択して配置します。",
            "JMeter はツリーの親子関係（スコープ）によって動作範囲を厳密に制御します。親要素の直下にある設定エレメントは配下の全サンプラーに継承されます。",
            "無関係な上位階層に追加すると、シナリオ内の全サンプラーに不要な設定が適用され、誤動作や意図しないヘッダ送信の原因となります。"
        ),
        (
            "2",
            "スコープ（有効範囲）の\n厳格な管理",
            "特定サンプラーに限定したい後処理（JSON抽出等）やヘッダは、必ずそのサンプラーの【子要素】として配置（サンプラーを右クリックして追加）します。",
            "サンプラーと同階層に置くと、その階層配下にある【すべてのサンプラー】に対して毎回実行されてしまい、負荷計測のオーバーヘッドや抽出失敗エラーを招きます。",
            "前処理や後処理が予期せぬAPIでも実行され、変数上書きや不要なエラーログが多発して正しい性能計測ができなくなります。"
        ),
        (
            "3",
            "変数参照の構文規則\n${変数名}",
            "JMeter 内で定義・抽出された変数は、画面上の任意の入力欄（URL、ヘッダ、本文、クエリ等）で ${変数名} と記述して呼び出します。",
            "JMeter はリクエスト送信直前に ${...} を見つけると、内部の変数マップ（JMeterVariables）から値を検索して文字列置換を行います。",
            "変数名の大文字・小文字不一致やスペルミスがあると置換されず、URLや本文にリテラル文字「${変数名}」がそのまま送信されて 400 Bad Request 等になります。"
        ),
        (
            "4",
            "インデント階層の\n視覚的確認",
            "Loop Controller や If Controller などの制御要素にサンプラーを含める際は、ドラッグ＆ドロップでその要素の【右下（子階層）】にインデントさせます。",
            "JMeter GUI では、コントローラの下に1段右にインデント（字下げ）されている要素だけが、そのコントローラの制御対象（子要素）として認識されます。",
            "単にコントローラの下に並んでいるだけ（同階層）だと、コントローラの外側に配置されたとみなされ、ループが1回しか実行されない原因になります。"
        ),
        (
            "5",
            "デバッグ部品による\n単体動作検証",
            "シナリオ構築時は、スレッドグループ内に [Debug Sampler (変数確認)] と [View Results Tree (結果ツリー)] を必ず配置し、1スレッド・1ループで動作確認します。",
            "Debug Sampler のレスポンスデータを見ることで、抽出された変数名と現在格納されている値（AUTH_TOKEN等）を画面上で視覚的に100%確認できます。",
            "CLI での多重負荷試験をいきなり実行すると、相関値の受け渡し失敗やCSVフォーマットエラーに気づかず、大量のエラーレスポンスを生成してしまいます。"
        )
    ]

    for idx, row_data in enumerate(principles):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["center", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    # Freeze panes below table header of Section 2
    ws.freeze_panes = "A5"
    return ws

print("Sheet 1 builder compiled.")
