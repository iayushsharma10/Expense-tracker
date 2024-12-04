import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import csv

# Global variables for expense tracking
monthly_budget = 0
total_expenses = 0
category_totals = {
    "🍔Food": 0,
    "🏠Home": 0,
    "💻Work": 0,
    "🥳Fun": 0,
    "👾Miscellaneous": 0
}
expense_data = []  # Store expenses with date

def set_budget(budget_entry, budget_label, remaining_budget_label):
    global monthly_budget
    try:
        budget = float(budget_entry.get())
        if budget <= 0:
            messagebox.showerror("Error", "Please enter a positive budget amount.")
            return
        monthly_budget = budget
        budget_label.config(text=f"Budget: Rs.{monthly_budget}")
        remaining_budget_label.config(text=f"Remaining Budget: Rs.{monthly_budget - total_expenses}")
        budget_entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Budget set successfully!")
    except ValueError:
        messagebox.showerror("Error", "Invalid input. Please enter a valid number.")

def add_expense(expense_name_entry, expense_amount_entry, category_var, expenses_listbox, remaining_budget_label, date_entry):
    global total_expenses
    expense_name = expense_name_entry.get()
    expense_amount = float(expense_amount_entry.get())
    selected_category = category_var.get()
    expense_date = date_entry.get_date()

    if expense_amount <= 0:
        messagebox.showerror("Error", "Please enter a positive amount.")
        return

    # Save the expense to the global data
    expense_data.append({
        "name": expense_name,
        "amount": expense_amount,
        "category": selected_category,
        "date": expense_date
    })

    # Update the category totals and total expenses
    category_totals[selected_category] += expense_amount
    total_expenses += expense_amount

    # Display expense in the listbox
    expenses_listbox.insert(tk.END, f"{expense_name} - Rs.{expense_amount} - {selected_category} - {expense_date}")
    expense_name_entry.delete(0, tk.END)
    expense_amount_entry.delete(0, tk.END)

    remaining_budget_label.config(text=f"Remaining Budget: Rs.{monthly_budget - total_expenses}")
    messagebox.showinfo("Success", "Expense added successfully!")

def summarize_expenses():
    summary = f"Expense Summary:\n"
    for category, total in category_totals.items():
        summary += f"{category}: Rs.{total}\n"
    summary += f"\nTotal Expenses: Rs.{total_expenses}\n"
    summary += f"Remaining Budget: Rs.{monthly_budget - total_expenses}"

    messagebox.showinfo("Expense Summary", summary)

def reset_budget(budget_label, remaining_budget_label, expenses_listbox):
    global monthly_budget, total_expenses, category_totals, expense_data
    monthly_budget = 0
    total_expenses = 0
    category_totals = {category: 0 for category in category_totals}
    expense_data = []  # Clear all expenses
    remaining_budget_label.config(text="Remaining Budget: Rs.0")
    budget_label.config(text="Budget: Rs.0")
    expenses_listbox.delete(0, tk.END)
    messagebox.showinfo("Reset", "Budget and expenses have been reset.")

def generate_csv():
    """Generate a CSV file containing all expenses and daily totals."""
    if not expense_data:
        messagebox.showerror("Error", "No expenses to export.")
        return

    # Group expenses by date to calculate daily totals
    daily_totals = {}
    for entry in expense_data:
        date = entry["date"]
        if date not in daily_totals:
            daily_totals[date] = 0
        daily_totals[date] += entry["amount"]

    # Create the CSV file path
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if filename:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Expense Name", "Amount", "Category"])
            for entry in expense_data:
                writer.writerow([entry['date'], entry['name'], entry['amount'], entry['category']])

            writer.writerow(["\nDaily Totals:"])
            for date, total in daily_totals.items():
                writer.writerow([date, total])

        messagebox.showinfo("Success", f"Expenses exported to {filename}.")

def generate_summary_csv():
    """Generate a summary CSV containing total expenses by category and total expenditure."""
    if not expense_data:
        messagebox.showerror("Error", "No expenses to summarize.")
        return

    # Create the summary CSV file path
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if filename:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Total Expenses"])
            for category, total in category_totals.items():
                writer.writerow([category, total])

            writer.writerow([])
            writer.writerow(["Total Expenses", total_expenses])
            writer.writerow(["Remaining Budget", monthly_budget - total_expenses])

        messagebox.showinfo("Success", f"Summary exported to {filename}.")

def generate_calendar(calendar_widget):
    """Generate a PNG calendar with daily expenses marked."""
    if not expense_data:
        messagebox.showerror("Error", "No expenses to generate calendar.")
        return

    # Get the selected month and year from the user
    selected_date = calendar_widget.get_date()
    year, month = selected_date.year, selected_date.month

    # Group expenses by date
    daily_totals = {}
    for entry in expense_data:
        if entry["date"].month == month and entry["date"].year == year:
            date_str = entry["date"].strftime("%Y-%m-%d")
            if date_str not in daily_totals:
                daily_totals[date_str] = 0
            daily_totals[date_str] += entry["amount"]

    # Generate a calendar image
    cal = Image.new('RGB', (500, 500), color='white')
    draw = ImageDraw.Draw(cal)
    font = ImageFont.load_default()

    # Draw the month and year
    draw.text((10, 10), f"Expenses for {selected_date.strftime('%B %Y')}", fill='black', font=font)

    # Draw the days and their totals
    for i in range(1, 32):
        day_str = f"{year}-{month:02d}-{i:02d}"
        y_offset = 40 + (i-1) * 15
        if day_str in daily_totals:
            amount = daily_totals[day_str]
            draw.text((10, y_offset), f"{i}: Rs.{amount}", fill='blue', font=font)
        else:
            draw.text((10, y_offset), f"{i}: No expenses", fill='black', font=font)

    # Save the calendar as a PNG file
    filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
    if filename:
        cal.save(filename)
        messagebox.showinfo("Success", f"Calendar saved to {filename}.")

