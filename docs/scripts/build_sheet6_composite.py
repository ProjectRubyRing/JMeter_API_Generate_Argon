# -*- coding: utf-8 -*-
"""
Sheet 6: 複合シナリオ・設計原則 (Composite Scenario, Scoping & Troubleshooting)
"""
from generate_guide_table_helpers import *

def build_sheet6(ws):
    ws.title = "複合シナリオ・設計原則"
    ws.views.sheetView[0].showGridLines = True
    ws.sheet_properties.tabColor = "999999"

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
        "複合シナリオ構築と JMeter 設計・運用原則（トラブルシューティング集）",
        "4 大シナリオパターンを統合した実践シナリオツリー構造、スコープ管理、CLI 実行設計、よくあるトラブル 10 選"
    )

    r = 4
    # Section 1
    r = add_section(ws, r, "1. 4 大パターン統合 総合実践シナリオの構成例")
    callout_tree = (
        "【総合シナリオのツリー構造（JMeter GUI 画面のインデント階層図）】\n\n"
        "Test Plan（テストプラン）\n"
        "  ├── HTTP Header Manager（全API共通: User-Agent, Accept 等）\n"
        "  ├── [任意] CSVデータ読込 (CSV Data Set Config: data/users.csv) ---------- 【② CSVデータ順次読込】\n"
        "  ├── Thread Group（スレッドグループ: 10スレッド, 3ループ）\n"
        "  │     ├── [任意] 乱数 RANDOM_NO (Random Variable: 1000〜9999) ----------- 【③ 数値IDランダム生成】\n"
        "  │     │\n"
        "  │     ├── API01: 認証ログイン (POST /api/v1/auth/login)\n"
        "  │     │     ├── Body Data: {\"username\": \"${USER_ID}\", \"password\": \"${PASSWORD}\"} - 【② CSVからPOST入力】\n"
        "  │     │     └── JSON Extractor (変数: AUTH_TOKEN) ------------------------ 【① 応答からトークン抽出】\n"
        "  │     │\n"
        "  │     ├── HTTP Header Manager (Authorization: Bearer ${AUTH_TOKEN}) -------- 【① 後続共通ヘッダへ反映】\n"
        "  │     │\n"
        "  │     ├── [ループ] 商品検索反復 (Loop Controller: 3回) -------------------- 【④ 特定APIのみ反復】\n"
        "  │     │     ├── API02: 商品検索 (GET /items?cat=${__Random(1,20,)}&p=${PAGE}) 【③ 乱数 & ④ ページング】\n"
        "  │     │     │     └── JSON Extractor (変数: ITEM_ID = $.items[0].id) ------- 【① 検索結果から商品ID抽出】\n"
        "  │     │     └── Flow Control Action (Pause: 1000ms) ------------------------ 【④ ループ内待機時間】\n"
        "  │     │\n"
        "  │     ├── API03: 注文登録 (POST /api/v1/orders) ----------------------------- 【①抽出値 ＆ ③乱数をPOST】\n"
        "  │     │     └── Body Data: {\"userId\": \"${USER_ID}\", \"itemId\": ${ITEM_ID}, \"qty\": ${__Random(1,5,)}}\n"
        "  │     │\n"
        "  │     ├── API04: ログアウト (POST /api/v1/auth/logout)\n"
        "  │     └── [任意] 変数確認 (Debug Sampler) ---------------------------------- 【単体検証・デバッグ】\n"
        "  │\n"
        "  └── [任意] 結果ツリー (View Results Tree) ----------------------------------- 【結果確認用リスナー】"
    )
    r = add_callout(ws, r, callout_tree)

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 2
    r = add_section(ws, r, "2. JMeter のスコープ（親子関係）と変数のライフサイクル")
    headers_scope = ["要素タイプ", "JMeter 上の配置場所", "適用範囲（スコープ）", "変数のライフサイクル", "誤った配置による障害"]
    r = add_table_header(ws, r, headers_scope)

    scopes = [
        (
            "設定エレメント\n(CSV / 乱数 / Defaults)",
            "Thread Group 直下 または\nTest Plan 直下",
            "同階層およびその配下にある【すべてのサンプラー】に適用されます。",
            "スレッド起動時に初期化され、ループごとに更新（CSV読込や乱数再生成）されます。",
            "サンプラー配下（子要素）に置くと、その特定サンプラーにしか設定が効かなくなります。"
        ),
        (
            "後処理 (Post Processor)\n(JSON / 正規表現抽出)",
            "抽出元サンプラーの【子要素】\n（API01 の直下）",
            "【親サンプラーのみ】。親サンプラーのレスポンスを受信した直後に 1 回だけ実行されます。",
            "抽出成功時にスレッドローカル変数に格納され、スレッドが生存する間保持されます。",
            "Thread Group 直下に置くと、グループ内の【全サンプラー実行後】に毎回実行されてエラーログが多発します。"
        ),
        (
            "HTTP Header Manager\n(リクエストヘッダ)",
            "サンプラー配下（個別）または\nThread Group 直下（共通）",
            "同階層および配下のサンプラーに適用。同名ヘッダがある場合は【深い階層（子要素）が優先】されます。",
            "リクエスト送信時にヘッダ文字列として評価・送信されます。",
            "ログイン前の API に認証ヘッダを付与してしまい、ログインAPIが 400 エラーになる事故。"
        ),
        (
            "JMeter 変数 (Variables)\n(${変数名})",
            "vars.put() / Extractor /\nCSV Data Set 等で生成",
            "【スレッドローカル（スレッド単位で完全分離）】。スレッドAの変数はスレッドBから見えません。",
            "各スレッドの実行開始から終了まで生存。別ループでも上書きされない限り値が保持されます。",
            "スレッド間でデータを共有したい場合は「JMeter プロパティ (${__P})」を使う必要があります。"
        )
    ]

    for idx, row_data in enumerate(scopes):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 3
    r = add_section(ws, r, "3. CLI 実行時（-JTHREADS, -JLOOPS）の総リクエスト数計算と負荷設計")
    callout_calc = (
        "【特定 API ループを含む場合の総リクエスト数 計算公式】\n\n"
        "  総リクエスト数 = スレッド数 (THREADS) × スレッドグルーグループ数 (LOOPS) × [ 各 API の 1 シナリオ内実行回数 の合計 ]\n\n"
        "【具体例での計算（上記総合シナリオ: THREADS=10, LOOPS=3, 商品検索ループ=3回 の場合）】\n"
        "  ・API01_ログイン: 10スレッド × 3ループ × 1回 = 30 回\n"
        "  ・API02_商品検索: 10スレッド × 3ループ × 3回 = 90 回 （※内部ループにより 3 倍発生！）\n"
        "  ・API03_注文登録: 10スレッド × 3ループ × 1回 = 30 回\n"
        "  ・API04_ログアウト: 10スレッド × 3ループ × 1回 = 30 回\n"
        "  --------------------------------------------------------\n"
        "  合計総リクエスト数 = 30 + 90 + 30 + 30 = 180 回\n\n"
        "【CLI 実行コマンド例（Linux / Windows 共通）】\n"
        "  jmeter -n -t output/api_test.jmx -l result/run_result.jtl -e -o result/html_report -JTHREADS=10 -JLOOPS=3"
    )
    r = add_callout(ws, r, callout_calc)

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 4
    r = add_section(ws, r, "4. よくあるトラブル 10 選と具体的解決手順（逆引きトラブルシューティング集）")
    headers_trouble = ["No", "トラブル現象・エラー", "主な原因", "JMeter GUI での調査・確認手順", "具体的な解決策・修正方法"]
    r = add_table_header(ws, r, headers_trouble)

    troubles = [
        (
            "1",
            "変数が置換されず\n「${VAR}」のまま送信される",
            "・変数名のスペルミス・大文字小文字の不一致\n・抽出元サンプラーがエラー等で変数を定義できていない",
            "View Results Tree で「[任意] 変数確認 (Debug Sampler)」の Response data を開き、目的の変数名が存在するか確認。",
            "・JSON Extractor の「作成する変数名」と後続の呼び出し名が完全一致しているか確認。\n・デフォルト値に「NOT_FOUND」を指定してエラー検知しやすくする。"
        ),
        (
            "2",
            "CLI 実行時に「File not found」で CSV が読めない",
            "・CSV のパスが Windows の絶対パス（C:\\...）になっている\n・JMeter 実行時のカレントディレクトリと相対パスがずれている",
            "jmeter.log を開き、読み込みに失敗している CSV の完全解決パスを確認。",
            "Filename 欄を「data/testdata.csv」のように JMX からの相対パスで指定するか、${__P(DATA_PATH,data/testdata.csv)} と記述して CLI から -JDATA_PATH= で渡す。"
        ),
        (
            "3",
            "全スレッドが CSV の\n「1 行目ばかり」読み込む",
            "CSV Data Set Config の Sharing Mode が「Current thread」になっている。",
            "GUI で CSV Data Set Config を開き、「Sharing mode」の設定値を確認。",
            "Sharing mode を「All threads (全スレッド)」に変更する。全スレッドで 1 つのファイルを順番に取り合うようになります。"
        ),
        (
            "4",
            "Loop Controller 内のサンプラーが 1 回しか動かない",
            "サンプラーが Loop Controller の配下（子要素）にインデント（字下げ）されておらず、外側に並んでいる。",
            "JMeter GUI のツリーで、対象サンプラーが Loop Controller より「右に1段下がっているか」を目視確認。",
            "対象サンプラーを Loop Controller の直下右側にドラッグ＆ドロップするか、[切り取り] → コントローラを右クリックして [貼り付け] を行う。"
        ),
        (
            "5",
            "POST リクエストで\nHTTP 415 エラーが返る",
            "リクエストヘッダに `Content-Type: application/json` が付与されていない。",
            "View Results Tree で該当リクエストの「Request」タブを開き、Request Headers に Content-Type があるか確認。",
            "サンプラー配下の HTTP Header Manager（または Thread Group 直下の共通ヘッダ）に `Content-Type: application/json` を追加する。"
        ),
        (
            "6",
            "Authorization ヘッダが\n後続 API に付与されない",
            "・Header Manager のスコープが外れている\n・ヘッダ値に「Bearer 」プレフィックスが漏れている",
            "View Results Tree で後続リクエストの Request Headers を確認。",
            "・Header Manager が後続サンプラーの子要素にあるか確認。\n・値欄に `Bearer ${AUTH_TOKEN}` とスペースを含めて正しく記述されているか確認。"
        ),
        (
            "7",
            "ループカウンタ\n${__jm__...__idx} が空文字になる",
            "変数内のコントローラ名と、GUI 上の Loop Controller の「Name (名前)」が完全一致していない。",
            "Debug Sampler の Response data を開き、「__jm__」で始まる変数名を検索して実際の変数名を確認。",
            "コントローラ名に合わせて `${__jm__名前__idx}` の「名前」部分を正確に修正する（全角・半角・スペースに注意）。"
        ),
        (
            "8",
            "Random Variable が\n毎回全く同じ数値を生成する",
            "Random Variable の「Random Seed」欄に固定値が入力されている。",
            "GUI で Random Variable を開き、「Random Seed」欄を確認。",
            "「Random Seed」欄を完全に【空欄】にする。シードを消去すれば実行ごとに異なる乱数列が生成されます。"
        ),
        (
            "9",
            "While Controller で\nテストが停止せず無限ループする",
            "終了条件が一度も True にならない、または最大ループ回数の安全ガードが入っていない。",
            "GUI で Loop Controller を開き、Loop Count の設定を確認。",
            "Groovy 式内に `&& (vars.get('__jm__While_Job__idx') ?: '0').toInteger() < 20` のように最大反復上限（ガード条件）を必ず設ける。"
        ),
        (
            "10",
            "ツールで JMX 再生成時に\n画面変更が上書き消滅した",
            "jmeter_api_tool の `generate` コマンドを `-t 元JMX` なしで実行して新規上書きしてしまった。",
            "output/ フォルダの変更履歴やバックアップを確認。",
            "・既存 JMX を保持して定義のみ同期する場合は `-t output/api_test.jmx`（更新モード）を指定する。\n・カスタマイズした JMX は別名（例: scenario_order_flow.jmx）で保存して管理する。"
        )
    ]

    for idx, row_data in enumerate(troubles):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["center", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    ws.freeze_panes = "A5"
    return ws

print("Sheet 6 builder compiled.")
