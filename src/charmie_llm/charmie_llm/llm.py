#!/usr/bin/env python3

# initial instructions:
# this is an example of the layout code for a task in our workspace
# It is used a threading system so the ROS2 functionalities are not blocked when executing the state machine
# So we create a thread for the main state machine of the task and another for the ROS2 funcitonalities
# It is being used Serve the Breakfast as an example, so when changing the code for a specific task:
# Ctrl+F "ServeBreakfast" and replace everything for the name of your task 

# THE MAIN GOAL IS FOR YOU TO ONLY CHANGE BELOW THE LINE THAT STATES: "def main(self):"

# The following code already has implemnted with examples the following modes:
# Speakers
# RGB
# Start Button
# Audio
# Face
# Neck
# Yolos
# Arm
# Door Start
# Navigation
# Initial Localisation Position

# The following modules are still missing:
# None


"""
NEXT I PROVIDE AN EXAMPLE ON HOW THE CODE OF A TASK SHOULD BE MADE:

->  ->  ->  ->  ->  HOW TO CREATE A TASK?

1) IMPORT ALL ROS2 TOPICS/SERVICES NECESSARY AND WAIT_FOR_SERVICE (THIS IS TIAGO JOB, ASK HIM TO HELP OR EXPLAIN)
2) PLAN THE STATES AND SET THE STATES FOR YOUR TASK:

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

# 3) CREATE THE STATE STRUCTURE:
        
        if self.state == self.Waiting_for_task_start:
                # your code here ...
                                
                # next state
                self.state = self.Approach_kitchen_counter

            elif self.state == self.Approach_kitchen_counter:
                # your code here ...
                                
                # next state
                self.state = self.Picking_up_spoon

            elif self.state == self.Picking_up_spoon:
                # your code here ...
                                
                # next state
                self.state = self.Picking_up_milk

            (...)

# 4) CREATE THE PSEUDOCODE OF EACH STATE:
            
            elif self.state == self.Picking_up_spoon:
                
                ##### NECK LOOKS AT TABLE

                ##### MOVES ARM TO TOP OF TABLE POSITION

                ##### SPEAK: Searching for objects

                ##### YOLO OBJECTS SEARCH FOR SPOON, FOR BOTH CAMERAS
                
                ##### SPEAK: Found spoon
                
                ##### SPEAK: Check face to see object detected

                ##### SHOW FACE DETECTED OBJECT

                ##### MOVE ARM TO PICK UP OBJECT 

                ##### IF AN ERROR IS DETECTED:

                    ##### SPEAK: There is a problem picking up the object

                    ##### MOVE ARM TO ERROR POSITION 
                
                    ##### NECK LOOK JUDGE

                    ##### SPEAK: Need help, put object on my hand as it is on my face

                    ##### SHOW FACE GRIPPER SPOON 

                    ##### WHILE OBJECT IS NOT IN GRIPPER:

                        ##### SPEAK: Close gripper in 3 2 1 

                        ##### ARM: CLOSE GRIPPER

                        ##### IF OBJECT NOT GRABBED: 

                            ##### SPEAK: There seems to be a problem, please retry.

                            ##### ARM OPEN GRIPPER
                        
                ##### NECK LOOK TRAY
                        
                ##### ARM PLACE OBJECT IN TRAY

                self.state = self.Picking_up_milk

# 5) REPLACE ALL THE SPEAKS IN PSEUDOCODE WITH self.set_speech(...), CREATE FILES IN ros2 run charmie_speakers save_audio

# 6) TEST ALL SENTENCES ALONE TO SEE IF EVERYTHING IS OK

# 5) REPLACE ALL THE FACE IN PSEUDOCODE WITH self.set_face(...)

# 6) TEST ALL FACES WITH THE PREVIOUS SETs ALREADY IMPLEMENTED TO SEE IF EVERYTHING IS OK

# 7) REPLACE ALL THE START_BUTTON AND RGB IN PSEUDOCODE WITH self.set_rgb(...) and self.wait_for_start_button()

# 8) TEST ALL START_BUTTON AND RGB WITH THE PREVIOUS SETs ALREADY IMPLEMENTED TO SEE IF EVERYTHING IS OK

# 9) REPLACE ALL THE AUDIO IN PSEUDOCODE WITH self.get_audio(...)

# 10) TEST ALL AUDIO WITH THE PREVIOUS GETs ALREADY IMPLEMENTED TO SEE IF EVERYTHING IS OK

# 11) REPLACE ALL THE NECK IN PSEUDOCODE WITH self.set_neck(...) OR ANY OF ALL THE OTHER FORMS TO SET THE NECK

# 12) TEST ALL NECK WITH THE PREVIOUS SETs ALREADY IMPLEMENTED TO SEE IF EVERYTHING IS OK

# 13) REPLACE ALL THE YOLO DETECTIONS IN PSEUDOCODE WITH self.activate_yolo_pose(...) and self.activate_yolo_objects

# 14) TEST ALL YOLOS WITH THE PREVIOUS ACTIVATES ALREADY IMPLEMENTED TO SEE IF EVERYTHING IS OK

# 15) REPLACE ALL THE ARM MOVE WITH self.set_arm(...)

# 16) TEST ALL ARM MOVE WITH THE PREVIOUS SETs ALREADY IMPLEMENTED TO SEE IF EVERYTHING IS OK

# 17) REPLACE THE SET INITIAL POSITION MOVE WITH self.set_initial_position(...)

# 18) TEST ALL SET INITIAL POSITION WITH THE PREVIOUS SETs ALREADY IMPLEMENTED TO SEE IF EVERYTHING IS OK

# 19) REPLACE THE NAVIGATION MOVE, ROTATE AND ORIENTATE WITH self.set_navigation(...)

# 20) TEST ALL SET NAVIGATION WITH THE PREVIOUS SETs ALREADY IMPLEMENTED TO SEE IF EVERYTHING IS OK

"""

