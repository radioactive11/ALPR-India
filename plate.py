from ctypes import *
import os
import cv2
import darknet
import glob


def convertBack(x, y, w, h):								# Convert from center coordinates to bounding box coordinates
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax


def cvDrawBoxes(detections, img):
    
    if len(detections) > 0:    								# If there are any detections
        plate_detection = 0
        for detection in detections:						# For each detection
            name_tag = detection[0].decode()				# Decode list of classes 
            if name_tag == 'license_plate':							# Filter detections for car class
                x, y, w, h = detection[2][0],\
                    detection[2][1],\
                    detection[2][2],\
                    detection[2][3]  						# Obtain the detection coordinates
                xmin, ymin, xmax, ymax = convertBack(
                    float(x), float(y), float(w), float(h))  	# Convert to bounding box coordinates
                xmax += xmax*0.05
                xmax = int(xmax)
                pt1 = (xmin, ymin)								# Format Coordinates for Point 1 and 2
                pt2 = (xmax, ymax)
                save_path = "cropped/"
                roi = img[ymin:ymax, xmin:xmax]
                cv2.imwrite(os.path.join(save_path, str(cvDrawBoxes.counter) + ".jpg"), roi)
                cvDrawBoxes.counter += 1
                cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1) 
                
            plate_detection += 1 								
    return img 												
    

cvDrawBoxes.counter = 0

netMain = None
metaMain = None
altNames = None


def YOLO(image_list):

    global metaMain, netMain, altNames
    configPath = "./cfg/alpr_tiny_test.cfg"
    weightPath = "./alpr_tiny.weights"
    metaPath = "./data/alpr.data"
    if not os.path.exists(configPath):
        raise ValueError("Invalid config path `" +
                         os.path.abspath(configPath)+"`")
    if not os.path.exists(weightPath):
        raise ValueError("Invalid weight path `" +
                         os.path.abspath(weightPath)+"`")
    if not os.path.exists(metaPath):
        raise ValueError("Invalid data file path `" +
                         os.path.abspath(metaPath)+"`")
    if netMain is None:
        netMain = darknet.load_net_custom(configPath.encode(
            "ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1
    if metaMain is None:
        metaMain = darknet.load_meta(metaPath.encode("ascii"))
    if altNames is None:
        try:
            with open(metaPath) as metaFH:
                metaContents = metaFH.read()
                import re
                match = re.search("names *= *(.*)$", metaContents,
                                  re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            altNames = [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass
    i = 0
    while (i < len(image_list)):
        image = cv2.imread(image_list[i])
        width = image.shape[1]
        height = image.shape[0]

        # Create an image we reuse for each detect
        darknet_image = darknet.make_image(width, height, 3)

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb = cv2.resize(image_rgb,
                                       (width, height),
                                       interpolation=cv2.INTER_LINEAR)

        darknet.copy_image_from_bytes(darknet_image, image_rgb.tobytes())

        detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.3)
        image = cvDrawBoxes(detections, image_rgb)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #cv2.imshow('Output', image)
        #cv2.waitKey(0)
        i += 1
    cv2.destroyAllWindows()

if __name__ == "__main__":
    #Get the list of Input Image Files
    
    image_path = "data/plates/"			#  Directory of the image folder
    image_list = glob.glob(image_path + "*.jpg")
    image_list.append(glob.glob(image_path + "*.png"))		#  Get list of Images
    while("" in image_list):
        image_list.remove("")
    print(image_list)		
    YOLO(image_list)