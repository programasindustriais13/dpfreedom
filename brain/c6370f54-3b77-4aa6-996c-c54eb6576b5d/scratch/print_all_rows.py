import openpyxl

wb = openpyxl.load_workbook("atestados_ficticio.xlsx", data_only=True)
sheet = wb.active

for i, row in enumerate(sheet.iter_rows(values_only=True), start=1):
    print(f"Row {i}: {row}")