import rclpy
from rclpy.node import Node

# import variables from standard libraries and both messages and services from custom charmie_interfaces
from example_interfaces.msg import Bool, String, Int16
from charmie_interfaces.msg import Yolov8Pose, DetectedPerson, Yolov8Objects, DetectedObject, TarNavSDNL
from charmie_interfaces.srv import SpeechCommand, SaveSpeechCommand, GetAudio, CalibrateAudio, SetNeckPosition, GetNeckPosition, SetNeckCoordinates, TrackObject, TrackPerson, ActivateYoloPose, ActivateYoloObjects, ArmTrigger, NavTrigger, SetFace

import threading
import time

# Constant Variables to ease RGB_MODE coding
RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, WHITE, ORANGE, PINK, BROWN  = 0, 10, 20, 30, 40, 50, 60, 70, 80, 90
SET_COLOUR, BLINK_LONG, BLINK_QUICK, ROTATE, BREATH, ALTERNATE_QUARTERS, HALF_ROTATE, MOON, BACK_AND_FORTH_4, BACK_AND_FORTH_8  = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9
CLEAR, RAINBOW_ROT, RAINBOW_ALL, POLICE, MOON_2_COLOUR, PORTUGAL_FLAG, FRANCE_FLAG, NETHERLANDS_FLAG = 255, 100, 101, 102, 103, 104, 105, 106


