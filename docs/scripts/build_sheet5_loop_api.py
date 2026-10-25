# -*- coding: utf-8 -*-
"""
Sheet 5: ④特定APIのループ実行 (Specific API Loop Execution within Scenario)
"""
from generate_guide_table_helpers import *

def build_sheet5(ws):
    ws.title = "④特定APIのループ実行"
    ws.views.sheetView[0].showGridLines = True
    ws.sheet_properties.tabColor = "808080"

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
        "④ シナリオ内での特定API複数回ループ実行手順（反復制御・ポーリング）",
        "一連のシナリオ（ログイン〜ログアウト）の中で、特定 API のみを選択的に N 回反復実行する完全手順"
    )

    r = 4
    # Section 1
    r = add_section(ws, r, "1. 特定 API のみループさせるユースケースと必要性")
    callout_text = (
        "【なぜ Thread Group のループ回数では不十分なのか？】\n"
        "・スレッドグループの「Loop Count (ループ回数)」は、グループ配下にある【すべての API】を先頭から末尾まで丸ごと繰り返します。\n"
        "・しかし現実の業務シナリオでは以下のパターンが一般的です:\n"
        "    1. ログイン（1 回だけ実行）\n"
        "    2. 商品検索 → 詳細閲覧（この一連の操作だけを 5 回繰り返す）\n"
        "    3. 注文確定（1 回だけ実行）\n"
        "    4. ログアウト（1 回だけ実行）\n"
        "・スレッドグループ全体を 5 回ループさせると、毎回ログインとログアウトが 5 回行われてしまい、極めて不自然な負荷モデルになります。\n"
        "・この「特定処理だけを何回も回す」制御を行うために、JMeter の「Loop Controller（ループコントローラ）」を使用します。\n\n"
        "【自動生成JMX（api_test.jmx）での適用対象】\n"
        "・api_test.jmx には「API01_ログイン」「API02_商品検索」「API03_注文登録」「API04_クッキー確認」が並列に配置されています。\n"
        "・本手順では「API02_商品検索」を Loop Controller 配下に移動させて 5 回反復させる具体的な構築手順を解説します。"
    )
    r = add_callout(ws, r, callout_text)

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 2
    r = add_section(ws, r, "2. Loop Controller の追加と階層移動手順（GUI操作ステップ完全解説）")
    headers_steps = ["手順", "操作名", "JMeter GUI での具体的な操作手順", "画面の状態・確認ポイント", "注意点・失敗防止策"]
    r = add_table_header(ws, r, headers_steps)

    steps = [
        (
            "Step 1",
            "Loop Controller の追加",
            "1. スレッドグループ内のループを開始したい位置（例: API01 の下）を右クリック\n"
            "2. [追加 (Add)] → [ロジックコントローラ (Logic Controller)] → [Loop Controller (ループコントローラ)] をクリック",
            "ツリーに「Loop Controller」という要素が新しく追加されます。",
            "スレッドグループと同階層ではなく、必ずスレッドグループの直下に追加してください。"
        ),
        (
            "Step 2",
            "名前の変更（可読性向上）",
            "追加した要素をクリックし、画面右側の「名前 (Name)」欄をわかりやすい名前に変更します。\n"
            "例: `[ループ] 商品検索反復(5回)`",
            "ツリーの表示名が変更され、どの API 群をまとめているか一目で把握できるようになります。",
            "名前は組み込み変数（`__jm__名前__idx`）で後から参照するため、全角スペースなどは避けると安全です。"
        ),
        (
            "Step 3",
            "ループ回数 (Loop Count) の設定",
            "Loop Controller の設定パネルで「Loop Count」欄に反復回数を入力します。\n"
            "・固定回数: `5`\n"
            "・変数指定: `${LOOP_COUNT}`",
            "指定した回数だけ、配下のサンプラーが繰り返し実行されます。",
            "「Infinite (無限)」にチェックを入れるとテストが永久に停止しなくなるため、必ずチェックを外して数値を指定します。"
        ),
        (
            "Step 4",
            "対象サンプラーの階層移動\n【最重要ステップ】",
            "1. ループさせたいサンプラー（例: `API02_商品検索(GET)`）をマウスで掴む\n"
            "2. Loop Controller の【右下（子階層）】に向けてドラッグ＆ドロップする\n"
            "（またはサンプラーを右クリック → [切り取り] → Loop Controller を右クリック → [貼り付け]）",
            "【見た目の確認】\n"
            "ツリー上で対象サンプラーが Loop Controller の下に【1段右にインデント（字下げ）】されて表示されていることを確認します。",
            "【超重要】\n"
            "同階層に並んでいるとループの内側に入っておらず、1回しか実行されません。必ず「右にインデントされているか」を目視確認してください！"
        )
    ]

    for idx, row_data in enumerate(steps):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["center", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 3
    r = add_section(ws, r, "3. Loop Controller の詳細設定項目")
    headers_l_cfg = ["GUI 設定項目名（日本語 / 英語）", "設定値 / 記述例", "選択肢", "詳細解説と動作仕様", "注意点・補足"]
    r = add_table_header(ws, r, headers_l_cfg)

    l_configs = [
        (
            "名前 (Name)",
            "[ループ] 商品検索反復(5回)",
            "任意の文字列",
            "コントローラの表示名。JMeter 5.x ではこの名前がループカウンタの変数名として使われます。",
            "わかりやすい名前を付けてください。"
        ),
        (
            "ループ回数 (Loop Count)",
            "5 (または ${LOOP_COUNT})",
            "正の整数 または 変数式",
            "配下の子要素を何回反復するかを指定します。数値を直接書くか、ユーザー定義変数 ${...} を指定可能。",
            "コマンドラインから `-JSEARCH_LOOPS=10` のように渡したい場合は `${__P(SEARCH_LOOPS,5)}` と書きます。"
        ),
        (
            "無限 (Infinite)",
            "チェックなし (False)",
            "チェックボックス",
            "チェックを入れると、スレッドが生存している限り無限に子要素を繰り返します。",
            "通常はチェックしません。時間指定（Duration）で負荷をかける場合のみ使用します。"
        )
    ]

    for idx, row_data in enumerate(l_configs):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 4
    r = add_section(ws, r, "4. ループカウンタの取得と動的ページング活用")
    callout_counter = (
        "【JMeter 5.x 組み込みループインデックス変数（__jm__コントローラ名__idx）】\n"
        "・JMeter 5.0 以降では、Loop Controller の配下で自動的に「${__jm__<コントローラ名>__idx}」という変数が利用可能になります。\n"
        "・値は「0 始まり」の整数（0, 1, 2, 3...）です。\n"
        "・例: コントローラ名が `Loop_Search` の場合 → 変数名は `${__jm__Loop_Search__idx}` となります。\n\n"
        "【1 始まりのページ番号（page=1, page=2...）へ変換して API に渡す方法】\n"
        "・多くの Web API ではページ番号は 1 始まりです。Groovy 関数を使って「+1」します:\n"
        "  構文: `${__groovy(vars.get('__jm__[ループ] 商品検索反復(5回)__idx').toInteger() + 1)}`\n"
        "・設定場所: `API02_商品検索` の [Parameters] タブで、名前: `page`、値: 上記の式 を入力。\n"
        "・これで、1 ループ目は `page=1`、2 ループ目は `page=2`、3 ループ目は `page=3` と自動的にページ送りしながら検索を反復します！"
    )
    r = add_callout(ws, r, callout_counter)

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 5
    r = add_section(ws, r, "5. ループ内の待機時間（思考時間・ペーシング）の配置ルール（必須）")
    callout_timer = (
        "【なぜループ内に待機時間が必要なのか？】\n"
        "・JMeter はデフォルトでは待機時間「0ms」でリクエストを送信します。\n"
        "・Loop Controller 内にタイマを入れないと、1 人のユーザーが 0.001 秒の隙間もなく連続して 5 回検索を叩くことになり、"
        "サーバの CPU を無駄に急騰させたり、DDoS 攻撃対策のレートリミット（429 Too Many Requests）に引っかかります。\n"
        "・人間が検索結果を見てから次のページを押すまでの「思考時間（Think Time: 1〜2秒）」を必ず挟んでください。"
    )
    r = add_callout(ws, r, callout_timer)

    headers_timer = ["待機の実装方法", "追加する JMeter 要素", "GUI での追加手順", "推奨設定値", "特徴とメリット"]
    r = add_table_header(ws, r, headers_timer)

    timers = [
        (
            "方法A: Flow Control Action\n（推奨・独立サンプラー）",
            "Flow Control Action\n(旧 Test Action)",
            "1. Loop Controller を右クリック\n"
            "2. [追加] → [サンプラー] → [Flow Control Action] を選択\n"
            "3. ループ内サンプラーの直下に配置",
            "Action: `Pause`\nDuration: `1000` (ms)",
            "独立したサンプラーとしてツリーに見えるため、待機時間の位置と長さが一目で分かりやすく、最も管理が容易です。"
        ),
        (
            "方法B: Constant Timer\n（定数タイマ）",
            "Constant Timer\n(定数タイマ)",
            "1. 対象サンプラー（API02）を右クリック\n"
            "2. [追加] → [タイマ] → [Constant Timer] を選択\n"
            "3. サンプラーの子要素として配置",
            "Thread Delay: `1000` (ms)",
            "サンプラーが実行される直前に常に 1000ms 待機します。サンプラー固有の遅延を持たせたい場合に適しています。"
        )
    ]

    for idx, row_data in enumerate(timers):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 6
    r = add_section(ws, r, "6. 発展編: While Controller（条件付きポーリング・完了待ち）")
    callout_while = (
        "【非同期バッチ・帳票生成などのポーリング制御】\n"
        "・「API を呼び出してステータスが COMPLETED になるまで 2 秒おきに最大 10 回ポーリングする」場合の構成です。\n"
        "・要素: Thread Group → [追加] → [ロジックコントローラ] → [While Controller]\n\n"
        "【Condition (条件式) の記述例】\n"
        "  `${__groovy(vars.get('JOB_STATUS') != 'COMPLETED' && (vars.get('__jm__While_Poll__idx') ?: '0').toInteger() < 10)}`\n"
        "  ※ 意味: `JOB_STATUS` が `COMPLETED` ではなく、かつループ回数が 10 回未満の間、配下の処理を繰り返す（無限ループ防止ガード付き）。\n\n"
        "【配下に置く要素】\n"
        "  1. ステータス取得 API（GET /jobs/123/status → 子要素の JSON Extractor で $.status を変数 JOB_STATUS に抽出）\n"
        "  2. Flow Control Action（Pause: 2000 ms → 2秒待機）"
    )
    r = add_callout(ws, r, callout_while)

    ws.freeze_panes = "A5"
    return ws

print("Sheet 5 builder compiled.")
