import payroll.template_loader as tl
import yaml

DATA_FILE = None
DATA_SHEET = "NOMINA"

TEMPLATE_FILE = tl.find_template()
TEMPLATE_SHEET = "Hoja1"
LOGO_PATH = str(tl.packaged_default_path("Logo.png"))
CONFIG_FILE = tl.find_config()

BLOCK_TOP_LEFT = "A1"
BLOCK_BOTTOM_RIGHT = "J28"
GAP_ROWS = 2

CELL_MAP = {
    "name": "E1",
    "salary": "A1",
    "extra_time": "D7",
    "bonus": "D8",
    "prime_vacation": "D9",
    "vacation": "D10",
    "loan": "D11",
    "Infonavit": "G8",
    "Fonacot": "G9",
    "loan_discount": "G11",
    "hours_deduction": "G6",
    "unit": "E2",
    "week": "C3",
    "pay_date": "F3",
    "days_worked": "G4",
    "weekly_total": "D6"
}

PLACE_NAMES = []

INVALID_ROW_NAMES = [
    "TOTALES", "Ʃ"
]