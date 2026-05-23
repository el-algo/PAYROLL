from openpyxl.utils.cell import column_index_from_string, get_column_letter

def a1_to_rc(a1: str) -> tuple[int, int]:
    a1 = a1.strip().upper()
    i = 0
    while i < len(a1) and a1[i].isalpha():
        i += 1
    col = column_index_from_string(a1[:i])
    row = int(a1[i:])
    return row, col

def rc_to_a1(row: int, col: int) -> str:
    return f"{get_column_letter(col)}{row}"
