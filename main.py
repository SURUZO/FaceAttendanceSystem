import os
import numpy as np
import pickle
import cv2
import face_recognition
import cvzone
import mysql.connector
from datetime import datetime



cap = cv2.VideoCapture(0)#webcam
cap.set(3, 640)
cap.set(4, 480)#webcam size

imgbackground=cv2.imread("Resources/background.png")#background

#modes (ACTIVE,MARKED,ETC)
folderModePath: str = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))


#encoding
print("loading Encode File")
file=open('EncodeFile.p','rb')
encodeListKnownWithIds=pickle.load(file)
file.close()
encodeListKnown,studentIds=encodeListKnownWithIds
print("Encode File Loaded")

modeType=2#active
counter=0
id=-1

while True:
    success, img = cap.read()

    imgs=cv2.resize(img,(0,0),None,0.25,0.25)
    imgs=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    faceCurFrame=face_recognition.face_locations(imgs)
    encodeCurFrame=face_recognition.face_encodings(imgs,faceCurFrame)

    imgbackground[162:162+480,55:55+640]=img#adding webcam to background
    imgbackground[40:40 + 633, 807:807 + 414] = imgModeList[modeType]

    if faceCurFrame:
        #comparing cam view and encoded list
        for encodeFace, faceLoc in zip(encodeCurFrame,faceCurFrame):
            matches=face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis=face_recognition.face_distance(encodeListKnown,encodeFace)
            #print(matches)
            #print(faceDis)

            matchIndex= np.argmin(faceDis)


            if faceDis[matchIndex] < 0.4:
                y1,x2,y2,x1 = faceLoc
                bbox=55+x1,162+y1,x2-x1,y2-y1
                imgbackground=cvzone.cornerRect(imgbackground,bbox,rt=0)
                id=studentIds[matchIndex]

                if counter==0:
                    counter=1
                    modeType=0#details
        if counter!=0:

            if counter==1:
                mydb = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="Root@123",
                    database="FaceRecognition"
                )

                # Create a cursor object to interact with the database
                cursor = mydb.cursor()
                select_query = "SELECT * FROM Record WHERE id = %s"
                cursor.execute(select_query, (id,))
                record = cursor.fetchone()

                # Check if a record was found
                if record:
                    # Retrieve the individual values from the record tuple
                    id = record[0]
                    name = record[1]
                    major = record[2]
                    starting_year = record[3]
                    total_attendance = record[4]
                    standing = record[5]
                    year = record[6]
                    last_attendance_time = record[7]
                    image = record[8]

                    # Create a dictionary for the student information
                    studentInfo = {
                        'id': id,
                        'name': name,
                        'major': major,
                        'starting_year': starting_year,
                        'total_attendance': total_attendance,
                        'standing': standing,
                        'year': year,
                        'last_attendance_time': last_attendance_time,
                        'image': image
                    }

                    datetimeObject = studentInfo['last_attendance_time']
                    secondsElapsed=(datetime.now()-datetimeObject).total_seconds()
                    if secondsElapsed >30:
                        studentInfo['total_attendance']+=1
                        update_query = "UPDATE Record SET total_attendance = total_attendance + 1 WHERE id = %s"
                        cursor.execute(update_query, (id,))
                        current_time = datetime.now()
                        current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
                        update_query = "UPDATE Record SET last_attendance_time = %s WHERE id = %s"
                        data = (current_time_str, id)
                        cursor.execute(update_query, data)
                    else:
                        modeType = 3#already marked
                        counter=0
                        # imgbackground[40:40 + 633, 807:807 + 414] = imgModeList[modeType]
                    mydb.commit()
                    cursor.close()
                    mydb.close()

            if modeType!=3:
                #print(studentInfo)
                if 10<counter<20:
                    modeType=1#marked
                #imgbackground[40:40 + 633, 807:807 + 414] = imgModeList[modeType]

                if counter<=10:
                    cv2.putText(imgbackground, str(studentInfo['total_attendance']), (861, 122),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(imgbackground, str(studentInfo['major']), (1006, 548),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(imgbackground, str(id), (1006, 491),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(imgbackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2, cv2.LINE_AA)
                    cv2.putText(imgbackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2, cv2.LINE_AA)
                    cv2.putText(imgbackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2, cv2.LINE_AA)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                    offset = (414 - w) // 2
                    cv2.putText(imgbackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 2, cv2.LINE_AA)
                    # Convert the image data to a numpy array
                    image_np = np.frombuffer(image, np.uint8)

                    # Decode the numpy array as an image
                    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

                    # Resize the image to the desired dimensions
                    img = cv2.resize(img, (216, 216))

                    # Add the image to imgBackground at the specified coordinates
                    imgbackground[172:172 + 216, 909:909 + 216] = img
                counter +=1

                if counter>=20:
                    counter=0
                    modeType=2#active
                    studentInfo=[]
                    img=[]
                    #imgbackground[40:40 + 633, 807:807 + 414] = imgModeList[modeType]
    else:
        modeType=2#active
        counter=0


    cv2.imshow("AttendEasy", imgbackground)
    cv2.waitKey(1)

