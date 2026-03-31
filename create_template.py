import openpyxl

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Customers"

headers = [
    "customer_name",
    "amount",
    "due_date",
    "phone_number",
    "attempts",
    "payment_plan_eligible",
    "notes"
]

ws.append(headers)

# Sample row
ws.append([
    "Rahul Mehta",
    "12500",
    "01/03/2026",
    "+91 9876543210",
    "3",
    "yes",
    "Customer previously said he would pay last week"
])

wb.save("customers.xlsx")
print("Template created: customers.xlsx")