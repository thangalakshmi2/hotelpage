
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from PIL import Image, ImageTk

class HotelManagement:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Management System")
        self.root.attributes('-fullscreen', True)  # Fullscreen
        self.root.configure(bg="lightblue")  # Set background color

        # Database connection
        self.conn = mysql.connector.connect(
            host="localhost",       
            user="root",   
            password="cs123",
            database="hotel_management6"
        )
        self.cursor = self.conn.cursor()

        self.create_tables()

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.bg_image = Image.open("image.jpg")  
        self.bg_image = self.bg_image.resize((screen_width, screen_height))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        bg_label = tk.Label(root, image=self.bg_photo)
        bg_label.place(relwidth=1, relheight=1)  

        title = tk.Label(root, text="Hotel Management System", font=("Arial", 24), bg="lightblue", fg="purple")
        title.pack(pady=50)

        book_btn = tk.Button(root, text="Book Room", font=("Arial", 14), command=self.book_room, bg="violet")
        book_btn.pack(pady=10)

        rooms_btn = tk.Button(root, text="View Available Rooms", font=("Arial", 14), command=self.view_rooms, bg="violet")
        rooms_btn.pack(pady=10)

        customers_btn = tk.Button(root, text="Customer Details", font=("Arial", 14), command=self.view_customers, bg="violet")
        customers_btn.pack(pady=10)

        delete_btn = tk.Button(root, text="Delete Customer", font=("Arial", 14), command=self.delete_customer, bg="violet")
        delete_btn.pack(pady=10)

        bill_btn = tk.Button(root, text="Generate Bill", font=("Arial", 14), command=self.generate_bill, bg="violet")
        bill_btn.pack(pady=10)

        exit_btn = tk.Button(root, text="Exit", font=("Arial", 14), command=root.destroy,bg="violet")
        exit_btn.pack(pady=10)

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS rooms (
                                room_no VARCHAR(10) PRIMARY KEY,
                                type VARCHAR(50),
                                price DECIMAL(10, 2))''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                                room_no VARCHAR(10) PRIMARY KEY,
                                name VARCHAR(100),
                                phone VARCHAR(15),
                                check_in_date DATE,
                                days_stayed INT,
                                FOREIGN KEY (room_no) REFERENCES rooms(room_no))''')

        self.cursor.execute('''INSERT IGNORE INTO rooms (room_no, type, price)
                               VALUES ('101', 'Single', 100.00), 
                                      ('102', 'Double', 150.00), 
                                      ('103', 'Suite', 250.00)''')
        self.conn.commit()

    def book_room(self):
        book_win = tk.Toplevel(self.root)
        book_win.title("Book a Room")
        book_win.configure(bg="lightblue")
        book_win.geometry("400x400")

        tk.Label(book_win, text="Room Type:", bg="pink").pack(pady=5)
        room_type = ttk.Combobox(book_win, values=["Single", "Double", "Suite"])
        room_type.pack(pady=5)

        tk.Label(book_win, text="Available Rooms:", bg="pink").pack(pady=5)
        room_list = ttk.Combobox(book_win)
        room_list.pack(pady=5)

        def update_rooms(event):
            selected_type = room_type.get()
            self.cursor.execute("SELECT room_no FROM rooms WHERE type = %s AND room_no NOT IN (SELECT room_no FROM customers)", (selected_type,))
            available_rooms = [room[0] for room in self.cursor.fetchall()]
            room_list['values'] = available_rooms

            room_type.bind("<<ComboboxSelected>>", update_rooms)

        tk.Label(book_win, text="Customer Name:", bg="pink").pack(pady=5)
        name_entry = tk.Entry(book_win)
        name_entry.pack(pady=5)

        tk.Label(book_win, text="Customer Phone:", bg="pink").pack(pady=5)
        phone_entry = tk.Entry(book_win)
        phone_entry.pack(pady=5)

        tk.Label(book_win, text="Days Stayed:", bg="pink").pack(pady=5)
        days_entry = tk.Entry(book_win)
        days_entry.pack(pady=5)

        def confirm_booking():
            room_no = room_list.get()
            name = name_entry.get()
            phone = phone_entry.get()
            days_stayed = days_entry.get()
            check_in_date = "2024-08-30"

            self.cursor.execute("SELECT * FROM rooms WHERE room_no = %s", (room_no,))
            room = self.cursor.fetchone()

            self.cursor.execute("SELECT room_no FROM customers WHERE room_no = %s", (room_no,))
            customer_room = self.cursor.fetchone()

            if room and not customer_room:
                self.cursor.execute("INSERT INTO customers (room_no, name, phone, check_in_date, days_stayed) VALUES (%s, %s, %s, %s, %s)",
                                    (room_no, name, phone, check_in_date, days_stayed))
                self.conn.commit()
                messagebox.showinfo("Success", f"Room {room_no} booked successfully!")
                book_win.destroy()
            else:
                messagebox.showerror("Error", "Room not available or already booked.")

        confirm_btn = tk.Button(book_win, text="Confirm Booking", command=confirm_booking, bg="green", fg="white")
        confirm_btn.pack(pady=10)

    def view_rooms(self):
        rooms_win = tk.Toplevel(self.root)
        rooms_win.title("Available Rooms")
        rooms_win.configure(bg="lightblue")
        rooms_win.geometry("300x200")

        self.cursor.execute("SELECT * FROM rooms WHERE room_no NOT IN (SELECT room_no FROM customers)")
        available_rooms = self.cursor.fetchall()

        for room in available_rooms:
            room_info = f"Room {room[0]}: {room[1]} - ${room[2]}"
            tk.Label(rooms_win, text=room_info, bg="violet").pack()

    def view_customers(self):
        cust_win = tk.Toplevel(self.root)
        cust_win.title("Customer Details")
        cust_win.configure(bg="lightblue")
        cust_win.geometry("300x250")

        self.cursor.execute("SELECT * FROM customers")
        customers = self.cursor.fetchall()

        for customer in customers:
            cust_info = f"Room {customer[0]} - {customer[1]} - {customer[2]} - Days Stayed: {customer[4]}"
            tk.Label(cust_win, text=cust_info, bg="lightblue").pack()

    def delete_customer(self):
        delete_win = tk.Toplevel(self.root)
        delete_win.title("Delete Customer")
        delete_win.configure(bg="lightblue")  
        delete_win.geometry("400x200")

        tk.Label(delete_win, text="Room Number:", bg="lightblue").pack(pady=5)
        room_entry = tk.Entry(delete_win)
        room_entry.pack(pady=5)

        def confirm_delete():
            room_no = room_entry.get()

            # Check if the customer exists
            self.cursor.execute("SELECT * FROM customers WHERE room_no = %s", (room_no,))
            customer = self.cursor.fetchone()

            if customer:
                self.cursor.execute("DELETE FROM customers WHERE room_no = %s", (room_no,))
                self.conn.commit()
                messagebox.showinfo("Success", f"Customer in Room {room_no} has been deleted.")
                delete_win.destroy()
            else:
                messagebox.showerror("Error", "Room number not found.")

        confirm_btn = tk.Button(delete_win, text="Delete", command=confirm_delete, bg="red", fg="white")
        confirm_btn.pack(pady=10)

    def generate_bill(self):
        bill_win = tk.Toplevel(self.root)
        bill_win.title("Generate Bill")
        bill_win.configure(bg="lightblue")
        bill_win.geometry("300x300")

        tk.Label(bill_win, text="Room Number:", bg="lightblue").pack(pady=5)
        room_entry = tk.Entry(bill_win)
        room_entry.pack(pady=5)

        def show_bill():
            room_no = room_entry.get()

            self.cursor.execute("SELECT * FROM customers WHERE room_no = %s", (room_no,))
            customer = self.cursor.fetchone()

            if customer:
                self.cursor.execute("SELECT price FROM rooms WHERE room_no = %s", (room_no,))
                room_price = self.cursor.fetchone()[0]
                total_price = room_price * customer[4] 

                bill_info = f"Customer Name: {customer[1]}\nPhone: {customer[2]}\nRoom Type: {customer[0]}\nTotal Bill: ${total_price}"
                tk.Label(bill_win, text=bill_info, bg="lightblue").pack(pady=20)
            else:
                messagebox.showerror("Error", "Room number ")
        show_bill_btn=tk.Button(bill_win,text="show Bill",command=show_bill,bg="yellow",fg="blue")
        show_bill_btn.pack(pady=10)
if __name__=="__main__":
    root=tk.Tk()
    app=HotelManagement(root)
    root.mainloop()
