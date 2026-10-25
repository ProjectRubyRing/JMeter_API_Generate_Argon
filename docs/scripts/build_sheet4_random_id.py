# -*- coding: utf-8 -*-
"""
Sheet 4: ③数値IDのランダム生成 (Random Numeric ID Generation within Range)
"""
from generate_guide_table_helpers import *

def build_sheet4(ws):
    ws.title = "③数値IDのランダム生成"
    ws.views.sheetView[0].showGridLines = True
    ws.sheet_properties.tabColor = "666666"

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
        "③ 指定範囲内の数値ID・乱数の動的生成手順（負荷分散・キャッシュ回避）",
        "指定された範囲内（例: 1000〜9999）の数値を毎回ランダムに生成し、API の URL・クエリ・本文へ渡す完全手順"
    )

    r = 4
    # Section 1
    r = add_section(ws, r, "1. なぜランダム数値が必要か？（業務ユースケース）")
    callout_text = (
        "【ランダム数値・動的IDを活用する 3 大メリット】\n"
        "1.【データベース競合（排他ロック・デッドロック）の回避】\n"
        "   全仮想ユーザーが同じ固定 ID（例: ID=1）に対して更新・購入を行うと、DB 上で激しい行ロック競合が発生し、現実の利用実態とかけ離れた遅延が発生します。\n"
        "2.【キャッシュ層（Redis / CDN / バッファプール）の回避】\n"
        "   毎回同じ ID を GET するとキャッシュから高速応答してしまい、バックエンド DB や外部システムへの真の負荷耐性を計測できません。\n"
        "3.【手軽なユニーク値・ID の分散】\n"
        "   CSV ファイルを用意する手間なく、数万件規模のユニークな注文番号や商品コードを即座にシミュレートできます。\n\n"
        "【自動生成JMX（api_test.jmx）での初期状態】\n"
        "・api_test.jmx では、Thread Group 配下に「[任意] 乱数 RANDOM_NO (Random Variable)」があらかじめ配置されています。\n"
        "・初期値として 1〜100000 の乱数を生成し変数 ${RANDOM_NO} に格納しています。この既存要素を修正するか、または組み込み関数を使用します。"
    )
    r = add_callout(ws, r, callout_text)

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 2
    r = add_section(ws, r, "2. 2 つの実現方法（比較と使い分け）")
    headers_comp = ["比較項目", "方法A: Random Variable（設定エレメント）", "方法B: 組み込み関数 ${__Random()}（関数記法）", "推奨ユースケース・選択基準"]
    r = add_table_header(ws, r, headers_comp)

    comparison = [
        (
            "概要・実装方式",
            "スレッドグループ配下に GUI 部品として「乱数変数」を追加し、ループごとに変数を自動生成する方式。",
            "サンプラーの入力欄（URL・クエリ・Body）に直接「${__Random(最小,最大,変数名)}」と記述する方式。",
            "【方法Bが最速・最も推奨】エレメント追加が不要で、あらゆる入力欄に即座に埋め込めます。"
        ),
        (
            "部品の追加要否",
            "必要（[追加] → [設定エレメント] → [Random Variable]）",
            "不要（JMeter 標準の組み込み関数。どこでも直接記述可能）",
            "設定エレメントを増やしたくない場合は方法Bが圧倒的に手軽です。"
        ),
        (
            "同一ループ内での値再利用",
            "【極めて容易】一度生成された変数（例: ${RND_ID}）は、そのループ内の複数の API で同じ値を共有可能。",
            "第3引数に変数名を指定すれば可能（例: ${__Random(1,100,MY_ID)} と書くと、後続で ${MY_ID} として再利用可能）。",
            "「GET で検索したIDと同じIDを後続の POST で注文する」といった相関を持たせたい場合は方法A、または方法Bの第3引数を活用。"
        ),
        (
            "1サンプラー内での複数乱数",
            "1つのエレメントにつき 1 つの変数しか生成できないため、複数の乱数が必要な場合はエレメントを複数配置する必要あり。",
            "1つのサンプラー内（Body 内など）で何回でも異なる範囲の乱数を記述可能（例: itemId と quantity で別々の乱数）。",
            "JSON ペイロード内に複数の異なる乱数フィールドを含める場合は、方法Bが圧倒的に柔軟で優れています。"
        ),
        (
            "ゼロ埋めフォーマット\n（桁数固定）",
            "Output Format 欄に「000000」と入力するだけで、簡単に「000123」のようなゼロ埋め数値を生成可能。",
            "標準ではゼロ埋め不可（${__groovy(String.format('%06d', ...))} 等が必要）。",
            "社員番号や商品コードなど「固定長 6 桁のゼロ埋め」が必要な業務システムでは、方法Aが便利です。"
        )
    ]

    for idx, row_data in enumerate(comparison):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left"],
            bold_cols=[1]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 3
    r = add_section(ws, r, "3. 方法A: Random Variable（設定エレメント）の設定手順（GUI画面操作）")
    callout_method_a = (
        "【JMeter GUI での追加・編集手順】\n"
        "・既存の修正: api_test.jmx のツリー上で「[任意] 乱数 RANDOM_NO」をクリック。\n"
        "・新規の追加: Thread Group を右クリック → [追加 (Add)] → [設定エレメント (Config Element)] → [Random Variable (乱数変数)] を選択。"
    )
    r = add_callout(ws, r, callout_method_a)

    headers_m_a = ["GUI 設定項目名（日本語 / 英語）", "推奨設定値 / 設定例", "選択肢", "詳細解説と動作仕様", "注意点・ベストプラクティス"]
    r = add_table_header(ws, r, headers_m_a)

    m_a_settings = [
        (
            "変数名 (Variable Name)",
            "RND_ITEM_ID",
            "半角英数字",
            "生成された乱数を格納する変数名。後続のリクエストでは ${RND_ITEM_ID} として呼び出します。",
            "大文字スネークケースを推奨します。"
        ),
        (
            "出力形式 (Output Format)",
            "空欄（通常の数値）\nまたは 000000（ゼロ埋め6桁）",
            "フォーマット文字列",
            "数値をゼロ埋めして桁数を固定したい場合に指定します（例: 42 → 000042）。通常の数値の場合は「空欄」にします。",
            "空欄にすると純粋な整数（1000〜9999）が出力されます。"
        ),
        (
            "最小値 (Minimum Value)",
            "1000",
            "整数値",
            "生成する乱数の最小値（範囲の開始値）。",
            "業務データの存在する最小 ID を指定します。"
        ),
        (
            "最大値 (Maximum Value)",
            "9999",
            "整数値",
            "生成する乱数の最大値（範囲の終了値）。",
            "業務データの存在する最大 ID を指定します。"
        ),
        (
            "ランダムシード (Random Seed)",
            "空欄（必ず空欄にすること！）",
            "整数値 または 空欄",
            "疑似乱数生成器の初期シード値。",
            "【最重要警告】ここに数値を入力すると、毎回全く同じ順序で乱数が生成されてしまい、テストのランダム性が失われます。必ず空欄にしてください。"
        ),
        (
            "スレッド単位で乱数を生成\n(Per Thread (User)?)",
            "True",
            "True / False",
            "仮想ユーザー（スレッド）ごとに独立した乱数生成器インスタンスを持つかどうか。",
            "True にすることで、複数スレッドが同時にアクセスしてもスレッド間で同一の乱数列になることを防ぎ、独立した分散を実現します。"
        )
    ]

    for idx, row_data in enumerate(m_a_settings):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 2]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 4
    r = add_section(ws, r, "4. 方法B: JMeter 組み込み関数 ${__Random()} の利用手順（最速・エレメント不要）")
    callout_method_b = (
        "【構文仕様】: ${__Random(最小値,最大値,変数名)}\n"
        "・第1引数: 乱数の最小値（必須、整数）\n"
        "・第2引数: 乱数の最大値（必須、整数）\n"
        "・第3引数: 格納先の変数名（任意。指定するとその変数にも値が保持され、後続で再利用可能。使わない場合は末尾カンマを残して省略可能）"
    )
    r = add_callout(ws, r, callout_method_b)

    headers_m_b = ["反映箇所・利用場所", "GUI 入力欄", "記述構文・設定例", "生成される値の例", "解説・応用テクニック"]
    r = add_table_header(ws, r, headers_m_b)

    m_b_examples = [
        (
            "URL パス内\n(Path)",
            "サンプラーの\n[Path] 入力欄",
            "/api/v1/items/${__Random(1000,9999,)}\n/api/v1/orders/${__Random(10000,99999,RND_ORDER_ID)}",
            "/api/v1/items/4582\n/api/v1/orders/78219",
            "サンプラーが実行される瞬間にランダムな数値に置換されて送信されます。"
        ),
        (
            "クエリパラメータ\n(Parameters)",
            "サンプラーの\n[Parameters] タブ",
            "名前: categoryId, 値: ${__Random(1,20,)}\n名前: maxPrice, 値: ${__Random(1000,50000,)}",
            "categoryId=14\nmaxPrice=32400",
            "複数のパラメータにそれぞれ異なる範囲の乱数を即座に割り当てられます。"
        ),
        (
            "JSON 本文\n(Body Data)",
            "サンプラーの\n[Body Data] タブ",
            '{\n'
            '  "orderId": ${__Random(100000,999999,RND_ORDER_ID)},\n'
            '  "itemId": ${__Random(1000,9999,)},\n'
            '  "quantity": ${__Random(1,10,)},\n'
            '  "amount": ${__Random(500,50000,)}\n'
            '}',
            '{\n'
            '  "orderId": 583921,\n'
            '  "itemId": 4209,\n'
            '  "quantity": 3,\n'
            '  "amount": 15600\n'
            '}',
            "【注意】JSON の数値フィールドなので、ダブルクォーテーションで囲まずに記述します。囲むと文字列型になってしまいます。"
        )
    ]

    for idx, row_data in enumerate(m_b_examples):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left", "left"],
            bold_cols=[1, 3]
        )

    ws.row_dimensions[r].height = 10.0
    r += 1

    # Section 5
    r = add_section(ws, r, "5. その他の乱数・ユニーク値生成関数一覧（実務リファレンス）")
    headers_funcs = ["関数構文", "生成される値の例", "主な利用シーン", "詳細解説と補足"]
    r = add_table_header(ws, r, headers_funcs)

    other_funcs = [
        (
            "${__UUID()}",
            "c73bcdcc-2669-4bf6-81d3-e4ae73fb1110",
            "トランザクションID、Idempotency-Key、一意の注文番号",
            "UUID v4 形式の 36 文字一意文字列を生成。重複が許されないリクエストヘッダやキーに最適。"
        ),
        (
            "${__RandomString(10,abcdefghijklmnopqrstuvwxyz0123456789,RND_STR)}",
            "k8x9m2p1q4",
            "ランダムなパスワード、仮登録トークン、英数字コード",
            "第1引数に文字数、第2引数に使用可能な文字セットを指定。任意の英数字文字列を動的生成。"
        ),
        (
            "${__time()}",
            "1730000000000",
            "エポックミリ秒タイムスタンプ、ユニークな連番代替",
            "現在時刻のミリ秒（UNIX エポック）を出力。常に単調増加するため一意性が極めて高い。"
        ),
        (
            "${__time(yyyy-MM-dd HH:mm:ss,)}",
            "2026-10-25 15:30:00",
            "日付時刻フィールド、リクエスト日時、予約日時",
            "指定したフォーマットで現在日時を出力。"
        ),
        (
            "${__RandomFromMultipleVars(VAR1|VAR2|VAR3,SELECTED)}",
            "選択された変数の値",
            "特定の候補リスト（例: 東京|大阪|名古屋）からランダム選択",
            "あらかじめ定義された複数の変数の中から、1つをランダムに選定。"
        )
    ]

    for idx, row_data in enumerate(other_funcs):
        r = add_table_row(
            ws, r, row_data,
            is_zebra=(idx % 2 == 1),
            align_list=["left", "left", "left", "left"],
            bold_cols=[1]
        )

    ws.freeze_panes = "A5"
    return ws

print("Sheet 4 builder compiled.")
