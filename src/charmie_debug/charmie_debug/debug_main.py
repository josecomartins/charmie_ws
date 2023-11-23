#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose2D, Vector3
from std_msgs.msg import Bool, Int16, String
from sensor_msgs.msg import LaserScan, Image
from charmie_interfaces.msg import Encoders, PS4Controller, RobotSpeech, SpeechType, TarNavSDNL, NeckPosition, TrackPerson, DetectedPerson, Yolov8Pose, RequestPointCloud


from cv_bridge import CvBridge
import cv2 
import time
import math

# import mediapipe as mp
import threading

class TRNode(Node):

    def __init__(self):
        super().__init__("Debug")
        self.get_logger().info("Initialised CHARMIE Debug Node")

        self.omni_move_publisher = self.create_publisher(Vector3, "omni_move", 10)
        self.controller_subscriber = self.create_subscription(PS4Controller, "controller_state", self.get_controller_callback, 10)
        
        ### help for navigation
        self.flag_pos_reached_publisher = self.create_publisher(Bool, "flag_pos_reached", 10)
        
        self.torso_test_publisher = self.create_publisher(Pose2D, "torso_test" , 10)

        self.create_timer(0.05, self.timer_callback)
        self.ps4_controller = PS4Controller()
        self.controller_updated = False




        """
        # Neck Topics
        self.neck_position_publisher = self.create_publisher(NeckPosition, "neck_to_pos", 10)
        self.neck_to_coords_publisher = self.create_publisher(Pose2D, "neck_to_coords", 10)
        self.neck_get_position_subscriber = self.create_subscription(NeckPosition, "get_neck_pos", self.get_neck_position_callback, 10)
        
        # Low Level Topics
        self.rgb_mode_publisher = self.create_publisher(Int16, "rgb_mode", 10)
        self.start_button_subscriber = self.create_subscription(Bool, "get_start_button", self.get_start_button_callback, 10)
        self.flag_start_button_publisher = self.create_publisher(Bool, "flag_start_button", 10)
        self.vccs_subscriber = self.create_subscription(Pose2D, "get_vccs", self.get_vccs_callback, 10)
        self.flag_vccs_publisher = self.create_publisher(Bool, "flag_vccs", 10)
        self.torso_pos_publisher = self.create_publisher(Pose2D, "torso_pos", 10)
        self.get_torso_pos_subscriber = self.create_subscription(Pose2D, "get_torso_pos", self.get_torso_pos_callback, 10)
        self.flag_torso_pos_publisher = self.create_publisher(Bool, "flag_torso_pos", 10)
        self.omni_move_publisher = self.create_publisher(Vector3, "omni_move", 10)
        self.get_encoders_subscriber = self.create_subscription(Encoders, "get_encoders", self.get_encoders_callback, 10)
        self.flag_encoders_publisher = self.create_publisher(Bool, "flag_encoders", 10)
        
        # PS4 Controller
        self.controller_subscriber = self.create_subscription(PS4Controller, "controller_state", self.get_controller_callback, 10)

        # LIDAR Hokuyo
        self.lidar_subscriber = self.create_subscription(LaserScan, "scan", self.get_lidar_callback, 10)

        # Speaker
        self.speaker_publisher = self.create_publisher(RobotSpeech, "speech_command", 10)
        self.flag_speaker_subscriber = self.create_subscription(Bool, "flag_speech_done", self.get_speech_done_callback, 10)

        # Intel Realsense
        self.color_image_subscriber = self.create_subscription(Image, "/color/image_raw", self.get_color_image_callback, 10)
        self.depth_image_subscriber = self.create_subscription(Image, "/depth/image_rect_raw", self.get_depth_image_callback, 10)

        # Face Shining RGB
        self.face_publisher = self.create_publisher(Int16, "face_command", 10)

        """
        # Audio
        # self.audio_command_publisher = self.create_publisher(SpeechType, "audio_command", 10)
        # self.get_speech_subscriber = self.create_subscription(String, "get_speech", self.get_speech_callback, 10)
        # self.flag_listening_subscriber = self.create_subscription(Bool, "flag_listening", self.flag_listening_callback, 10)
        """
        # Navigation 
        self.target_position_publisher = self.create_publisher(TarNavSDNL, "target_pos", 10)
        self.flag_pos_reached_subscriber = self.create_subscription(Bool, "flag_pos_reached", self.flag_pos_reached_callback, 10)

        # Door Start
        self.start_door_publisher = self.create_publisher(Bool, 'start_door', 10) 
        self.done_start_door_subscriber = self.create_subscription(Bool, 'done_start_door', self.done_start_door_callback, 10) 
        
        """
        # Neck Topics
        # self.neck_to_position_publisher = self.create_publisher(NeckPosition, "neck_to_pos", 10)
        # self.neck_to_coords_publisher = self.create_publisher(Pose2D, "neck_to_coords", 10)
        # self.neck_follow_person_publisher = self.create_publisher(TrackPerson, "neck_follow_person",10)
        # self.neck_get_position_subscriber = self.create_subscription(NeckPosition, "get_neck_pos", self.get_neck_position_callback, 10)
        
        
        # self.yolov8_pose_subscriber = self.create_subscription(Yolov8Pose, "person_pose", self.yolov8_pose_callback, 10)


        # self.yolo_poses = Yolov8Pose()


        """    
        time.sleep(1)
        a = NeckPosition()
        a.pan = 230.0
        a.tilt = 165.0
        self.neck_to_position_publisher.publish(a)
        time.sleep(2)

        # test track person
        self.neck_follow_person_publisher = self.create_publisher(TrackPerson, 'neck_follow_person', 10) 
        self.person_pose_filtered_subscriber = self.create_subscription(Yolov8Pose, 'person_pose_filtered', self.person_pose_filtered_callback, 10) 
        self.person_pose = Yolov8Pose()


        self.request_point_cloud_publisher = self.create_publisher(RequestPointCloud, 'ask_point_cloud', 10) 

        """
        # self.create_timer(0.1, self.request_point_cloud_person)
        # self.create_timer(10, self.request_audio)

        # self.request_audio()
        # self.help_neck_follow_person()


    def get_controller_callback(self, controller: PS4Controller):
        print("TRIANGLE = ", controller.triangle, "CIRCLE = ", controller.circle, "CROSS = ", controller.cross, "SQUARE = ", controller.square)
        print("UP = ", controller.arrow_up, "RIGHT = ", controller.arrow_right, "DOWN = ", controller.arrow_down, "LEFT = ", controller.arrow_left)
        print("L1 = ", controller.l1, "R1 = ", controller.r1, "L3 = ", controller.l3, "R3 = ", controller.r3)
        print("SHA = ", controller.share, "OPT = ", controller.options, "PS = ", controller.ps)
        print("L2 = ", controller.l2, "R2 = ", controller.r2)
        print("L3_ang = ", controller.l3_ang, "L3_dis = ", controller.l3_dist, "L3_xx = ", controller.l3_xx, "L3_yy = ", controller.l3_yy)
        print("R3_ang = ", controller.r3_ang, "R3_dis = ", controller.r3_dist, "R3_xx = ", controller.r3_xx, "R3_yy = ", controller.r3_yy)
        self.ps4_controller = controller
        self.controller_updated = True

    """
    def request_audio(self):
        
        sp = SpeechType()
        sp.yes_or_no = False
        sp.restaurant = True
        self.audio_command_publisher.publish(sp)
        print("Requested Audio")


    def get_speech_callback(self, speech: String):
        # speech_str = RobotSpeech()
        
        
        # self.start_audio()

        if speech.data == "ERROR":
            print("I could not understand what you said, can you repeat please?")
            # speech_str.command = "I could not understand what you said, can you repeat please?"
            # speech_str.language = 'en'
            # self.speaker_publisher.publish(speech_str)
        else:
            print(speech.data)
            # speech_str.command = "Hello my name is Tiago."
            # speech_str.language = 'en'
            # speech_str.command = "Bom dia, o meu nome é Tiago e gosto de Robôs. Já agora, qual é a comida na cantina hoje?"
            # speech_str.command = "Qual é a comida na cantina hoje?"
            # speech_str.command = speech.data
            # speech_str.language = 'en'
            # self.speaker_publisher.publish(speech_str)
        time.sleep(3)
        self.request_audio()
        

    def done_start_door_callback(self, flag: Bool):
        print("Recebi Fim do Start Door")


    def yolov8_pose_callback(self, yp: Yolov8Pose):
        self.yolo_poses = yp

    """


    def timer_callback(self):
        # neck = NeckPosition()
        # flag_start_button = Bool()
        # flag_vccs = Bool()
        # flag_torso = Bool()
        # rgb_mode = Int16()
        # torso_pos = Pose2D()
        omni_move = Vector3()
        # flag_encoders = Bool()

        if self.controller_updated:
            

            pos = Pose2D()
            if self.ps4_controller.arrow_up >= 2:
                pos.x = float(1)
                print("LEGS UP")
            elif self.ps4_controller.arrow_down >= 2:
                pos.x = float(-1)
                print("LEGS DOWN")
            else:
                pos.x = float(0)
                print("LEGS STOP")

            if self.ps4_controller.arrow_right >= 2:
                pos.y = float(1)
                print("TORSO UP")
            elif self.ps4_controller.arrow_left >= 2:
                pos.y = float(-1)
                print("TORSO DOWN")
            else:
                pos.y = float(0)
                print("TORSO STOP")

            self.torso_test_publisher.publish(pos)
            


            if self.ps4_controller.cross >= 2:
                pos = Bool()
                pos.data = True
                self.flag_pos_reached_publisher.publish(pos)
                print("NAVIGATION DONE")

            # if self.ps4_controller.cross == 2: # RISING
            #     rgb_mode.data = 4
                #self.rgb_mode_publisher.publish(rgb_mode)
            # elif self.ps4_controller.cross == 1: # FALLING:
            #     rgb_mode.data = 2
                #self.rgb_mode_publisher.publish(rgb_mode)

            if self.ps4_controller.l3_dist > 0.0:
                omni_move.x = self.ps4_controller.l3_ang
                omni_move.y = self.ps4_controller.l3_dist*100/5
            else:
                omni_move.x = 0.0
                omni_move.y = 0.0


            if self.ps4_controller.r3_dist > 0.0:
                omni_move.z = 100 + self.ps4_controller.r3_xx*10
            else:
                omni_move.z = 100.0
            
           
            self.omni_move_publisher.publish(omni_move)
            self.controller_updated = False



