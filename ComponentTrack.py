import tkinter as tk # Importing tkinter and shortening it to tk. 
from tkinter import ttk # Importing ttk for treeview.
import csv # Importing csv for data handling
import os # Importing os to check if files exists
from datetime import datetime # Importing datetime to record time for logs
import hashlib # Importing to hash password

def hashPassword(password): # takes password and hashes it
    return hashlib.sha256(password.encode()).hexdigest()

StockThreshold = 5 # Global variable for minimum stock threshold before being considered low

class Component: # Class for all components
    def __init__(self, name, sku, quantity, status): # Initialises component with a name, sku, quantity and a status
        self.name = name
        self.sku = sku
        self.quantity = int(quantity)
        self.status = status
    
    def lowStock(self): # Checks if stock is low
        return self.quantity <= StockThreshold
    
    def columnList(self): # Returns component data in column form
        return [self.name, self.sku, str(self.quantity), self.status]
    

class Logger: # Handles logs
    def __init__(self, logfile="logs.csv"): # Sets up logs file
        self.logfile = logfile
        if not os.path.exists(self.logfile):
            with open(self.logfile, "w", newline = "") as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Action", "SKU"])
    
    def log(self, action, sku="N/A"): # Adds new log entries with sku deafaulted to N/A
        with open(self.logfile, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now(), action, sku])

    def readLogs(self): # Reads all entries from log file
        logs = []
        try:
            with open(self.logfile, "r", newline = "") as file:
                csvreader = csv.DictReader(file)
                for row in csvreader:
                    logs.append(row)
        except FileNotFoundError:
            pass
        return logs
    

class Authentication: # All authentication
    def __init__(self,users_file = "users.csv"):
        self.users_file = users_file
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w", newline = "") as file:
                writer = csv.writer(file)
                writer.writerow(["username", "password_hash"])
                writer.writerow(["test", hashPassword("test123")])

    def userValidation(self, username, password): # Validates users entered login details
        hashed_pass = hashPassword(password)
        try:
            with open(self.users_file, "r", newline = "") as file:
                csvreader = csv.DictReader(file)
                for row in csvreader:
                    if row["username"] == username and row["password_hash"] == hashed_pass:
                        return True
        except FileNotFoundError:
            pass
        return False
    
class InventoryManager: # Manages inventory data stored in the file
    def __init__(self, filename ="inventory.csv"):
        self.filename = filename

        with open(self.filename, "a+", newline = "") as file:
            file.seek(0)
            csvreader = csv.reader(file)
            headers = next(csvreader, None)

            if headers != ["Item Name", "SKU", "Quantity", "Status"]: # Checks if headers are valid
                file.seek(0) # Moves pointer to beginning
                rows = list(csvreader) # reads file and makes it into a list
                file.seek(0)
                file.truncate() # Clears contents of file

                writer = csv.writer(file)
                writer.writerow(["Item Name", "SKU", "Quantity", "Status"])
                writer.writerows(rows)

    def load(self): # Loads all components from file
        components = []
        with open(self.filename, "r", newline = "") as file:
            csvreader = csv.DictReader(file) # Reads rows as dictionaries

            fields = {"Item Name", "SKU", "Quantity", "Status"}
            if not fields.issubset(csvreader.fieldnames): # Checks if all fields are in the file
                return components
            
            for row in csvreader: # Creates components from row data in these columns
                components.append(Component(row["Item Name"], row["SKU"], row["Quantity"], row["Status"]))
        return components
    
    def skuExists(self, sku): # Checks if sku already exists in file
        components = self.load()
        for component in components:
            if component.sku == sku:
                return True
        return False
    
    def add(self, component): # Adds new component to the file
        with open(self.filename, "a", newline = "") as file:
            writer = csv.DictWriter(file, fieldnames = ["Item Name", "SKU", "Quantity", "Status"])
            writer.writerow({"Item Name": component.name, "SKU": component.sku, "Quantity": component.quantity, "Status": component.status})

    def remove(self, sku): # Removes components from file
        rows = []
        removed = False
        with open(self.filename, "r", newline = "") as file:
            csvreader = csv.DictReader(file)
            for row in csvreader:
                if row["SKU"] != sku:
                    rows.append(row)
                else:
                    removed = True

        if removed == True: 
            with open(self.filename, "w", newline = "") as file:
                writer = csv.DictWriter(file, fieldnames = ["Item Name", "SKU", "Quantity", "Status"])
                writer.writeheader()
                writer.writerows(rows)
       
        return removed
    
    def updateQuantity(self, sku, new_quantity): # Updates the quanitity of a component
        rows = []
        updated = False
        with open(self.filename, "r", newline = "") as file:
            csvreader = csv.DictReader(file)
            for row in csvreader:
                if row["SKU"] == sku:
                    row["Quantity"] = str(new_quantity)
                    row["Status"] = "Low Stock" if int(new_quantity) <= StockThreshold else "Sufficient Stock"
                    updated = True
                rows.append(row)
    
        if updated:
            with open(self.filename, "w", newline = "") as file:
                writer = csv.DictWriter(file, fieldnames=["Item Name", "SKU", "Quantity", "Status"])
                writer.writeheader()
                writer.writerows(rows)
        return updated



