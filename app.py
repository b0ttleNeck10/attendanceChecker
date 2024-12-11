from datetime import datetime
from flask import Flask,render_template,request,redirect,flash
from dbhelper import *
from icecream import ic
import cv2
import pyqrcode
import os

uploadfolder='static/images'
app = Flask(__name__)
app.config['UPLOAD_FOLDER']=uploadfolder
app.config['SECRET_KEY']='mysecretkey'


@app.route("/register",methods=['POST'])
def register()->None:
    idno:str = request.form['idno']
    lastname:str = request.form['lastname']
    firstname:str = request.form['firstname']
    course:str = request.form['course']
    level:str = request.form['level']
    
    file = request.files['uploadimage']
    image_filename = uploadfolder+"/register/"+file.filename
    file.save(image_filename)
    ic(image_filename)
    
    qrc = pyqrcode.create(idno)
    qrc_filename = uploadfolder+"/qrcode/"+idno+'.png'
    qrc.png(qrc_filename, scale=8)
    ic(qrc_filename)
    
    ok:bool = add_record('students',idno=idno,lastname=lastname,firstname=firstname,course=course,level=level,image=image_filename,qrcode=qrc_filename)
    
    message = 'error adding student'
    if ok:message = 'New Student Added'
    flash(message)
    
    return redirect("/")

@app.route("/deletestudent",methods=['GET'])
def deletestudent()->None:
    idno = request.args.get('idno')
    
    if idno:
        ok = delete_record('students', idno=idno)
        
        if ok:
            flash('Student record deleted successfully.')
        else:
            flash('Failed to delete student record.')

    return redirect("/")

@app.route("/")
def index()->None:
    students:list = getall_records('students')
    return render_template("index.html",pagetitle="registration",students=students)

@app.route("/viewattendance")
def viewattendance()->None:
    attendance = getall_attendance('attendance')
    return render_template("view_attendance.html",pagetitle="view attendance", attendance=attendance)

@app.route("/checkattendance", methods=['GET', 'POST'])
def checkattendance():
    student = None

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            idno = data.get('idno', '').strip()

            if not idno:
                return {"success": False, "message": "Invalid QR code data."}, 400

            student = getprocess(f"SELECT * FROM students WHERE idno = '{idno}'")

            if student:
                student = student[0]
                student_dict = dict(student)
                lastname = student_dict['lastname']
                firstname = student_dict['firstname']
                logtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Add the attendance record
                add_record('attendance', idno=idno, lastname=lastname, firstname=firstname, logtime=logtime)

                return {"success": True, "student": student_dict}, 200
            else:
                return {"success": False, "message": "Student not found."}, 404

    return render_template("check_attendance.html", pagetitle="Check Attendance", student=student)

if __name__=="__main__":
    app.run(debug=True)