#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from functools import partial
from example_interfaces.msg import Bool, Float32, Int16, String 
from charmie_interfaces.msg import Yolov8Pose, DetectedPerson, Yolov8Objects, DetectedObject, TarNavSDNL
from charmie_interfaces.srv import TrackObject, TrackPerson, ActivateYoloPose, ActivateYoloObjects, SpeechCommand, NavTrigger
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseWithCovarianceStamped
import numpy as np
import math

import cv2 
import threading
import time
from cv_bridge import CvBridge

# Constant Variables to ease RGB_MODE coding
RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE, ORANGE, PINK, BROWN  = 0, 10, 20, 30, 40, 50, 60, 70, 80, 90
SET_COLOUR, BLINK_LONG, BLINK_QUICK, ROTATE, BREATH, ALTERNATE_QUARTERS, HALF_ROTATE, MOON, BACK_AND_FORTH_4, BACK_AND_FORTH_8  = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
CLEAR, RAINBOW_ROT, RAINBOW_ALL, POLICE, MOON_2_COLOUR, PORTUGAL_FLAG, FRANCE_FLAG, NETHERLANDS_FLAG = 255, 100, 101, 102, 103, 104, 105, 106

class TestNode(Node):

    def __init__(self):
        super().__init__("Debug")
        self.get_logger().info("Initialised CHARMIE Debug Navigation and Localisation Node")

        # Navigation
        self.target_pos_publisher = self.create_publisher(TarNavSDNL, "target_pos", 10)
        self.flag_pos_reached_subscriber = self.create_subscription(Bool, "flag_pos_reached", self.flag_navigation_reached_callback, 10) 

        # Localisation
        self.initialpose_publisher = self.create_publisher(PoseWithCovarianceStamped, "initialpose", 10)

        # Low level
        self.rgb_mode_publisher = self.create_publisher(Int16, "rgb_mode", 10)

        # Speakers
        self.speech_command_client = self.create_client(SpeechCommand, "speech_command")
        
        # Navigation
        self.nav_trigger_client = self.create_client(NavTrigger, "nav_trigger")

        # Navigation
        while not self.nav_trigger_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Navigation Trigger Command...")

        
        ### CHECK IF ALL SERVICES ARE RESPONSIVE ###
        # Speakers
        # while not self.speech_command_client.wait_for_service(1.0):
        #     self.get_logger().warn("Waiting for Server Speech Command...")

        # Wait Variables
        self.waited_for_end_of_track_person = False
        self.waited_for_end_of_track_object = False
        self.waited_for_end_of_speaking = False

        # Code Variables
        self.flag_navigation_reached = False
        
        # Success and Message confirmations for all set_(something) CHARMIE functions
        self.rgb_success = True
        self.rgb_message = ""
        self.speech_success = True
        self.speech_message = ""
        self.navigation_success = True
        self.navigation_message = ""


    def flag_navigation_reached_callback(self, flag: Bool):
        self.flag_navigation_reached = flag

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


def main(args=None):
    rclpy.init(args=args)
    node = TestNode()
    th_main = threading.Thread(target=thread_main_restaurant, args=(node,), daemon=True)
    th_main.start()
    rclpy.spin(node)
    rclpy.shutdown()

def thread_main_restaurant(node: TestNode):
    main = RestaurantMain(node)
    main.main()