class LoginWindow: # Creates login gui window 
    def __init__(self, root, main):
        self.root = root
        self.main = main
        self.root.title("Login") # Setting window title
        self.root.geometry("600x300") # Setting window size
        self.font_size = ("Arial", 16) # sets font_size to 16 which is bigger as it was too small
  
        self.frame = tk.Frame(root)# Puts the login area into a frame
        self.frame.place(relx = 0.5, rely = 0.5, anchor = "center") # Centres the frame into the middle of the screen

        tk.Label(self.frame, text = "Login", font = self.font_size).grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "Username", font = self.font_size).grid(row = 1, column = 0)
        tk.Label(self.frame, text = "Password", font = self.font_size).grid(row = 2, column = 0)

        self.username_entry = tk.Entry(self.frame, font = self.font_size)
        self.password_entry = tk.Entry(self.frame, font = self.font_size, show = "*") # Password will show as '*' when typing
        self.username_entry.grid(row = 1, column = 1)
        self.password_entry.grid(row = 2, column = 1)

        self.login_button = tk.Button(self.frame, text = "Login", font = self.font_size, command = self.login)
        self.login_button.grid(row = 3, column = 0, columnspan = 2)

        self.result_label = tk.Label(self.frame, text = "",  font = self.font_size)
        self.result_label.grid(row = 4, column = 0, columnspan = 2)

    def login(self): # Login confirmation function
        entered_username = self.username_entry.get().strip()
        entered_password = self.password_entry.get().strip() #Getting the inputted username and password and assigning them to variables.

        if self.main.auth.userValidation(entered_username, entered_password):
            self.result_label.config(text = "Login Success")
            self.main.logger.log("Login Success", "N/A")
            self.frame.destroy() # Removes login window for an extra layer of security
            InventoryWindow(self.root, self.main)
        else:
            self.result_label.config(text = "Login Failed")
            self.main.logger.log("Login Failed", "N/A")


