                                                                                                                        ## PYTHONTGTG_AOE  10.0.0
                                                                                                                        ## Import Modules
import tkinter as tk                                                                                                    ## tkinter
from io import BytesIO                                                                                                  ## iobytes
from tkinter import messagebox                                                                                          ## tkinter messagebox
from tkinter import ttk                                                                                                 ## tkinter
from tkinter import *                                                                                                   ## tkinter
from datetime import datetime                                                                                           ## datetime
import requests                                                                                                         ## Requests
from PIL import Image, ImageTk                                                                                          ## Pillow
from GUI_newimg.funcfile import save_log                                                                                ## funcfulle
from key import *                                                                                                       ### key for API

def exit_applet():                                                                                                      ## define function to exit the applet
                                                                                                                        ##OCCOM --> small exit statement
    log_message("[ INFO ]: Exiting Applet")                                                                             ## log exit to log
    exit()                                                                                                              ## exit() to exit app
                                                                                                                        ## format time with local_time(hour:minute)
def format_time(iso_time):                                                                                              ## function to format time
    try:                                                                                                                ## do
        dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))                                                    ## datetime init
        local_time = dt.astimezone()                                                                                    ## gettimezone
        return local_time.strftime("%H:%M")                                                                             ## 19:00 eg
    except ValueError:                                                                                                  ## except there is no timevalue then ve
        return "Unknown Error!"                                                                                         ## return "ue!", instead of actual problem

                                                                                                                        ##fetch order with api

def fetch_orders():                                                                                                     ## define order function
    log_message("[ INFO ]: Fetching orders...")                                                                         ## log
    try:                                                                                                                ## do
        active_orders = client.get_active()                                                                             ## get active order with client.api
        if not isinstance(active_orders, dict) or "orders" not in active_orders:                                        ## if orders is not in format of  raise a ve
            raise ValueError("Unexpected API response format.")                                                         ## raise error for api format
        orders_list = active_orders.get("orders", [])                                                                   ## put orders into a list
    except Exception as e:                                                                                              ## except a error then exit empty list
        log_message(f"[ ERROR ]: Error fetching active orders: {e}")                                                    ## log the message for error
        messagebox.showerror("Error", f"Error fetching active orders: {e}")                                             ## show messagebox for error
        return []                                                                                                       ## return empty list

    orders_data = []                                                                                                    ## init list for orders_data
    for order in orders_list:                                                                                           ## for order in orders list do this
        try:
            image_url = order.get("item_cover_image", {}).get("current_url", "")                                        ## get imageurl to display
            order_info = {                                                                                              ## init order info
                "name": order.get("item_name", "Unknown"),                                                              ## get the name of item
                "store_name": order.get("store_name", "Unknown"),                                                       ## get store name
                "address": order.get("pickup_location", {}).get("address", {}).get("address_line", "Unknown"),          ## get adress of order
                "longitude": order.get("pickup_location", {}).get("location", {}).get("longitude", "Unknown"),          ## alongside long
                "latitude": order.get("pickup_location", {}).get("location", {}).get("latitude", "Unknown"),            ## with lat
                "price": order.get("total_price", {}).get("minor_units", 0) / (                                         ## with price
                        10 ** order.get("total_price", {}).get("decimals", 2)),                                         ## calc order price to 2 decimals
                "currency": order.get("total_price", {}).get("code", "Unknown"),                                        ## get currency (mostly EUR for europe)
                "payment_method": order.get("payment_method_display_name", "Unknown"),                                  ## get payment method (paypal, klarna)
                "pickup_window": {                                                                                      ## init for a pickup window (time)
                    "start": format_time(order.get("pickup_interval", {}).get("start", "Unknown")),                     ## get starting window for pickup time
                    "end": format_time(order.get("pickup_interval", {}).get("end", "Unknown"))                          ## get end of pickup window
                },
                "image_url": image_url                                                                                  ## get image url
            }
            orders_data.append(order_info)                                                                              ## append this into the orders_data list
        except Exception as e:                                                                                          ## for exception do something
            log_message(f"[ FATAL ERROR ]: Skipping an order due to an error: {e}")                                     ## log message for fatal error and throw exception

    return orders_data                                                                                                  ## return orders_data for function


