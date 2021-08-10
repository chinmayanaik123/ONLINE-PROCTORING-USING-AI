def visual_based():
    #combination of both eye and head tracking
    import cv2 as cv                         #code to track eye
    import dlib
    import constants as _constant
    import eye 
    import time
    from concurrent.futures.thread import ThreadPoolExecutor
    #to find the whether the person looking right or left
    import numpy as np
    import math
    from face_detector import get_face_detector, find_faces,draw_faces,draw_red
    from face_landmarks import get_landmark_model, detect_marks
    e=0         
    prev_frame_time = 0    # to get frame rates
    # used to record the time at which we processed current frame
    executor = ThreadPoolExecutor(max_workers=1)
    new_frame_time = 0      
    cap = cv.VideoCapture(0)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(
        "shape_predictor_68_face_landmarks.dat")
    currentframe = 0
    is_message_final = False
    
    def show_message(text):
        cv.putText(frame, text, (20, 30), cv.FONT_HERSHEY_DUPLEX, 0.8, (147, 58, 31), 2)
    def warning():
        cv.putText(frame,"Candidate looking away from screen ", (30, 30), cv.FONT_HERSHEY_DUPLEX, 0.6, (0,0,255), 1)

    face_model = get_face_detector()
    landmark_model = get_landmark_model()
    ret, frame = cap.read()
    size = frame.shape
    font = cv.FONT_HERSHEY_DUPLEX
    # 3D model points.
    model_points = np.array([
                                (0.0, 0.0, 0.0),             # Nose tip
                                (0.0, -330.0, -65.0),        # Chin
                                (-225.0, 170.0, -135.0),     # Left eye left corner
                                (225.0, 170.0, -135.0),      # Right eye right corne
                                (-150.0, -150.0, -125.0),    # Left Mouth corner
                                (150.0, -150.0, -125.0)      # Right mouth corner
                            ])
    # Camera internals
    focal_length = size[1]
    center = (size[1]/2, size[0]/2)
    camera_matrix = np.array(
                            [[focal_length, 0, center[0]],
                            [0, focal_length, center[1]],
                            [0, 0, 1]], dtype = "double"
                            )
    def get_2d_points(frame, rotation_vector, translation_vector, camera_matrix, val):
        """Return the 3D points present as 2D for making annotation box"""
        point_3d = []
        dist_coeffs = np.zeros((4,1))
        rear_size = val[0]
        rear_depth = val[1]
        point_3d.append((-rear_size, -rear_size, rear_depth))
        point_3d.append((-rear_size, rear_size, rear_depth))
        point_3d.append((rear_size, rear_size, rear_depth))
        point_3d.append((rear_size, -rear_size, rear_depth))
        point_3d.append((-rear_size, -rear_size, rear_depth))
        
        front_size = val[2]
        front_depth = val[3]
        point_3d.append((-front_size, -front_size, front_depth))
        point_3d.append((-front_size, front_size, front_depth))
        point_3d.append((front_size, front_size, front_depth))
        point_3d.append((front_size, -front_size, front_depth))
        point_3d.append((-front_size, -front_size, front_depth))
        point_3d = np.array(point_3d, dtype=np.float).reshape(-1, 3)
        
        # Map to 2d frame points
        (point_2d, _) = cv.projectPoints(point_3d,
                                        rotation_vector,
                                        translation_vector,
                                        camera_matrix,
                                        dist_coeffs)
        point_2d = np.int32(point_2d.reshape(-1, 2))
        return point_2d

    def draw_annotation_box(frame, rotation_vector, translation_vector, camera_matrix,
                            rear_size=300, rear_depth=0, front_size=500, front_depth=400,
                            color=(255, 255, 0), line_width=2):
    
        rear_size = 1
        rear_depth = 0
        front_size = frame.shape[1]
        front_depth = front_size*2
        val = [rear_size, rear_depth, front_size, front_depth]
        point_2d = get_2d_points(frame, rotation_vector, translation_vector, camera_matrix, val)
        
        
    def head_pose_points(frame, rotation_vector, translation_vector, camera_matrix):
    
        rear_size = 1
        rear_depth = 0
        front_size = frame.shape[1]
        front_depth = front_size*2
        val = [rear_size, rear_depth, front_size, front_depth]
        point_2d = get_2d_points(frame, rotation_vector, translation_vector, camera_matrix, val)
        y = (point_2d[5] + point_2d[8])//2
        x = point_2d[2]
        
        return (x, y)

    while True:
        ret, frame = cap.read()
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces = detector(gray)
        for face in faces:
            gaze = 0
            landmarks = predictor(gray, face)
            left_blink_ratio = eye.get_blinking_ratio(_constant.left_eye, landmarks, frame)
            right_blink_ratio = eye.get_blinking_ratio(_constant.right_eye, landmarks, frame)
            both_eye = (left_blink_ratio + right_blink_ratio) / 2
 
            left_gaze_ratio = eye.get_gaze_ratio(_constant.left_eye, landmarks, frame, gray)
            right_gaze_ratio = eye.get_gaze_ratio(_constant.right_eye, landmarks, frame, gray)
            if left_gaze_ratio != None and right_gaze_ratio != None:
                average_age_ratio = (left_gaze_ratio + right_gaze_ratio) / 2
                gaze = average_age_ratio
                #print(gaze)
                if gaze <  0.6:                  #0.25       #0.6
                    # show_eye_status('Candidate is Seeing LEFT')
                    e="l"
                    
                elif gaze > 2:                 #2.5       #2
                    # show_eye_status('Candidate is Seeing RIGHT')
                    e="r"
                else:
                    # show_eye_status('Candidate is Seeing CENTER')
                    e="c"

        if ret == True:
            faces = find_faces(frame, face_model)
            for face in faces:
                marks = detect_marks(frame, landmark_model, face)
                image_points = np.array([
                                        marks[30],     # Nose tip
                                        marks[8],     # Chin
                                        marks[36],     # Left eye left corner
                                        marks[45],     # Right eye right corne
                                        marks[48],     # Left Mouth corner
                                        marks[54]      # Right mouth corner
                                    ], dtype="double")
                dist_coeffs = np.zeros((4,1)) # Assuming no lens distortion
                (success, rotation_vector, translation_vector) = cv.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv.SOLVEPNP_UPNP)
                
                (nose_end_point2D, jacobian) = cv.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector, translation_vector, camera_matrix, dist_coeffs)
                
                p1 = ( int(image_points[0][0]), int(image_points[0][1]))
                p2 = ( int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
                x1, x2 = head_pose_points(frame, rotation_vector, translation_vector, camera_matrix)

            
                try:
                    m = (x2[1] - x1[1])/(x2[0] - x1[0])
                    ang2 = int(math.degrees(math.atan(-1/m)))
                except:
                    ang2 = 90
                    
            
                if ang2 >= 40:                                    #40
                    print('Head right')
                    draw_red(frame, faces)
                    cv.putText(frame, "Head RIGHT", (30, 60), cv.FONT_HERSHEY_DUPLEX, 0.6, (255,255,255), 1)
                    warning()
                    cv.imwrite("image.png", frame)
                elif ang2 <= -40:   
                    draw_red(frame, faces)                             #-40
                    print('Head left')
                    cv.putText(frame, "Head LEFT", (30, 60), cv.FONT_HERSHEY_DUPLEX, 0.6, (255,255,255), 1)
                    warning()
                    cv.imwrite("image.png", frame)
                elif e=="l":
                    cv.putText(frame, "Candidate is Seeing RIGHT", (30, 60), cv.FONT_HERSHEY_DUPLEX, 0.6, (255,255,255), 1)
                    warning()
                elif e=="r":
                    cv.putText(frame, "Candidate is Seeing LEFT", (30, 60), cv.FONT_HERSHEY_DUPLEX, 0.6, (255,255,255), 1)
                    warning()
                elif e=="c":
                    cv.putText(frame, "Candidate is Seeing CENTER", (30, 60), cv.FONT_HERSHEY_DUPLEX, 0.6, (255,255,255), 1)
                
              
                draw_faces(frame, faces)
        new_frame_time = time.time()
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time
        print(fps)
        cv.imshow('frame', frame)
        key = cv.waitKey(2)
        if key == 27:     # press escape key to stop execution
            break
    cap.release()
    cv.destroyAllWindows()
visual_based()
