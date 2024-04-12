#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from example_interfaces.msg import Bool, String, Int16
from geometry_msgs.msg import Pose2D
from charmie_interfaces.msg import Yolov8Pose, DetectedPerson, Yolov8Objects, DetectedObject
from charmie_interfaces.srv import SpeechCommand, GetAudio, CalibrateAudio, SetNeckPosition, GetNeckPosition, SetNeckCoordinates, TrackObject, TrackPerson, ActivateYoloPose, ActivateYoloObjects

# Constant Variables to ease RGB_MODE coding
RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE, ORANGE, PINK, BROWN  = 0, 10, 20, 30, 40, 50, 60, 70, 80, 90
SET_COLOUR, BLINK_LONG, BLINK_QUICK, ROTATE, BREATH, ALTERNATE_QUARTERS, HALF_ROTATE, MOON, BACK_AND_FORTH_4, BACK_AND_FORTH_8  = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
CLEAR, RAINBOW_ROT, RAINBOW_ALL, POLICE, MOON_2_COLOUR, PORTUGAL_FLAG, FRANCE_FLAG, NETHERLANDS_FLAG = 255, 100, 101, 102, 103, 104, 105, 106

import cv2 
import threading
import time
from cv_bridge import CvBridge

class ServeBreakfastNode(Node):

    def __init__(self):
        super().__init__("ServeBreakfast")
        self.get_logger().info("Initialised CHARMIE ServeBreakfast Node")


        ### Topics (Publisher and Subscribers) ###   
        # Low Level 
        self.rgb_mode_publisher = self.create_publisher(Int16, "rgb_mode", 10)   
        self.start_button_subscriber = self.create_subscription(Bool, "get_start_button", self.get_start_button_callback, 10)
        self.flag_start_button_publisher = self.create_publisher(Bool, "flag_start_button", 10) 
        # Face
        self.image_to_face_publisher = self.create_publisher(String, "display_image_face", 10)
        self.custom_image_to_face_publisher = self.create_publisher(String, "display_custom_image_face", 10)
        # Yolo Pose
        # self.person_pose_filtered_subscriber = self.create_subscription(Yolov8Pose, "person_pose_filtered", self.person_pose_filtered_callback, 10)
        # Yolo Objects
        self.object_detected_filtered_subscriber = self.create_subscription(Yolov8Objects, "objects_detected_filtered", self.object_detected_filtered_callback, 10)


        ### Services (Clients) ###
        # Speakers
        self.speech_command_client = self.create_client(SpeechCommand, "speech_command")
        # Audio
        # self.get_audio_client = self.create_client(GetAudio, "audio_command")
        # self.calibrate_audio_client = self.create_client(CalibrateAudio, "calibrate_audio")
        # Neck
        self.set_neck_position_client = self.create_client(SetNeckPosition, "neck_to_pos")
        self.get_neck_position_client = self.create_client(GetNeckPosition, "get_neck_pos")
        self.set_neck_coordinates_client = self.create_client(SetNeckCoordinates, "neck_to_coords")
        self.neck_track_person_client = self.create_client(TrackPerson, "neck_track_person")
        self.neck_track_object_client = self.create_client(TrackObject, "neck_track_object")
        # Yolos
        # self.activate_yolo_pose_client = self.create_client(ActivateYoloPose, "activate_yolo_pose")
        self.activate_yolo_objects_client = self.create_client(ActivateYoloObjects, "activate_yolo_objects")


        ### CHECK IF ALL SERVICES ARE RESPONSIVE ###
        # Speakers
        while not self.speech_command_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Speech Command...")
        # Audio
        # while not self.get_audio_client.wait_for_service(1.0):
        #     self.get_logger().warn("Waiting for Audio Server...")
        # while not self.calibrate_audio_client.wait_for_service(1.0):
        #     self.get_logger().warn("Waiting for Calibrate Audio Server...")
        # Neck 
        while not self.set_neck_position_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Set Neck Position Command...")
        while not self.get_neck_position_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Get Neck Position Command...")
        while not self.set_neck_coordinates_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Set Neck Coordinates Command...")
        while not self.neck_track_person_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Set Neck Track Object Command...")
        while not self.neck_track_object_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Set Neck Track Person Command...")
        # Yolos
        # while not self.activate_yolo_pose_client.wait_for_service(1.0):
        #     self.get_logger().warn("Waiting for Server Yolo Pose Activate Command...")
        while not self.activate_yolo_objects_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Yolo Objects Activate Command...")
        

        # Variables
        self.waited_for_end_of_speaking = False
        self.waited_for_end_of_neck_pos = False
        self.waited_for_end_of_neck_coords = False
        self.waited_for_end_of_get_neck = False
        self.waited_for_end_of_track_person = False
        self.waited_for_end_of_track_object = False

        self.br = CvBridge()
        self.detected_people = Yolov8Pose()
        self.detected_objects = Yolov8Objects()
        self.start_button_state = False

        # Success and Message confirmations for all set_(something) CHARMIE functions
        self.speech_success = True
        self.speech_message = ""
        self.rgb_success = True
        self.rgb_message = ""
        # self.calibrate_audio_success = True
        # self.calibrate_audio_message = ""
        # self.audio_command = ""
        self.face_success = True
        self.face_message = ""
        self.neck_success = True
        self.neck_message = ""
        self.track_person_success = True
        self.track_person_message = ""
        self.track_object_success = True
        self.track_person_message = ""
        # self.activate_yolo_pose_success = True
        # self.activate_yolo_pose_message = ""
        self.activate_yolo_objects_success = True
        self.activate_yolo_objects_message = ""

        self.br = CvBridge()
        self.detected_people = Yolov8Pose()
        self.detected_objects = Yolov8Objects()
        self.start_button_state = False

        self.get_neck_position = [1.0, 1.0]
        

    # def person_pose_filtered_callback(self, det_people: Yolov8Pose):
    #     self.detected_people = det_people
    # 
    #     current_frame = self.br.imgmsg_to_cv2(self.detected_people.image_rgb, "bgr8")
    #     current_frame_draw = current_frame.copy()
    #     
    #     cv2.imshow("Yolo Pose TR Detection 2", current_frame_draw)
    #     cv2.waitKey(10)

    def object_detected_filtered_callback(self, det_object: Yolov8Objects):
        self.detected_objects = det_object

        current_frame = self.br.imgmsg_to_cv2(self.detected_objects.image_rgb, "bgr8")
        current_frame_draw = current_frame.copy()


        # img = [0:720, 0:1280]
        corr_image = False
        thresh_h = 50
        thresh_v = 200

        if self.detected_objects.num_objects > 0:

            x_min = 1280
            x_max = 0
            y_min = 720
            y_max = 0

            for object in self.detected_objects.objects:      
            
                if object.object_class == "Dishes":
                    corr_image = True

                    if object.box_top_left_x < x_min:
                        x_min = object.box_top_left_x
                    if object.box_top_left_x+object.box_width > x_max:
                        x_max = object.box_top_left_x+object.box_width

                    if object.box_top_left_y < y_min:
                        y_min = object.box_top_left_y
                    if object.box_top_left_y+object.box_height > y_max:
                        y_max = object.box_top_left_y+object.box_height

                    start_point = (object.box_top_left_x, object.box_top_left_y)
                    end_point = (object.box_top_left_x+object.box_width, object.box_top_left_y+object.box_height)
                    cv2.rectangle(current_frame_draw, start_point, end_point, (255,255,255) , 4) 

                    cv2.circle(current_frame_draw, (object.box_center_x, object.box_center_y), 5, (255, 255, 255), -1)
                    
            
            for object in self.detected_objects.objects:      
                
                if object.object_class == "Dishes":
                
                    if object.box_top_left_y < 30: # depending on the height of the box, so it is either inside or outside
                        start_point_text = (object.box_top_left_x-2, object.box_top_left_y+25)
                    else:
                        start_point_text = (object.box_top_left_x-2, object.box_top_left_y-22)
                        
                    # just to test for the "serve the breakfast" task...
                    aux_name = object.object_name
                    if object.object_name == "Fork" or object.object_name == "Knife":
                        aux_name = "Spoon"
                    elif object.object_name == "Plate" or object.object_name == "Cup":
                        aux_name = "Bowl"

                    text_size, _ = cv2.getTextSize(f"{aux_name}", cv2.FONT_HERSHEY_DUPLEX, 1, 1)
                    text_w, text_h = text_size
                    cv2.rectangle(current_frame_draw, (start_point_text[0], start_point_text[1]), (start_point_text[0] + text_w, start_point_text[1] + text_h), (255,255,255), -1)
                    cv2.putText(current_frame_draw, f"{aux_name}", (start_point_text[0], start_point_text[1]+text_h+1-1), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)

        if corr_image:
            # current_frame_draw = current_frame_draw[x_min:y_min, x_max,y_max]
            # img = current_frame_draw[y_min:y_max, x_min,x_max]
            cv2.imshow("c", current_frame_draw[max(y_min-thresh_v,0):min(y_max+thresh_v,720), max(x_min-thresh_h,0):min(x_max+thresh_h,1280)])
            cv2.waitKey(10)
            pass
        # cv2.imshow("Yolo Objects TR Detection", current_frame_draw)
        # cv2.waitKey(10)

        # cv2.imwrite("object_detected_test4.jpg", current_frame_draw[max(y_min-thresh_v,0):min(y_max+thresh_v,720), max(x_min-thresh_h,0):min(x_max+thresh_h,1280)]) 
        # cv2.waitKey(10)

    ### LOW LEVEL START BUTTON ###
    def get_start_button_callback(self, state: Bool):
        self.start_button_state = state.data
        # print("Received Start Button:", state.data)

    ### ACTIVATE YOLO POSE SERVER FUNCTIONS ###
    # def call_activate_yolo_pose_server(self, activate=True, only_detect_person_legs_visible=False, minimum_person_confidence=0.5, minimum_keypoints_to_detect_person=7, only_detect_person_right_in_front=False, only_detect_person_arm_raised=False, characteristics=False):
    #     request = ActivateYoloPose.Request()
    #     request.activate = activate
    #     request.only_detect_person_legs_visible = only_detect_person_legs_visible
    #     request.minimum_person_confidence = minimum_person_confidence
    #     request.minimum_keypoints_to_detect_person = minimum_keypoints_to_detect_person
    #     request.only_detect_person_arm_raised = only_detect_person_arm_raised
    #     request.only_detect_person_right_in_front = only_detect_person_right_in_front
    #     request.characteristics = characteristics
    # 
    #     self.activate_yolo_pose_client.call_async(request)\

    ### ACTIVATE YOLO OBJECTS SERVER FUNCTIONS ###
    def call_activate_yolo_objects_server(self, activate_objects=True, activate_shoes=False, activate_doors=False, minimum_objects_confidence=0.5):
        request = ActivateYoloObjects.Request()
        request.activate_objects = activate_objects
        request.activate_shoes = activate_shoes
        request.activate_doors = activate_doors
        request.minimum_objects_confidence = minimum_objects_confidence

        self.activate_yolo_objects_client.call_async(request)
        
    #### SPEECH SERVER FUNCTIONS #####
    def call_speech_command_server(self, filename="", command="", quick_voice=False, wait_for_end_of=True, show_in_face=False):
        request = SpeechCommand.Request()
        request.filename = filename
        request.command = command
        request.quick_voice = quick_voice
        request.show_in_face = show_in_face
    
        future = self.speech_command_client.call_async(request)
        # print("Sent Command")

        if wait_for_end_of:
            # future.add_done_callback(partial(self.callback_call_speech_command, a=filename, b=command))
            future.add_done_callback(self.callback_call_speech_command)
        else:
            self.speech_success = True
            self.speech_message = "Wait for answer not needed"

    def callback_call_speech_command(self, future): #, a, b):

        try:
            # in this function the order of the line of codes matter
            # it seems that when using future variables, it creates some type of threading system
            # if the falg raised is here is before the prints, it gets mixed with the main thread code prints
            response = future.result()
            self.get_logger().info(str(response.success) + " - " + str(response.message))
            self.speech_success = response.success
            self.speech_message = response.message
            # time.sleep(3)
            self.waited_for_end_of_speaking = True
        except Exception as e:
            self.get_logger().error("Service call failed %r" % (e,))   


    #### AUDIO SERVER FUNCTIONS #####
    # def call_audio_server(self, yes_or_no=False, receptionist=False, gpsr=False, restaurant=False, wait_for_end_of=True):
    #     request = GetAudio.Request()
    #     request.yes_or_no = yes_or_no
    #     request.receptionist = receptionist
    #     request.gpsr = gpsr
    #     request.restaurant = restaurant
    # 
    #     future = self.get_audio_client.call_async(request)
    #     # print("Sent Command")
    # 
    #     if wait_for_end_of:
    #         future.add_done_callback(self.callback_call_audio)
    #     else:
    #         self.track_person_success = True
    #         self.track_person_message = "Wait for answer not needed"
    
    # def callback_call_audio(self, future):
    # 
    #     try:
    #         # in this function the order of the line of codes matter
    #         # it seems that when using future variables, it creates some type of threading system
    #         # if the flag raised is here is before the prints, it gets mixed with the main thread code prints
    #         response = future.result()
    #         self.get_logger().info(str(response.command))
    #         self.audio_command = response.command
    #         # self.track_object_success = response.success
    #         # self.track_object_message = response.message
    #         # time.sleep(3)
    #         self.waited_for_end_of_audio = True
    #     except Exception as e:
    #         self.get_logger().error("Service call failed %r" % (e,))


    # def call_calibrate_audio_server(self, wait_for_end_of=True):
    #     request = CalibrateAudio.Request()
    # 
    #     future = self.calibrate_audio_client.call_async(request)
    #     # print("Sent Command")
    # 
    #     if wait_for_end_of:
    #         future.add_done_callback(self.callback_call_calibrate_audio)
    #     else:
    #         self.track_person_success = True
    #         self.track_person_message = "Wait for answer not needed"
    
    # def callback_call_calibrate_audio(self, future):
    #
    #     try:
    #         # in this function the order of the line of codes matter
    #         # it seems that when using future variables, it creates some type of threading system
    #         # if the flag raised is here is before the prints, it gets mixed with the main thread code prints
    #         response = future.result()
    #         self.get_logger().info(str(response.success) + " - " + str(response.message))
    #         self.track_person_success = response.success
    #         self.track_person_message = response.message
    #         # self.track_object_success = response.success
    #         # self.track_object_message = response.message
    #         # time.sleep(3)
    #         self.waited_for_end_of_calibrate_audio = True
    #     except Exception as e:
    #         self.get_logger().error("Service call failed %r" % (e,))

    #### SET NECK POSITION SERVER FUNCTIONS #####
    def call_neck_position_server(self, position=[0, 0], wait_for_end_of=True):
        request = SetNeckPosition.Request()
        request.pan = float(position[0])
        request.tilt = float(position[1])
        
        future = self.set_neck_position_client.call_async(request)
        # print("Sent Command")

        if wait_for_end_of:
            # future.add_done_callback(partial(self.callback_call_speech_command, a=filename, b=command))
            future.add_done_callback(self.callback_call_set_neck_command)
        else:
            self.neck_success = True
            self.neck_message = "Wait for answer not needed"
    
    def callback_call_set_neck_command(self, future): #, a, b):

        try:
            # in this function the order of the line of codes matter
            # it seems that when using future variables, it creates some type of threading system
            # if the falg raised is here is before the prints, it gets mixed with the main thread code prints
            response = future.result()
            self.get_logger().info(str(response.success) + " - " + str(response.message))
            self.speech_success = response.success
            self.speech_message = response.message
            # time.sleep(3)
            self.waited_for_end_of_neck_pos = True
        except Exception as e:
            self.get_logger().error("Service call failed %r" % (e,))   


    #### SET NECK COORDINATES SERVER FUNCTIONS #####
    def call_neck_coordinates_server(self, x, y, z, tilt, flag, wait_for_end_of=True):
        request = SetNeckCoordinates.Request()
        request.coords.x = float(x)
        request.coords.y = float(y)
        request.coords.z = float(z)
        request.is_tilt = flag
        request.tilt = float(tilt)
        
        future = self.set_neck_coordinates_client.call_async(request)
        # print("Sent Command")

        if wait_for_end_of:
            # future.add_done_callback(partial(self.callback_call_speech_command, a=filename, b=command))
            future.add_done_callback(self.callback_call_set_neck_coords_command)
        else:
            self.neck_success = True
            self.neck_message = "Wait for answer not needed"
    
    def callback_call_set_neck_coords_command(self, future): #, a, b):

        try:
            # in this function the order of the line of codes matter
            # it seems that when using future variables, it creates some type of threading system
            # if the falg raised is here is before the prints, it gets mixed with the main thread code prints
            response = future.result()
            self.get_logger().info(str(response.success) + " - " + str(response.message))
            self.speech_success = response.success
            self.speech_message = response.message
            # time.sleep(3)
            self.waited_for_end_of_neck_coords = True
        except Exception as e:
            self.get_logger().error("Service call failed %r" % (e,))   


    #### GET NECK POSITION SERVER FUNCTIONS #####
    def call_get_neck_position_server(self):
        request = GetNeckPosition.Request()
        
        future = self.get_neck_position_client.call_async(request)
        # print("Sent Command")

        # future.add_done_callback(partial(self.callback_call_speech_command, a=filename, b=command))
        future.add_done_callback(self.callback_call_get_neck_command)
    
    def callback_call_get_neck_command(self, future): #, a, b):

        try:
            # in this function the order of the line of codes matter
            # it seems that when using future variables, it creates some type of threading system
            # if the falg raised is here is before the prints, it gets mixed with the main thread code prints
            response = future.result()
            self.get_logger().info("Received Neck Position: (%s" %(str(response.pan) + ", " + str(response.tilt)+")"))
            self.get_neck_position[0] = response.pan
            self.get_neck_position[1] = response.tilt
            # time.sleep(3)
            self.waited_for_end_of_get_neck = True
        except Exception as e:
            self.get_logger().error("Service call failed %r" % (e,))   


    #### NECK SERVER FUNCTIONS #####
    # def call_neck_track_person_server(self, person, body_part="Head", wait_for_end_of=True):
    #     request = TrackPerson.Request()
    #     request.person = person
    #     request.body_part = body_part
    # 
    #     future = self.neck_track_person_client.call_async(request)
    #     # print("Sent Command")
    # 
    #     if wait_for_end_of:
    #         future.add_done_callback(self.callback_call_neck_track_person)
    #     else:
    #         self.track_person_success = True
    #         self.track_person_message = "Wait for answer not needed"
    
    # def callback_call_neck_track_person(self, future):
    # 
    #     try:
    #         # in this function the order of the line of codes matter
    #         # it seems that when using future variables, it creates some type of threading system
    #         # if the falg raised is here is before the prints, it gets mixed with the main thread code prints
    #         response = future.result()
    #         self.get_logger().info(str(response.success) + " - " + str(response.message))
    #         self.track_person_success = response.success
    #         self.track_person_message = response.message
    #         # time.sleep(3)
    #         self.waited_for_end_of_track_person = True
    #     except Exception as e:
    #         self.get_logger().error("Service call failed %r" % (e,))


    def call_neck_track_object_server(self, object, wait_for_end_of=True):
        request = TrackObject.Request()
        request.object = object

        future = self.neck_track_object_client.call_async(request)
        # print("Sent Command")

        if wait_for_end_of:
            future.add_done_callback(self.callback_call_neck_track_object)
        else:
            self.track_person_success = True
            self.track_person_message = "Wait for answer not needed"
    
    def callback_call_neck_track_object(self, future):

        try:
            # in this function the order of the line of codes matter
            # it seems that when using future variables, it creates some type of threading system
            # if the falg raised is here is before the prints, it gets mixed with the main thread code prints
            response = future.result()
            self.get_logger().info(str(response.success) + " - " + str(response.message))
            self.track_object_success = response.success
            self.track_object_message = response.message
            # time.sleep(3)
            self.waited_for_end_of_track_object = True
        except Exception as e:
            self.get_logger().error("Service call failed %r" % (e,))


