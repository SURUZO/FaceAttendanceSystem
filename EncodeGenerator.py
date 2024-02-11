import os
import cv2
import face_recognition
import pickle

folderPath = 'Images'
PathList = os.listdir(folderPath)
imgList = []
studentIds = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])


def findEncodings(imagesList, existingIds):
    encodeList = []
    skippedIds = []
    for img, studentId in zip(imagesList, studentIds):
        if studentId in existingIds:
            skippedIds.append(studentId)
            continue

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList, skippedIds


print("Encoding Started....")

# Load existing data from the file
if os.path.exists("EncodeFile.p"):
    file = open("EncodeFile.p", 'rb')
    existingData = pickle.load(file)
    file.close()
    existingEncodeList, existingStudentIds = existingData

    # Find encodings for new images, skipping existing student IDs
    encodeListKnown, skippedIds = findEncodings(imgList, existingStudentIds)

    # Append new data to the existing data
    existingEncodeList.extend(encodeListKnown)
    existingStudentIds.extend(studentIds)

    # Write the combined data back to the file
    file = open("EncodeFile.p", 'wb')
    pickle.dump([existingEncodeList, existingStudentIds], file)
    file.close()

    if len(skippedIds) > 0:
        print("Skipped encoding for images with the following student IDs:")
        print(skippedIds)
else:
    # Write the data to a new file if it doesn't exist
    encodeListKnown, _ = findEncodings(imgList, [])
    encodeListKnownWithIds = [encodeListKnown, studentIds]
    file = open("EncodeFile.p", 'wb')
    pickle.dump(encodeListKnownWithIds, file)
    file.close()

print("File saved")
