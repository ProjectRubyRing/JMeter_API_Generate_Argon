# -*- coding: utf-8 -*-
"""
Sheet 2: ①API依存関係・値受け渡し (API Dependency & Correlation)
"""
from generate_guide_table_helpers import *

def build_sheet2(ws):
    ws.title = "①API依存関係・値受け渡し"
    ws.views.sheetView[0].showGridLines = True
    ws.sheet_properties.tabColor = "333333"

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
        "① API間の依存関係設定と動的な値の受け渡し手順（相関設定・Correlation）",
        "前APIのレスポンス（JSON/ヘッダ/本文）からデータを抽出し、後続APIのリクエスト（パス/クエリ/ヘッダ/本文）へ設定する完全手順"
    )

    r = 4
    # Section 1
    r = add_section(ws, r, "1. 依存関係の基本アーキテクチャとデータフロー")
    callout_text = (
        "【処理の流れ（ログイン認証から後続API呼出の完全フロー）】\n"
        "・ステップ1【呼出元 API】: API01_ログイン(POST JSON) を実行し、サーバから認証応答 JSON を受信します。\n"
        "・ステップ2【抽出処理】: API01 の直下に子要素として配置した「JSON Extractor」が起動し、応答 JSON の $.data.token から値を抽出して変数 AUTH_TOKEN に格納。\n"
        "・ステップ3【ヘッダ反映】: 後続の API02_商品検索(GET) の直下（または Thread Group 直下）の「HTTP Header Manager」が Authorization: Bearer ${AUTH_TOKEN} を自動付与して送信。\n"
        "・ステップ4【パス・本文反映】: さらに API03_注文登録(POST) のように、URLパス (/orders/${ORDER_ID}) やリクエスト本文 ({\"token\":\"${AUTH_TOKEN}\"}) へも ${変数名} で自由に埋め込み可能。\n\n"
        "【自動生成JMX（api_test.jmx）での初期状態】\n"
        "・api_test.jmx では、API01_ログイン(POST JSON) の配下に「[任意] API01 JSON抽出 AUTH_TOKEN」および「[任意] API01 JSON抽出 LOGIN_SEQ」が初期配置されています。\n"
        "・既存のこれらを右クリックしてパラメータを修正するか、または別のサンプラーに新規に後処理（Post Processors）を追加して利用します。"
    )
    r = add_callout(ws, r, callout_text)

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 2
    r = add_section(ws, r, "2. 抽出部品の設定方法（JMeter GUI画面操作）")

    # Sub-header A
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    c = ws.cell(r, 1, "部品A: JSON Extractor（JSON レスポンスからの高速抽出・最も推奨）")
    c.font = font_m(size=10, bold=True, color=C_SUB_TH_FG)
    c.fill = fill_s(C_SUB_TH_BG)
    ws.row_dimensions[r].height = 32.0
    for col in range(2, 7):
        ws.cell(r, col).fill = fill_s(C_SUB_TH_BG)
    r += 1

    headers_json = ["GUI 設定項目名（日本語 / 英語）", "推奨設定値 / 設定例", "選択肢 / 入力形式", "詳細解説と動作仕様", "注意点・ベストプラクティス"]
    r = add_table_header(ws, r, headers_json)

    json_settings = [
        (
            "名前 (Name)",
            "JSON Extractor - 認証トークン抽出",
            "任意の文字列",
            "要素の表示名。どのサンプラーの何を抽出しているか明記すると、シナリオ全体の可読性が大幅に向上します。",
            "自動生成された名前に「- トークン抽出」のように目的を追記すると分かりやすいです。"
        ),
        (
            "適用先 (Apply to)",
            "Main sample only",
            "Main sample only\nSub-samples only\nMain sample and sub-samples",
            "通常の HTTP リクエストサンプラーの応答から抽出する場合は常に「Main sample only」を選択します。",
            "リダイレクト先や画像などの埋め込みリソース（サブリクエスト）から取得する場合のみ変更します。"
        ),
        (
            "作成する変数名\n(Names of created variables)",
            "AUTH_TOKEN;USER_ID",
            "半角英数字（セミコロン区切りで複数指定可能）",
            "抽出した値を格納する変数名を指定します。後続の API では ${AUTH_TOKEN} として呼び出します。",
            "大文字・小文字は厳格に区別されます。可読性と誤認防止のため、大文字スネークケースを強く推奨します。"
        ),
        (
            "JSON パス表現式\n(JSON Path expressions)",
            "$.data.token;$.data.user.id",
            "JSONPath 構文（セミコロン区切り）",
            "レスポンス JSON 内の抽出対象要素を指定する JSONPath 式。変数名の個数と合わせてセミコロンで区切ります。",
            "ルート要素を表す「$」から書き始めます。存在しないパスを指定した場合はデフォルト値が代入されます。"
        ),
        (
            "一致番号 (Match Numbers)",
            "1;1",
            "半角数値（セミコロン区切り）",
            "・1 : 最初に見つかった 1 件を取得（通常の単一オブジェクトは常に 1）\n"
            "・0 : 一致した候補の中からランダムに 1 件を取得\n"
            "・-1 : 一致した全件を取得（配列形式で ${VAR_1}, ${VAR_2}... と ${VAR_matchNr} が生成される）",
            "特定のアイテムを1つだけ取りたい場合は「1」、一覧リストを取得して後でループさせたい場合は「-1」を指定します。"
        ),
        (
            "デフォルト値 (Default Values)",
            "NO_TOKEN;NO_USER_ID",
            "任意の文字列（セミコロン区切り）",
            "指定した JSON パスが見つからなかった場合（エラー応答やスキーマ不一致時）に変数へ格納される代替値。",
            "空欄にすると変数が作成されず「${AUTH_TOKEN}」のまま残り原因調査が困難になるため、必ず「NOT_FOUND」等を明記してください。"
        )
    ]

    for idx, row_data in enumerate(json_settings):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    # Sub-table: JSONPath Cheat Sheet
    ws.row_dimensions[r].height = 8.0
    r += 1

    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    c = ws.cell(r, 1, "実務で使える JSONPath 逆引き早見表")
    c.font = font_m(size=10, bold=True, color=C_SUB_TH_FG)
    c.fill = fill_s(C_SUB_TH_BG)
    ws.row_dimensions[r].height = 32.0
    for col in range(2, 7):
        ws.cell(r, col).fill = fill_s(C_SUB_TH_BG)
    r += 1

    headers_jp = ["抽出したい対象の構造", "レスポンス JSON の構造例", "JSONPath 式の書き方", "取得される結果", "解説・応用テクニック"]
    r = add_table_header(ws, r, headers_jp)

    jp_cheat = [
        (
            "ルート直下の単一値",
            '{"token": "eyJhbGciOi...", "status": 200}',
            "$.token",
            "eyJhbGciOi...",
            "最頻出パターン。直下のキー名を「.キー名」で指定します。"
        ),
        (
            "ネストされたオブジェクト",
            '{"data": {"user": {"id": 1050, "role": "admin"}}}',
            "$.data.user.id",
            "1050",
            "階層をドットで掘り進めて指定します。"
        ),
        (
            "配列の先頭要素",
            '{"items": [{"id": 101, "name": "Apple"}, {"id": 102}]}',
            "$.items[0].id",
            "101",
            "インデックス「[0]」で配列の最初のオブジェクトを指定します。"
        ),
        (
            "配列の末尾要素",
            '{"items": [{"id": 101}, {"id": 999}]}',
            "$.items[-1].id",
            "999",
            "負のインデックス「[-1]」で最新（最後）の要素を安全に取得できます。"
        ),
        (
            "条件フィルタ（特定条件一致）",
            '{"items": [{"id": 1, "active": false}, {"id": 2, "active": true}]}',
            "$.items[?(@.active == true)].id",
            "2",
            "「?(@.キー == 値)」で条件に合致する要素だけをフィルタリングして抽出します。"
        ),
        (
            "配列内の全要素を一括抽出",
            '{"items": [{"id": 10}, {"id": 20}, {"id": 30}]}',
            "$.items[*].id",
            "10, 20, 30",
            "Match No に「-1」を指定すると、${ID_1}=10, ${ID_2}=20, ${ID_3}=30, ${ID_matchNr}=3 が自動生成されます。"
        )
    ]

    for idx, row_data in enumerate(jp_cheat):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 3]
        )

    # Sub-header B: Regular Expression Extractor
    ws.row_dimensions[r].height = 8.0
    r += 1

    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    c = ws.cell(r, 1, "部品B: Regular Expression Extractor（正規表現抽出・ヘッダやHTML用）")
    c.font = font_m(size=10, bold=True, color=C_SUB_TH_FG)
    c.fill = fill_s(C_SUB_TH_BG)
    ws.row_dimensions[r].height = 32.0
    for col in range(2, 7):
        ws.cell(r, col).fill = fill_s(C_SUB_TH_BG)
    r += 1

    headers_regex = ["GUI 設定項目名", "推奨設定値 / 設定例", "選択肢", "詳細解説", "主な利用シーン"]
    r = add_table_header(ws, r, headers_regex)

    regex_settings = [
        (
            "チェックするフィールド\n(Field to check)",
            "Response Headers (または Body)",
            "Body\nResponse Headers\nURL\nResponse Code",
            "抽出対象が Set-Cookie や Location 等の HTTP ヘッダにある場合は「Response Headers」を選択します。本文の場合は「Body」。",
            "認証クッキー、リダイレクト先URL、CSRFトークンの取得"
        ),
        (
            "参照名 (Reference Name)",
            "COOKIE_SESSION_ID",
            "半角英数字",
            "抽出した値を格納する変数名。後続では ${COOKIE_SESSION_ID} で利用します。",
            "単一の変数名を指定"
        ),
        (
            "正規表現 (Regular Expression)",
            "Set-Cookie: session_id=([^;]+);",
            "正規表現パターン",
            "抽出したい値を丸括弧「( )」でキャプチャグループとして囲みます。",
            "Cookie ヘッダ、Location ヘッダのパラメータ抽出"
        ),
        (
            "テンプレート (Template)",
            "$1$",
            "グループ指定文字列",
            "正規表現内のどのキャプチャグループを変数に代入するかを指定します。「$1$」は最初の ( ) の中身。",
            "通常は常に「$1$」を指定"
        ),
        (
            "一致番号 (Match No.)",
            "1",
            "数値 (1, 0, -1)",
            "複数マッチした場合の取得位置。1 は最初、-1 は全件、0 はランダム。",
            "通常は「1」を指定"
        ),
        (
            "デフォルト値 (Default Value)",
            "NO_COOKIE_FOUND",
            "任意の文字列",
            "正規表現がマッチしなかった場合に変数へ代入される値。",
            "エラー切り分けのため空欄にせず明記"
        )
    ]

    for idx, row_data in enumerate(regex_settings):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    # Sub-header C: Boundary Extractor
    ws.row_dimensions[r].height = 8.0
    r += 1

    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
    c = ws.cell(r, 1, "部品C: Boundary Extractor（境界抽出・最高速な文字列抽出）")
    c.font = font_m(size=10, bold=True, color=C_SUB_TH_FG)
    c.fill = fill_s(C_SUB_TH_BG)
    ws.row_dimensions[r].height = 32.0
    for col in range(2, 7):
        ws.cell(r, col).fill = fill_s(C_SUB_TH_BG)
    r += 1

    headers_boundary = ["GUI 設定項目名", "設定値 / 設定例", "選択肢", "詳細解説", "特徴・メリット"]
    r = add_table_header(ws, r, headers_boundary)

    boundary_settings = [
        (
            "左境界 (Left Boundary)",
            '"token":"',
            "任意の文字列",
            "抽出したい値の直前にある文字列を完全に一致するように記述します。",
            "正規表現を使わないため CPU 負荷が極めて低く高速"
        ),
        (
            "右境界 (Right Boundary)",
            '"',
            "任意の文字列",
            "抽出したい値の直後にある文字列を記述します。",
            "左境界と右境界に挟まれた文字列が変数に格納されます"
        ),
        (
            "一致番号 (Match No.)",
            "1",
            "数値 (1, 0, -1)",
            "1 は最初に見つかった文字列を抽出します。",
            "大量の負荷をかけるシナリオで正規表現のCPU消費を抑えたい場合に最適"
        )
    ]

    for idx, row_data in enumerate(boundary_settings):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 3
    r = add_section(ws, r, "3. 抽出変数を後続 API へ反映する具体的手順（各箇所別）")
    headers_reflect = ["反映先・箇所", "GUI の操作画面・タブ", "設定例 / 記述構文", "JMeter GUI での具体的設定手順", "動作仕様・注意点"]
    r = add_table_header(ws, r, headers_reflect)

    reflections = [
        (
            "URL パス\n(Path)",
            "対象サンプラーの\n[Path] 入力欄",
            "/api/v1/orders/${ORDER_ID}\n/api/v1/users/${USER_ID}/profile",
            "1. 後続サンプラー（例: API02_商品検索 や API03_注文登録）を選択\n"
            "2. パス入力欄で動的にしたい箇所を ${変数名} に書き換える",
            "JMeter がリクエスト送信時に ${ORDER_ID} を実際の数値（例: 1050）に置換します。前後のスラッシュ漏れに注意してください。"
        ),
        (
            "クエリパラメータ\n(Parameters)",
            "対象サンプラーの\n[Parameters] タブ",
            "名前: token\n値: ${AUTH_TOKEN}",
            "1. サンプラーの [Parameters] タブで [追加] ボタンをクリック\n"
            "2. [名前] にパラメータ名（例: token）を入力\n"
            "3. [値] に ${AUTH_TOKEN} を入力\n"
            "4. [URL エンコード?] にチェックを入れる",
            "GET リクエスト等のクエリ文字列（?token=...）として送信されます。特殊記号を含む場合は URL エンコードを有効にしてください。"
        ),
        (
            "HTTP リクエストヘッダ\n(Header Manager)",
            "サンプラー配下の\n[HTTP Header Manager]",
            "名前: Authorization\n値: Bearer ${AUTH_TOKEN}",
            "1. 後続サンプラー配下の HTTP Header Manager を開く\n"
            "2. [追加] をクリック\n"
            "3. [名前] に Authorization\n"
            "4. [値] に Bearer ${AUTH_TOKEN}",
            "全 API で共通して使うトークンの場合は、Thread Group 直下の共通 HTTP Header Manager に設定しても有効です。"
        ),
        (
            "リクエスト本文 (JSON)\n(Body Data)",
            "対象サンプラーの\n[Body Data] タブ",
            '{\n  "orderId": ${ORDER_ID},\n  "token": "${AUTH_TOKEN}",\n  "remark": "テスト"\n}',
            "1. サンプラーの [Body Data] タブを選択\n"
            "2. JSON 本文を記述し、動的項目を ${変数名} に置き換える",
            "【最重要】JSON 構文上、文字列フィールドは \"${AUTH_TOKEN}\" のようにダブルクォーテーションで囲み、数値フィールドは ${ORDER_ID} とクォートなしで記述します。"
        )
    ]

    for idx, row_data in enumerate(reflections):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 4
    r = add_section(ws, r, "4. 抽出動作の確認・デバッグ手順（トラブルシューティング）")
    callout_debug = (
        "【GUI 上での 100% 確実な動作確認ステップ】\n"
        "1.【単体実行】: Thread Group のスレッド数を「1」、ループ回数を「1」にして、ツールバーの「開始 (緑の三角)」をクリック。\n"
        "2.【Debug Sampler の確認】: 「[任意] 変数確認 (Debug Sampler)」をクリックし、「Response data」タブを開きます。\n"
        "   アルファベット順に JMeter 変数一覧が表示されるので、目的の変数（例: AUTH_TOKEN=eyJhbGci... や ORDER_ID=1050）が正常に格納されているか確認。\n"
        "3.【後続サンプラーの確認】: 後続 API（API02 や API03）をクリックし、「Request」タブを開きます。\n"
        "   「Request Headers」に「Authorization: Bearer eyJhbGci...」が正しく送られているか、本文の「${...}」が実値に置換されているかを確認。\n\n"
        "【値が取れない（NOT_FOUND やリテラルのまま）場合の 3大チェックポイント】\n"
        "・チェック1: JSONPath 式の構文ミス（ルートの「$」が抜けていないか、キー名の大文字小文字がレスポンスと完全一致しているか）。\n"
        "・チェック2: 抽出元 API が 200 OK 以外のステータス（401 や 500）でエラー応答を返していないか（View Results Tree で抽出元 API の応答を確認）。\n"
        "・チェック3: JSON Extractor の配置場所（親サンプラーの子要素になっておらず、関係ない兄弟階層に配置されていないか）。"
    )
    r = add_callout(ws, r, callout_debug)

    ws.freeze_panes = "A5"
    return ws

print("Sheet 2 builder compiled.")