def main(args=None):
    rclpy.init(args=args)
    node = ServeBreakfastNode()
    th_main = threading.Thread(target=ThreadMainServeBreakfast, args=(node,), daemon=True)
    th_main.start()
    rclpy.spin(node)
    rclpy.shutdown()

def ThreadMainServeBreakfast(node: ServeBreakfastNode):
    main = ServeBreakfastMain(node)
    main.main()

class ServeBreakfastMain():

    def __init__(self, node: ServeBreakfastNode):
        self.node = node

    def set_speech(self, filename="", command="", quick_voice=False, show_in_face=False, wait_for_end_of=True):

        self.node.call_speech_command_server(filename=filename, command=command, wait_for_end_of=wait_for_end_of, quick_voice=quick_voice, show_in_face=show_in_face)
        
        if wait_for_end_of:
          while not self.node.waited_for_end_of_speaking:
            pass
        self.node.waited_for_end_of_speaking = False

        return self.node.speech_success, self.node.speech_message

    def set_rgb(self, command="", wait_for_end_of=True):
        
        temp = Int16()
        temp.data = command
        self.node.rgb_mode_publisher.publish(temp)

        self.node.rgb_success = True
        self.node.rgb_message = "Value Sucessfully Sent"

        return self.node.rgb_success, self.node.rgb_message
 
    def wait_for_start_button(self):

        self.node.start_button_state = False

        t = Bool()
        t.data = True
        self.node.flag_start_button_publisher.publish(t)

        while not self.node.start_button_state:
            pass

        t.data = False 
        self.node.flag_start_button_publisher.publish(t)

    """    
    def get_audio(self, yes_or_no=False, receptionist=False, gpsr=False, restaurant=False, question="", wait_for_end_of=True):

        if yes_or_no or receptionist or gpsr or restaurant:

            # this code continuously asks for new audio info eveytime it gets an error for mishearing
            audio_error_counter = 0
            keywords = "ERROR"
            while keywords=="ERROR":
                
                self.set_speech(filename=question, wait_for_end_of=True)
                self.node.call_audio_server(yes_or_no=yes_or_no, receptionist=receptionist, gpsr=gpsr, restaurant=restaurant, wait_for_end_of=wait_for_end_of)
                
                if wait_for_end_of:
                    while not self.node.waited_for_end_of_audio:
                        pass
                self.node.waited_for_end_of_audio = False

                keywords = self.node.audio_command  
                
                if keywords=="ERROR":
                    audio_error_counter += 1

                    if audio_error_counter == 2:
                        self.set_speech(filename="generic/please_wait", wait_for_end_of=True)
                        self.calibrate_audio(wait_for_end_of=True)
                        audio_error_counter = 0

                    self.set_speech(filename="generic/not_understand_please_repeat", wait_for_end_of=True)

            return self.node.audio_command  

        else:
            self.node.get_logger().error("ERROR: No audio type selected")
            return "ERROR: No audio type selected" 

    def calibrate_audio(self, wait_for_end_of=True):
            
        self.node.call_calibrate_audio_server(wait_for_end_of=wait_for_end_of)

        if wait_for_end_of:
            while not self.node.waited_for_end_of_calibrate_audio:
                pass
        self.node.waited_for_end_of_calibrate_audio = False

        return self.node.calibrate_audio_success, self.node.calibrate_audio_message 
    """
    
    def set_face(self, command="", custom="", wait_for_end_of=True):
        
        if custom == "":
            temp = String()
            temp.data = command
            self.node.image_to_face_publisher.publish(temp)
        else:
            temp = String()
            temp.data = custom
            self.node.custom_image_to_face_publisher.publish(temp)

        self.node.face_success = True
        self.node.face_message = "Value Sucessfully Sent"

        return self.node.face_success, self.node.face_message
    
    def set_neck(self, position=[0, 0], wait_for_end_of=True):

        self.node.call_neck_position_server(position=position, wait_for_end_of=wait_for_end_of)
        
        if wait_for_end_of:
          while not self.node.waited_for_end_of_neck_pos:
            pass
        self.node.waited_for_end_of_neck_pos = False

        return self.node.neck_success, self.node.neck_message
    
    def set_neck_coords(self, position=[], ang=0.0, wait_for_end_of=True):

        if len(position) == 2:
            self.node.call_neck_coordinates_server(x=position[0], y=position[1], z=0.0, tilt=ang, flag=True, wait_for_end_of=wait_for_end_of)
        elif len(position) == 3:
            print("You tried neck to coordintes using (x,y,z) please switch to (x,y,theta)")
            pass
            # The following line is correct, however since the functionality is not implemented yet, should not be called
            # self.node.call_neck_coordinates_server(x=position[0], y=position[1], z=position[2], tilt=0.0, flag=False, wait_for_end_of=wait_for_end_of)
        else:
            print("Something went wrong")
        
        if wait_for_end_of:
          while not self.node.waited_for_end_of_neck_coords:
            pass
        self.node.waited_for_end_of_neck_coords = False

        return self.node.neck_success, self.node.neck_message
    
    def get_neck(self, wait_for_end_of=True):
    
        self.node.call_get_neck_position_server()
        
        if wait_for_end_of:
          while not self.node.waited_for_end_of_get_neck:
            pass
        self.node.waited_for_end_of_get_neck = False


        return self.node.get_neck_position[0], self.node.get_neck_position[1] 
    
    # def activate_yolo_pose(self, activate=True, only_detect_person_legs_visible=False, minimum_person_confidence=0.5, minimum_keypoints_to_detect_person=7, only_detect_person_right_in_front=False, only_detect_person_arm_raised=False, characteristics=False, wait_for_end_of=True):
    #     
    #     self.node.call_activate_yolo_pose_server(activate=activate, only_detect_person_legs_visible=only_detect_person_legs_visible, minimum_person_confidence=minimum_person_confidence, minimum_keypoints_to_detect_person=minimum_keypoints_to_detect_person, only_detect_person_right_in_front=only_detect_person_right_in_front, only_detect_person_arm_raised=only_detect_person_arm_raised, characteristics=characteristics)
    # 
    #     self.node.activate_yolo_pose_success = True
    #     self.node.activate_yolo_pose_message = "Activated with selected parameters"
    # 
    #     return self.node.activate_yolo_pose_success, self.node.activate_yolo_pose_message

    def activate_yolo_objects(self, activate_objects=True, activate_shoes=False, activate_doors=False, minimum_objects_confidence=0.5, wait_for_end_of=True):
        
        # self.node.call_activate_yolo_pose_server(activate=activate, only_detect_person_legs_visible=only_detect_person_legs_visible, minimum_person_confidence=minimum_person_confidence, minimum_keypoints_to_detect_person=minimum_keypoints_to_detect_person, only_detect_person_right_in_front=only_detect_person_right_in_front, characteristics=characteristics)
        self.node.call_activate_yolo_objects_server(activate_objects=activate_objects, activate_shoes=activate_shoes, activate_doors=activate_doors, minimum_objects_confidence=minimum_objects_confidence)

        self.node.activate_yolo_objects_success = True
        self.node.activate_yolo_objects_message = "Activated with selected parameters"

        return self.node.activate_yolo_objects_success, self.node.activate_yolo_objects_message

    # def track_person(self, person, body_part="Head", wait_for_end_of=True):
    # 
    #     self.node.call_neck_track_person_server(person=person, body_part=body_part, wait_for_end_of=wait_for_end_of)
    # 
    #     if wait_for_end_of:
    #       while not self.node.waited_for_end_of_track_person:
    #         pass
    #     self.node.waited_for_end_of_track_person = False
    # 
    #     return self.node.track_person_success, self.node.track_person_message
 
    def track_object(self, object, wait_for_end_of=True):

        self.node.call_neck_track_object_server(object=object, wait_for_end_of=wait_for_end_of)
        
        if wait_for_end_of:
          while not self.node.waited_for_end_of_track_object:
            pass
        self.node.waited_for_end_of_track_object = False

        return self.node.track_object_success, self.node.track_object_message   

    def main(self):
        
        # Task Related Variables
        self.Waiting_for_task_start = 0
        self.Approach_kitchen_counter = 1
        self.Detect_all_objects = 10
        self.Picking_up_spoon = 2
        self.Picking_up_milk = 3
        self.Picking_up_cereal = 4
        self.Picking_up_bowl = 5
        self.Approach_kitchen_table = 6
        self.Placing_bowl = 7
        self.Placing_cereal = 8
        self.Placing_milk = 9
        self.Placing_spoon = 10
        self.Final_State = 11

        # Neck Positions
        self.look_forward = [0, 0]
        self.look_navigation = [0, -30]
        self.look_judge = [45, 0]
        self.look_table_objects = [-45, -45]
        self.look_table_objects_temp = [45, -45]
        self.look_tray = [0, -60]

        # to debug just a part of the task you can just change the initial state, example:
        # self.state = self.Approach_kitchen_table
        self.state = self.Detect_all_objects

        ########## ADJUST ALL THE WAIT FOR END OF
        ########## I THINK IT MAKE SENSE TO DO THE DETECTION ONCE AT THE START RATHER THAN AT THE START OF EACH OBJECT, IT SAVES TIME MOVING THE ARM...
        ########## ADICIONAR RGBs

        self.node.get_logger().info("IN SERVE THE BREAKFAST MAIN")

        while True:

            if self.state == self.Waiting_for_task_start:

                """
                # p, t = self.get_neck()
                # self.node.get_logger().info("p, t = %s" %(str(p)+", "+str(t)))



                # self.set_face("help_pick_cereal")

                

                self.set_speech(filename="sb_ready_start", wait_for_end_of=True)
                
                # self.node.get_logger().info("p, t = %s" %(str(self.node.get_neck_position[0])+", "+str(self.node.get_neck_position[1])))


                # self.set_speech(filename="waiting_door_open", wait_for_end_of=False)
                
                # self.set_rgb(RED+ALTERNATE_QUARTERS)
                # self.set_face("help_pick_milk")

                ###### WAITS FOR START BUTTON / DOOR OPEN

                time.sleep(2)
                
                # self.set_neck(position=[-180, 20], wait_for_end_of=True)
                

                self.set_neck_coords(position=[1.0, 1.0], ang=30, wait_for_end_of=True)

                time.sleep(2)
                
                self.set_neck_coords(position=[2.0, 1.0, 2.0], wait_for_end_of=True)

                time.sleep(2)
                
                self.set_neck_coords(position=[0.0, 2.0], ang=0, wait_for_end_of=True)

                time.sleep(2)
                
                self.set_neck_coords(position=[-2.0, 2.0], ang=-30, wait_for_end_of=True)

                time.sleep(2)
                
                self.set_neck_coords(position=[0.0, -2.0], ang=0, wait_for_end_of=True)

                # print(s,m)
                
                self.set_speech(filename="waiting_start_button", wait_for_end_of=True) # must change to door open

                # p, t = self.get_neck(wait_for_end_of=True)
                # self.node.get_logger().info("p, t = %s" %(str(p)+", "+str(t)))

                while True:
                    pass
                """

                # self.set_neck(position=self.look_forward) #, wait_for_end_of=True)
                self.activate_yolo_objects(activate_objects=False)

                self.set_face("demo5")

                self.set_speech(filename="serve_breakfast/sb_ready_start", show_in_face=True, wait_for_end_of=True)

                self.set_speech(filename="generic/waiting_start_button", show_in_face=True, wait_for_end_of=True) # must change to door open

                ###### WAITS FOR START BUTTON / DOOR OPEN

                time.sleep(2)

                self.state = self.Approach_kitchen_counter

            elif self.state == self.Approach_kitchen_counter:

                # self.set_neck(position=self.look_navigation) # , wait_for_end_of=True)

                self.set_speech(filename="serve_breakfast/sb_moving_kitchen_counter", wait_for_end_of=True)

                ###### MOVEMENT TO THE KITCHEN COUNTER

                self.set_speech(filename="serve_breakfast/sb_arrived_kitchen_counter", wait_for_end_of=True)
                
                self.state = self.Detect_all_objects













            elif self.state == self.Detect_all_objects:

                self.set_neck(position=self.look_navigation) # , wait_for_end_of=True)

                self.set_speech(filename="serve_breakfast/sb_arrived_kitchen_counter", wait_for_end_of=True)
                
                self.set_neck(position=self.look_table_objects_temp, wait_for_end_of=True)
                
                # self.set_speech(filename="generic/search_objects", wait_for_end_of=True)

                # time.sleep(5)

                list_of_neck_position_search = [[0, 0], [10,10], [-10,10], [10,-5], [-10,-5]]

                self.activate_yolo_objects(activate_objects=True)
                for pos in list_of_neck_position_search:

                    print(pos)
                    new_neck_pos = [self.look_table_objects_temp[0] + pos[0], self.look_table_objects_temp[1] + pos[1]]
                    # new_neck_pos[0] = self.look_table_objects_temp[0] + pos[0]
                    # new_neck_pos[1] = self.look_table_objects_temp[1] + pos[1]
                    self.set_neck(position=new_neck_pos, wait_for_end_of=True)
                    self.set_speech(filename="generic/search_objects", wait_for_end_of=True)
                    time.sleep(2)


                self.set_neck(position=self.look_navigation) # , wait_for_end_of=True)
                self.activate_yolo_objects(activate_objects=False)
                while True:
                    pass

                self.state = self.Picking_up_spoon













            elif self.state == self.Picking_up_spoon:

                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)

                ##### MOVES ARM TO TOP OF TABLE POSITION

                self.set_speech(filename="generic/search_objects", wait_for_end_of=True)

                ##### YOLO OBJECTS SEARCH FOR SPOON, FOR BOTH CAMERAS

                # self.set_neck(position=self.look_judge, wait_for_end_of=True)

                self.set_speech(filename="serve_breakfast/sb_found_spoon", show_in_face=True, wait_for_end_of=True)

                self.set_speech(filename="generic/check_face_object_detected", wait_for_end_of=True)

                ##### SHOW FACE DETECTED OBJECT

                ##### MOVE ARM TO PICK UP OBJECT 

                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)

                ##### IF AN ERROR IS DETECTED:
                
                self.set_speech(filename="generic/problem_pick_object", wait_for_end_of=True) # False
                   
                    ##### MOVE ARM TO ERROR POSITION 
                
                # self.set_neck(position=self.look_judge, wait_for_end_of=True)
                
                self.set_speech(filename="generic/check_face_put_object_hand", wait_for_end_of=True)

                self.set_face("help_pick_spoon") 

                time.sleep(2)
                
                    ##### WHILE OBJECT IS NOT IN GRIPPER:
                
                self.set_speech(filename="arm/arm_close_gripper", wait_for_end_of=True)

                        ##### ARM CLOSE GRIPPER

                        ##### IF OBJECT NOT GRABBED:
                
                self.set_speech(filename="arm/arm_error_receive_object", wait_for_end_of=True)
                        
                            ##### ARM OPEN GRIPPER
                
                self.set_face("demo5")
                        
                # self.set_neck(position=self.look_tray, wait_for_end_of=True)
                
                ##### ARM PLACE OBJECT IN TRAY

                self.state = self.Picking_up_milk

            elif self.state == self.Picking_up_milk:

                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)

                ##### MOVES ARM TO TOP OF TABLE POSITION

                self.set_speech(filename="generic/search_objects", wait_for_end_of=True)

                ##### YOLO OBJECTS SEARCH FOR MILK, FOR BOTH CAMERAS

                # self.set_neck(position=self.look_judge, wait_for_end_of=True)

                self.set_speech(filename="serve_breakfast/sb_found_milk", show_in_face=True, wait_for_end_of=True)

                self.set_speech(filename="generic/check_face_object_detected", wait_for_end_of=True)

                ##### SHOW FACE DETECTED OBJECT

                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)

                ##### MOVE ARM TO PICK UP OBJECT 

                ##### IF AN ERROR IS DETECTED:
                
                self.set_speech(filename="generic/problem_pick_object", wait_for_end_of=True) # False
                   
                    ##### MOVE ARM TO ERROR POSITION 
                
                # self.set_neck(position=self.look_judge, wait_for_end_of=True)             
                
                self.set_speech(filename="generic/check_face_put_object_hand", wait_for_end_of=True)

                self.set_face("help_pick_milk") 

                time.sleep(2)
                
                    ##### WHILE OBJECT IS NOT IN GRIPPER:
                
                self.set_speech(filename="arm/arm_close_gripper", wait_for_end_of=True)

                        ##### ARM CLOSE GRIPPER

                        ##### IF OBJECT NOT GRABBED:
                
                self.set_speech(filename="arm/arm_error_receive_object", wait_for_end_of=True)
                        
                            ##### ARM OPEN GRIPPER
                
                self.set_face("demo5")
                        
                # self.set_neck(position=self.look_tray, wait_for_end_of=True)
                        
                ##### ARM PLACE OBJECT IN TRAY

                self.state = self.Picking_up_cereal
           
            elif self.state == self.Picking_up_cereal:

                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)

                ##### MOVES ARM TO TOP OF TABLE POSITION

                self.set_speech(filename="generic/search_objects", wait_for_end_of=True)

                ##### YOLO OBJECTS SEARCH FOR CEREAL, FOR BOTH CAMERAS

                # self.set_neck(position=self.look_judge, wait_for_end_of=True)
                
                self.set_speech(filename="serve_breakfast/sb_found_cereal", show_in_face=True, wait_for_end_of=True)

                self.set_speech(filename="generic/check_face_object_detected", wait_for_end_of=True)

                ##### SHOW FACE DETECTED OBJECT

                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)

                ##### MOVE ARM TO PICK UP OBJECT 

                ##### IF AN ERROR IS DETECTED:
                
                self.set_speech(filename="generic/problem_pick_object", wait_for_end_of=True) # False
                   
                    ##### MOVE ARM TO ERROR POSITION
                
                # self.set_neck(position=self.look_judge, wait_for_end_of=True)
                
                self.set_speech(filename="generic/check_face_put_object_hand", wait_for_end_of=True)

                self.set_face("help_pick_cereal") 

                time.sleep(2)
                
                    ##### WHILE OBJECT IS NOT IN GRIPPER:
                
                self.set_speech(filename="arm/arm_close_gripper", wait_for_end_of=True)

                        ##### ARM CLOSE GRIPPER

                        ##### IF OBJECT NOT GRABBED:
                
                self.set_speech(filename="arm/arm_error_receive_object", wait_for_end_of=True)
                        
                            ##### ARM OPEN GRIPPER
                
                self.set_face("demo5")

                # self.set_neck(position=self.look_tray, wait_for_end_of=True)
                        
                ##### ARM PLACE OBJECT IN TRAY

                self.state = self.Picking_up_bowl

            elif self.state == self.Picking_up_bowl:

                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)

                ##### MOVES ARM TO TOP OF TABLE POSITION

                self.set_speech(filename="generic/search_objects", wait_for_end_of=True)

                ##### YOLO OBJECTS SEARCH FOR BOWL, FOR BOTH CAMERAS

                # self.set_neck(position=self.look_judge, wait_for_end_of=True)

                self.set_speech(filename="serve_breakfast/sb_found_bowl", show_in_face=True, wait_for_end_of=True)

                self.set_speech(filename="generic/check_face_object_detected", wait_for_end_of=True)

                ##### SHOW FACE DETECTED OBJECT

                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)

                ##### MOVE ARM TO PICK UP OBJECT 

                ##### IF AN ERROR IS DETECTED:
                
                self.set_speech(filename="generic/problem_pick_object", wait_for_end_of=True) # False
                   
                    ##### MOVE ARM TO ERROR POSITION 
                
                # self.set_neck(position=self.look_judge, wait_for_end_of=True)

                self.set_speech(filename="generic/check_face_put_object_hand", wait_for_end_of=True)
                    
                self.set_face("help_pick_bowl") 

                time.sleep(2)
                
                    ##### WHILE OBJECT IS NOT IN GRIPPER:
                
                self.set_speech(filename="arm/arm_close_gripper", wait_for_end_of=True)

                        ##### ARM CLOSE GRIPPER

                        ##### IF OBJECT NOT GRABBED:
                
                self.set_speech(filename="arm/arm_error_receive_object", wait_for_end_of=True)
                        
                            ##### ARM OPEN GRIPPER

                self.set_face("demo5")

                # self.set_neck(position=self.look_tray, wait_for_end_of=True)
                        
                ##### ARM PLACE OBJECT IN TRAY

                self.state = self.Approach_kitchen_table

            elif self.state == self.Approach_kitchen_table:

                self.set_speech(filename="generic/objects_all_collected", wait_for_end_of=True)

                # self.set_neck(position=[0, -30], wait_for_end_of=True)

                self.set_speech(filename="serve_breakfast/sb_moving_kitchen_table", wait_for_end_of=True)

                ###### MOVEMENT TO THE KITCHEN TABLE

                self.set_speech(filename="serve_breakfast/sb_arrived_kitchen_table", wait_for_end_of=True)

                self.set_speech(filename="generic/place_object_table", wait_for_end_of=True)

                self.set_speech(filename="generic/place_stay_clear", wait_for_end_of=True)

                self.state = self.Placing_bowl

            elif self.state == self.Placing_bowl:

                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)
                time.sleep(1)

                ##### ARM MOVE TO TABLE

                ##### ARM PLACE OBJECT

                self.set_speech(filename="generic/place_object_placed", wait_for_end_of=True)

                self.state = self.Placing_cereal 

            elif self.state == self.Placing_cereal:

                # self.set_neck(position=self.look_tray, wait_for_end_of=True)
                time.sleep(1)
                ##### ARM MOVE TRAY

                ##### ARM PICK OBJECT 

                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)

                ##### ARM MOVE TO TABLE

                ##### ARM POUR IN BOWL

                ##### ARM PLACE OBJECT

                self.set_speech(filename="generic/place_object_placed", wait_for_end_of=True)

                self.state = self.Placing_milk
           
            elif self.state == self.Placing_milk:

                # self.set_neck(position=self.look_tray, wait_for_end_of=True)
                time.sleep(1)

                ##### ARM MOVE TRAY

                ##### ARM PICK OBJECT 

                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)

                ##### ARM MOVE TO TABLE

                ##### ARM POUR IN BOWL

                ##### ARM PLACE OBJECT

                self.set_speech(filename="generic/place_object_placed", wait_for_end_of=True)

                self.state = self.Placing_spoon

            elif self.state == self.Placing_spoon:

                # self.set_neck(position=self.look_tray, wait_for_end_of=True)
                time.sleep(1)

                ##### ARM MOVE TRAY

                ##### ARM PICK OBJECT 

                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)

                ##### ARM MOVE TO TABLE

                ##### ARM PLACE OBJECT

                self.set_speech(filename="generic/place_object_placed", wait_for_end_of=True)

                self.state = self.Final_State 
                
            elif self.state == self.Final_State:

                # self.set_neck(position=self.look_judge) # , wait_for_end_of=True)

                self.set_speech(filename="serve_breakfast/sb_finished", wait_for_end_of=True)

                while True:
                    pass

            else:
                pass
