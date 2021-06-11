import cv2 as cv
import dlib
import constants as _constant
import eye


cap = cv.VideoCapture(0)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
message = ''
currentframe = 0
currentChar = ''
previousChar = ''
is_message_final = False

def show_message(text):
    cv.putText(frame, text, (20, 30), cv.FONT_HERSHEY_DUPLEX, 0.8, (147, 58, 31), 2)

def show_eye_status(text):
    # cv.putText(frame, text, (20, 30), cv.FONT_HERSHEY_DUPLEX, 0.7, (147, 58, 31), 1)
    cv.putText(frame, text, (20, 60), cv.FONT_HERSHEY_DUPLEX, 0.6, (147, 58, 31), 1)


while True:
    _, frame = cap.read()
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        gaze = 0
        landmarks = predictor(gray, face)

        # brinking events
        left_blink_ratio = eye.get_blinking_ratio(_constant.left_eye, landmarks, frame)
        right_blink_ratio = eye.get_blinking_ratio(_constant.right_eye, landmarks, frame)
        both_eye = (left_blink_ratio + right_blink_ratio) / 2
        # print(both_eye)
        if (both_eye > _constant.blinking_ratio):
            show_eye_status('Candidates EYE CLOSED')
            currentChar = '/'

        else:
        # # gazing events
            left_gaze_ratio = eye.get_gaze_ratio(_constant.left_eye, landmarks, frame, gray)
            right_gaze_ratio = eye.get_gaze_ratio(_constant.right_eye, landmarks, frame, gray)
            if left_gaze_ratio != None and right_gaze_ratio != None:
                average_age_ratio = (left_gaze_ratio + right_gaze_ratio) / 2
                gaze = average_age_ratio
                #print(gaze)
                if gaze < .6:
                    show_eye_status('Candidate is Seeing LEFT')
                    currentChar = '-'
                elif gaze > 2:
                    show_eye_status('Candidate is Seeing RIGHT')
                    currentChar = '.'
                else:
                    show_eye_status('Candidate is Seeing CENTER')
                    currentChar = ''

       
    cv.imshow("Frame", frame)

    key = cv.waitKey(2)
    if key == 27: #escape key
        break
cap.release()
cv.destroyAllWindows()