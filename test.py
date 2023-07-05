import main

img1 = "./testing_data/chuck_d"
img2 = "./testing_data/chuck"

res = main.face_match(img1,img2)

if (res == True):
    print("The face in "+img1+" matches with the face in "+img2)
else :
    print("The face in "+img1+" does not matches with the face in "+img2)

