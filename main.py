import tkinter as tk
from io import BytesIO
from tkinter import messagebox, ttk, Menu
from datetime import datetime
import requests
from PIL import Image, ImageTk
#from funcfile import save_log
from key import *

def exit_applet():
    log_message("[ INFO ]: Exiting Applet")
    exit()

def format_time(iso_time):
    try:
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
        local_time = dt.astimezone()
        return local_time.strftime("%H:%M")
    except ValueError:
        return "Unknown Error!"

def fetch_orders():
    log_message("[ INFO ]: Fetching orders...")
    try:
        active_orders = client.get_active()
        if not isinstance(active_orders, dict) or "orders" not in active_orders:
            raise ValueError("Unexpected API response format.")
        orders_list = active_orders.get("orders", [])
    except Exception as e:
        log_message(f"[ ERROR ]: Error fetching active orders: {e}")
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
                "quantity": order.get("quantity", 1),
                "longitude": order.get("pickup_location", {}).get("location", {}).get("longitude", "Unknown"),
                "latitude": order.get("pickup_location", {}).get("location", {}).get("latitude", "Unknown"),
                "price": order.get("total_price", {}).get("minor_units", 0) / (10 ** order.get("total_price", {}).get("decimals", 2)),
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
            log_message(f"[ FATAL ERROR ]: Skipping an order due to an error: {e}")

    return orders_data

def display_orders():
    log_message("[ INFO ]: Displaying orders...")
    orders = fetch_orders()
    if not orders:
        messagebox.showinfo("Info", "No active orders found.")
        log_message("[ ERROR ]: No active orders found.")
        return

    for widget in frame.winfo_children():
        widget.destroy()

    for order in orders:
        text = (f"{order['name']} - {order['store_name']}\n"
                f"Address: {order['address']}\n"
                f"Quantity: {order['quantity']}\n"
                f"Price: {order['price']} {order['currency']}\n"
                f"Payment: {order['payment_method']}\n"
                f"Pickup: {order['pickup_window']['start']} to {order['pickup_window']['end']}\n")
        label = tk.Label(frame, text=text, justify="left", padx=10, pady=5, anchor="w", font=("Arial", 10),
                         bg="#f0f0f0", relief="ridge")
        label.pack(fill="x", pady=5)

        if order["image_url"]:
            try:
                response = requests.get(order["image_url"])
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                img_label = tk.Label(frame, image=img_tk)
                img_label.image = img_tk
                img_label.pack(pady=5)
            except Exception as e:
                log_message(f"[ ERROR ]: Failed to load image: {e}")

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text.insert(tk.END, f"{timestamp} - {message}\n")
    log_text.yview(tk.END)

def on_startup():
    log_message("[ INFO ]: Application started.")
    display_orders()

root = tk.Tk()
root.title("TGTG Orders")
root.geometry("500x600")
root.configure(bg="#ffffff")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

orders_tab = tk.Frame(notebook, bg="#ffffff")
notebook.add(orders_tab, text="Orders")

log_tab = tk.Frame(notebook, bg="#ffffff")
notebook.add(log_tab, text="Log")

def about():
    messagebox.showinfo("About", "PythonTGTG Script for fetching Orders on Desktop")
def save_log():
    try:
        log_content = log_text.get("1.0", tk.END)
        with open("log_file.log", "w") as log_file:
            log_file.write(log_content)
        log_message("[ INFO ]: Log file saved successfully.")
    except Exception as e:
        log_message(f"[ ERROR ]: Error saving log file: {e}")
        messagebox.showerror("Error", f"Error saving log file: {e}")


menu = Menu(root)
root.config(menu=menu)
filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Exit", command=exit_applet)
filemenu.add_command(label="Refetch", command=display_orders)
filemenu.add_command(label="Save Log", command=save_log)
filemenu.add_separator()
filemenu.add_command(label="About", command=about)

frame = tk.Frame(orders_tab, bg="#ffffff")
frame.pack(fill="both", expand=True, padx=10, pady=10)

log_text = tk.Text(log_tab, wrap=tk.WORD, height=15, font=("Arial", 10), bg="#f0f0f0")
log_text.pack(fill="both", expand=True, padx=10, pady=10)

def save_log():
    try:
        log_content = log_text.get("1.0", tk.END)
        with open("log_file.log", "w") as log_file:
            log_file.write(log_content)
        log_message("[ INFO ]: Log file saved successfully.")
    except Exception as e:
        log_message(f"[ ERROR ]: Error saving log file: {e}")
        messagebox.showerror("Error", f"Error saving log file: {e}")

root.after(1000, on_startup)
root.mainloop()