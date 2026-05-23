import argparse
from payroll.services.generator import generate_payroll_receipts
from payroll.config import DATA_FILE

def main():
    p = argparse.ArgumentParser(description="Generate payroll receipts from data.xlsx")
    p.add_argument("--data-file", default=DATA_FILE, help="Path to data xlsx")
    p.add_argument("--out", default=None, help="Output XLSX filename (default=YYYY-MM-DD.xlsx)")
    args = p.parse_args()

    def progress(msg: str):
        print(msg)

    generate_payroll_receipts(args.data_file, progress_cb=progress, out_filename=args.out)

if __name__ == "__main__":
    main()