def main(args=None):
    rclpy.init(args=args)
    node = TRNode()
    rclpy.spin(node)
    rclpy.shutdown()


"""
def main(args=None):
    rclpy.init(args=args)
    node = TRNode()
    th_main = threading.Thread(target=thread_main_debug, args=(node,), daemon=True)
    th_main.start()
    rclpy.spin(node)
    rclpy.shutdown()

def thread_main_debug(node: TRNode):
    main = DebugMain(node)
    main.main()

class DebugMain():

    def __init__(self, node: TRNode):
        self.node = node
        
        self.state = 0

        self.image_height = 720
        self.image_width = 1280
        #self.state = 1
        

    def main(self):

        print("IN THREAD MAIN")

        ##### 1) olhar para umas coordenadas
        pose = Pose2D()
        pose.x = 2.0
        pose.y = 2.0
        pose.theta = 180.0
        self.node.neck_to_coords_publisher.publish(pose)

        neck_pos = NeckPosition()
        
        ##### 2) ler o yolo pose
        latest_yp = Yolov8Pose()
        dist = 10000 # supposedly should be +inf
        id_to_follow = 0
        while len(latest_yp) == 0:

            latest_yp = self.node.yolo_poses

            for p in latest_yp:
                print(p.kp_nose_x, p.kp_nose_y)

                ##### 3) ver qual a pessoa mais no centro
                dist_aux = math.dist([p.kp_nose_x, p.kp_nose_y], [self.image_width//2, self.image_height//2]) 
                if dist_aux < dist:
                    dist = dist_aux
                    ##### 4) decorar o ID
                    id_to_follow = p.index_person
                    print("TIME TO FOLLOW A PERSON... PLEASE WAIT")
            time.sleep(3)
        
        
        ##### 5) estar constantemente a mandar follow person com a detected person do ID escolhido
        while True:

            lp = self.node.yolo_poses
            correct_person = DetectedPerson()

            id_selected_still_correct = False
            for p in lp:
                if p.index_person == id_to_follow:
                    correct_person = p
                    id_selected_still_correct = True

            if id_selected_still_correct:
                # olhar para a pessoa
                self.node.neck_follow_person_publisher(correct_person)
            else:
                # olhar para cima 
                neck_pos.pan = 180
                neck_pos.tilt = 210
                self.node.neck_to_position_publisher.publish(neck_pos)

            time.sleep(0.5)

            print('.')
            pass






"""







