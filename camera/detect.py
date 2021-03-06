import os
import argparse
import cv2
import numpy as np
import sys
import time
from threading import Thread
import importlib.util
from tensorflow.lite.python.interpreter import Interpreter
from VideoController import VideoStream
from centroidtracker import CentroidTracker
#from head import Head


GRAPH_NAME = "detect.tflite"
LABELMAP_NAME = "labelmap.txt"
min_conf_threshold = float(0.5)
imW = 1800
imH = 720

    
CWD_PATH = os.getcwd()

PATH_TO_CKPT = os.path.join(CWD_PATH,GRAPH_NAME)

PATH_TO_LABELS = os.path.join(CWD_PATH,LABELMAP_NAME)

class PeopleDetector():
    __interpreter: Interpreter
    __labels:list
    __alive: bool
    
    def __init__(self):
        self.__alive = True
        with open(PATH_TO_LABELS, 'r') as f:
            self.__labels = [line.strip() for line in f.readlines()]
        
        if self.__labels[0] == '???':
            del(self.__labels[0])
        
        self.__interpreter  = Interpreter(model_path=PATH_TO_CKPT)
        self.__interpreter.allocate_tensors()
         
         
    def run(self) -> None:
        input_details = self.__interpreter.get_input_details()
        output_details = self.__interpreter.get_output_details()
        height = input_details[0]['shape'][1]
        width = input_details[0]['shape'][2]

        floating_model = (input_details[0]['dtype'] == np.float32)

        input_mean = 127.5
        input_std = 127.5

        # Initialize frame rate calculation
        frame_rate_calc = 1
        freq = cv2.getTickFrequency()

# Initialize video stream
        videostream = VideoStream(resolution=(imW,imH),framerate=30).start()
        ct = CentroidTracker()
       # h = Head()
        time.sleep(1)
        frame_count = 0


        while (self.__alive):


            t1 = cv2.getTickCount()

            frame1 = videostream.read()
            frame_count += 1
            frame = frame1.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (width, height))
            input_data = np.expand_dims(frame_resized, axis=0)

            if floating_model:
                input_data = (np.float32(input_data) - input_mean) / input_std

            self.__interpreter.set_tensor(input_details[0]['index'],input_data)
            self.__interpreter.invoke()

            boxes = self.__interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
            classes = self.__interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
            scores = self.__interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
            rects =  []
            r = []
            val = []
            track_id = 0
            max_size = 0
            for i in range(len(scores)):
                if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):
                    
                    object_name = self.__labels[int(classes[i])]
                    if object_name == "person":
                        rects =  []
                        ymin = int(max(1,(boxes[i][0] * imH)))
                        rects.append(ymin)
                        xmin = int(max(1,(boxes[i][1] * imW)))
                        rects.append(xmin)
                        ymax = int(min(imH,(boxes[i][2] * imH)))
                        rects.append(ymax)
                        xmax = int(min(imW,(boxes[i][3] * imW)))
                        rects.append(xmax)
                        rects = [xmin,ymin,xmax,ymax]

                        val = np.array(rects)
                        r.append(val.astype("int"))
                        cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
            

            #Draw label

                        object_name = self.__labels[int(classes[i])] # Look up object name from "labels" array using class index
                        xmid = xmin + ((xmax-xmin)/2)
                        p = 640 - xmid
                    
                        #angle = h.find_angle(p * (1/64))
                        #rot = h.rotate(angle)
                        #label = '%s: %d - %d%%' % (object_name, xmin,xmax) # Example: 'person: 72%'
                        #labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                        #label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                        #cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                        #cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text



    # Draw framerate in corner of frame
            
            objects = ct.update(r)
            #frame_size = output[1]
            
            #print(output)
            print(objects)
            cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
            

                
    #All the results have been drawn on the frame, so it's time to display it.
            flag = 0
            next_id = 0
            i = 0
            new_coord = []
            next_coord = []
            coord = []
            for (objectID, centroid) in objects.items():
                if(objectID == track_id):
                    flag =1
                    new_coord = centroid 
                if(i == 0):
                    next_id = objectID
                    next_coord = centroid 
                    i += 1
                text = "ID {}".format(objectID)
                cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

            if(flag ==0):
                track_id = next_id
                coord = next_coord
            else:
                coord = new_coord
            
            # head rotation
            


        
            cv2.imshow('Object detector', frame)
            
    # Calculate framerate
            t2 = cv2.getTickCount()
            time1 = (t2-t1)/freq
            frame_rate_calc= 1/time1

    # Press 'q' to quit
            if cv2.waitKey(1) == ord('q'):
                break
            
    def stop(self) -> None:
        # Clean up
        cv2.destroyAllWindows()
        videostream.stop()
        self.__alive = False



        
if __name__ == '__main__':
    
    p = PeopleDetector()
    p.run()
