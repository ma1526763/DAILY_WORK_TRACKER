import requests
from tkinter import *
from tkcalendar import Calendar
import webbrowser
from datetime import datetime
from tkinter import messagebox
import os

# chnage here
USERNAME = "yourusername"
GRAPH_ID = "yougraphid"
MY_SECRET_TOKEN = os.environ['MY_SECRET_TOKEN']
GRAPH_NAME = "Python Working Hours"
PIXELA_END_POINT = "https://pixe.la/v1/users"
GRAPHS_ENDPOINT = f"{PIXELA_END_POINT}/{USERNAME}/graphs"
URL = f"{GRAPHS_ENDPOINT}/{GRAPH_ID}.html"
pixel_header = {
    "X-USER-TOKEN": MY_SECRET_TOKEN,
}
def internet():
    try:
        requests.get(PIXELA_END_POINT)
    except requests.exceptions.ConnectionError:
        messagebox.showinfo(title="No internet Connection", message="Please check your internet connection!!")
        return False
    else:
        return True

############# CREATE USER ON PIXEL ##########
def create_pixel_user():
    create_user_params = {
        "token": MY_SECRET_TOKEN,
        "username": USERNAME,
        "agreeTermsOfService": "yes",
        "notMinor": "yes",
    }
    user_response = requests.post(PIXELA_END_POINT, json=create_user_params)
    print(user_response.text)

########## CREATE GRAPH ##########
def create_graph():
    graphs_params = {
        "id": GRAPH_ID,
        "name": GRAPH_NAME,
        "unit": "hours",
        "type": "float",
        "color": "sora",
    }
    graph_response = requests.post(GRAPHS_ENDPOINT, json=graphs_params, headers=pixel_header)
    print(graph_response.text)

################# OPEN BROWSRE #################
def open_browser():
    if not internet():
        return
    webbrowser.open(URL, new=1)

################ CHECK VALID DATE (NOT GREATER THAN today) #############
def check_valid_date(u_date):
    return messagebox.showinfo(title="Invalid date", message="Please Choose today or previous dates only!!") \
        if u_date > datetime.now().strftime("%Y%m%d") else True

############# GET DATE FROM CALENDER #############
def get_calender_date():
    d = cal.get_date().split("/")
    return f"20{d[2]}{d[0] if int(d[0]) >= 10 else '0' + d[0]}{d[1] if int(d[1]) >= 10 else '0' + d[1]}"

########## MAKE ENTERIES EMPTY ################
def make_entry_empty():
    hour_entry.delete(0, END)
    minutes_entry.delete(0, END)
    hour_entry.focus()

########### VALIDATION #########
def user_input_validation(entry, h_m, upper_limit):
    try:
        hour_or_minutes = entry.get()
        if not hour_or_minutes:
            hour_or_minutes = 0
        hour_or_minutes = int(hour_or_minutes)
    except ValueError:
        messagebox.showinfo(title=f"Wrong {h_m}", message=f"Please choose {h_m.lower()} b/w 1-{upper_limit}")
    else:
        if hour_or_minutes < 0 or hour_or_minutes > upper_limit:
            messagebox.showinfo(title=f"Wrong {h_m}", message=f"Please choose {h_m.lower()} b/w 1-{upper_limit}")
            return False
        return hour_or_minutes

################# CHECK ALREADY PIXEL ##############
def check_already_pixel(u_date, check_same=False):
    response = "503"
    data = {}
    # checking 503 as they will produce error 25% of time for free version
    while response == "503":
        data = requests.get(f"{GRAPHS_ENDPOINT}/{GRAPH_ID}/{u_date}", headers=pixel_header)
        response = str(data)[-5:-2]
    if check_same:
        if data.json()['quantity'] == f"{hour_entry.get()}.{minutes_entry.get()}":
            messagebox.showinfo(title="Updating same value", message="You are updating the same value again!\nPlease change the value.")
            return "100"
    return response

################# GET VALID HOURS/MINUTES ########
def get_valid_hours_minutes(pixel_adding=False):
    valid_hours = user_input_validation(hour_entry, "Hours", 24)
    if valid_hours or str(valid_hours) == "0":
        valid_minutes = user_input_validation(minutes_entry, "Minutes", 60)
        if valid_hours == valid_minutes == 0:
            messagebox.showinfo(title="Empty Fields", message="Both hours and minutes can't be empty")
            return False, False
        if valid_minutes or str(valid_minutes) == "0":
            if valid_minutes < 10:
                valid_minutes = f"0{str(valid_minutes)}"
            user_date = get_calender_date()
            response = check_already_pixel(user_date)
            if response != "200":
                return valid_hours, valid_minutes
            if pixel_adding:
                messagebox.showinfo(title="Pixel Already Exists",
                                    message=f"PIXEL ALREADY EXISTS FOR {cal.get_date()}.\n\nYOU CAN UPDATE/DELETE IT.")
                make_entry_empty()
            else:
                return valid_hours, valid_minutes
    return False, False

