from pathlib import Path
from openpyxl.drawing.image import Image as XLImage
from payroll.utils.a1rc import a1_to_rc, rc_to_a1

def add_block_images(ws, base_row: int, base_col: int, anchors, logo_path: str | Path, size=(130,108)):
    if not logo_path or not Path(logo_path).exists():
        return
    for a1 in anchors:
        rel_r, rel_c = a1_to_rc(a1)
        r = base_row + (rel_r - 1)
        c = base_col + (rel_c - 1)
        img = XLImage(str(logo_path))
        img.width, img.height = size
        ws.add_image(img, rc_to_a1(r, c))
