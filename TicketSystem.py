import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
import pickle
import os


# Base Customer Class
class Customer:
    def __init__(self, customer_id: int, name: str, email: str, password: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.password = password
        self.order_history = []  # List of Order objects

    def add_order(self, order):
        self.order_history.append(order)


# Ticket Classes
class Ticket:
    def __init__(self, ticket_id: int, ticket_type: str, price: float, validity: str, discount: float = 0.0):
        self.ticket_id = ticket_id
        self.ticket_type = ticket_type
        self.price = price
        self.validity = validity
        self.discount = discount

    def calculate_price(self):
        return self.price * (1 - self.discount)


# Order Class
class Order:
    def __init__(self, order_id: int, customer_name: str):
        self.order_id = order_id
        self.customer_name = customer_name
        self.tickets = []  # List of Ticket objects
        self.total_amount = 0.0
        self.date = datetime.now()

    def add_ticket(self, ticket: Ticket):
        self.tickets.append(ticket)
        self.calculate_total()

    def calculate_total(self):
        self.total_amount = sum(ticket.calculate_price() for ticket in self.tickets)
        return self.total_amount

    def display_summary(self):
        ticket_summary = "\n".join([f"{ticket.ticket_type}: {ticket.calculate_price()}" for ticket in self.tickets])
        return (
            f"Order ID: {self.order_id}\nCustomer: {self.customer_name}\n"
            f"Tickets:\n{ticket_summary}\nTotal: {self.total_amount:.2f} DHS\nDate: {self.date.strftime('%Y-%m-%d %H:%M:%S')}"
        )


# Admin Dashboard Class
class AdminDashboard:
    def __init__(self):
        self.sales_data = []  # List of Orders
        self.capacity = 10000  # Maximum daily capacity
        self.ticket_sales = {}  # Track number of tickets sold per type

    def add_sale(self, order):
        self.sales_data.append(order)
        for ticket in order.tickets:
            self.ticket_sales[ticket.ticket_type] = self.ticket_sales.get(ticket.ticket_type, 0) + 1

    def view_sales_summary(self):
        if not self.sales_data:
            return "No sales recorded yet."
        summary = "\n\n".join([order.display_summary() for order in self.sales_data])
        return f"Sales Summary:\n{summary}"

    def view_ticket_sales(self):
        if not self.ticket_sales:
            return "No tickets sold yet."
        return "\n".join([f"{ticket_type}: {count}" for ticket_type, count in self.ticket_sales.items()])


# GUI Application
class TicketBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Adventure Land Ticket Booking")
        self.root.geometry("800x600")

        # Initialize data
        self.customers = self.load_data("customers.pkl") or {}  # email -> Customer object
        self.orders = []  # List of all orders
        self.current_customer = None
        self.current_order = None
        self.ticket_id_counter = 1001
        self.order_id_counter = 2001

        # Ticket types
        self.available_tickets = self.load_data("tickets.pkl") or [
            Ticket(101, "Single Day Pass", 275, "1 Day"),
            Ticket(102, "Two-Day Pass", 480, "2 Days"),
            Ticket(103, "Annual Membership", 1840, "1 Year", 0.15),
            Ticket(104, "Child Ticket", 185, "1 Day"),
            Ticket(105, "Group Ticket (10+)", 220, "1 Day", 0.2),
            Ticket(106, "VIP Experience", 550, "1 Day"),
        ]

        # Admin dashboard
        self.admin_dashboard = self.load_data("admin_dashboard.pkl") or AdminDashboard()

        # Predefined admin credentials
        self.admin_credentials = {"admin": "admin123"}

        # Build UI
        self.build_login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def save_data(self, filename, data):
        with open(filename, "wb") as file:
            pickle.dump(data, file)

    def load_data(self, filename):
        if os.path.exists(filename):
            with open(filename, "rb") as file:
                return pickle.load(file)
        return None

    # --- Login Screen ---
    def build_login_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Adventure Land Ticket Booking", font=("Arial", 20)).pack(pady=20)
        tk.Label(self.root, text="Login or Create an Account", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Email/Username:").pack(pady=5)
        self.email_entry = tk.Entry(self.root, width=30)
        self.email_entry.pack()

        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, width=30, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.root, text="Create Account", command=self.create_account_screen).pack(pady=5)
        tk.Button(self.root, text="Admin Login", command=self.admin_login).pack(pady=5)

    # --- Admin Login ---
    def admin_login(self):
        username = self.email_entry.get()
        password = self.password_entry.get()

        if username in self.admin_credentials and self.admin_credentials[username] == password:
            self.build_admin_dashboard()
        else:
            messagebox.showerror("Error", "Invalid admin credentials.")

    # --- Admin Dashboard ---
    def build_admin_dashboard(self):
        self.clear_screen()
        tk.Label(self.root, text="Admin Dashboard", font=("Arial", 20)).pack(pady=20)

        # Admin functionalities
        tk.Button(self.root, text="View Ticket Sales Summary", command=self.view_ticket_sales_summary).pack(pady=10)
        tk.Button(self.root, text="Manage Tickets", command=self.manage_tickets).pack(pady=10)
        tk.Button(self.root, text="Manage Users", command=self.manage_users).pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.build_login_screen).pack(pady=10)

        self.save_data("admin_dashboard.pkl", self.admin_dashboard)

    def view_ticket_sales_summary(self):
        self.clear_screen()
        tk.Label(self.root, text="Ticket Sales Summary", font=("Arial", 20)).pack(pady=20)

        summary = self.admin_dashboard.view_ticket_sales()
        tk.Label(self.root, text=summary, font=("Arial", 14), anchor="w", justify="left").pack(pady=20)

        tk.Button(self.root, text="Back to Admin Dashboard", command=self.build_admin_dashboard).pack(pady=10)

    # --- Manage Tickets ---
    def manage_tickets(self):
        self.clear_screen()
        tk.Label(self.root, text="Manage Tickets", font=("Arial", 20)).pack(pady=20)

        # Display all tickets with Delete buttons
        for ticket in self.available_tickets:
            frame = tk.Frame(self.root)
            frame.pack(pady=5, anchor="w", padx=20)

            # Display ticket details
            ticket_details = f"{ticket.ticket_id}: {ticket.ticket_type} - {ticket.price} DHS ({ticket.validity})"
            tk.Label(frame, text=ticket_details, font=("Arial", 12), anchor="w", justify="left").pack(side="left")

            # Delete button for the ticket
            delete_button = tk.Button(frame, text="Delete", command=lambda t=ticket: self.delete_ticket(t), bg="red", fg="white")
            delete_button.pack(side="right", padx=10)

        # Add a button to go back or add new tickets
        tk.Button(self.root, text="Add Ticket", command=self.add_ticket_screen).pack(pady=10)
        tk.Button(self.root, text="Back to Admin Dashboard", command=self.build_admin_dashboard).pack(pady=20)

    def delete_ticket(self, ticket):
        """Delete a ticket and update the data file."""
        if ticket in self.available_tickets:
            self.available_tickets.remove(ticket)
            self.save_data("tickets.pkl", self.available_tickets)
            messagebox.showinfo("Success", "Ticket deleted successfully!")
            self.manage_tickets()
        else:
            messagebox.showerror("Error", "Ticket not found!")

    def add_ticket_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Add New Ticket", font=("Arial", 20)).pack(pady=20)

        tk.Label(self.root, text="Ticket Type:").pack(pady=5)
        ticket_type_entry = tk.Entry(self.root, width=30)
        ticket_type_entry.pack()

        tk.Label(self.root, text="Price:").pack(pady=5)
        price_entry = tk.Entry(self.root, width=30)
        price_entry.pack()

        tk.Label(self.root, text="Validity:").pack(pady=5)
        validity_entry = tk.Entry(self.root, width=30)
        validity_entry.pack()

        def save_ticket():
            ticket_type = ticket_type_entry.get()
            price = float(price_entry.get())
            validity = validity_entry.get()

            new_ticket = Ticket(self.ticket_id_counter, ticket_type, price, validity)
            self.ticket_id_counter += 1
            self.available_tickets.append(new_ticket)
            self.save_data("tickets.pkl", self.available_tickets)

            messagebox.showinfo("Success", "New ticket added!")
            self.manage_tickets()

        tk.Button(self.root, text="Save Ticket", command=save_ticket).pack(pady=10)
        tk.Button(self.root, text="Back to Manage Tickets", command=self.manage_tickets).pack(pady=10)

    # --- Manage Users ---
    def manage_users(self):
        self.clear_screen()
        tk.Label(self.root, text="Manage Users", font=("Arial", 20)).pack(pady=20)

        # Display all users with Delete buttons
        for email, customer in list(self.customers.items()):
            frame = tk.Frame(self.root)
            frame.pack(pady=5, anchor="w", padx=20)

            # Display user details
            customer_details = f"{customer.customer_id}: {customer.name} ({customer.email})"
            tk.Label(frame, text=customer_details, font=("Arial", 12), anchor="w", justify="left").pack(side="left")

            # Delete button for the user
            delete_button = tk.Button(frame, text="Delete", command=lambda e=email: self.delete_user(e), bg="red", fg="white")
            delete_button.pack(side="right", padx=10)

        tk.Button(self.root, text="Back to Admin Dashboard", command=self.build_admin_dashboard).pack(pady=20)
    def delete_user(self, email):
        """Delete a user and update the data file."""
        if email in self.customers:
            del self.customers[email]
            self.save_data("customers.pkl", self.customers)
            messagebox.showinfo("Success", "User deleted successfully!")
            self.manage_users()
        else:
            messagebox.showerror("Error", "User not found!")
    # --- Customer Side ---
    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if email in self.customers and self.customers[email].password == password:
            self.current_customer = self.customers[email]
            self.ticket_selection_screen()
        else:
            messagebox.showerror("Error", "Invalid email or password.")

    def create_account_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Create an Account", font=("Arial", 20)).pack(pady=20)

        tk.Label(self.root, text="Name:").pack(pady=5)
        self.name_entry = tk.Entry(self.root, width=30)
        self.name_entry.pack()

        tk.Label(self.root, text="Email:").pack(pady=5)
        self.email_entry = tk.Entry(self.root, width=30)
        self.email_entry.pack()

        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, width=30, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Create Account", command=self.create_account).pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.build_login_screen).pack(pady=5)

    def create_account(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        if email in self.customers:
            messagebox.showerror("Error", "An account with this email already exists.")
            return

        if not name or not email or not password:
            messagebox.showerror("Error", "All fields are required.")
            return

        new_customer = Customer(customer_id=len(self.customers) + 1, name=name, email=email, password=password)
        self.customers[email] = new_customer
        self.save_data("customers.pkl", self.customers)

        messagebox.showinfo("Success", "Account created successfully!")
        self.build_login_screen()

    def ticket_selection_screen(self):
        self.clear_screen()
        tk.Label(self.root, text=f"Welcome, {self.current_customer.name}", font=("Arial", 20)).pack(pady=20)
        tk.Label(self.root, text="Select a Ticket", font=("Arial", 14)).pack(pady=10)

        for ticket in self.available_tickets:
            ticket_details = f"{ticket.ticket_type} - {ticket.price} DHS ({ticket.validity})"
            tk.Button(
                self.root,
                text=ticket_details,
                command=lambda t=ticket: self.add_ticket_to_order(t),
                width=50
            ).pack(pady=5)

        tk.Button(self.root, text="Finalize Order", command=self.finalize_order).pack(pady=10)
        tk.Button(self.root, text="View Order History", command=self.view_order_history).pack(pady=10)
        tk.Button(self.root, text="Logout", command=self.build_login_screen).pack(pady=5)

    def add_ticket_to_order(self, ticket):
        if not self.current_order:
            self.current_order = Order(
                order_id=self.order_id_counter,
                customer_name=self.current_customer.name
            )
            self.order_id_counter += 1

        self.current_order.add_ticket(ticket)
        messagebox.showinfo("Success", f"{ticket.ticket_type} added to your order!")

    def finalize_order(self):
        if not self.current_order or not self.current_order.tickets:
            messagebox.showerror("Error", "No tickets added to the order.")
            return

        self.payment_interface()

    def payment_interface(self):
        self.clear_screen()
        tk.Label(self.root, text="Payment Interface", font=("Arial", 20)).pack(pady=20)
        tk.Label(self.root, text="Choose Payment Method:", font=("Arial", 14)).pack(pady=10)

        def confirm_payment(method):
            self.current_customer.add_order(self.current_order)
            self.admin_dashboard.add_sale(self.current_order)

            self.save_data("customers.pkl", self.customers)
            self.save_data("admin_dashboard.pkl", self.admin_dashboard)

            self.current_order = None
            messagebox.showinfo("Success", f"Payment successful using {method}!")
            self.ticket_selection_screen()

        tk.Button(self.root, text="Credit Card", command=lambda: confirm_payment("Credit Card")).pack(pady=10)
        tk.Button(self.root, text="Debit Card", command=lambda: confirm_payment("Debit Card")).pack(pady=10)

        tk.Button(self.root, text="Back to Tickets", command=self.ticket_selection_screen).pack(pady=10)

    def view_order_history(self):
        self.clear_screen()
        tk.Label(self.root, text="Order History", font=("Arial", 20)).pack(pady=20)

        if not self.current_customer.order_history:
            tk.Label(self.root, text="No orders found.", font=("Arial", 14)).pack(pady=10)
        else:
            for order in self.current_customer.order_history:
                order_summary = order.display_summary()
                tk.Label(self.root, text=order_summary, font=("Arial", 12), anchor="w", justify="left").pack(pady=10)

        tk.Button(self.root, text="Back", command=self.ticket_selection_screen).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = TicketBookingApp(root)
    root.mainloop()