"""
    def help_neck_follow_person(self):

        ### olhar para coords

        while True:
                
            n = Pose2D()
            n.x = 1.0
            n.y = 1.0
            n.theta = 180.0
            self.neck_to_coords_publisher.publish(n)
            time.sleep(0.5)
                
            n = Pose2D()
            n.x = 0.0
            n.y = 1.0
            n.theta = 180.0
            self.neck_to_coords_publisher.publish(n)
            time.sleep(0.5)
                
            n = Pose2D()
            n.x = -1.0
            n.y = 1.0
            n.theta = 180.0
            self.neck_to_coords_publisher.publish(n)
            time.sleep(0.5)
                
            n = Pose2D()
            n.x = 0.0
            n.y = 1.0
            n.theta = 180.0
            self.neck_to_coords_publisher.publish(n)
            time.sleep(0.5)


        ### selecionar o ID da pessoa mais central

        # a cada iteração: 
            # follow person do ID X
        # testar para 30 FPS
        pass

    """




"""
    def request_point_cloud_person(self):
        if self.person_pose.num_person > 0:
            aux = RequestPointCloud()
            aux.box_top_left_x = self.person_pose.persons[0].box_top_left_x
            aux.box_top_left_y = self.person_pose.persons[0].box_top_left_y
            aux.box_width = self.person_pose.persons[0].box_width
            aux.box_height = self.person_pose.persons[0].box_height
            aux.retrieve_bbox = False

            p1 = Pose2D()
            p1.x = float(self.person_pose.persons[0].kp_nose_x)
            p1.y = float(self.person_pose.persons[0].kp_nose_y)
            aux.requested_point_coords.append(p1)

            p2 = Pose2D()
            p2.x = float(self.person_pose.persons[0].kp_shoulder_left_x)
            p2.y = float(self.person_pose.persons[0].kp_shoulder_left_y)
            aux.requested_point_coords.append(p2)

            p3 = Pose2D()
            p3.x = float(self.person_pose.persons[0].kp_hip_right_x)
            p3.y = float(self.person_pose.persons[0].kp_hip_right_y)
            aux.requested_point_coords.append(p3)

            self.request_point_cloud_publisher.publish(aux)    

    def person_pose_filtered_callback(self, pose: Yolov8Pose):        
        self.person_pose = pose
        pass

        # print(pose.num_person)
        # if pose.num_person > 0:
        #     aux = TrackPerson()
        #     aux.person = pose.persons[0]
        #     aux.kp_number = 5
        #     aux.is_center = True   
        #     self.neck_follow_person_publisher.publish(aux)    











        
    def get_neck_position_callback(self, pos: NeckPosition):
        print("Received Neck Position: pan =", int(pos.pan), " tilt = ", int(pos.tilt))

    def get_start_button_callback(self, state: Bool):
        print("Received Start Button: ", state.data)

    def get_vccs_callback(self, vcc: Pose2D):
        print("Received VCC: ", vcc.x, ", and Emergency: ", bool(vcc.y))

    def get_torso_pos_callback(self, torso_pos: Pose2D):
        print("Received Legs Angle: ", torso_pos.x, ", and Torso Angle: ", torso_pos.y)

    def get_encoders_callback(self, encoders: Encoders):
        print("Received Encoders: ", encoders.enc_m1, encoders.enc_m2, encoders.enc_m3, encoders.enc_m4)

    def get_controller_callback(self, controller: PS4Controller):
        print("TRIANGLE = ", controller.triangle, "CIRCLE = ", controller.circle, "CROSS = ", controller.cross, "SQUARE = ", controller.square)
        print("UP = ", controller.arrow_up, "RIGHT = ", controller.arrow_right, "DOWN = ", controller.arrow_down, "LEFT = ", controller.arrow_left)
        print("L1 = ", controller.l1, "R1 = ", controller.r1, "L3 = ", controller.l3, "R3 = ", controller.r3)
        print("SHA = ", controller.share, "OPT = ", controller.options, "PS = ", controller.ps)
        print("L2 = ", controller.l2, "R2 = ", controller.r2)
        print("L3_ang = ", controller.l3_ang, "L3_dis = ", controller.l3_dist, "L3_xx = ", controller.l3_xx, "L3_yy = ", controller.l3_yy)
        print("R3_ang = ", controller.r3_ang, "R3_dis = ", controller.r3_dist, "R3_xx = ", controller.r3_xx, "R3_yy = ", controller.r3_yy)
        self.ps4_controller = controller
        self.controller_updated = True

    def get_lidar_callback(self, scan: LaserScan):
        # print(scan)
        pass

    def get_speech_done_callback(self, state: Bool):
        print("Received Speech Flag: ", state.data)
        self.start_audio()

    def get_color_image_callback(self, img: Image):
        # print(img)
        print("---")
        self.get_logger().info('Receiving color video frame')
        current_frame = self.br.imgmsg_to_cv2(img, "bgr8")

    """
