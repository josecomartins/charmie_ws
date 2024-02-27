#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

import threading

from example_interfaces.msg import Bool, String, Int16
from geometry_msgs.msg import Pose2D
from charmie_interfaces.srv import SpeechCommand, SetNeckPosition, GetNeckPosition

import time

# Constant Variables to ease RGB_MODE coding
RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE, ORANGE, PINK, BROWN  = 0, 10, 20, 30, 40, 50, 60, 70, 80, 90
SET_COLOUR, BLINK_LONG, BLINK_QUICK, ROTATE, BREATH, ALTERNATE_QUARTERS, HALF_ROTATE, MOON, BACK_AND_FORTH_4, BACK_AND_FORTH_4  = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
CLEAR, RAINBOW_ROT, RAINBOW_ALL, POLICE, MOON_2_COLOUR, PORTUGAL_FLAG, FRANCE_FLAG, NETHERLANDS_FLAG = 255, 100, 101, 102, 103, 104, 105, 106


class ServeBreakfastNode(Node):

    def __init__(self):
        super().__init__("ServeBreakfast")
        self.get_logger().info("Initialised CHARMIE ServeBreakfast Node")


        ### Topics (Publisher and Subscribers) ###  
        # Face
        self.image_to_face_publisher = self.create_publisher(String, "display_image_face", 10)
        self.custom_image_to_face_publisher = self.create_publisher(String, "display_custom_image_face", 10)

        # Low level
        self.rgb_mode_publisher = self.create_publisher(Int16, "rgb_mode", 10)

        # Neck
        # self.neck_position_publisher = self.create_publisher(NeckPosition, "neck_to_pos", 10)
        self.neck_to_coords_publisher = self.create_publisher(Pose2D, "neck_to_coords", 10)


        ### Services (Clients) ###
        # Neck
        self.set_neck_position_client = self.create_client(SetNeckPosition, "neck_to_pos")
        self.get_neck_position_client = self.create_client(GetNeckPosition, "get_neck_pos")

        # Speakers
        self.speech_command_client = self.create_client(SpeechCommand, "speech_command")


        ### CHECK IF ALL SERVICES ARE RESPONSIVE ###
        # Neck 
        while not self.set_neck_position_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Set Neck Position Command...")
        while not self.get_neck_position_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Get Neck Position Command...")

        # Speakers
        while not self.speech_command_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Speech Command...")

        # Variables
        self.waited_for_end_of_speaking = False
        self.waited_for_end_of_neck = False
        self.waited_for_end_of_get_neck = False

        # Sucess and Message confirmations for all set_(something) CHARMIE functions
        self.speech_sucess = True
        self.speech_message = ""
        self.neck_sucess = True
        self.neck_message = ""
        self.rgb_sucess = True
        self.rgb_message = ""
        self.face_sucess = True
        self.face_message = ""

        self.get_neck_position = [1.0, 1.0]
        

    #### SPEECH SERVER FUCNTIONS #####
    def call_speech_command_server(self, filename="", command="", quick_voice=False, wait_for_end_of=True):
        request = SpeechCommand.Request()
        request.filename = filename
        request.command = command
        request.quick_voice = quick_voice
    
        future = self.speech_command_client.call_async(request)
        # print("Sent Command")

        if wait_for_end_of:
            # future.add_done_callback(partial(self.callback_call_speech_command, a=filename, b=command))
            future.add_done_callback(self.callback_call_speech_command)
        else:
            self.speech_sucess = True
            self.speech_message = "Wait for answer not needed"

    def callback_call_speech_command(self, future): #, a, b):

        try:
            # in this function the order of the line of codes matter
            # it seems that when using future variables, it creates some type of threading system
            # if the falg raised is here is before the prints, it gets mixed with the main thread code prints
            response = future.result()
            self.get_logger().info(str(response.success) + " - " + str(response.message))
            self.speech_sucess = response.success
            self.speech_message = response.message
            # time.sleep(3)
            self.waited_for_end_of_speaking = True
        except Exception as e:
            self.get_logger().error("Service call failed %r" % (e,))   


    #### SET NECK POSITION SERVER FUCNTIONS #####
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
            self.speech_sucess = True
            self.speech_message = "Wait for answer not needed"
    
    def callback_call_set_neck_command(self, future): #, a, b):

        try:
            # in this function the order of the line of codes matter
            # it seems that when using future variables, it creates some type of threading system
            # if the falg raised is here is before the prints, it gets mixed with the main thread code prints
            response = future.result()
            self.get_logger().info(str(response.success) + " - " + str(response.message))
            self.speech_sucess = response.success
            self.speech_message = response.message
            # time.sleep(3)
            self.waited_for_end_of_neck = True
        except Exception as e:
            self.get_logger().error("Service call failed %r" % (e,))   


    #### GET NECK POSITION SERVER FUCNTIONS #####
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

