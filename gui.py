from tkinter import Tk, Label, Button, Spinbox, Frame, Canvas
import sort

# Function to clear the quantities
def clear_order(order):
    for spinbox in order:
        spinbox.delete(0, 'end')
        spinbox.insert(0, 0)

# Function to create a new order frame
def create_order_frame(root, order_num):
    frame = Frame(root, width=600)
    frame.pack(fill='x', padx=10, pady=5)
    
    Label(frame, text=f'Order {order_num}', font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5)
    Label(frame, text='Quantity', font=("Arial", 14)).grid(row=0, column=1, padx=10, pady=5)
    
    # Large product
    large_spinbox = Spinbox(frame, from_=0, to=100, width=5, font=("Arial", 14))
    large_spinbox.grid(row=0, column=2, padx=5)
    
    # Medium product
    medium_spinbox = Spinbox(frame, from_=0, to=100, width=5, font=("Arial", 14))
    medium_spinbox.grid(row=0, column=3, padx=5)
    
    # Small product
    small_spinbox = Spinbox(frame, from_=0, to=100, width=5, font=("Arial", 14))
    small_spinbox.grid(row=0, column=4, padx=5)
    
    Button(frame, text='Clear', command=lambda: clear_order([large_spinbox, medium_spinbox, small_spinbox]), font=("Arial", 14)).grid(row=0, column=5, padx=5)
    
    # Separator line
    Canvas(frame, height=2, bg="black").grid(row=1, columnspan=6, sticky="we", pady=(10, 0))

    return large_spinbox, medium_spinbox, small_spinbox

# Function to handle submit button click
def submit():
    global stackOrder
    global isSubmitOrder
    stackOrder = []

    for i, order in enumerate(orders, start=1):
        large, medium, small = [spinbox.get() for spinbox in order]
        print(f"Order {i}: Large={large}, Medium={medium}, Small={small}")
        stackOrder.append([int(large),int(medium),int(small)])

    isSubmitOrder = True
    root.destroy()  # Close the form

# Function to show the form
def show_form():
    global root
    root = Tk()
    root.title('Order Management System')
    root.geometry('600x360')
    root.attributes('-topmost', True) 

    # Header labels
    header_frame = Frame(root, width=600)
    header_frame.pack(fill='x', padx=10, pady=(10, 5))

    Label(header_frame, text='', font=("Arial", 14)).grid(row=1, column=2, padx=90)  # Empty cell for alignment
    Label(header_frame, text='Large', font=("Arial", 14)).grid(row=1, column=3, padx=10)
    Label(header_frame, text='Medium', font=("Arial", 14)).grid(row=1, column=4, padx=10)
    Label(header_frame, text='Small', font=("Arial", 14)).grid(row=1, column=5, padx=10)

    # Creating the order frames
    global orders
    orders = [create_order_frame(root, i) for i in range(1, 5)]

    # Submit button
    submit_button = Button(root, text='Submit', font=("Arial", 14), command=submit)
    submit_button.pack(side='right', padx=10, pady=10)

    root.mainloop()

