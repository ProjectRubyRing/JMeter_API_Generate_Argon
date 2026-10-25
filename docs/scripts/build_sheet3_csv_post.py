# -*- coding: utf-8 -*-
"""
Sheet 3: ②CSVデータ順次POST利用 (CSV Sequential POST Data Feeding)
"""
from generate_guide_table_helpers import *

def build_sheet3(ws):
    ws.title = "②CSVデータ順次POST利用"
    ws.views.sheetView[0].showGridLines = True
    ws.sheet_properties.tabColor = "4D4D4D"

    col_widths = {
        "A": 16.0,
        "B": 28.0,
        "C": 32.0,
        "D": 22.0,
        "E": 44.0,
        "F": 34.0
    }
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width

    add_header_banner(
        ws,
        "② POST入力データのCSV順次読込・利用手順（データ駆動型テスト・DDT）",
        "外部 CSV ファイルからテストデータを 1 行ずつ読み込み、POST / PUT / PATCH のリクエスト本文へ動的に設定する完全手順"
    )

    r = 4
    # Section 1
    r = add_section(ws, r, "1. CSV データ駆動テストの仕組みと自動生成JMXでの構成")
    callout_text = (
        "【データ駆動テスト（Data-Driven Testing: DDT）のアーキテクチャ】\n"
        "・JMeter の「CSV Data Set Config」を使うと、外部 CSV ファイルに用意した大量の行データ（ユーザアカウント、注文商品、送金額など）を、"
        "各仮想ユーザー（スレッド）および各反復（ループ）ごとに先頭から 1 行ずつ順次読み込んで変数化できます。\n"
        "・1 行に含まれる各列のカンマ区切り値が、指定した「変数名」（例: USER_ID, PASSWORD, AMOUNT）に格納され、POST サンプラーのリクエスト本文で "
        "${USER_ID} のように参照されます。\n"
        "・これにより、全仮想ユーザーが同じ固定データでリクエストする不自然なテストを回避し、何千人もの異なるユーザーが異なるデータで一斉アクセスする"
        "実運用に極めて近い負荷をシミュレートできます。\n\n"
        "【自動生成JMX（api_test.jmx）での初期状態】\n"
        "・本ツールで生成された api_test.jmx では、Thread Group 配下に「[任意] CSVデータ読込 (CSV Data Set Config)」が最初から組み込まれています。\n"
        "・また、同梱の output/data/testdata.csv（USER_ID,PASSWORD,KEYWORD 等）がすでに生成されています。\n"
        "・既存の「[任意] CSVデータ読込」のファイルパスや変数名を業務要件に合わせて修正するだけで、即座にCSV駆動テストを開始できます。"
    )
    r = add_callout(ws, r, callout_text)

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 2
    r = add_section(ws, r, "2. CSV ファイルの設計と作成規約")
    headers_csv = ["項目", "設計規約・要件", "具体例", "詳細解説と推奨理由", "トラブル防止策"]
    r = add_table_header(ws, r, headers_csv)

    csv_rules = [
        (
            "ファイル配置場所",
            "JMX からの相対パス",
            "data/testdata.csv\ndata/user_orders.csv",
            "JMX ファイルが置かれているディレクトリを基準とした相対パス（例: data/*.csv）に配置します。",
            "絶対パス（C:\\...）を記述すると、Linux サーバ等の CLI 実行環境へ移行した際にファイルが見つからずエラーになります。"
        ),
        (
            "文字コード (Encoding)",
            "UTF-8 (BOM なし)",
            "UTF-8",
            "日本語などのマルチバイト文字を含む場合は、必ず UTF-8（BOM なし）で保存します。",
            "Excel から保存する際は「CSV UTF-8 (コンマ区切り) (*.csv)」を選択してください。Shift-JIS だと文字化けします。"
        ),
        (
            "ヘッダ行の有無",
            "先頭行にヘッダを付与\n（推奨）",
            "USER_ID,PASSWORD,ITEM_ID,AMOUNT",
            "先頭行に列名（変数名）を英字で記述しておくと、JMeter の「変数名」欄を空欄にするだけで列名を変数名として自動認識します。",
            "ヘッダを付ける場合、CSV Data Set Config の「先頭行を無視」を False（変数名空欄時）または True（変数名手動指定時）に正しく設定します。"
        ),
        (
            "サンプル CSV 構造例",
            "文字列・数値・カンマ混在",
            'USER_ID,PASSWORD,ITEM_ID,AMOUNT,MEMO\nuser001,Passw0rd!01,1001,5000,"通常注文"\nuser002,Passw0rd!02,1002,12000,"備考,カンマあり"',
            "文字列データの中にカンマが含まれる場合は、ダブルクォーテーションで囲みます（Allow quoted data? を True に設定）。",
            "余計な空行を末尾に入れないようにしてください。空行があると空文字リクエストが送信されて 400 Bad Request になります。"
        )
    ]

    for idx, row_data in enumerate(csv_rules):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 3
    r = add_section(ws, r, "3. CSV Data Set Config の詳細設定（JMeter GUI画面操作）")
    callout_gui_path = (
        "【JMeter GUI での追加・編集手順】\n"
        "・既存の修正: api_test.jmx のツリー上で「[任意] CSVデータ読込」をクリックし、右側パネルで設定を変更します。\n"
        "・新規の追加: Thread Group を右クリック → [追加 (Add)] → [設定エレメント (Config Element)] → [CSV Data Set Config] を選択。"
    )
    r = add_callout(ws, r, callout_gui_path)

    headers_config = ["GUI 設定項目名（日本語 / 英語）", "推奨設定値 / 設定例", "選択肢 / 入力形式", "詳細解説と動作仕様", "注意点・トラブル防止策"]
    r = add_table_header(ws, r, headers_config)

    config_settings = [
        (
            "ファイル名 (Filename)",
            "data/testdata.csv\n(または ${__P(DATA_PATH,data/testdata.csv)})",
            "相対パス または 絶対パス",
            "読み込む CSV ファイルのパス。${__P(プロパティ名,デフォルト値)} 形式にしておくと、CLI 実行時に -JDATA_PATH=... で外部から切り替え可能です。",
            "Windows / Linux 間でパス区切り文字の差異を避けるため、必ずスラッシュ「/」を使用した相対パスで記述します。"
        ),
        (
            "ファイルエンコーディング\n(File encoding)",
            "UTF-8",
            "UTF-8\nShift_JIS\nEUC-JP 等",
            "CSV ファイルの文字コード。日本語データが含まれる場合は常に「UTF-8」を指定します。",
            "空欄にすると OS のデフォルト文字コード（Windows では MS932/Shift-JIS、Linux では UTF-8）となり環境差異が発生します。"
        ),
        (
            "変数名 (Variable Names)",
            "空欄（ヘッダ自動読込時）\nまたは USER_ID,PASSWORD,ITEM_ID",
            "カンマ区切りの変数名リスト",
            "CSV の各列を格納する変数名。CSV の 1 行目に列名がある場合は「空欄」にしておくのが最も保守性が高く推奨されます。",
            "CSV にヘッダ行がない場合は、列の並び順通りにカンマ区切りで変数名を記述してください（例: COL1,COL2,COL3）。"
        ),
        (
            "先頭行を無視\n(Ignore first line)",
            "False (変数名空欄時)\nまたは True (変数名手動指定時)",
            "True / False",
            "CSV の 1 行目をデータ行ではなくヘッダ行として読み飛ばすかどうかのフラグ。",
            "「変数名」を手動入力した場合は、1行目のヘッダ文字（USER_IDなど）がデータとして送信されないよう「True」に設定します。"
        ),
        (
            "区切り文字 (Delimiter)",
            ",",
            ", (カンマ)\n\\t (タブ) 等",
            "列の区切り文字。通常の CSV は「,」、TSV ファイルの場合は「\\t」を入力します。",
            "タブ区切りの場合は「\\t」と文字通り入力します。"
        ),
        (
            "引用符内の改行等を許可\n(Allow quoted data?)",
            "True",
            "True / False",
            "ダブルクォーテーションで囲まれたデータ内にカンマや改行が含まれることを許可するかどうか。",
            "住所や備考欄などでカンマや改行を含むデータを扱う場合は、必ず「True」にしてください。False だと列ずれが発生します。"
        ),
        (
            "ファイル終端でループ\n(Recycle on EOF?)",
            "True (繰返し時)\nまたは False (1回限りの時)",
            "True / False",
            "CSV の最終行まで読み終わった後、再び 1 行目に戻って繰り返し読み込むかどうか。",
            "【使い分け】アカウントを何回も使い回して長時間負荷をかける場合は「True」、一度きりのデータ（ワンタイムトークン等）は「False」。"
        ),
        (
            "ファイル終端でスレッド停止\n(Stop thread on EOF?)",
            "False (Recycle=True 時)\nまたは True (Recycle=False 時)",
            "True / False",
            "CSV の終端に達したとき、その仮想ユーザースレッドの実行を停止するかどうか。",
            "Recycle を False にした場合は、こちらを「True」にすることで、データがなくなったスレッドから順次安全にテストを終了できます。"
        ),
        (
            "共有モード (Sharing mode)",
            "All threads (全スレッド)",
            "All threads\nCurrent thread group\nCurrent thread",
            "【All threads】: 全仮想ユーザーで 1 つの CSV を共有し、スレッド間で重複なく 1 行ずつ順次取り合います（最も一般的）。\n"
            "【Current thread】: 各スレッドが個別に 1 行目から読み始めます（スレッドごとに同じデータを実行したい場合）。",
            "異なるユーザーで同時ログインするテストでは、必ず「All threads」を選択してください。重複ログインを防げます。"
        )
    ]

    for idx, row_data in enumerate(config_settings):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 4
    r = add_section(ws, r, "4. POST サンプラーへの組み込み手順（Body Data 設定）")
    callout_body_step = (
        "【JMeter GUI でのサンプラー設定手順】\n"
        "1. 対象サンプラー（例: API01_ログイン(POST JSON) や API03_注文登録(POST form)）をクリック。\n"
        "2. 右側パネルで「Body Data」タブ（JSON送信時）または「Parameters」タブ（Form送信時）を選択します。\n"
        "3. HTTP Header Manager に「Content-Type: application/json」が設定されていることを確認してください。"
    )
    r = add_callout(ws, r, callout_body_step)

    headers_body = ["送信フォーマット", "設定タブ", "ペイロード記述例（設定値）", "型変換・構文ルール", "動作仕様・注意点"]
    r = add_table_header(ws, r, headers_body)

    body_examples = [
        (
            "JSON 本文\n(application/json)",
            "Body Data タブ",
            '{\n'
            '  "username": "${USER_ID}",\n'
            '  "password": "${PASSWORD}",\n'
            '  "itemId": ${ITEM_ID},\n'
            '  "quantity": ${QUANTITY},\n'
            '  "role": "${ROLE}"\n'
            '}',
            "・文字列型フィールド: \"${USER_ID}\"（クォーテーションで囲む）\n"
            "・数値型フィールド: ${ITEM_ID}（クォーテーションなし）\n"
            "・真偽値型: ${IS_ACTIVE}（true/false、クォートなし）",
            "【超重要】数値フィールドをクォーテーションで囲んで \"${ITEM_ID}\" と書くと、文字列として送信されてサーバ側で 400 Validation Error になる場合があります。"
        ),
        (
            "Form データ\n(x-www-form-urlencoded)",
            "Parameters タブ",
            "名前: username, 値: ${USER_ID}\n"
            "名前: password, 値: ${PASSWORD}\n"
            "名前: itemId, 値: ${ITEM_ID}\n"
            "名前: quantity, 値: ${QUANTITY}",
            "[追加] ボタンで 1 行ずつパラメータを追加し、[値] 列に ${変数名} を設定します。[URL エンコード?] にチェックを入れます。",
            "従来の HTML フォーム送信や multipart/form-data の場合は Parameters タブを使用します。"
        )
    ]

    for idx, row_data in enumerate(body_examples):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 5
    r = add_section(ws, r, "5. 自動生成 JMX 要素との関係と切り替え手順")
    callout_relation = (
        "【既存の「[任意] CSVデータ読込」を本番用 CSV に切り替える手順】\n"
        "1. 新しい CSV ファイル（例: data/production_users.csv）をプロジェクトの data/ フォルダ内に配置します。\n"
        "2. JMeter GUI でツリー上の「[任意] CSVデータ読込」をクリック。\n"
        "3. Filename 欄を「data/production_users.csv」に書き換えて保存（Ctrl+S）。\n"
        "4. Thread Group を 1スレッド/2ループ で実行し、「[任意] 変数確認 (Debug Sampler)」で 1ループ目と 2ループ目で異なるユーザー情報が読み込まれていることを確認。\n"
        "5. これだけで、シナリオ全体へ外部CSVのデータ駆動テストが完全に適用されます。"
    )
    r = add_callout(ws, r, callout_relation)

    ws.freeze_panes = "A5"
    return ws

print("Sheet 3 builder compiled.")