class RestaurantMain():

    def __init__(self, node: TestNode):
        self.node = node
    

    def set_rgb(self, command="", wait_for_end_of=True):
        
        temp = Int16()
        temp.data = command
        self.node.rgb_mode_publisher.publish(temp)

        self.node.rgb_success = True
        self.node.rgb_message = "Value Sucessfully Sent"

        return self.node.rgb_success, self.node.rgb_message

    def set_speech(self, filename="", command="", quick_voice=False, show_in_face=False, wait_for_end_of=True):

        self.node.call_speech_command_server(filename=filename, command=command, wait_for_end_of=wait_for_end_of, quick_voice=quick_voice, show_in_face=show_in_face)
        
        if wait_for_end_of:
          while not self.node.waited_for_end_of_speaking:
            pass
        self.node.waited_for_end_of_speaking = False

        return self.node.speech_success, self.node.speech_message

    # def track_object(self, object, wait_for_end_of=True):
    # 
    #     self.node.call_neck_track_object_server(object=object, wait_for_end_of=wait_for_end_of)
    #     
    #     if wait_for_end_of:
    #        while not self.node.waited_for_end_of_track_object:
    #         pass
    #     self.node.waited_for_end_of_track_object = False
    # 
    #     return self.node.track_object_success, self.node.track_object_message   
    
    def set_navigation(self, movement="", target=[0.0, 0.0], absolute_angle=0.0, flag_not_obs=False, follow_me=False, wait_for_end_of=True):


        if movement.lower() != "move" and movement.lower() != "rotate" and movement.lower() != "orientate":
            self.node.get_logger().error("WRONG MOVEMENT NAME: PLEASE USE: MOVE, ROTATE OR ORIENTATE.")

            self.navigation_success = False
            self.navigation_message = "Wrong Movement Name"

        else:
            
            navigation = TarNavSDNL()

            # Pose2D target_coordinates
            # string move_or_rotate
            # float32 orientation_absolute
            # bool flag_not_obs
            # bool follow_me

            navigation.target_coordinates.x = target[0]
            navigation.target_coordinates.y = target[1]
            navigation.move_or_rotate = movement
            navigation.orientation_absolute = absolute_angle
            navigation.flag_not_obs = flag_not_obs
            navigation.follow_me = follow_me

            self.node.flag_navigation_reached = False
            
            self.node.target_pos_publisher.publish(navigation)

            if wait_for_end_of:
                while not self.node.flag_navigation_reached:
                    pass
                self.node.flag_navigation_reached = False

            self.navigation_success = True
            self.navigation_message = "Arrived at selected location"

        return self.node.navigation_success, self.node.navigation_message   


    def set_initial_position(self, initial_position):

        task_initialpose = PoseWithCovarianceStamped()

        task_initialpose.header.frame_id = "map"
        task_initialpose.header.stamp = self.node.get_clock().now().to_msg()

        task_initialpose.pose.pose.position.x = initial_position[1]
        task_initialpose.pose.pose.position.y = -initial_position[0]
        task_initialpose.pose.pose.position.z = 0.0

        # quaternion = self.get_quaternion_from_euler(0,0,math.radians(initial_position[2]))

        # Convert an Euler angle to a quaternion.
        # Input
        #     :param roll: The roll (rotation around x-axis) angle in radians.
        #     :param pitch: The pitch (rotation around y-axis) angle in radians.
        #     :param yaw: The yaw (rotation around z-axis) angle in radians.
        # 
        # Output
        #     :return qx, qy, qz, qw: The orientation in quaternion [x,y,z,w] format

        roll = 0.0
        pitch = 0.0
        yaw = math.radians(initial_position[2])

        task_initialpose.pose.pose.orientation.x = np.sin(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) - np.cos(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
        task_initialpose.pose.pose.orientation.y = np.cos(roll/2) * np.sin(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.cos(pitch/2) * np.sin(yaw/2)
        task_initialpose.pose.pose.orientation.z = np.cos(roll/2) * np.cos(pitch/2) * np.sin(yaw/2) - np.sin(roll/2) * np.sin(pitch/2) * np.cos(yaw/2)
        task_initialpose.pose.pose.orientation.w = np.cos(roll/2) * np.cos(pitch/2) * np.cos(yaw/2) + np.sin(roll/2) * np.sin(pitch/2) * np.sin(yaw/2)
        
        self.node.initialpose_publisher.publish(task_initialpose)


    def main(self):
        Waiting_for_start_button = 0
        Searching_for_clients = 1
        Navigation_to_person = 2
        Receiving_order_speach = 3
        Receiving_order_listen_and_confirm = 4
        Collect_order_from_barman = 5
        Delivering_order_to_client = 6
        Final_State = 7
        
        # self.initial_position = [-2.5, 1.5, 0]
        self.initial_position = [-1.0, 1.5, -90.0]

        # navigation positions
        self.front_of_sofa = [-2.5, 1.5]
        self.sofa = [-2.5, 3.0]
        
        # VARS ...
        self.state = Waiting_for_start_button

        while True:

            if self.state == Waiting_for_start_button:
                # your code here ...

                # If initial position is inside while loop you are telling the robot the wrong localisation.
                # This command must only be sent once, at the start of the task
                self.set_initial_position(self.initial_position)

                # next state
                self.state = Searching_for_clients

            elif self.state == Searching_for_clients:
                #print('State 1 = Hand Raising Detect')

                time.sleep(3)
                
                # this gives an error because "orient" is a non-existing movement type and does not send anything to navigation 
                self.set_navigation(movement="orient", target=self.front_of_sofa, flag_not_obs=True, wait_for_end_of=True)

                print("2 move")

                self.set_navigation(movement="orientate", absolute_angle=90.0, flag_not_obs=True, wait_for_end_of=True)

                print("3 move")

                self.set_navigation(movement="move", target=self.front_of_sofa, flag_not_obs=True, wait_for_end_of=True)

                print("4 move")

                self.set_navigation(movement="rotate", target=self.sofa, flag_not_obs=True, wait_for_end_of=True)

                print("5 move")

                # your code here ...
                                
                # next state
                # self.state = Final_State
            
            elif self.state == Final_State:
                # self.node.speech_str.command = "I have finished my restaurant task." 
                # self.node.speaker_publisher.publish(self.node.speech_str)
                # self.wait_for_end_of_speaking()  
                self.state += 1
                print("Finished task!!!")

            else:
                pass