class LLMNode(Node):

    def __init__(self):
        super().__init__("LLM")
        self.get_logger().info("Initialised CHARMIE LLM Node")

        ### Topics (Publisher and Subscribers) ###   
        # Low Level 
        self.rgb_mode_publisher = self.create_publisher(Int16, "rgb_mode", 10)   
        
        ### Services (Clients) ###
        # Speakers
        self.speech_command_client = self.create_client(SpeechCommand, "speech_command")
        self.save_speech_command_client = self.create_client(SaveSpeechCommand, "save_speech_command")
        # Audio
        self.get_audio_client = self.create_client(GetAudio, "audio_command")
        self.calibrate_audio_client = self.create_client(CalibrateAudio, "calibrate_audio")
        # Face
        self.face_command_client = self.create_client(SetFace, "face_command")
        
        # if is necessary to wait for a specific service to be ON, uncomment the two following lines
        # Speakers
        while not self.speech_command_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Speech Command...")
        while not self.save_speech_command_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Save Speech Command...")
        # Audio
        while not self.get_audio_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Audio Server...")
        while not self.calibrate_audio_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Calibrate Audio Server...")
        # Face
        while not self.face_command_client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Server Face Command...")
        
        # Variables 
        self.waited_for_end_of_audio = False
        self.waited_for_end_of_calibrate_audio = False
        self.waited_for_end_of_speaking = False
        self.waited_for_end_of_save_speaking = False
        self.waited_for_end_of_face = False

        # Success and Message confirmations for all set_(something) CHARMIE functions
        self.speech_success = True
        self.speech_message = ""
        self.save_speech_success = True
        self.save_speech_message = ""
        self.rgb_success = True
        self.rgb_message = ""
        self.calibrate_audio_success = True
        self.calibrate_audio_message = ""
        self.audio_command = ""
        self.face_success = True
        self.face_message = ""
        

    #### FACE SERVER FUNCTIONS #####
    def call_face_command_server(self, command="", custom="", wait_for_end_of=True):
        request = SetFace.Request()
        request.command = command
        request.custom = custom
        
        future = self.face_command_client.call_async(request)
        
        if wait_for_end_of:
            future.add_done_callback(self.callback_call_face_command)
        else:
            self.face_success = True
            self.face_message = "Wait for answer not needed"
    
    def callback_call_face_command(self, future): #, a, b):

        try:
            # in this function the order of the line of codes matter
            # it seems that when using future variables, it creates some type of threading system
            # if the falg raised is here is before the prints, it gets mixed with the main thread code prints
            response = future.result()
            self.get_logger().info(str(response.success) + " - " + str(response.message))
            self.face_success = response.success
            self.face_message = response.message
            # time.sleep(3)
            self.waited_for_end_of_face = True
        except Exception as e:
            self.get_logger().error("Service call failed %r" % (e,))


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


    #### SAVE SPEECH SERVER FUNCTIONS #####
    def call_save_speech_command_server(self, filename="", command="", wait_for_end_of=True):
        request = SaveSpeechCommand.Request()
        request.filename = filename
        request.command = command
    
        future = self.save_speech_command_client.call_async(request)
        # print("Sent Command")

        if wait_for_end_of:
            # future.add_done_callback(partial(self.callback_call_speech_command, a=filename, b=command))
            future.add_done_callback(self.callback_call_save_speech_command)
        else:
            self.speech_success = True
            self.speech_message = "Wait for answer not needed"
    
    def callback_call_save_speech_command(self, future): #, a, b):

        try:
            # in this function the order of the line of codes matter
            # it seems that when using future variables, it creates some type of threading system
            # if the falg raised is here is before the prints, it gets mixed with the main thread code prints
            response = future.result()
            self.get_logger().info(str(response.success) + " - " + str(response.message))
            self.save_speech_success = response.success
            self.save_speech_message = response.message
            # time.sleep(3)
            self.waited_for_end_of_save_speaking = True
        except Exception as e:
            self.get_logger().error("Service call failed %r" % (e,))


    #### AUDIO SERVER FUNCTIONS #####
    def call_audio_server(self, yes_or_no=False, receptionist=False, gpsr=False, restaurant=False, wait_for_end_of=True):
        request = GetAudio.Request()
        request.yes_or_no = yes_or_no
        request.receptionist = receptionist
        request.gpsr = gpsr
        request.restaurant = restaurant

        future = self.get_audio_client.call_async(request)
        # print("Sent Command")

        if wait_for_end_of:
            future.add_done_callback(self.callback_call_audio)
        else:
            self.track_person_success = True
            self.track_person_message = "Wait for answer not needed"
    
    def callback_call_audio(self, future):

        try:
            # in this function the order of the line of codes matter
            # it seems that when using future variables, it creates some type of threading system
            # if the flag raised is here is before the prints, it gets mixed with the main thread code prints
            response = future.result()
            self.get_logger().info(str(response.command))
            self.audio_command = response.command
            # self.track_object_success = response.success
            # self.track_object_message = response.message
            # time.sleep(3)
            self.waited_for_end_of_audio = True
        except Exception as e:
            self.get_logger().error("Service call failed %r" % (e,))


    def call_calibrate_audio_server(self, wait_for_end_of=True):
        request = CalibrateAudio.Request()

        future = self.calibrate_audio_client.call_async(request)
        # print("Sent Command")

        if wait_for_end_of:
            future.add_done_callback(self.callback_call_calibrate_audio)
        else:
            self.track_person_success = True
            self.track_person_message = "Wait for answer not needed"
    
    def callback_call_calibrate_audio(self, future):

        try:
            # in this function the order of the line of codes matter
            # it seems that when using future variables, it creates some type of threading system
            # if the flag raised is here is before the prints, it gets mixed with the main thread code prints
            response = future.result()
            self.get_logger().info(str(response.success) + " - " + str(response.message))
            self.track_person_success = response.success
            self.track_person_message = response.message
            # self.track_object_success = response.success
            # self.track_object_message = response.message
            # time.sleep(3)
            self.waited_for_end_of_calibrate_audio = True
        except Exception as e:
            self.get_logger().error("Service call failed %r" % (e,))


# main function that already creates the thread for the task state machine
def main(args=None):
    rclpy.init(args=args)
    node = LLMNode()
    th_main = threading.Thread(target=ThreadMainLLM, args=(node,), daemon=True)
    th_main.start()
    rclpy.spin(node)
    rclpy.shutdown()

