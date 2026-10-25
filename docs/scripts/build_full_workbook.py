# -*- coding: utf-8 -*-
"""
Master script to assemble docs/JMeter_Scenario_Customization_Guide.xlsx
and run complete verification and quality enforcement.
"""

import os
import openpyxl
from openpyxl.styles import Font
from build_sheet1_overview import build_sheet1
from build_sheet2_correlation import build_sheet2
from build_sheet3_csv_post import build_sheet3
from build_sheet4_random_id import build_sheet4
from build_sheet5_loop_api import build_sheet5
from build_sheet6_composite import build_sheet6

def main():
    print("Initializing Workbook with Meiryo UI base font...")
    wb = openpyxl.Workbook()

    # Enforce Meiryo UI at the workbook engine level
    if wb._fonts:
        wb._fonts[0].name = "Meiryo UI"
    for s in wb._named_styles:
        if hasattr(s, "font") and s.font:
            s.font.name = "Meiryo UI"

    # Remove default sheet
    default_sheet = wb.active

    # Create sheets in order
    print("Building Sheet 1: 目次・概要...")
    ws1 = wb.create_sheet("目次・概要")
    build_sheet1(ws1)

    print("Building Sheet 2: ①API依存関係・値受け渡し...")
    ws2 = wb.create_sheet("①API依存関係・値受け渡し")
    build_sheet2(ws2)

    print("Building Sheet 3: ②CSVデータ順次POST利用...")
    ws3 = wb.create_sheet("②CSVデータ順次POST利用")
    build_sheet3(ws3)

    print("Building Sheet 4: ③数値IDのランダム生成...")
    ws4 = wb.create_sheet("③数値IDのランダム生成")
    build_sheet4(ws4)

    print("Building Sheet 5: ④特定APIのループ実行...")
    ws5 = wb.create_sheet("④特定APIのループ実行")
    build_sheet5(ws5)

    print("Building Sheet 6: 複合シナリオ・設計原則...")
    ws6 = wb.create_sheet("複合シナリオ・設計原則")
    build_sheet6(ws6)

    # Remove the blank initial sheet
    wb.remove(default_sheet)

    # Global Quality Enforcement Pass
    print("\nExecuting Global Quality Enforcement Pass...")
    total_cells = 0
    font_fixed_count = 0

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        ws.views.sheetView[0].showGridLines = True

        for r in range(1, ws.max_row + 1):
            for c in range(1, ws.max_column + 1):
                cell = ws.cell(row=r, column=c)
                total_cells += 1

                # Ensure font is strictly Meiryo UI
                current_font = cell.font
                if current_font is None:
                    cell.font = Font(name="Meiryo UI", size=9.5)
                    font_fixed_count += 1
                elif current_font.name != "Meiryo UI":
                    cell.font = Font(
                        name="Meiryo UI",
                        size=current_font.size or 9.5,
                        bold=current_font.bold or False,
                        italic=current_font.italic or False,
                        color=current_font.color
                    )
                    font_fixed_count += 1

    print(f"Total cells inspected: {total_cells}")
    print(f"Cells explicitly set to Meiryo UI: {font_fixed_count}")

    # Resolve repository root directory based on this script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))

    # Ensure output directories exist
    docs_dir = os.path.join(repo_root, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    target_path = os.path.join(docs_dir, "JMeter_Scenario_Customization_Guide.xlsx")
    wb.save(target_path)
    print(f"\nSuccessfully generated primary file: {target_path}")

    # Also save a copy at workspace root
    root_copy = os.path.join(repo_root, "JMeter_Scenario_Customization_Guide.xlsx")
    wb.save(root_copy)
    print(f"Successfully generated root copy: {root_copy}")

if __name__ == "__main__":
    main()