def main(args=None):
    rclpy.init(args=args)
    node = ServeBreakfastNode()
    th_main = threading.Thread(target=thread_main_serve_breakfast, args=(node,), daemon=True)
    th_main.start()
    rclpy.spin(node)
    rclpy.shutdown()

def thread_main_serve_breakfast(node: ServeBreakfastNode):
    main = ServeBreakfastMain(node)
    main.main()

class ServeBreakfastMain():

    def __init__(self, node: ServeBreakfastNode):
        self.node = node
        
        # Task Related Variables
        self.Waiting_for_task_start = 0
        self.Approach_kitchen_counter = 1
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

        # to debug just a part of the task you can just change the initial state, example:
        # self.state = self.Approach_kitchen_table
        self.state = self.Waiting_for_task_start

    ##### SETS #####

    def set_speech(self, filename="", command="", quick_voice=False, wait_for_end_of=True):

        self.node.call_speech_command_server(filename=filename, command=command, wait_for_end_of=wait_for_end_of, quick_voice=quick_voice)
        
        if wait_for_end_of:
          while not self.node.waited_for_end_of_speaking:
            pass
        self.node.waited_for_end_of_speaking = False

        return self.node.speech_sucess, self.node.speech_message

    def set_neck(self, position=[0, 0], wait_for_end_of=True):

        self.node.call_neck_position_server(position=position, wait_for_end_of=wait_for_end_of)
        
        if wait_for_end_of:
          while not self.node.waited_for_end_of_neck:
            pass
        self.node.waited_for_end_of_neck = False

        return self.node.neck_sucess, self.node.neck_message
    
    def set_rgb(self, command="", wait_for_end_of=True):
        
        temp = Int16()
        temp.data = command
        self.node.rgb_mode_publisher.publish(temp)

        self.node.rgb_sucess = True
        self.node.rgb_message = "Value Sucessfully Sent"

        return self.node.rgb_sucess, self.node.rgb_message
    
    def set_face(self, command="", custom="", wait_for_end_of=True):
        
        if custom == "":
            temp = String()
            temp.data = command
            self.node.image_to_face_publisher.publish(temp)
        else:
            temp = String()
            temp.data = custom
            self.node.custom_image_to_face_publisher.publish(temp)

        self.node.face_sucess = True
        self.node.face_message = "Value Sucessfully Sent"

        return self.node.face_sucess, self.node.face_message


    ##### GETS #####
    def get_neck(self, wait_for_end_of=True):
    
        self.node.call_get_neck_position_server()
        
        if wait_for_end_of:
          while not self.node.waited_for_end_of_get_neck:
            pass
        self.node.waited_for_end_of_get_neck = False


        return self.node.get_neck_position[0], self.node.get_neck_position[1] 



    def main(self):

        self.node.get_logger().info("IN SERVE THE BREAKFAST MAIN")

        while True:

            ##### ADJUST WAIT_FOR_END_OF_SPEAKING
            if self.state == self.Waiting_for_task_start:

                p, t = self.get_neck()
                # self.node.get_logger().info("p, t = %s" %(str(p)+", "+str(t)))

                self.set_face("demo5")

                self.set_neck(position=[30, 30], wait_for_end_of=True)

                self.set_speech(filename="sb_ready_start", wait_for_end_of=True)
                
                # self.node.get_logger().info("p, t = %s" %(str(self.node.get_neck_position[0])+", "+str(self.node.get_neck_position[1])))


                # self.set_speech(filename="waiting_door_open", wait_for_end_of=False)
                
                # self.set_rgb(RED+ALTERNATE_QUARTERS)
                # self.set_face("help_pick_milk")

                ###### WAITS FOR START BUTTON / DOOR OPEN

                time.sleep(2)
                
                self.set_neck(position=[-180, 20], wait_for_end_of=True)
                
                # print(s,m)
                
                self.set_speech(filename="waiting_start_button", wait_for_end_of=True) # must change to door open

                # p, t = self.get_neck(wait_for_end_of=True)
                # self.node.get_logger().info("p, t = %s" %(str(p)+", "+str(t)))

                # while True:
                #     pass
                
                self.state = self.Approach_kitchen_counter

            elif self.state == self.Approach_kitchen_counter:

                ##### NECK LOOKS TO NAVIGATION

                self.set_speech(filename="sb_moving_kitchen_counter", wait_for_end_of=True)

                ###### MOVEMENT TO THE KITCHEN COUNTER

                self.set_speech(filename="sb_arrived_kitchen_counter", wait_for_end_of=True)
                
                self.state = self.Picking_up_spoon

            elif self.state == self.Picking_up_spoon:
                
                ##### NECK LOOKS AT TABLE

                ##### MOVES ARM TO TOP OF TABLE POSITION

                self.set_speech(filename="search_objects", wait_for_end_of=True)

                ##### YOLO OBJECTS SEARCH FOR SPOON, FOR BOTH CAMERAS

                self.set_speech(filename="sb_found_spoon", wait_for_end_of=True)

                self.set_speech(filename="check_face_object_detected", wait_for_end_of=True)

                ##### SHOW FACE DETECTED OBJECT

                ##### MOVE ARM TO PICK UP OBJECT 

                ##### IF AN ERROR IS DETECTED:
                
                self.set_speech(filename="problem_pick_object", wait_for_end_of=True) # False
                   
                    ##### MOVE ARM TO ERROR POSITION 
                
                    ##### NECK LOOK JUDGE
                
                self.set_speech(filename="check_face_put_object_hand", wait_for_end_of=True)
                    
                    ##### SHOW FACE GRIPPER SPOON 
                
                    ##### WHILE OBJECT IS NOT IN GRIPPER:
                
                self.set_speech(filename="arm_close_gripper", wait_for_end_of=True)

                        ##### ARM CLOSE GRIPPER

                        ##### IF OBJECT NOT GRABBED:
                
                self.set_speech(filename="arm_error_receive_object", wait_for_end_of=True)
                        
                            ##### ARM OPEN GRIPPER
                        
                ##### NECK LOOK TRAY
                
                ##### ARM PLACE OBJECT IN TRAY

                self.state = self.Picking_up_milk

            elif self.state == self.Picking_up_milk:

                ##### NECK LOOKS AT TABLE

                ##### MOVES ARM TO TOP OF TABLE POSITION

                self.set_speech(filename="search_objects", wait_for_end_of=True)

                ##### YOLO OBJECTS SEARCH FOR MILK, FOR BOTH CAMERAS

                self.set_speech(filename="sb_found_milk", wait_for_end_of=True)

                self.set_speech(filename="check_face_object_detected", wait_for_end_of=True)

                ##### SHOW FACE DETECTED OBJECT

                ##### MOVE ARM TO PICK UP OBJECT 

                ##### IF AN ERROR IS DETECTED:
                
                self.set_speech(filename="problem_pick_object", wait_for_end_of=True) # False
                   
                    ##### MOVE ARM TO ERROR POSITION 
                
                    ##### NECK LOOK JUDGE
                
                self.set_speech(filename="check_face_put_object_hand", wait_for_end_of=True)
                    
                    ##### SHOW FACE GRIPPER MILK 
                
                    ##### WHILE OBJECT IS NOT IN GRIPPER:
                
                self.set_speech(filename="arm_close_gripper", wait_for_end_of=True)

                        ##### ARM CLOSE GRIPPER

                        ##### IF OBJECT NOT GRABBED:
                
                self.set_speech(filename="arm_error_receive_object", wait_for_end_of=True)
                        
                            ##### ARM OPEN GRIPPER
                        
                ##### NECK LOOK TRAY
                        
                ##### ARM PLACE OBJECT IN TRAY

                self.state = self.Picking_up_cereal
           
            elif self.state == self.Picking_up_cereal:

                ##### NECK LOOKS AT TABLE

                ##### MOVES ARM TO TOP OF TABLE POSITION

                self.set_speech(filename="search_objects", wait_for_end_of=True)

                ##### YOLO OBJECTS SEARCH FOR CEREAL, FOR BOTH CAMERAS

                self.set_speech(filename="sb_found_cereal", wait_for_end_of=True)

                self.set_speech(filename="check_face_object_detected", wait_for_end_of=True)

                ##### SHOW FACE DETECTED OBJECT

                ##### MOVE ARM TO PICK UP OBJECT 

                ##### IF AN ERROR IS DETECTED:
                
                self.set_speech(filename="problem_pick_object", wait_for_end_of=True) # False
                   
                    ##### MOVE ARM TO ERROR POSITION 
                
                    ##### NECK LOOK JUDGE
                
                self.set_speech(filename="check_face_put_object_hand", wait_for_end_of=True)
                    
                    ##### SHOW FACE GRIPPER SPOON 
                
                    ##### WHILE OBJECT IS NOT IN GRIPPER:
                
                self.set_speech(filename="arm_close_gripper", wait_for_end_of=True)

                        ##### ARM CLOSE GRIPPER

                        ##### IF OBJECT NOT GRABBED:
                
                self.set_speech(filename="arm_error_receive_object", wait_for_end_of=True)
                        
                            ##### ARM OPEN GRIPPER
                        
                ##### NECK LOOK TRAY
                        
                ##### ARM PLACE OBJECT IN TRAY

                self.state = self.Picking_up_bowl

            elif self.state == self.Picking_up_bowl:

                ##### NECK LOOKS AT TABLE

                ##### MOVES ARM TO TOP OF TABLE POSITION

                self.set_speech(filename="search_objects", wait_for_end_of=True)

                ##### YOLO OBJECTS SEARCH FOR BOWL, FOR BOTH CAMERAS

                self.set_speech(filename="sb_found_bowl", wait_for_end_of=True)

                self.set_speech(filename="check_face_object_detected", wait_for_end_of=True)

                ##### SHOW FACE DETECTED OBJECT

                ##### MOVE ARM TO PICK UP OBJECT 

                ##### IF AN ERROR IS DETECTED:
                
                self.set_speech(filename="problem_pick_object", wait_for_end_of=True) # False
                   
                    ##### MOVE ARM TO ERROR POSITION 
                
                    ##### NECK LOOK JUDGE

                self.set_speech(filename="check_face_put_object_hand", wait_for_end_of=True)
                    
                    ##### SHOW FACE GRIPPER BOWL 
                
                    ##### WHILE OBJECT IS NOT IN GRIPPER:
                
                self.set_speech(filename="arm_close_gripper", wait_for_end_of=True)

                        ##### ARM CLOSE GRIPPER

                        ##### IF OBJECT NOT GRABBED:
                
                self.set_speech(filename="arm_error_receive_object", wait_for_end_of=True)
                        
                            ##### ARM OPEN GRIPPER
                        
                ##### NECK LOOK TRAY
                        
                ##### ARM PLACE OBJECT IN TRAY

                self.state = self.Approach_kitchen_table

            elif self.state == self.Approach_kitchen_table:

                self.set_speech(filename="objects_all_collected", wait_for_end_of=True)

                ##### NECK LOOKS TO NAVIGATION

                self.set_speech(filename="sb_moving_kitchen_table", wait_for_end_of=True)

                ###### MOVEMENT TO THE KITCHEN TABLE

                self.set_speech(filename="sb_arrived_kitchen_table", wait_for_end_of=True)

                self.set_speech(filename="place_object_table", wait_for_end_of=True)

                self.set_speech(filename="place_stay_clear", wait_for_end_of=True)

                self.state = self.Placing_bowl

            elif self.state == self.Placing_bowl:

                ##### NECK TRAY

                ##### NECK TABLE

                ##### ARM MOVE TO TABLE

                ##### ARM PLACE OBJECT

                self.set_speech(filename="place_object_placed", wait_for_end_of=True)

                self.state = self.Placing_cereal 

            elif self.state == self.Placing_cereal:

                ##### NECK TRAY

                ##### ARM MOVE TRAY

                ##### ARM PICK OBJECT 

                ##### NECK TABLE

                ##### ARM MOVE TO TABLE

                ##### ARM POUR IN BOWL

                ##### ARM PLACE OBJECT

                self.set_speech(filename="place_object_placed", wait_for_end_of=True)

                self.state = self.Placing_milk
           
            elif self.state == self.Placing_milk:

                ##### NECK TRAY

                ##### ARM MOVE TRAY

                ##### ARM PICK OBJECT 

                ##### NECK TABLE

                ##### ARM MOVE TO TABLE

                ##### ARM POUR IN BOWL

                ##### ARM PLACE OBJECT

                self.set_speech(filename="place_object_placed", wait_for_end_of=True)

                self.state = self.Placing_spoon

            elif self.state == self.Placing_spoon:

                ##### NECK TRAY

                ##### ARM MOVE TRAY

                ##### ARM PICK OBJECT 

                ##### NECK TABLE

                ##### ARM MOVE TO TABLE

                ##### ARM PLACE OBJECT

                self.set_speech(filename="place_object_placed", wait_for_end_of=True)

                self.state = self.Final_State 
                
            elif self.state == self.Final_State:

                self.set_speech(filename="sb_finished", wait_for_end_of=True)

                while True:
                    pass

            else:
                pass
