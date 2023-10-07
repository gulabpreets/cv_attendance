import os
import pickle
import numpy as np
import cv2 as cv
import face_recognition
import cvzone
import numpy as np
from extractData import extractData
from encodeGenerator import encode_student_images
import openpyxl
import datetime
from toPNG import toPNG
from mail import send_mail

# ******************************************************
# List of mail
# ******************************************************
mailList=["gulabpreets01@gmail.com,yashikasharma1775@gmail.com"]

subject = "Attendance of your ward"

# ******************************************************
# code for converting other format images to png format
# ******************************************************
toPNG()


# ******************************************************
# code for excel file
# ******************************************************

current_date = datetime.datetime.now().strftime('%Y-%m-%d')

# Create a counter to track the file number
file_counter = 1
excel_file_name = f'{current_date}({file_counter}).xlsx'
excel_folder_path = 'Excel'  # Specify the folder path here

# Check for existing files and increment the counter if needed
while os.path.exists(os.path.join(excel_folder_path, excel_file_name)):
    file_counter += 1
    excel_file_name = f'{current_date}({file_counter}).xlsx'

# Create a new Excel file with the calculated file name and path
excel_file_path = os.path.join(excel_folder_path, excel_file_name)
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.append(['ID', 'Name', 'Time', 'Date'])

# ******************************************************
# # code for deleting encoded file
# ******************************************************

file_path = 'EncodeFile.p'  # Replace with the actual file path you want to delete

try:
    os.remove(file_path)
    print(f"File '{file_path}' deleted successfully.")
except OSError as e:
    print(f"Error deleting the file '{file_path}': {e}")

encode_student_images()


url1 = 'http://100.92.150.188:8080/video'
url2 = 'http://192.168.8.58:8080/video'
url3 = 'http://[2401:4900:594e:59d2::8]:8080/video'

cap = cv.VideoCapture(0)
imgBackground = cv.imread('Resources/background.png') 



cap.set(3,1280)
cap.set(4,720)

folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv.imread(os.path.join(folderModePath,path)))

# print(imgModeList)




# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
print(studentIds)
# print(encodeListKnown)
print("Encode File Loaded")

modeType = 0
# 0-Active
# 1-Student
# 2-Marked
# 3-Already Marked
# 4-Unknown Student
# 5-Matched   
# 6-No Student

target_height, target_width = 216, 216

counter = 0
id = -1
imgStudent = []
student_attendance_marked = {}  # Create an empty dictionary to track student attendance
print("student attendence mark list",student_attendance_marked)

while True:
    success, img = cap.read()
    
    imgS = cv.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv.cvtColor(imgS, cv.COLOR_BGR2RGB)
    
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
    
    
    # imgBackground[162:162+480, 55:55+640] = img
    imgBackground[162:162+480, 55:55+640] = cv.resize(img, (640, 480))  # Resize img to match the target dimensions
    
    imgBackground[44:44+633, 808:808+414] = imgModeList[6]


    if faceCurFrame:
        # print("Printing after if FaceCurFrame",faceCurFrame)
        imgBackground[44:44+633, 808:808+414] = imgModeList[4]
        
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace) #Lower the dis better the match
            # print("matches", matches)
            # print("faceDis", faceDis)
            y1, x2, y2, x1 = faceLoc #getting info for showing boundging box ()
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0) 
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
    
            matchIndex = np.argmin(faceDis)
            # print("Match Index", matchIndex)

            if matches[matchIndex]:
                imgBackground[44:44+633, 808:808+414] = imgModeList[5]
                # print("Known Face Detected")
                # print(studentIds[matchIndex])

                id = studentIds[matchIndex]
                # print(id)
                # print(type(id))
                studentData = extractData(id)
                # print("Student Data", studentData)

                if id  in student_attendance_marked:
                    #here screen should show attendance is already marked
                    # and screen should also show the details of the student
                    imgBackground[44:44+633, 808:808+414] = imgModeList[3]
                    # showing name of the student
                    cv.putText(imgBackground, studentData[1], (870 , 445),cv.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 2)
                    # showing id of the student
                    cv.putText(imgBackground, studentData[0], (1006, 493),
                                    cv.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    # print("student attendence mark list",student_attendance_marked)
                    #showing students' phtot
                    
                    student_image_path = f'images/{id}.png'
                    imgStudent = cv.imread(student_image_path)
                    if imgStudent.shape[:2] != (target_height, target_width):
                        resized_imgStudent = cv.resize(imgStudent, (target_width, target_height))
                        imgBackground[175:175 + target_height, 909:909 + target_width] = resized_imgStudent
                    else:
                        imgBackground[175:175 + target_height, 909:909 + target_width] = imgStudent     

                    
                    # cv.waitKey(1)
                
                if id not in student_attendance_marked:
                    send_mail(mailList,"Your Ward " + studentData[1] + "was present today in class.",subject)
                    student_attendance_marked[id] = True  # Mark the student as attendance recorded
                    # here screen should show for 3 sec that attendance marked
                    # then after 3sec screen should show the details of the student
                    imgBackground[44:44+633, 808:808+414] = imgModeList[2]
                    print("Fist tym encountered")
                    # cv.waitKey(10000)  # Wait for 3 seconds
                    # making excel 
                    data_to_record = [studentData[0], studentData[1], studentData[4], studentData[3]]
                    print(data_to_record)
                    sheet.append(data_to_record)
                    
        
    cv.imshow("Face Attendance", imgBackground)
    cv.waitKey(1)
    workbook.save(excel_file_path)   
    
   
   
   
        