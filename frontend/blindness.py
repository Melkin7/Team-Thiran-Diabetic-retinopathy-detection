# Importing all packages
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from PIL import Image
import os
import sys

# Add parent directory to Python path to enable imports from organized structure
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import mysql.connector
from tkinter.filedialog import askopenfilename, asksaveasfilename
import mysql.connector as sk
from backend.model import *
from messaging.send_sms import *
from reports.report_generator import create_report
from reports.pdf_report import create_pdf_report
from frontend.report_verification_dialog import show_verification_dialog
from messaging.send_whatsapp import send_report_whatsapp
print('GUI SYSTEM STARTED...')
#---------------------------------------------------------------------------------

def LogIn():
    username = box1.get()

    u = 1

    if len(username) == 0:
        u = 0
        messagebox.showinfo("Error", "You must enter something Sir")

    if u:
            password = box2.get()

            if len(password):
                query = "SELECT 1 FROM THEGREAT WHERE USERNAME = %s AND PASSWORD = %s"
                sql.execute(query, (username, password))

                if sql.fetchone():
                    messagebox.showinfo('Hello Sir', 'Welcome to the System')
                    global y
                    y = True
                else:
                    messagebox.showinfo('Sorry', 'Wrong Username or Password')
                    y = False
            else:
                messagebox.showinfo("Error", "You must enter a password Sir!!")

def OpenFile():
    username = box1.get()
    if y:
        try:
            # File selection dialog
            a = askopenfilename()
            if not a:  # User cancelled
                return
            
            print(f"Analyzing image: {a}")
            messagebox.showinfo("Processing", "Processing image... Please wait.")
            
            # Get model prediction
            value, classes = main(a)
            
            # Generate professional medical report
            print("Generating medical report...")
            report = create_report(
                username=username,
                severity_level=value,
                confidence_score=float(value) * 20,  # Approximate confidence
                image_path=a,
                age="N/A",
                gender="N/A"
            )
            
            # Generate PDF report
            print("Creating PDF report...")
            pdf_path = create_pdf_report(report, image_path=a)
            print(f"✅ PDF created: {pdf_path}")
            
            # Show initial prediction
            messagebox.showinfo(
                "Detection Complete",
                f"DR Classification: {classes}\nSeverity Level: {value}\n\n"
                f"Please review the detailed report in the next screen."
            )
            
            # Show verification dialog
            print("Showing verification dialog...")
            result = show_verification_dialog(root, report, pdf_path)
            
            if result and result.get('verified'):
                # User verified - proceed with sending
                send_method = result.get('method', 'both')
                
                # Get recipient phone number from environment or database
                recipient_phone = os.getenv('RECIPIENT_PHONE', '+919043890506')
                
                # Get SMS summary and WhatsApp text
                from report_generator import MedicalReportGenerator
                generator = MedicalReportGenerator(username, username, "N/A", "N/A")
                sms_summary = generator.get_report_summary(report)
                whatsapp_text = generator.get_report_text(report)
                
                # Send based on selected method
                if send_method in ['sms', 'both']:
                    print("Sending SMS...")
                    send_report_sms(recipient_phone, sms_summary)
                
                if send_method in ['whatsapp', 'both']:
                    print("Sending WhatsApp...")
                    send_report_whatsapp(recipient_phone, whatsapp_text, pdf_path)
                
                messagebox.showinfo(
                    "Report Sent",
                    f"✓ Medical report sent successfully via {send_method.upper()}!\n\n"
                    f"Report ID: {report['report_id']}\n"
                    f"PDF saved: {pdf_path}"
                )
            else:
                # User cancelled
                messagebox.showinfo("Cancelled", "Report sending cancelled by user.")
            
            # Update database
            query = "UPDATE THEGREAT SET PREDICT = %s WHERE USERNAME = %s"
            sql.execute(query, (value, username))
            connection.commit()
            
            # Display analyzed image
            image = Image.open(a)
            file = image.convert('RGB')
            plt.imshow(np.array(file))
            plt.title(f'DR Detection Result: {classes} (Level {value})')
            plt.show()
            
            print('✅ Analysis complete! Thanks for using the system!')
            
        except Exception as error:
            print(f"Error: {error}")
            messagebox.showerror("Error", "File processing failed. Please try again.")

    else:
        messagebox.showinfo("Login Required", "Please login first to upload images.")


x = 0
y = False


def Signup():
    username = box1.get()
    password = box2.get()

    u = 1

    if len(username) == 0 or len(password) == 0:
        u = 0
        messagebox.showinfo("Error", "You must enter something Sir")

    if u:
        query1 = "SELECT * FROM THEGREAT"
        sql.execute(query1)

        data = sql.fetchall()

        z = 1

        for i in data:
            if i[0] == username:
                messagebox.showinfo("Sorry Sir", "This  username is already registered, try a new one")
                z = 0

        if z:
            query = "INSERT INTO THEGREAT (USERNAME, PASSWORD) VALUES(%s, %s)"
            messagebox.showinfo("signed up", ("Hi ",username ,"\n Now you can login with your credentials !"))
            sql.execute(query, (username, password))
            connection.commit()


#-----------------------------------------------------------------------------------------


db_host = os.getenv("DR_DB_HOST", "localhost")
db_user = os.getenv("DR_DB_USER", "dr_user")
db_password = os.getenv("DR_DB_PASSWORD", "dr_password_2024")
db_name = os.getenv("DR_DB_NAME", "diabetic_retinopathy_db")

connection = sk.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)

sql = connection.cursor()

root = Tk()

root.geometry('700x400')
root.title("Team Thiran - Diabetic Retinopathy Detection System")
root.configure(bg='pale turquoise')


label1 = Label(root, text="DR Detection System", font=('Arial', 30))
label1.grid(padx=30, pady=30, row=0, column=0, sticky='W')

label2 = Label(root, text="Enter your username: ", font=('Arial', 20))
label2.grid(padx=10, pady=10, row=1, column=0, sticky='W')

label3 = Label(root, text="Enter your password: ", font=('Arial', 20))
label3.grid(padx=10, pady=20, row=2, column=0, sticky='W')

box1 = Entry(root)
box1.grid(row=1, column=1)

box2 = Entry(root, show='*')
box2.grid(row=2, column=1)

button3 = Button(root, text="Signup", command=Signup)
button3.grid(padx=10, pady=20, row=3, column=1)

button1 = Button(root, text="LogIn", command=LogIn)
button1.grid(padx=10, pady=20, row=3, column=2)

button2 = Button(root, text="Upload Image", command=OpenFile)
button2.grid(padx=10, pady=20, row=2, column=3)

# concurrency control in InnoDB
# Read_locks useful when locks another user trying to update the value in the same row which is allocated for another user , both at the same time
#SELECT * FROM t1, t2 FOR SHARE OF t1 FOR UPDATE OF t2;
# START TRANSACTION;
# SELECT * FROM your_table WHERE state != 'PROCESSING'
#   ORDER BY date_added ASC LIMIT 1 FOR UPDATE;
# if (rows_selected = 0) { //finished processing the queue, abort}
# else {
# UPDATE your_table WHERE id = $row.id SET state = 'PROCESSING'
# COMMIT;
#
# // row is processed here, outside of the transaction, and it can take as much time as we want
#
# // once we finish:
# DELETE FROM your_table WHERE id = $row.id and state = 'PROCESSING' LIMIT 1;
# }

if __name__ == '__main__':
    root.mainloop()
