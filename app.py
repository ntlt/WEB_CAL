import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_time_data():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run headlessly
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://factorialhr.com/free-time-card-calculator-online")

        # Extract clock-in and clock-out times from the table
        times = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        
        for row in rows:
            day = row.find_element(By.TAG_NAME, "td").text  # First td for day
            if day in days:
                clock_in = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) input").get_attribute("value")  # Second td for clock-in
                clock_out = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) input").get_attribute("value")  # Third td for clock-out
                times[day] = (clock_in, clock_out)

        driver.quit()
        return times
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while fetching data: {e}")
        return {}

def calculate_hours(clock_in, clock_out):
    format_24h = "%H:%M"  # Adjusted to 24-hour format
    clock_in_time = datetime.strptime(clock_in, format_24h)
    clock_out_time = datetime.strptime(clock_out, format_24h)
    return (clock_out_time - clock_in_time).seconds / 3600

def calculate_leave_time(friday_clock_in):
    times = get_time_data()
    total_hours = 0
    for clock_in, clock_out in times.values():
        if clock_in and clock_out:
            total_hours += calculate_hours(clock_in, clock_out)

    required_hours = 40
    remaining_hours = required_hours - total_hours
    friday_clock_in_time = datetime.strptime(friday_clock_in, "%I:%M %p")
    friday_leave_time = friday_clock_in_time + timedelta(hours=remaining_hours)

    messagebox.showinfo("Leave Time", f"You can leave on Friday at: {friday_leave_time.strftime('%I:%M %p')}")

def update_table(tree):
    # Clear existing data in the treeview
    for item in tree.get_children():
        tree.delete(item)

    times = get_time_data()
    for day, (clock_in, clock_out) in times.items():
        tree.insert("", "end", values=(day, clock_in, clock_out))

def create_table():
    root = tk.Tk()
    root.title("Time Card Calculator")
    root.configure(bg="#B2E5D4")  # Pastel green background

    frame = ttk.Frame(root, padding="10")
    frame.pack(pady=10)

    columns = ["Day", "Clock In", "Clock Out"]
    tree = ttk.Treeview(frame, columns=columns, show='headings', height=8)
    tree.heading("Day", text="Day")
    tree.heading("Clock In", text="Clock In")
    tree.heading("Clock Out", text="Clock Out")
    
    # Styling the Treeview
    style = ttk.Style()
    style.configure("Treeview", background="#D6E8D4", foreground="black", rowheight=25, fieldbackground="#D6E8D4")
    style.map("Treeview", background=[("selected", "#A8E1C8")])

    tree.pack()

    # Button to fetch and update the table
    fetch_button = tk.Button(root, text="Fetch Data", command=lambda: update_table(tree), bg="#A8E1C8", fg="black", padx=10, pady=5)
    fetch_button.pack(pady=10)

    # Entry for Friday clock-in time
    friday_clock_in_label = tk.Label(root, text="Enter Friday Clock In Time (e.g., 09:00 AM):", bg="#B2E5D4")
    friday_clock_in_label.pack()
    friday_clock_in_entry = tk.Entry(root, bg="white", fg="black", font=("Arial", 12))
    friday_clock_in_entry.pack()

    # Button to calculate leave time
    calculate_button = tk.Button(root, text="Calculate Leave Time", command=lambda: calculate_leave_time(friday_clock_in_entry.get()), bg="#A8E1C8", fg="black", padx=10, pady=5)
    calculate_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_table()