""" 
        image = cv2.cvtColor(current_frame, cv2.COLOR_RGB2BGR)
        height, width, _ = image.shape
        results = self.pose.process(image)
        #print("RESULTS")

        print('A')

        if results.pose_landmarks:
            print('found landmarks')
            self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS, self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2), self.mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=2, circle_radius=2))
            #LEFT_SIDE_IMG
            
            point_face_x = (round(results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE].x*width,2))
            point_face_y = (round(results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE].y*height,2))
            
            print(point_face_x, point_face_y)

            hip = (round(results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP ].y*height,2))
            
            print(hip)
            
            shoulder = (round(results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y*height,2))
            
            print(shoulder)
            
            #cv2.line(image, (center_x,center_y), (point_face[0],point_face[1]), (0, 255, 255), 2)

            num_person = 1
            
            cv2.imshow("Landmarks", image)
            cv2.waitKey(1)
        else: """
        # print('didnt found landmarks')
        #cv2.imshow("c_camera", current_frame)   
        #cv2.waitKey(1)
            
        
"""
    def get_depth_image_callback(self, img: Image):
        # print(img)
        print("---")
        self.get_logger().info('Receiving depth video frame')
        current_frame = self.br.imgmsg_to_cv2(img)
        #cv2.imshow("d_camera", current_frame)   
        #cv2.waitKey(1)

    def flag_listening_callback(self, flag: Bool):
        print("Finished Listening, now analising...")
    """



