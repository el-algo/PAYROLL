from payroll.utils.a1rc import a1_to_rc, rc_to_a1  # rc_to_a1 is used by images
from openpyxl.cell.cell import MergedCell

def set_cell_safely(ws, row: int, col: int, value):
    for rng in ws.merged_cells.ranges:
        if rng.min_row <= row <= rng.max_row and rng.min_col <= col <= rng.max_col:
            row, col = rng.min_row, rng.min_col
            break
    ws.cell(row=row, column=col).value = value

def fill_block(ws, base_row: int, base_col: int, obj, cell_map: dict):
    for attr, tpl_a1 in cell_map.items():
        rel_r, rel_c = a1_to_rc(tpl_a1)
        target_r = base_row + (rel_r - 1)
        target_c = base_col + (rel_c - 1)
        value = getattr(obj, attr, None)
        if value is None:
            value = 0
        set_cell_safely(ws, target_r, target_c, value)

def paste_template_to_sheet_n_times(ws_src, ws_dst, r1, c1, r2, c2, N, gap=4, start_row=1, start_col=1, copier=None):
    height = r2 - r1 + 1
    for i in range(N):
        dest_r = start_row + i * (height + gap)
        copier(ws_src, r1, c1, r2, c2, ws_dst, dest_r, start_col)
