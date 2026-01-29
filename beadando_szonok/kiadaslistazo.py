from email.utils import parsedate_to_datetime
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
import mysql.connector
from datetime import datetime, timedelta
import pandas as pd
import locale

locale.setlocale(locale.LC_ALL, '')  # Set the locale to the default system locale


db=mysql.connector.connect(
    host="localhost",
    user="root",
    password="***",
    database="dbs"
    )

cur=db.cursor()
#cur.execute("CREATE DATABASE dbs")
# cur.execute("CREATE TABLE Data (Kezelő VARCHAR(50), Időpont TIMESTAMP, Név VARCHAR(50), Bér INT(10), Motiváció INT(10), Megjegyzés VARCHAR(200) )")
# db.commit()
# cur.execute("SELECT * FROM Loginfo")
# for x in cur:
#     print(x)


def login():
  global una
  una=entry_un.get()
  pwd=entry_pw.get()
  cur.execute("SELECT * FROM Loginfo WHERE una=%s and pwd=%s", [(una),(pwd)])
  res=cur.fetchall()
  if res and una=="admin":      
      window.destroy()      
      adwin()
  elif res:
      window.destroy()
      uswin()
  else:
     messagebox.showinfo("","Hibás adatok!")

def adwin():
    # Admin window
    awindow=ttk.Window(themename='darkly')
    awindow.title('KPadmin')
    awindow.geometry(f"{winwid}x{winhei}+{xco}+{yco}")
    awindow.focus_force()
    def uman(): 

        def uadd():
            def regus():
                una=uane.get()
                pwd=uape.get()
                sql="INSERT INTO Loginfo (una, pwd) VALUES (%s,%s)"
                val=(una,pwd)
                cur.execute(sql,val)
                db.commit()
                uane.delete(0, tk.END)
                uape.delete(0, tk.END)
                update_ulist()
                uane.focus_force()
            def on_ent(event=None):
                uab.invoke()
                
            uaw=ttk.Window(themename='darkly')
            uaw.geometry(f"{winwid}x{winhei-100}+{xco}+{yco}")
            uaw.title("Add user")
            uaw.bind('<Return>', on_ent)
            uane=ttk.Entry(master=uaw)            
            uane.focus_force()
            uane.pack(pady=20)
           
            uape=ttk.Entry(master=uaw)
            uape.pack(pady=20)
            uab=ttk.Button(master=uaw, text="Hozzáad", command=regus)
            uab.pack(pady=20)
            
            uaw.mainloop()
            
        def udel():
            index = ulist.curselection()
            if index:
                selected_item = ulist.get(index)
                delete_query = "DELETE FROM Loginfo WHERE BINARY una = %s"
                cur.execute(delete_query, (selected_item[0],))
                db.commit()
                update_ulist()       



        umanwin=ttk.Window(themename='darkly')
        umanwin.title("User management")        
        umanwin.geometry(f"{winwid}x{winhei+300}+{xco}+{yco-150}")
        umanwin.focus_force()
        cur.execute("SELECT * FROM Loginfo")
        entries=cur.fetchall()
        

        def on_select(event):
            # Get the selected item index
            index = ulist.curselection()
            if index:
                selected_item = ulist.get(index)
                
        def update_ulist():
            ulist.delete(0, tk.END)
            cur.execute("SELECT * FROM Loginfo")
            entries=cur.fetchall()
            for entry in entries:
                ulist.insert(tk.END,entry)

        global ulist
        ulist = tk.Listbox(master=umanwin,selectmode=tk.SINGLE)
        for entry in entries:
            ulist.insert(tk.END,entry)
        ulist.pack(expand=True, fill="both")
        ulist.bind("<<ListboxSelect>>", on_select)
        
                
        button_frame = ttk.Frame(master=umanwin)
        button_frame.pack(side="bottom", fill="both")
        addbutt=ttk.Button(master=umanwin, text="Add", command=uadd)
        addbutt.pack(side="left", padx=50, pady=5)
        delbutt=ttk.Button(master=umanwin, text="Del", command=udel)
        delbutt.pack(side="left", padx=5, pady=5)
        umanwin.mainloop()
        
    def get_export_filename():
        # Get the date for the previous month
        previous_month = datetime.now().replace(day=1) - timedelta(days=1)
    
        # Format the filename as "export_previous_month_year.xlsx"
        filename = f"export_{previous_month.strftime('%B_%Y')}.xlsx"
    
        return filename