"""
    def flag_pos_reached_callback(self, flag: Bool):

        time.sleep(5.0)
        nav = TarNavSDNL()
        nav.flag_not_obs = False
        nav.move_target_coordinates.x = 2.0
        nav.move_target_coordinates.y = 3.0
        nav.rotate_target_coordinates.x = -3.0 
        nav.rotate_target_coordinates.y = 3.0 
        
        self.target_position_publisher.publish(nav)


    def start_audio(self):
        # print(snet)
        aud = SpeechType()
        aud.yes_or_no = False
        aud.receptionist = False
        aud.restaurant = True
        self.audio_command_publisher.publish(aud)
        print(aud)
    """
    
    # def timer_callback4(self):
        
        # if self.init == True:
        #     self.start_audio()
        #     self.init = False 
        
        # speak = RobotSpeech()
        #speak.command = "Red Wine"
        # speak.language = 'en'


        #self.speaker_publisher.publish(speak)
        
        
        
        # speak = RobotSpeech()
        
""" 
        speak.command = "RedWine"


        self.speaker_publisher.publish(speak) """
        


        # rgb = Int16()

        # rgb.data = 100
        # self.rgb_mode_publisher.publish(rgb)
        # print("Enviei RGB", self.rgb_ctr)





        # self.rgb_ctr +=10

        # if self.rgb_ctr > 91:
        #     self.rgb_ctr = 2