def ThreadMainLLM(node: LLMNode):
    main = LLMMain(node)
    main.main()

class LLMMain():

    def __init__(self, node: LLMNode):
        # create a node instance so all variables ros related can be acessed
        self.node = node

    def set_speech(self, filename="", command="", quick_voice=False, show_in_face=False, wait_for_end_of=True):

        self.node.call_speech_command_server(filename=filename, command=command, wait_for_end_of=wait_for_end_of, quick_voice=quick_voice, show_in_face=show_in_face)
        
        if wait_for_end_of:
          while not self.node.waited_for_end_of_speaking:
            pass
        self.node.waited_for_end_of_speaking = False

        return self.node.speech_success, self.node.speech_message
    
    def save_speech(self, filename="", command="", wait_for_end_of=True):

        # the commands should be lists, because you can send a list of commands and a list of filenames,
        # making it possible to create multiple temp commands with one instruction
        # But if by mistake someone sends them as a string (beause set_speech is done that way) I correct it  
        file = []
        comm = [] 
        if isinstance(filename, str) and isinstance(command, str):
            file.append(filename)
            comm.append(command)
        elif isinstance(filename, list) and isinstance(command, list):
            file = filename
            comm = command
        
        if len(file) > 0 and len(comm) > 0:

            self.node.call_save_speech_command_server(filename=file, command=comm, wait_for_end_of=wait_for_end_of)
            
            if wait_for_end_of:
                while not self.node.waited_for_end_of_save_speaking:
                    pass
            self.node.waited_for_end_of_save_speaking = False

            return self.node.save_speech_success, self.node.save_speech_message

        else:

            self.node.get_logger().error("Could not generate save speech as as filename and command types are incompatible.")
            return False, "Could not generate save speech as as filename and command types are incompatible."

    def set_rgb(self, command="", wait_for_end_of=True):
        
        temp = Int16()
        temp.data = command
        self.node.rgb_mode_publisher.publish(temp)

        self.node.rgb_success = True
        self.node.rgb_message = "Value Sucessfully Sent"

        return self.node.rgb_success, self.node.rgb_message
 
    def get_audio(self, yes_or_no=False, receptionist=False, gpsr=False, restaurant=False, question="", face_hearing="charmie_face_green", wait_for_end_of=True):

        if yes_or_no or receptionist or gpsr or restaurant:

            # this code continuously asks for new audio info eveytime it gets an error for mishearing
            audio_error_counter = 0
            keywords = "ERROR"
            while keywords=="ERROR":
                
                self.set_speech(filename=question, wait_for_end_of=True)
                self.set_face(face_hearing)
                self.node.call_audio_server(yes_or_no=yes_or_no, receptionist=receptionist, gpsr=gpsr, restaurant=restaurant, wait_for_end_of=wait_for_end_of)
                
                if wait_for_end_of:
                    while not self.node.waited_for_end_of_audio:
                        pass
                self.node.waited_for_end_of_audio = False
                self.set_face("charmie_face")

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
    
    def set_face(self, command="", custom="", wait_for_end_of=True):
        
        self.node.call_face_command_server(command=command, custom=custom, wait_for_end_of=wait_for_end_of)
        
        if wait_for_end_of:
            while not self.node.waited_for_end_of_face:
                pass
        self.node.waited_for_end_of_face = False

        return self.node.face_success, self.node.face_message
    
    # main state-machine function
    def main(self):
        
        # States in LLM Task
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
        
        # State the robot starts at, when testing it may help to change to the state it is intended to be tested
        self.state = self.Waiting_for_task_start

        # debug print to know we are on the main start of the task
        self.node.get_logger().info("In LLM Main...")

        while True:

            if self.state == self.Waiting_for_task_start:
                print("State:", self.state, "- Waiting_for_task_start")

                # your code here ...
                
                self.set_rgb(command=MAGENTA+ALTERNATE_QUARTERS)

                self.set_speech(filename="generic/waiting_door_open", wait_for_end_of=True)
                
                self.calibrate_audio(wait_for_end_of=True)
                        
                ### RECEPTIONIST AUDIO EXAMPLE
                command = self.get_audio(receptionist=True, question="receptionist/receptionist_question", wait_for_end_of=True)
                print("Finished:", command)
                keyword_list= command.split(" ")
                print(keyword_list[0], keyword_list[1])
                self.set_speech(filename="receptionist/recep_first_guest_"+keyword_list[0].lower(), wait_for_end_of=True)
                self.set_speech(filename="receptionist/recep_drink_"+keyword_list[1].lower(), wait_for_end_of=True)  

                # change face, to standard face
                self.set_face("charmie_face")

                time.sleep(1)

                # next state
                self.state = self.Approach_kitchen_counter

            elif self.state == self.Approach_kitchen_counter:
                print("State:", self.state, "- Approach_kitchen_counter")
                # your code here ...
                                
                # next state
                self.state = self.Picking_up_spoon

            elif self.state == self.Picking_up_spoon:
                print("State:", self.state, "- Picking_up_spoon")

                ##### NECK LOOKS AT TABLE
                # self.set_neck(position=self.look_table_objects, wait_for_end_of=True)

                ##### MOVES ARM TO TOP OF TABLE POSITION

                ##### SPEAK: Searching for objects
                # self.set_speech(filename="generic/search_objects", wait_for_end_of=True)

                ##### YOLO OBJECTS SEARCH FOR SPOON, FOR BOTH CAMERAS
                # self.set_neck(position=self.look_judge, wait_for_end_of=True)
                
                ##### SPEAK: Found spoon
                # self.set_speech(filename="serve_breakfast/sb_found_spoon", show_in_face=True, wait_for_end_of=True)
                
                ##### SPEAK: Check face to see object detected
                # self.set_speech(filename="generic/check_face_object_detected", wait_for_end_of=True)

                ##### SHOW FACE DETECTED OBJECT (CUSTOM)

                ##### MOVE ARM TO PICK UP OBJECT 

                ##### IF AN ERROR IS DETECTED:

                    ##### SPEAK: There is a problem picking up the object
                    # self.set_speech(filename="generic/problem_pick_object", wait_for_end_of=True) # False

                    ##### MOVE ARM TO ERROR POSITION 
                
                    ##### NECK LOOK JUDGE
                    # self.set_neck(position=self.look_judge, wait_for_end_of=True)

                    ##### SPEAK: Need help, put object on my hand as it is on my face
                    # self.set_speech(filename="generic/check_face_put_object_hand", wait_for_end_of=True)

                    ##### SHOW FACE GRIPPER SPOON 
                    # self.set_face("help_pick_spoon") 

                    ##### WHILE OBJECT IS NOT IN GRIPPER:

                        ##### SPEAK: Close gripper in 3 2 1 
                        # self.set_speech(filename="arm/arm_close_gripper", wait_for_end_of=True)

                        ##### ARM: CLOSE GRIPPER

                        ##### IF OBJECT NOT GRABBED: 

                            ##### SPEAK: There seems to be a problem, please retry.
                            # self.set_speech(filename="arm/arm_error_receive_object", wait_for_end_of=True)

                            ##### ARM OPEN GRIPPER
                
                ##### SET FACE TO STANDARD FACE
                # self.set_face("charmie_face")
                        
                ##### NECK LOOK TRAY
                # self.set_neck(position=self.look_tray, wait_for_end_of=True)
                        
                ##### ARM PLACE OBJECT IN TRAY

                self.state = self.Picking_up_milk

            elif self.state == self.Picking_up_milk:
                print("State:", self.state, "- Picking_up_milk")
                # your code here ...
                                                
                # next state
                self.state = self.Picking_up_cereal
           
            elif self.state == self.Picking_up_cereal:
                print("State:", self.state, "- Picking_up_cereal")
                # your code here ...
                                
                # next state
                self.state = self.Picking_up_bowl

            elif self.state == self.Picking_up_bowl:
                print("State:", self.state, "- Picking_up_bowl")
                # your code here ...
                                
                # next state
                self.state = self.Approach_kitchen_table

            elif self.state == self.Approach_kitchen_table:
                print("State:", self.state, "- Approach_kitchen_table")
                # your code here ...
                                
                # next state
                self.state = self.Placing_bowl

            elif self.state == self.Placing_bowl:
                print("State:", self.state, "- Placing_bowl")
                # your code here ...
                                
                # next state
                self.state = self.Placing_cereal 

            elif self.state == self.Placing_cereal:
                print("State:", self.state, "- Placing_cereal")
                # your code here ...
                                
                # next state
                self.state = self.Placing_milk
           
            elif self.state == self.Placing_milk:
                print("State:", self.state, "- Placing_milk")
                # your code here ...
                                
                # next state
                self.state = self.Placing_spoon

            elif self.state == self.Placing_spoon:
                print("State:", self.state, "- Placing_spoon")
                # your code here ...
                                
                # next state
                self.state = self.Final_State 
                
            elif self.state == self.Final_State:
                
                self.set_speech(filename="serve_breakfast/sb_finished", wait_for_end_of=True)

                # Lock after finishing task
                while True:
                    pass

            else:
                pass
