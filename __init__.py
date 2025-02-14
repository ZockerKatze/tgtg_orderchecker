import tkinter as tk
from datetime import datetime
from io import BytesIO
from tkinter import messagebox
from tkinter import ttk

import requests
from PIL import Image, ImageTk

from key import *


def format_time(iso_time):
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        local_time = dt.astimezone()
        return local_time.strftime("%H:%M")  # Only time (no date)
    except Exception:
        return "Unknown Error!"


def fetch_orders():
    log_message("Fetching orders...")
    try:
        active_orders = client.get_active()
        if not isinstance(active_orders, dict) or "orders" not in active_orders:
            raise ValueError("Unexpected API response format.")
        orders_list = active_orders.get("orders", [])
    except Exception as e:
        log_message(f"Error fetching active orders: {e}")
        messagebox.showerror("Error", f"Error fetching active orders: {e}")
        return []

    orders_data = []
    for order in orders_list:
        try:
            image_url = order.get("item_cover_image", {}).get("current_url", "")
            order_info = {
                "name": order.get("item_name", "Unknown"),
                "store_name": order.get("store_name", "Unknown"),
                "address": order.get("pickup_location", {}).get("address", {}).get("address_line", "Unknown"),
                "longitude": order.get("pickup_location", {}).get("location", {}).get("longitude", "Unknown"),
                "latitude": order.get("pickup_location", {}).get("location", {}).get("latitude", "Unknown"),
                "price": order.get("total_price", {}).get("minor_units", 0) / (
                        10 ** order.get("total_price", {}).get("decimals", 2)),
                "currency": order.get("total_price", {}).get("code", "Unknown"),
                "payment_method": order.get("payment_method_display_name", "Unknown"),
                "pickup_window": {
                    "start": format_time(order.get("pickup_interval", {}).get("start", "Unknown")),
                    "end": format_time(order.get("pickup_interval", {}).get("end", "Unknown"))
                },
                "image_url": image_url
            }
            orders_data.append(order_info)
        except Exception as e:
            log_message(f"Skipping an order due to an error: {e}")

    return orders_data


def display_orders():
    log_message("Displaying orders...")
    orders = fetch_orders()
    if not orders:
        messagebox.showinfo("Info", "No active orders found.")
        log_message("No active orders found.")
        return

    for widget in frame.winfo_children():
        widget.destroy()

    for order in orders:
        text = f"{order['name']} - {order['store_name']}\nAddress: {order['address']}\nPrice: {order['price']} {order['currency']}\nPayment: {order['payment_method']}\nPickup: {order['pickup_window']['start']} to {order['pickup_window']['end']}\n"
        label = tk.Label(frame, text=text, justify="left", padx=10, pady=5, anchor="w", font=("Arial", 10),
                         bg="#f0f0f0", relief="ridge")
        label.pack(fill="x", pady=5)

        if order["image_url"]:
            try:
                response = requests.get(order["image_url"])
                img_data = BytesIO(response.content)
                img = Image.open(img_data)

                # Resize the image to fit within 150x150 but maintain aspect ratio
                max_size = (150, 150)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                img_tk = ImageTk.PhotoImage(img)
                img_label = tk.Label(frame, image=img_tk)
                img_label.image = img_tk  # Keep reference to avoid garbage collection
                img_label.pack(pady=5)
            except Exception as e:
                log_message(f"Failed to load image: {e}")


def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text.insert(tk.END, f"{timestamp} - {message}\n")
    log_text.yview(tk.END)  # Scroll to the bottom


def on_startup():
    log_message("Application started.")
    # Automatically fetch orders at startup
    display_orders()


# GUI Setup
root = tk.Tk()
root.title("TGTG Orders")
root.geometry("500x600")
root.configure(bg="#ffffff")

# Create Notebook (tab control)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Create a tab for displaying orders
orders_tab = tk.Frame(notebook, bg="#ffffff")
notebook.add(orders_tab, text="Orders")

# Create a tab for the fetch button
button_tab = tk.Frame(notebook, bg="#ffffff")
notebook.add(button_tab, text="Actions")

# Create a tab for logging
log_tab = tk.Frame(notebook, bg="#ffffff")
notebook.add(log_tab, text="Log")

# Create a frame to hold order data
frame = tk.Frame(orders_tab, bg="#ffffff")
frame.pack(fill="both", expand=True, padx=10, pady=10)

# Create the Fetch Orders button in the 'Actions' tab
fetch_button = tk.Button(button_tab, text="Fetch Orders", command=display_orders, font=("Arial", 12, "bold"),
                         bg="white", fg="#128cdc", padx=10, pady=5, anchor="w")
fetch_button.pack(pady=10, anchor="w")

# Create a Text widget for logging
log_text = tk.Text(log_tab, wrap=tk.WORD, height=15, font=("Arial", 10), bg="#f0f0f0")
log_text.pack(fill="both", expand=True, padx=10, pady=10)


# Function to save log to a .log file
def save_log():
    try:
        log_content = log_text.get("1.0", tk.END)  # Get all the log text
        with open("log_file.log", "w") as log_file:  # Open the file in write mode
            log_file.write(log_content)  # Save log content to file
        log_message("Log file saved successfully.")
    except Exception as e:
        log_message(f"Error saving log file: {e}")
        messagebox.showerror("Error", f"Error saving log file: {e}")


# Create the Save Log button in the 'Actions' tab
save_log_button = tk.Button(button_tab, text="Save Log", command=save_log, font=("Arial", 12, "bold"),
                            bg="white", fg="#128cdc", padx=10, pady=5, anchor="w")
save_log_button.pack(pady=10, anchor="w")  # Align to the left (west)

# Automatically fetch orders at startup
root.after(1000, on_startup)

root.mainloop()