""" def timer_callback2(self):

        p = Pose2D()
        if self.neck_ctr == 0:
            p.x = float(3)
            p.y = float(2)
            p.theta = float(180)
        if self.neck_ctr == 1:
            p.x = float(2)
            p.y = float(2)
            p.theta = float(180)
        if self.neck_ctr == 2:
            p.x = float(1)
            p.y = float(2)
            p.theta = float(180)
        if self.neck_ctr == 3:
            p.x = float(0)
            p.y = float(2)
            p.theta = float(180)
        if self.neck_ctr == 4:
            p.x = float(-1)
            p.y = float(2)
            p.theta = float(180)
        if self.neck_ctr == 5:
            p.x = float(-2)
            p.y = float(2)
            p.theta = float(180)

        self.neck_to_coords_publisher.publish(p)
        
        self.neck_ctr += 1
        if self.neck_ctr == 6:
            self.neck_ctr = 0

        """
"""
    def timer_callback_audio(self):
        if self.init == True:
            self.start_audio()
            self.init = False 


    def timer_callback3(self):
        # if self.init_start_door:
        aux_start_door = Bool()
        aux_start_door.data = True
        self.start_door_publisher.publish(aux_start_door)
        print("Fiz pedido da Door")
        # self.init_start_door = False


        face = Int16()
        
        face.data = self.face_counter
        self.face_publisher.publish(face)

        self.face_counter += 1

        if self.face_counter > 1:
            self.face_counter = 0

        if self.flag_init_nav:

            nav = TarNavSDNL()
            nav.flag_not_obs = False
            nav.move_target_coordinates.x = 0.0
            nav.move_target_coordinates.y = 3.0
            nav.rotate_target_coordinates.x = 2.0 
            nav.rotate_target_coordinates.y = 3.0 
            
            self.target_position_publisher.publish(nav)

            self.flag_init_nav = False

        # self.nav_ctr -= 0.5

    def timer_callback(self):
        neck = NeckPosition()
        flag_start_button = Bool()
        flag_vccs = Bool()
        flag_torso = Bool()
        rgb_mode = Int16()
        torso_pos = Pose2D()
        omni_move = Vector3()
        flag_encoders = Bool()

        if self.controller_updated:
            if self.ps4_controller.cross == 2: # RISING
                rgb_mode.data = 4
                self.rgb_mode_publisher.publish(rgb_mode)
            elif self.ps4_controller.cross == 1: # FALLING:
                rgb_mode.data = 2
                self.rgb_mode_publisher.publish(rgb_mode)

            if self.ps4_controller.l3_dist > 0.0:
                omni_move.x = self.ps4_controller.l3_ang
                omni_move.y = self.ps4_controller.l3_dist*100/5
            else:
                omni_move.x = 0.0
                omni_move.y = 0.0


            if self.ps4_controller.r3_dist > 0.0:
                omni_move.z = 100 + self.ps4_controller.r3_xx*10
            else:
                omni_move.z = 100.0
            
           
            self.omni_move_publisher.publish(omni_move)
            self.controller_updated = False
        """