########## ADD PIXEL #########
def add_pixel():
    user_date = get_calender_date()
    if not internet():
        return
    if str(check_valid_date(user_date)) != "True":
        return
    hours, minutes = get_valid_hours_minutes(pixel_adding=True)
    if hours or minutes:
        add_pixel_params = {
            "date": user_date,
            "quantity": f"{hours}.{minutes}",
        }
        response = "503"
        while response == "503":
            response = requests.post(f"{GRAPHS_ENDPOINT}/{GRAPH_ID}", json=add_pixel_params, headers=pixel_header)
            response = str(response)[-5:-2]
        messagebox.showinfo(title="Pixel added Successfully",
                            message=f"Pixel for {f'{hours} hours' if hours else ''} {f'{minutes} minutes' if minutes else ''} has been added on {cal.get_date()}")
        make_entry_empty()

################### UPDATE PIXEL ###############
def update_pixel():
    user_date = get_calender_date()
    if not internet():
        return
    if str(check_valid_date(user_date)) != "True":
        return
    hours, minutes = get_valid_hours_minutes()
    if hours or minutes:
        update_pixel_params = {
            "quantity": f"{hours}.{minutes}"
        }
        response = check_already_pixel(user_date, check_same=True)
        if response == "200":
            invalid_response = "503"
            while invalid_response == "503":
                invalid_response = requests.put(f"{GRAPHS_ENDPOINT}/{GRAPH_ID}/{user_date}", json=update_pixel_params, headers=pixel_header)
                invalid_response = str(invalid_response)[-5:-2]
            messagebox.showinfo(title="Pixel updated Successfully",
                                message=f"Pixel for {f'{hours} hours' if hours else ''} {f'{minutes} minutes' if minutes else ''} has been updated on {cal.get_date()}")
            make_entry_empty()
        elif response == "100":
            return
        else:
            messagebox.showinfo(title="UPDATE FAILED", message=f"No Pixel exists for {cal.get_date()}.")

################## DELETE PIXEL #################
def delete_pixel():
    user_date = get_calender_date()
    if not internet():
        return
    if str(check_valid_date(user_date)) != "True":
        return
    response = check_already_pixel(user_date)
    if response == "200":
        invalid_response = "503"
        while invalid_response == "503":
            invalid_response = requests.delete(f"{GRAPHS_ENDPOINT}/{GRAPH_ID}/{user_date}", headers=pixel_header)
            invalid_response = str(invalid_response)[-5:-2]
        messagebox.showinfo(title="Pixel Deleted Successfully",
                            message=f"Pixel for {cal.get_date()} has been deleted Successfully.")
    else:
        messagebox.showinfo(title="DELETION FAILED",
                            message=f"No Pixel exists for {cal.get_date()}\nPlease add the pixel first on {cal.get_date()}")

#################### RUN ONLY ONCE TO CREATE USER AND GRAPH ################
# create_pixel_user()
# create_graph()

###################### GUI ############################
window = Tk()
window.title("Work Time")
window.geometry("800x500+200+100")
window.resizable(False, False)
canvas = Canvas(width=800, height=500)
canvas.place(x=0, y=0)
img = PhotoImage(file="img.png")
canvas.create_image(400, 250, image=img)

# CALENDAR
cal = Calendar(window, selectmode='day', year=datetime.now().year, month=datetime.now().month,
               day=datetime.now().day, font="Arial 16", background="black", disabledbackground="black",
               bordercolor="black", headersbackground="black", normalbackground="#765c43", foreground='white',
               normalforeground='white', headersforeground='white')
cal.place(x=200, y=30)

# ENTRY
hour_label = Label(text="Hours", font=("Arial", 18, "bold"))
hour_label.place(x=200, y=326)
hour_entry = Entry(width=7, font=("Arial", 18), highlightthickness=2, highlightbackground="red", highlightcolor="red")
hour_entry.place(x=281, y=326)
hour_entry.focus()
minutes_label = Label(text="Minutes", font=("Arial", 18, "bold"))
minutes_label.place(x=420, y=326)
minutes_entry = Entry(width=5, font=("Arial", 18), highlightthickness=2, highlightbackground="red",
                      highlightcolor="red")
minutes_entry.place(x=526, y=326)

# BUTTONS
add_button = Button(text="ADD", background="green", foreground="white", font=("Arial", 15, "bold"), command=add_pixel)
add_button.place(x=200, y=370, width=180)
delete_button = Button(text="DELETE", background="red", foreground="white", font=("Arial", 15, "bold"),
                       command=delete_pixel)
delete_button.place(x=420, y=370, width=180)
update_button = Button(text="UPDATE", background="blue", foreground="white", font=("Arial", 15, "bold"),
                       command=update_pixel)
update_button.place(x=200, y=420, width=180)
view_button = Button(text="VIEW JOURNEY", background="gold", foreground="white", font=("Arial", 15, "bold"),
                     command=open_browser)
view_button.place(x=420, y=420, width=180)
window.mainloop()