class InventoryWindow: # Creates actual component management window
    def __init__(self, root, main):
        self.root = root
        self.main = main
        self.window = tk.Toplevel(root)
        self.window.title("Component Tracker")
        self.window.geometry("900x600")
        self.font_size = ("Arial", 16)
        self.inventory = main.inventory

        tk.Label(self.window, text = "Component Tracker", font = self.font_size).pack(pady = 10)
         
        self.inputFrame = tk.Frame(self.window)
        self.inputFrame.pack(pady=10)

        tk.Label(self.inputFrame, text = "Item Name", font = self.font_size).grid(row = 0, column = 0)
        tk.Label(self.inputFrame, text = "SKU", font = self.font_size).grid(row = 1, column = 0)
        tk.Label(self.inputFrame, text = "Quantity", font = self.font_size).grid(row = 2, column = 0)
 
        self.item_entry = tk.Entry(self.inputFrame, font = self.font_size)
        self.sku_entry = tk.Entry(self.inputFrame, font = self.font_size)
        self.quantity_entry = tk.Entry(self.inputFrame, font = self.font_size)
        self.item_entry.grid(row = 0, column = 1)
        self.sku_entry.grid(row = 1, column = 1)
        self.quantity_entry.grid(row = 2, column = 1)

        tk.Button(self.inputFrame, text = "Add Item", font = self.font_size, command = self.addItem).grid(row = 3, column = 0)
        tk.Button(self.inputFrame, text = "Remove Item", font = self.font_size, command = self.removeItem).grid(row = 3, column = 1)
        tk.Button(self.inputFrame, text = "Search Item", font = self.font_size, command = self.searchItem).grid(row = 3, column = 2)
        tk.Button(self.inputFrame, text = "Logs", font = self.font_size, command = self.openLogs).grid(row = 3, column = 3)
        tk.Button(self.inputFrame, text = "Update Quantity", font = self.font_size, command = self.updateQuantity).grid(row = 3, column = 4)
        tk.Button(self.inputFrame, text="Show All", font=self.font_size, command=self.loadInventory).grid(row=4, column=2)

        self.message_label = tk.Label(self.window, text = "", font = self.font_size)
        self.message_label.pack()

        self.tree = ttk.Treeview(self.window, columns=("Item Name", "SKU", "Quantity", "Status"), show = "headings") # Displays data in a table using treeview
        for column in ("Item Name", "SKU", "Quantity", "Status"):
            self.tree.heading(column, text = column)
            self.tree.column(column, width = 200)
        self.tree.pack(pady = 10, fill = "both", expand = True)

        self.loadInventory()

    def loadInventory(self): # Refreshes the treeview with current data
        self.tree.delete(*self.tree.get_children())
        for component in self.inventory.load():
            self.tree.insert("", "end", values = component.columnList())

    def addItem(self): # Handles adding an component to inventory
        name =  self.item_entry.get().strip()
        sku = self.sku_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
 
        if not name or not sku or not quantity:
            self.message_label.config(text = "All fields required")
            return
        if not sku.isdigit() or int(sku) <= 0:
            self.message_label.config(text = "SKU must be a positive number")
            return
        if not quantity.isdigit() or int(quantity) <= 0:
            self.message_label.config(text = "Quantity must be a positive number")
            return
        
        if self.inventory.skuExists(sku):
            self.message_label.config(text = "Item already exists")
            return
        
        status = ""

        if int(quantity) <= StockThreshold: # Uses global variable to check if quantity of stock is low
            status = "Low Stock"
        else:
            status = "Sufficient Stock"
        
        comp = Component(name, sku, quantity, status)
        self.inventory.add(comp)
        self.main.logger.log("Item added", sku)
        self.loadInventory()

    def removeItem(self): # Removes item from inventory
        sku = self.sku_entry.get().strip()
        if not sku:
            self.message_label.config(text = "Enter SKU to remove")
            return
        if self.inventory.remove(sku):
            self.message_label.config(text = "Item removed")
            self.main.logger.log("Item removed", sku)
        else:
            self.message_label.config(text = "Item not found")
        self.loadInventory()

    def searchItem(self): # Searches for and only displays item with given SKU
        sku = self.sku_entry.get().strip()
        if not sku:
            self.message_label.config(text = "Enter SKU to search")
            return
        self.tree.delete(*self.tree.get_children())
        found = False
        for component in self.inventory.load():
            if component.sku == sku:
                self.tree.insert("", "end", values = component.columnList())
                found = True
        if found == True:
            self.message_label.config(text = "Item found")
        else:
            self.message_label.config(text = "Item not found")

    def openLogs(self): # Opens the logs window
        LogsWindow(self.root, self.main)

    def updateQuantity(self):
        sku = self.sku_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
    
        if not sku or not quantity:
            self.message_label.config(text="Enter SKU and quantity")
            return
        if not quantity.isdigit() or int(quantity) <= 0:
            self.message_label.config(text="Quantity must be a positive number")
            return
    
        if self.inventory.updateQuantity(sku, int(quantity)):
            self.message_label.config(text="Quantity updated")
            self.main.logger.log("Quantity updated", sku)
            self.loadInventory()
        else:
            self.message_label.config(text="Item not found")

class LogsWindow: # Creates a logs window with the logger data.
    def __init__(self, root, main):
        self.window = tk.Toplevel(root)
        self.window.title("Logs")
        self.window.geometry("600x600")

        tree = ttk.Treeview(self.window, columns=("Timestamp", "Action", "SKU"), show = "headings") # Uses treeview to make a table for logger window

        for column in ("Timestamp", "Action", "SKU"):
            tree.heading(column, text = column)
            tree.column(column, width = 220)

        tree.pack(fill = "both", expand = True, pady = 10)

        for log in main.logger.readLogs():
            tree.insert("", "end", values = (log["Timestamp"], log["Action"], log["SKU"]))

class Main: # Initalises whole program
    def __init__(self):
        self.auth = Authentication() # Handles login details
        self.logger = Logger() # Logger details
        self.inventory = InventoryManager() # Creating an instance of the inventory manager
        self.root = tk.Tk() # Creates main tkinter window
        LoginWindow(self.root, self) # Creates and displays login window
        self.root.mainloop() # Starts program

Main() # Creates an instance of main to start the program