# Function to export data from MySQL table to Excel
    def export_data():
        try:
            # Get the current month and year
            current_month = datetime.now().month
            current_year = datetime.now().year
        
            # Get the first and last day of the current month
            first_day_month = datetime(current_year, current_month, 1)
            last_day_month = datetime(current_year, current_month + 1, 1) - timedelta(days=1)
        
            # Execute SQL query to fetch data for the current month
            sql = "SELECT Kezelő, Időpont, Név, Bér, Motiváció, Megjegyzés FROM Data WHERE Időpont >= %s AND Időpont <= %s"
            cur.execute(sql, (first_day_month, last_day_month))
            data = cur.fetchall()
        
            # Convert data to DataFrame
            df = pd.DataFrame(data, columns=['Kezelő', 'Időpont','Név', 'Bér', 'Motiváció', 'Megjegyzés'])
        
            # Get filename for export
            filename = get_export_filename()
        
            # Write DataFrame to Excel file
            df.to_excel(filename, index=False)
        
            messagebox.showinfo("Success", f"Data exported to '{filename}' successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {e}") 

    umanbt=ttk.Button(master=awindow, text= "User management", command=uman)
    umanbt.pack(pady=30)

    def user_has_data_this_month(user):
        try:
            # Get the current month and year
            current_month = datetime.now().month
            current_year = datetime.now().year
        
            # Get the first and last day of the current month
            first_day_month = datetime(current_year, current_month, 1)
            last_day_month = datetime(current_year, current_month + 1, 1) - timedelta(days=1)
        
            # Execute SQL query to check if the user has submitted data this month
            sql = "SELECT COUNT(*) FROM Data WHERE Kezelő = %s AND Időpont >= %s AND Időpont <= %s"
            cur.execute(sql, (user, first_day_month, last_day_month))
            count = cur.fetchone()[0]
        
            # Return True if the user has submitted data, False otherwise
            return count > 0
        except Exception as e:
            print("Error checking user data:", e)
            return False

# Function to check completion
    def check_completion():
        try:
            # Create a new window for completion check
            completion_window = tk.Toplevel(awindow)
            completion_window.title("Completion Check")
            completion_window.geometry(f"{winwid}x{winhei+300}+{xco}+{yco-150}")
            # Get the list of users (excluding admin)
            cur.execute("SELECT una FROM Loginfo WHERE una != 'admin'")
            users = [row[0] for row in cur.fetchall()]

            # Create a Listbox to display users
            user_listbox = tk.Listbox(completion_window, selectmode=tk.SINGLE)
            user_listbox.pack(expand=True, fill="both")

            # Populate the Listbox with users
            for user in users:
                if user_has_data_this_month(user):
                    user_listbox.insert(tk.END, user)
                    user_listbox.itemconfig(tk.END, {'bg': 'green'})  # Highlight in green
                else:
                    user_listbox.insert(tk.END, user)

            # Function to close the completion window
            def close_completion_window():
                completion_window.destroy()

            # Add a button to close the window
            close_button = ttk.Button(completion_window, text="Close", command=close_completion_window)
            close_button.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Error checking completion: {e}")

    checo=ttk.Button(master=awindow, text="Check completion", command=check_completion)
    checo.pack(pady=30)
    
    exp=ttk.Button(master=awindow, text="Export data", command=export_data)
    exp.pack(pady=30)
    def on_exit():
        try:
            db.close()
            cur.close()
            # Close the database connection
        except Exception as e:
            print("Error closing database connection:", e)
        try:
            awindow.destroy()  # Destroy the Tkinter window
        except Exception as f:
            print("Hiba", f)


   
    
    awindow.protocol("WM_DELETE_WINDOW", on_exit)
    awindow.mainloop()


