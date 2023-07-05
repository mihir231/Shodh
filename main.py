import PIL.Image
import numpy as np
import dlib

def _convertImgToNpArray(img):
    
    im = PIL.Image.open(img)
    return np.array(im)


def _extractFaceEncodings(img_np):

    #Getting face locations in image
    #mmod_human_face_detector.dat
    cnn_face_detection_model = "./models/cnn_face_detector_model.dat"
    cnn_face_detector = dlib.cnn_face_detection_model_v1(cnn_face_detection_model)
    face_location = cnn_face_detector(img_np)

    if( len(face_location) == 0):
        return None

    face_location = cnn_face_detector(img_np)[0]  
    #shape_predictor_5_face_landmarks.dat
    face_landmark_model = "./models/face_landmarks_model.dat"
    pose_predictor = dlib.shape_predictor(face_landmark_model)

    #css = _rect_to_css(face_location.rect)
    
    #face_location = _trim_css_to_bounds(css, img_np.shape)
    #face_location = _css_to_rect(face_location)

    face_landmark = pose_predictor(img_np, face_location.rect)   
    
    #dlib_face_recognition_resnet_model_v1.dat.bz2
    face_recognition_model = "./models/face_recognition_model.dat"
    face_recognition = dlib.face_recognition_model_v1(face_recognition_model)
    
    return np.array( face_recognition.compute_face_descriptor(img_np, face_landmark, 1) )
 


def face_match(img1,img2):

    img1_np = _convertImgToNpArray(img1)
    img2_np = _convertImgToNpArray(img2)

    enc_1 = _extractFaceEncodings(img1_np)
    enc_2 = _extractFaceEncodings(img2_np)

    distance = "No Face Found"
    if (enc_1 is not None and enc_2 is not None) :
        #euclidean distance
        distance = np.linalg.norm(enc_1-enc_2,axis=0)

    print("Distance: "+str(distance))
    if (distance < 0.65) :
        return True
    else:
        return False


