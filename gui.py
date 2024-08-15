from tkinter import Tk, Label, Button, Spinbox, Frame, Canvas, messagebox

isSubmitOrder = False

# Function to clear the quantities
def clear_order(order):
    for spinbox in order:
        spinbox.delete(0, 'end')
        spinbox.insert(0, 0)

# Function to create a new order frame
def create_order_frame(root, order_num):
    frame = Frame(root, width=800)
    frame.pack(fill='x', padx=10, pady=6)
    
    Label(frame, text=f'Order {order_num}', font=("Arial", 18)).grid(row=0, column=0, padx=5)
    Label(frame, text='Quantity', font=("Arial", 18)).grid(row=0, column=1, padx=10)
    
    # Large product
    large_spinbox = Spinbox(frame, from_=0, to=100, width=5, font=("Arial", 18))
    large_spinbox.grid(row=0, column=2, padx=5, ipady=12)
    
    # Medium product
    medium_spinbox = Spinbox(frame, from_=0, to=100, width=5, font=("Arial", 18))
    medium_spinbox.grid(row=0, column=3, padx=5, ipady=12)
    
    # Small product
    small_spinbox = Spinbox(frame, from_=0, to=100, width=5, font=("Arial", 18))
    small_spinbox.grid(row=0, column=4, padx=5, ipady=12)
    
    Button(frame, text='Clear', command=lambda: clear_order([large_spinbox, medium_spinbox, small_spinbox]), font=("Arial", 18)).grid(row=0, column=5, padx=5)
    
    # Separator line
    Canvas(frame, height=2, bg="black").grid(row=1, columnspan=6, sticky="we", pady=(10, 0))

    return large_spinbox, medium_spinbox, small_spinbox

# Function to handle submit button click
def submit():
    global stackOrder
    global isSubmitOrder
    stackOrder = []

    for i, order in enumerate(orders, start=1):
        large, medium, small = [int(spinbox.get()) for spinbox in order]
        total_quantity = large + medium + small

        if total_quantity >= 4:
            messagebox.showerror("Error", f"Order {i} must have under 3 items in total.")
            return  # Exit the function if any order has fewer than 4 items

        print(f"Order {i}: Large={large}, Medium={medium}, Small={small}")
        stackOrder.append([large, medium, small])

    isSubmitOrder = True  # Set the flag to True
    root.destroy()  # Close the form

# Function to show the form
def show_form():
    global root
    global isSubmitOrder
    root = Tk()
    root.title('Order Management System')
    root.resizable(False, False)
    # Center the form on the screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - root.winfo_reqwidth()*4) // 2
    y = (screen_height - root.winfo_reqheight()*3) // 2
    root.geometry(f'+{x}+{y}')
    root.attributes('-topmost', True) 

    # Header labels
    header_frame = Frame(root, width=800)
    header_frame.pack(fill='x', padx=10, pady=(5, 0))

    Label(header_frame, text='', font=("Arial", 18)).grid(row=1, column=2, padx=105)  # Empty cell for alignment
    Label(header_frame, text='Large', font=("Arial", 18)).grid(row=1, column=3, padx=10)
    Label(header_frame, text='Medium', font=("Arial", 18)).grid(row=1, column=4, padx=10)
    Label(header_frame, text='Small', font=("Arial", 18)).grid(row=1, column=5, padx=10)

    # Creating the order frames
    global orders
    orders = [create_order_frame(root, i) for i in range(1, 5)]

    # Submit button
    submit_button = Button(root, text='Submit', font=("Arial", 18), command=submit)
    submit_button.pack(side='right', padx=15, pady=10)

    root.mainloop()

show_form()