def display_orders():                                                                                                   ## define function for displaying orders
    log_message("[ INFO ]: Displaying orders...")                                                                       ## log message to term with display orders
    orders = fetch_orders()                                                                                             ## orders = fetch_orders() function
    if not orders:                                                                                                      ## if not orders then throw
        messagebox.showinfo("Info", "No active orders found.")                                                          ## messagebox throw info no active orders
        log_message("[ ERROR ]: No active orders found.")                                                               ## log the message to term
        return                                                                                                          ## return NOTHING?

    for widget in frame.winfo_children():                                                                               ## for widget in frame.winfo_children()
        widget.destroy()                                                                                                ## destroy widget

    for order in orders:                                                                                                ## if there is a order in orderslist then do following
        text = (f"{order['name']} - {order['store_name']}\n"                                                            ## ordername == storename
                f"Address: {order['address']}\n"                                                                        ## adress
                f"Price: {order['price']} {order['currency']}\n"                                                        ## price
                f"Payment: {order['payment_method']}\n"                                                                 ## payment method
                f"Pickup: {order['pickup_window']['start']} to {order['pickup_window']['end']}\n")                      ## pickup window
        label = tk.Label(frame, text=text, justify="left", padx=10, pady=5, anchor="w", font=("Arial", 10),             ## create label
                         bg="#f0f0f0", relief="ridge")
        label.pack(fill="x", pady=5)                                                                                    ## fix label with pady=5 and fill it into "x"

        if order["image_url"]:                                                                                          ## for image url do
            try:                                                                                                        ## try? fuckin do!
                response = requests.get(order["image_url"])                                                             ## if response is getted then check for image url
                img_data = BytesIO(response.content)                                                                    ## with byteIO do something with the image data
                img = Image.open(img_data)                                                                              ## open the image

                                                                                                                        ## Resize the image to fit within 150x150 but maintain aspect ratio
                max_size = (150, 150)                                                                                   ## maxsize == 150x150
                img.thumbnail(max_size, Image.Resampling.LANCZOS)                                                       ## dont ask me what this does

                img_tk = ImageTk.PhotoImage(img)                                                                        ## display the image
                img_label = tk.Label(frame, image=img_tk)                                                               ## display
                img_label.image = img_tk  # Keep reference to avoid garbage collection                                  ## more displaying
                img_label.pack(pady=5)                                                                                  ## pack pady do 5
            except Exception as e:                                                                                      ## except there is exception for the data
                log_message(f"[ ERROR ]: Failed to load image: {e}")                                                    ## log to term


def log_message(message):                                                                                               ## log message funciton used everywhere in this script
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")                                                            ## use datetime.now which does not work for some reason
    log_text.insert(tk.END, f"{timestamp} - {message}\n")                                                               ## log text insert the time
    log_text.yview(tk.END)  # Scroll to the bottom                                                                      ## do some tk stuff


def on_startup():                                                                                                       ## onstart function
    log_message("[ INFO ]: Application started.")                                                                       ## log to terminal
    display_orders()                                                                                                    ## Automatically fetch orders at startup


                                                                                                                        # GUI Setup
root = tk.Tk()
root.title("TGTG Orders")                                                                                               ## title for window "TGTG Orders"
root.geometry("500x600")                                                                                                ## 500x600 res for window
root.configure(bg="#ffffff")                                                                                            ## config bg to white

                                                                                                                        ## THIS IS IMPORTANT! Create Notebook (tab control)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

orders_tab = tk.Frame(notebook, bg="#ffffff")                                                                           ## Automatically fetch orders at startup
notebook.add(orders_tab, text="Orders")                                                                                 ## add text

log_tab = tk.Frame(notebook, bg="#ffffff")                                                                              ## Automatically fetch orders at startup
notebook.add(log_tab, text="Log")                                                                                       ## add text to notebook

def about():                                                                                                            ## define about function
    messagebox.showinfo("About","PythonTGTG Script for fetching Orders on Desktop")                                     ## little info in a msgbox


menu = Menu(root)                                                                                                       ## define menu as a root for tkinter
root.config(menu=menu)                                                                                                  ## actually use tkinter to config it now
filemenu = Menu(menu)                                                                                                   ## make filemenu a second var for menu
menu.add_cascade(label="File",menu=filemenu)                                                                            ## make title for filemenu "file"
filemenu.add_command(label="Exit",command=exit_applet)                                                                  ## exit app button
filemenu.add_command(label="Refetch",command=display_orders)
filemenu.add_command(label="Save Log",command=save_log)
filemenu.add_separator()
filemenu.add_command(label="About",command=about)

                                                                                                                        # Create a frame to hold order data
frame = tk.Frame(orders_tab, bg="#ffffff")                                                                              ## create background with white color
frame.pack(fill="both", expand=True, padx=10, pady=10)                                                                  ## pady/x 10 and fill it with param "both"

# Create a Text widget for logging
log_text = tk.Text(log_tab, wrap=tk.WORD, height=15, font=("Arial", 10), bg="#f0f0f0")                                  ## log to extra tab in tknotepad
log_text.pack(fill="both", expand=True, padx=10, pady=10)                                                               ## format some


                                                                                                                        ## Function to save log to a .log file
def save_log():                                                                                                         ## define savelog function
    try:                                                                                                                ## do
        log_content = log_text.get("1.0", tk.END)                                                                       ## Get all the log text
        with open("log_file.log", "w") as log_file:                                                                     ## Open the file in write mode
            log_file.write(log_content)                                                                                 ## Save log content to file
        log_message("[ INFO ]: Log file saved successfully.")                                                           ## log message
    except Exception as e:                                                                                              ## except exception as e
        log_message(f"[ ERROR ]: Error saving log file: {e}")                                                           ## throw error
        messagebox.showerror("Error", f"Error saving log file: {e}")                                                    ## show a msg box

root.after(1000, on_startup)                                                                                            ## Automatically fetch orders at startup
root.mainloop()                                                                                                         ## do mainloop
