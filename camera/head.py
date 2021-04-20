#from servo import Servo
from adafruit_servokit import ServoKit
import math


#kit = ServoKit(channels=16)

class Head:
    __angle: int
    __alive: bool
    __rot: int
    
    def __init__(self):
        self.__alive = True
        self.__angle = 90
        self.__rot = 90
        
    def find_angle(self, pos) -> int:
        
        q = pos/50        
        self.__angle = math.degrees(math.atan(q))
        #if(__angle > 180)
        return self.__angle
    
    def rotate(self, ang) -> None:
        
        print("moving head")
        
        self.__rot = 90 + ang
            
        if(self.__rot > 180):
            self.__rot = 180
            print("moving to %d",self.__rot)
            #kit.servo[0].angle = 180
        elif(self.__rot < 0):
            self.__rot = 180
            print("moving to %d",self.__rot)
            #kit.servo[0].angle = 0
            
        else:
            print("moving to %d",self.__rot)
            #kit.servo[0].angle = __rot
            
        return self.__rot
        
        
        
    
    