"""
        if self.counter == 0:
            neck.pan = 180.0
            neck.tilt = 180.0 
            self.flag_get_neck_position = False
            # self.flag_get_start_button = False
            # self.flag_get_vccs = False
            self.flag_get_torso = False
            self.flag_get_encoders = False
            rgb_mode.data = 1
            self.rgb_mode_publisher.publish(rgb_mode)
            torso_pos.x = 66.0
            torso_pos.y = 85.0
            self.torso_pos_publisher.publish(torso_pos)
            omni_move.x = 0.0
            omni_move.y = 0.0
            omni_move.z = 100.0 - 10.0
            self.omni_move_publisher.publish(omni_move)
        if self.counter == 1:
            neck.pan = 270.0
            neck.tilt = 180.0 
            omni_move.x = 0.0
            omni_move.y = 0.0
            omni_move.z = 100.0 + 10.0
            self.omni_move_publisher.publish(omni_move)
        if self.counter == 2:
            neck.pan = 180.0
            neck.tilt = 180.0 
            self.flag_get_neck_position = True
            # self.flag_get_start_button = True
            # self.flag_get_vccs = True
            self.flag_get_torso = True
            self.flag_get_encoders = True
            rgb_mode.data = 2
            self.rgb_mode_publisher.publish(rgb_mode)
            torso_pos.x = 64.0
            torso_pos.y = 75.0
            self.torso_pos_publisher.publish(torso_pos)
            omni_move.x = 0.0
            omni_move.y = 20.0
            omni_move.z = 100.0
            self.omni_move_publisher.publish(omni_move)
        if self.counter == 3:
            neck.pan = 90.0
            neck.tilt = 180.0 
            omni_move.x = 180.0
            omni_move.y = 20.0
            omni_move.z = 100.0
            self.omni_move_publisher.publish(omni_move)
        if self.counter == 4:
            neck.pan = 180.0
            neck.tilt = 180.0 
            self.flag_get_neck_position = False
            # self.flag_get_start_button = False
            # self.flag_get_vccs = False
            self.flag_get_torso = False
            self.flag_get_encoders = False
            rgb_mode.data = 3
            self.rgb_mode_publisher.publish(rgb_mode)
            torso_pos.x = 66.0
            torso_pos.y = 85.0
            self.torso_pos_publisher.publish(torso_pos)
            omni_move.x = 90.0
            omni_move.y = 20.0
            omni_move.z = 100.0
            self.omni_move_publisher.publish(omni_move)
        if self.counter == 5:
            neck.pan = 180.0
            neck.tilt = 120.0 
            omni_move.x = 270.0
            omni_move.y = 20.0
            omni_move.z = 100.0
            self.omni_move_publisher.publish(omni_move)
        if self.counter == 6:
            neck.pan = 180.0
            neck.tilt = 180.0 
            self.flag_get_neck_position = True
            # self.flag_get_start_button = True
            # self.flag_get_vccs = True
            self.flag_get_torso = True
            self.flag_get_encoders = True
            rgb_mode.data = 4
            self.rgb_mode_publisher.publish(rgb_mode)
            torso_pos.x = 64.0
            torso_pos.y = 75.0
            self.torso_pos_publisher.publish(torso_pos)
            omni_move.x = 0.0
            omni_move.y = 20.0
            omni_move.z = 100.0 - 10.0
            self.omni_move_publisher.publish(omni_move)
        if self.counter == 7:
            neck.pan = 180.0
            neck.tilt = 235.0 
            self.counter = -1
            omni_move.x = 0.0
            omni_move.y = 20.0
            omni_move.z = 100.0 + 10.0
            self.omni_move_publisher.publish(omni_move)

        
        self.neck_position_publisher.publish(neck)


        # flag_start_button.data = self.flag_get_start_button
        # self.flag_start_button_publisher.publish(flag_start_button)

        # flag_vccs.data = self.flag_get_vccs
        # self.flag_vccs_publisher.publish(flag_vccs)

        flag_torso.data = self.flag_get_torso
        self.flag_torso_pos_publisher.publish(flag_torso)

        flag_encoders.data = self.flag_get_encoders
        self.flag_encoders_publisher.publish(flag_encoders)

        print("DATA SENT ", self.counter)
        # self.counter+=1
        """