def main():
    global monthly_budget

    root = tk.Tk()
    root.title("Khaatabook")
    root.geometry("1000x700")
    root.configure(bg="#2e2e2e")

    # Create a frame to center the content
    frame = tk.Frame(root, bg="#2e2e2e", padx=30, pady=30)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    # Create Left Frame (Expense Input Section)
    left_frame = tk.Frame(frame, bg="#2e2e2e", padx=20, pady=20)
    left_frame.grid(row=0, column=0, padx=20, pady=20)

    # Budget Label and Remaining Budget Label
    budget_label = ttk.Label(left_frame, text="Budget: Rs.0", font=("Arial", 18), anchor='w', foreground="white", background="#2e2e2e")
    budget_label.grid(row=0, column=0, pady=10, sticky="w", columnspan=2)

    remaining_budget_label = ttk.Label(left_frame, text="Remaining Budget: Rs.0", font=("Arial", 18), anchor='w', foreground="white", background="#2e2e2e")
    remaining_budget_label.grid(row=1, column=0, pady=10, sticky="w", columnspan=2)

    # Set Budget Section
    budget_entry = ttk.Entry(left_frame, font=("Arial", 14), width=15)
    budget_entry.grid(row=2, column=0, pady=10, sticky="w")

    set_budget_button = ttk.Button(left_frame, text="Set Budget", command=lambda: set_budget(budget_entry, budget_label, remaining_budget_label))
    set_budget_button.grid(row=3, column=0, pady=10, sticky="ew", columnspan=2)

    # Expense Entry Section
    expense_name_label = ttk.Label(left_frame, text="Expense Name", font=("Arial", 14), foreground="white", background="#2e2e2e")
    expense_name_label.grid(row=4, column=0, pady=5, sticky='w')

    expense_name_entry = ttk.Entry(left_frame, font=("Arial", 14), width=20)
    expense_name_entry.grid(row=5, column=0, pady=5)

    expense_amount_label = ttk.Label(left_frame, text="Expense Amount", font=("Arial", 14), foreground="white", background="#2e2e2e")
    expense_amount_label.grid(row=6, column=0, pady=5, sticky='w')

    expense_amount_entry = ttk.Entry(left_frame, font=("Arial", 14), width=20)
    expense_amount_entry.grid(row=7, column=0, pady=5)

    category_var = tk.StringVar(root)
    category_var.set("🍔Food")

    category_menu = ttk.Combobox(left_frame, textvariable=category_var, values=["🍔Food", "🏠Home", "💻Work", "🥳Fun", "👾Miscellaneous"], font=("Arial", 14))
    category_menu.grid(row=8, column=0, pady=10)

    # Calendar for Date Selection
    calendar_widget = Calendar(left_frame, selectmode='day', year=2024, month=12, day=1)
    calendar_widget.grid(row=9, column=0, pady=10)

    add_expense_button = ttk.Button(left_frame, text="Add Expense", command=lambda: add_expense(expense_name_entry, expense_amount_entry, category_var, expenses_listbox, remaining_budget_label, calendar_widget))
    add_expense_button.grid(row=10, column=0, pady=10)

    # Create Right Frame (Buttons and Expense List)
    right_frame = tk.Frame(frame, bg="#2e2e2e", padx=20, pady=20)
    right_frame.grid(row=0, column=1, padx=20, pady=20)

    # Expenses Listbox
    expenses_listbox = tk.Listbox(right_frame, height=10, width=50, font=("Arial", 12), fg="white", bg="#333333", selectmode=tk.SINGLE)
    expenses_listbox.grid(row=0, column=0, pady=20, columnspan=2)

    # Buttons Organized in Groups
    button_frame = tk.Frame(right_frame, bg="#2e2e2e")
    button_frame.grid(row=1, column=0, columnspan=2, pady=20)

    # Summary and Reset Buttons
    summarize_button = ttk.Button(button_frame, text="Show Summary", command=summarize_expenses)
    summarize_button.grid(row=0, column=0, padx=10)

    reset_button = ttk.Button(button_frame, text="Reset Budget", command=lambda: reset_budget(budget_label, remaining_budget_label, expenses_listbox))
    reset_button.grid(row=0, column=1, padx=10)

    # Export CSV and Calendar Buttons
    export_csv_button = ttk.Button(button_frame, text="Export CSV", command=generate_csv)
    export_csv_button.grid(row=1, column=0, padx=10)

    export_summary_button = ttk.Button(button_frame, text="Export Summary CSV", command=generate_summary_csv)
    export_summary_button.grid(row=1, column=1, padx=10)

    generate_calendar_button = ttk.Button(button_frame, text="Generate Calendar", command=lambda: generate_calendar(calendar_widget))
    generate_calendar_button.grid(row=2, column=0, padx=10)

    root.mainloop()

if __name__ == "__main__":
    main()