def uswin():
    initial_rows_count = 15  # Number of initial rows to display

    # Function to save data entered by the user
    def save_data():
        try:
            # Check if there is data in the first row's "Név" entry field
            nev_data_first_row = nev_entries[0].get()
            if not nev_data_first_row:
                messagebox.showwarning("Figyelmeztetés", "Kérem töltse ki a név mezőt!")
                return

            # Save data from entry fields
            for i in range(initial_rows_count):
                nev_data = nev_entries[i].get()
                if nev_data:  # Save data only if there is data in the "Név" entry field
                    ber_data = ber_entries[i].get().replace(',', '')  # Remove thousand separator comma
                    ber_data = int(ber_data) if ber_data.isdigit() else 0  # Convert to integer
                    motivacio_data = motivacio_entries[i].get().replace(',', '')  # Remove thousand separator comma
                    motivacio_data = int(motivacio_data) if motivacio_data.isdigit() else 0  # Convert to integer
                    megjegyzes_data = megjegyzes_entries[i].get()

                    # Insert data into the database (I assume you have defined db and cur variables elsewhere)
                    sql = "INSERT INTO Data (Kezelő, Időpont, Név, Bér, Motiváció, Megjegyzés) VALUES (%s, %s, %s, %s, %s, %s)"
                    values = (una, datetime.now(), nev_data, ber_data, motivacio_data, megjegyzes_data)
                    cur.execute(sql, values)
                    db.commit()

            # Display success message
            messagebox.showinfo("OK!", "Sikeres adatbevitel!")
        except Exception as e:
            messagebox.showerror("Hiba", f"Error occurred: {e}")

    # Function to fetch latest data for the current user with minute accuracy
    def fetch_latest_data():
        try:
            # Execute SQL query to fetch the latest timestamp for the current user
            sql_latest_timestamp = "SELECT MAX(Időpont) FROM Data WHERE Kezelő = %s"
            cur.execute(sql_latest_timestamp, (una,))
            latest_timestamp = cur.fetchone()[0]

            # If there is no data in the database, return an empty list
            if latest_timestamp is None:
                return []

            # Execute SQL query to fetch data for the latest timestamp
            sql_latest_data = "SELECT Név, Bér, Motiváció, Megjegyzés FROM Data WHERE Kezelő = %s AND Időpont = %s"
            cur.execute(sql_latest_data, (una, latest_timestamp))
            latest_data = cur.fetchall()

            return latest_data
        except Exception as e:
            print("Error fetching latest data:", e)
            return []

    # Create the user window
    uwindow = tk.Tk()
    uwindow.title('Adatbevitel')

    # Define a frame to contain the entry fields
    frame = ttk.Frame(uwindow)
    frame.pack(padx=10, pady=10)

    # Entry labels
    nev_label = ttk.Label(master=frame, text='Név')
    nev_label.grid(row=0, column=0)

    ber_label = ttk.Label(master=frame, text='Bér')
    ber_label.grid(row=0, column=1)

    motivacio_label = ttk.Label(master=frame, text='Motiváció')
    motivacio_label.grid(row=0, column=2)

    megjegyzes_label = ttk.Label(master=frame, text='Megjegyzés')
    megjegyzes_label.grid(row=0, column=3)

   # Function to update entry field value with thousand separator comma
    def update_entry_with_comma(entry):
        # Get current entry field value
        value = entry.get()
    
        # Remove any commas from the value
        value = value.replace(',', '')
    
        # Format value with thousand separator comma
        formatted_value = locale.format_string("%d", int(value), grouping=True) if value.isdigit() else value
    
        # Update entry field with formatted value
        entry.delete(0, tk.END)
        entry.insert(tk.END, formatted_value)

    # Entry fields for data entry
    nev_entries, ber_entries, motivacio_entries, megjegyzes_entries = [], [], [], []

    for i in range(initial_rows_count):
        nev_entry = ttk.Entry(master=frame)
        nev_entry.grid(row=i+1, column=0)
        nev_entries.append(nev_entry)

        ber_entry = ttk.Entry(master=frame, justify=tk.RIGHT)
        ber_entry.grid(row=i+1, column=1)
        ber_entries.append(ber_entry)
        # Bind callback function to update value with comma separator when typing
        ber_entry.bind('<KeyRelease>', lambda event, entry=ber_entry: update_entry_with_comma(entry))

        motivacio_entry = ttk.Entry(master=frame, justify=tk.RIGHT)
        motivacio_entry.grid(row=i+1, column=2)
        motivacio_entries.append(motivacio_entry)
        # Bind callback function to update value with comma separator when typing
        motivacio_entry.bind('<KeyRelease>', lambda event, entry=motivacio_entry: update_entry_with_comma(entry))

        megjegyzes_entry = ttk.Entry(master=frame)
        megjegyzes_entry.grid(row=i+1, column=3)
        megjegyzes_entries.append(megjegyzes_entry)


    # Fetch latest data and populate entry fields
    latest_data = fetch_latest_data()  # Assuming fetch_latest_data() fetches data for the current user
    if latest_data:
        for i, data in enumerate(latest_data):
            nev_entries[i].insert(0, data[0] if data[0] else "")  # Populate "Név" entry field
            ber_entries[i].insert(0, locale.format_string("%d", data[1], grouping=True) if data[1] is not None else "")  # Populate "Bér" entry field
            motivacio_entries[i].insert(0, locale.format_string("%d", data[2], grouping=True) if data[2] is not None else "")  # Populate "Motiváció" entry field
            megjegyzes_entries[i].insert(0, data[3] if data[3] else "")  # Populate "Megjegyzés" entry field

    # Save button to save data
    save_button = ttk.Button(master=uwindow, text="Save", command=save_data)
    save_button.pack(padx=10, pady=10)

    # Run the main loop
    uwindow.mainloop()


   



# Login Window
def on_enter(event=None):
    loginbutton.invoke()

window = ttk.Window(themename='darkly')
window.title('Bejelentkezés')

winwid=300
winhei=300
scrwid=window.winfo_screenwidth()
scrhei=window.winfo_screenheight()
xco=(scrwid-winwid)//2
yco=(scrhei-winhei)//2

window.geometry(f"{winwid}x{winhei}+{xco}+{yco}")
window.bind('<Return>', on_enter)

title_label = ttk.Label(master=window)
title_label.pack(pady=25)

entry_un= ttk.Entry(master=window)
entry_un.focus_set()
entry_un.pack()

un_label = ttk.Label(master=window, text='Felhasználó', font='Timesnewroman 8')
un_label.pack()

entry_pw= ttk.Entry(master=window, show="*")
entry_pw.pack()

pw_label = ttk.Label(master=window, text='Jelszó', font='Timesnewroman 8')
pw_label.pack()

loginbutton=ttk.Button(master=window, text="Login", command=login)
loginbutton.pack(pady=20)


def on_exit():
    try:
        db.close()
        cur.close()
        # Close the database connection
    except Exception as e:
        print("Error closing database connection:", e)
    try:
        window.destroy()  # Destroy the Tkinter window
    except Exception as f:
        print("Hiba", f)




window.protocol("WM_DELETE_WINDOW", on_exit)
window.mainloop()
