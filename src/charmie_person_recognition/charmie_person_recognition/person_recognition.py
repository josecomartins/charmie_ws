#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from example_interfaces.msg import Bool, String, Float32, Int16
from geometry_msgs.msg import Pose2D, Point
from sensor_msgs.msg import Image
from charmie_interfaces.msg import NeckPosition, DetectedPerson, Yolov8Pose, ListOfPoints, SearchForPerson, ListOfImages, ListOfStrings, RobotSpeech
from cv_bridge import CvBridge, CvBridgeError
import cv2
import time
import threading
import math
import numpy as np

# fourcc = cv2.VideoWriter_fourcc(*'H264')  # You can also use 'XVID' or 'MJPG' codecs
# width, height = 1280, 720  # You can adjust the resolution
# out = cv2.VideoWriter('charmie_test_26.avi', cv2.VideoWriter_fourcc(*'MJPG'), 20.0, (width, height))

# TO DO TIAGO RIBEIRO:
# - crop face from color_image according to yolo pose  
# - crop hands from color_image according to yolo pose  
# - crop feet from color_image according to yolo pose  
# - sincronizar imagem da camara com imagem do yolo pose 
# - filtro imagens fora do ecra


class PersonRec():
    def __init__(self):
        print("New Person Recognition Class Initialised")

    # your code here

class PersonRecognitionNode(Node):

    def __init__(self):
        super().__init__("PersonRecognition")
        self.get_logger().info("Initialised CHARMIE Person Recognition Node")


        # Low Level: RGB
        self.rgb_mode_publisher = self.create_publisher(Int16, "rgb_mode", 10)

        # image and pose subscriptions
        self.color_image_subscriber = self.create_subscription(Image, "/color/image_raw", self.get_color_image_callback, 10)
        self.person_pose_filtered_subscriber = self.create_subscription(Yolov8Pose, "person_pose_filtered", self.get_person_pose_filtered_callback, 10)   
        
        self.neck_position_publisher = self.create_publisher(NeckPosition, "neck_to_pos", 10)
        self.neck_to_coords_publisher = self.create_publisher(Pose2D, "neck_to_coords", 10)
        
        self.search_for_person_subscriber = self.create_subscription(SearchForPerson, "search_for_person", self.search_for_person_callback, 10)
        self.search_for_person_publisher = self.create_publisher(ListOfPoints, "search_for_person_points", 10)
        # self.create_timer(2, self.check_person_feet)

        self.only_detect_person_right_in_front_publisher = self.create_publisher(Bool, "only_det_per_right_in_front", 10)
        
        # Speaker
        self.speaker_publisher = self.create_publisher(RobotSpeech, "speech_command", 10)
        self.flag_speaker_subscriber = self.create_subscription(Bool, "flag_speech_done", self.get_speech_done_callback, 10)

        self.cropped_image_publisher = self.create_publisher(ListOfImages, '/cropped_image', 10)
        

        self.check_stickler_rules_subscriber = self.create_subscription(Bool, "check_stickler_rules", self.check_stickler_rules_callback, 10)

        self.robot = PersonRec()

        self.latest_color_image = Image()
        self.latest_person_pose = Yolov8Pose()
        self.br = CvBridge()

        self.search_for_person_data = SearchForPerson()
        self.speech_str = RobotSpeech()
        self.flag_speech_done = False

        self.search_for_person_flag = False
        self.check_stickler_rules = False
        self.check_if_charmie_is_being_followed = False
        
    def check_stickler_rules_callback(self, state: Bool):
        print("Check Stickler Flag Arrived")
        self.check_stickler_rules = state.data

    def search_for_person_callback(self, sfp: SearchForPerson):
        print("Received a start for person")
        self.search_for_person_data = sfp
        self.search_for_person_flag = True

    def get_color_image_callback(self, img: Image):
        self.latest_color_image = img
        
        # generate video for yolo pose dataset
        # frame = self.br.imgmsg_to_cv2(img, "bgr8")
        # cv2.imshow('Frame', frame)
        # cv2.waitKey(5)
        # out.write(frame)
        
    def get_person_pose_filtered_callback(self, pose: Yolov8Pose):
        self.latest_person_pose = pose
        # print("IN")

    def get_speech_done_callback(self, state: Bool):
        self.flag_speech_done = state.data
        # print("Received Speech Flag:", state.data)

    def check_person_face(self):
        print("Face Image")
        
        # ROS2 Image Bridge for OpenCV
        print("a")
        try:
            current_frame = self.br.imgmsg_to_cv2(self.latest_color_image, "bgr8")
        except Exception as error:
            print("An error occurred:", error) # An error occurred: name 'x' is not defined
        
        print("b")
        current_pose = self.latest_person_pose

        # Crop the image to the rectangle
        # cropped_image = current_frame[100:600, 100:400]

        # Save the cropped image to a file
        # cv2.imwrite("cropped_image.jpg", cropped_image)

        print(current_pose.num_person)

        ctr = 0
        if len(current_pose.persons) > 0:
            for person in current_pose.persons:
                ctr+=1

                # y1 = topo bounding box y
                # y2 =  maior y dos dois ombros
                # x1 = ombro mais a esq
                # x2 = ombro mais a direita
                
                y1 = person.box_top_left_y
                y2 = min(person.kp_shoulder_right_y, person.kp_shoulder_left_y)


                x1 = min(person.kp_shoulder_right_x, person.kp_shoulder_left_x)
                x2 = max(person.kp_shoulder_right_x, person.kp_shoulder_left_x)

                print("F:", y1, y2, " - ", x1, x2)

                cropped_image = current_frame[y1:y2, x1:x2]

                print("image size:", cropped_image.shape[1], cropped_image.shape[0])
            
                # n_pixeis_x = x2-x1
                # n_pixeis_y = y2-y1
                # print("Pixeis Face:", n_pixeis_x, n_pixeis_y)

                if cropped_image.shape[0] == 0 or  cropped_image.shape[1]:
                    cropped_image = current_frame[0:1, 0:1]

                try:
                    # Save the cropped image to a file
                    cv2.imwrite("cropped_face_"+str(ctr)+".jpg", cropped_image)
                except:
                    print("An exception has occurred!")

                print(person.conf_person)
                
        else:
            cropped_image = current_frame[0:1, 0:1]


        bridge = CvBridge()
        image = bridge.cv2_to_imgmsg(cropped_image, "bgr8")#, encoding="passthrough")
        # self.cropped_image_publisher.publish(image_message)
        return image
    
    def check_person_hands(self):
        print("Hands Image")
        
        # ROS2 Image Bridge for OpenCV
        try:
            current_frame = self.br.imgmsg_to_cv2(self.latest_color_image, "bgr8")
        except Exception as error:
            print("An error occurred:", error) # An error occurred: name 'x' is not defined
        current_pose = self.latest_person_pose

        print(current_pose.num_person)

        ctr = 0
        if len(current_pose.persons) > 0:
            for person in current_pose.persons:
                ctr+=1
            
                threshold = 100

                y1_l = max(person.kp_wrist_left_y - threshold, 0)
                y2_l = min(person.kp_wrist_left_y + threshold, current_frame.shape[0])

                x1_l = max(person.kp_wrist_left_x - threshold, 0)
                x2_l = min(person.kp_wrist_left_x + threshold, current_frame.shape[1])

                y1_r = max(person.kp_wrist_right_y - threshold, 0)
                y2_r = min(person.kp_wrist_right_y + threshold, current_frame.shape[0])

                x1_r = max(person.kp_wrist_right_x - threshold, 0)
                x2_r = min(person.kp_wrist_right_x + threshold, current_frame.shape[1])
 
                print("HL:", y1_l, y2_l, " - ", x1_l, x2_l)
                print("HR:", y1_r, y2_r, " - ", x1_r, x2_r)

                # Crop the image to the rectangle
                cropped_image_l = current_frame[y1_l:y2_l, x1_l:x2_l]
                cropped_image_r = current_frame[y1_r:y2_r, x1_r:x2_r]

                print("image size left:", cropped_image_l.shape[1], cropped_image_l.shape[0])
                print("image size right:", cropped_image_r.shape[1], cropped_image_r.shape[0])
                # pode na mesma acontecer de a imagem ter um eixo vazio?..., caso a mão esteja fora do ecrã, testar pós qualificação

                try:
                    # Save the cropped image to a file
                    cv2.imwrite("cropped_hand_left_"+str(ctr)+".jpg", cropped_image_l)
                    cv2.imwrite("cropped_hand_right_"+str(ctr)+".jpg", cropped_image_r)
                except:
                    print("An exception has occurred!")

                print(person.conf_person)

        else:
                cropped_image_l = current_frame[0:1, 0:1]
                cropped_image_r = current_frame[0:1, 0:1]
        
        
        bridge = CvBridge()
        image_l = bridge.cv2_to_imgmsg(cropped_image_l, "bgr8")#, encoding="passthrough")
        image_r = bridge.cv2_to_imgmsg(cropped_image_r, "bgr8")#, encoding="passthrough")
        # self.cropped_image_publisher.publish(image_message)
        return image_l, image_r

    def check_person_feet(self):
        
        # ROS2 Image Bridge for OpenCV
        try:
            current_frame = self.br.imgmsg_to_cv2(self.latest_color_image, "bgr8")
        except Exception as error:
            print("An error occurred:", error) # An error occurred: name 'x' is not defined
        current_pose = self.latest_person_pose

        print(current_pose.num_person)

        ctr = 0
        if len(current_pose.persons) > 0:
            for person in current_pose.persons:
                ctr+=1

                threshold = 60

                y1_l = max(person.kp_ankle_left_y - threshold, 0)
                y2_l = min(person.kp_ankle_left_y + threshold, current_frame.shape[0])

                x1_l = max(person.kp_ankle_left_x - threshold, 0)
                x2_l = min(person.kp_ankle_left_x + threshold, current_frame.shape[1])


                y1_r = max(person.kp_ankle_right_y - threshold, 0)
                y2_r = min(person.kp_ankle_right_y + threshold, current_frame.shape[0])

                x1_r = max(person.kp_ankle_right_x - threshold, 0)
                x2_r = min(person.kp_ankle_right_x + threshold, current_frame.shape[1])
 
                print("FL:", y1_l, y2_l, " - ", x1_l, x2_l)
                print("FR:", y1_r, y2_r, " - ", x1_r, x2_r)

                # Crop the image to the rectangle
                cropped_image_l = current_frame[y1_l:y2_l, x1_l:x2_l]
                cropped_image_r = current_frame[y1_r:y2_r, x1_r:x2_r]

                print("image size left:", cropped_image_l.shape[1], cropped_image_l.shape[0])
                print("image size right:", cropped_image_r.shape[1], cropped_image_r.shape[0])
                # pode na mesma acontecer de a imagem ter um eixo vazio?..., caso a mão esteja fora do ecrã, testar pós qualificação

                try:
                    # Save the cropped image to a file
                    cv2.imwrite("cropped_foot_left_"+str(ctr)+".jpg", cropped_image_l)
                    cv2.imwrite("cropped_foot_right_"+str(ctr)+".jpg", cropped_image_r)
                except:
                    print("An exception has occurred!")

                print(person.conf_person)

        else:
            cropped_image_l = current_frame[0:1, 0:1]
            cropped_image_r = current_frame[0:1, 0:1]

        bridge = CvBridge()
        image_l = bridge.cv2_to_imgmsg(cropped_image_l, "bgr8")#, encoding="passthrough")
        image_r = bridge.cv2_to_imgmsg(cropped_image_r, "bgr8")#, encoding="passthrough")
        # self.cropped_image_publisher.publish(image_message)
        return image_l, image_r

    def check_person_garbage_nearby(self):
        
        # ROS2 Image Bridge for OpenCV
        try:
            current_frame = self.br.imgmsg_to_cv2(self.latest_color_image, "bgr8")
        except Exception as error:
            print("An error occurred:", error) # An error occurred: name 'x' is not defined
        current_pose = self.latest_person_pose

        # Crop the image to the rectangle
        # cropped_image = current_frame[100:600, 100:400]

        # Save the cropped image to a file
        # cv2.imwrite("cropped_image.jpg", cropped_image)

        print(current_pose.num_person)

        ctr = 0
        if len(current_pose.persons) > 0:
            for person in current_pose.persons:
                ctr+=1

                # y1 = topo bounding box y
                # y2 =  maior y dos dois ombros
                # x1 = ombro mais a esq
                # x2 = ombro mais a direita
                
                # int32 kp_wrist_left_x
                # int32 kp_wrist_left_y
                # float32 kp_wrist_left_conf

                # int32 kp_wrist_right_x
                # int32 kp_wrist_right_y
                # float32 kp_wrist_right_conf

                threshold_h = 250
                threshold_v = 300

                y1 = max(person.kp_knee_left_y, person.kp_knee_right_y)
                y2 = min(person.kp_knee_left_y + threshold_v, person.kp_knee_right_y + threshold_v, current_frame.shape[0])

                x1 = max(person.kp_ankle_right_x - threshold_h, 0)
                x2 = min(person.kp_ankle_left_x + threshold_h, current_frame.shape[1])

                print("SurrFloor:", y1, y2, " - ", x1, x2)

                # Crop the image to the rectangle
                cropped_image = current_frame[y1:y2, x1:x2]

                print("image size:", cropped_image.shape[1], cropped_image.shape[0])

                if cropped_image.shape[0] == 0 or cropped_image.shape[1] == 0:
                    cropped_image = current_frame[0:1, 0:1]
                    
                try:
                    # Save the cropped image to a file
                    cv2.imwrite("cropped_floor_"+str(ctr)+".jpg", cropped_image)
                except:
                    print("An exception has occurred!")

                print(person.conf_person)
        else:
            cropped_image = current_frame[0:1, 0:1]


        bridge = CvBridge()
        image = bridge.cv2_to_imgmsg(cropped_image, "bgr8")#, encoding="passthrough")
        # self.cropped_image_publisher.publish(image_message)
        return image

def main(args=None):
    rclpy.init(args=args)
    node = PersonRecognitionNode()
    th_main = threading.Thread(target=thread_main_person_recognition, args=(node,), daemon=True)
    th_main.start()
    rclpy.spin(node)
    rclpy.shutdown()


def thread_main_person_recognition(node: PersonRecognitionNode):
    main = PersonRecognitionMain(node)
    main.main()

class PersonRecognitionMain():

    def __init__(self, node: PersonRecognitionNode):
        self.node = node
        # Create a black image

    def main(self):

        time.sleep(1.0)


        self.show_restaurant_detected_customers_with_imread_images()

        while True:
        
            #print(self.node.search_for_person_flag)
            if self.node.search_for_person_flag:
                self.search_for_person()
                # self.aux_for_imread()
                self.node.search_for_person_flag = False

            if self.node.check_stickler_rules:
                self.check_stickler_rules()
                self.node.check_stickler_rules = False
                
            if self.node.check_if_charmie_is_being_followed:
                self.check_if_charmie_is_being_followed()


    def wait_for_end_of_speaking(self):
        while not self.node.flag_speech_done:
            pass
        self.node.flag_speech_done = False

    def check_if_charmie_is_being_followed(self):

        # sends info to yolo pose to only detect people right in front of the camera
        pose = Bool()
        pose.data = True
        self.node.only_detect_person_right_in_front_publisher.publish(pose)

        # looks back to check if is being followed 
        neck_look_back = NeckPosition()
        neck_look_back.pan = float(360)
        neck_look_back.tilt = float(180)
        self.node.neck_position_publisher.publish(neck_look_back)

        time.sleep(1.0)

        # self.node.speech_str.command = "Please Follow Me. Keep yourself approximately 1 meter behind me. If you start to get behind I will warn you"
        self.node.speech_str.command = "Please Follow Me. Come behind me."
        self.node.speaker_publisher.publish(self.node.speech_str)
        self.wait_for_end_of_speaking()

        person_here = False
        while not person_here:
            if len(self.node.latest_person_pose.persons) > 0:
                self.node.speech_str.command = "Thanks for coming behind me. Let's roll."
                self.node.speaker_publisher.publish(self.node.speech_str)
                self.wait_for_end_of_speaking()
                person_here = True
            else:
                # the person stopped following the robot
                self.node.speech_str.command = "Please come behind me. I need you to follow me."
                self.node.speaker_publisher.publish(self.node.speech_str)
                self.wait_for_end_of_speaking()
                time.sleep(3.0)


        prev_number_of_person = 1    
        while True:
          

            if len(self.node.latest_person_pose.persons) > 0:
                if prev_number_of_person == 0:
                    self.node.speech_str.command = "Thanks for coming back. Let's roll."
                    self.node.speaker_publisher.publish(self.node.speech_str)
                    self.wait_for_end_of_speaking()    
                    prev_number_of_person = 1   
                # everything is ok
                pass
            else:
                # the person stopped following the robot
                self.node.speech_str.command = "You are falling behind, please come back. I will wait here for you"
                self.node.speaker_publisher.publish(self.node.speech_str)
                self.wait_for_end_of_speaking()        
                prev_number_of_person = 0
                time.sleep(3.0)



    def check_stickler_rules(self):
        print("Checking Stickler Rules")
        face_img = self.node.check_person_face()
        left_hand_img, right_hand_img = self.node.check_person_hands()
        left_foot_img, right_foot_img = self.node.check_person_feet()
        surrounding_feet_img = self.node.check_person_garbage_nearby()

        imgs = ListOfImages()
        imgs.images.append(left_hand_img)
        imgs.images.append(right_hand_img)
        imgs.images.append(surrounding_feet_img)
        imgs.images.append(left_foot_img)
        imgs.images.append(right_foot_img)
        self.node.cropped_image_publisher.publish(imgs)
        # time.sleep(5)


    def search_for_person(self):
        print("In Search for Person.")
        
        rgb = Int16()
        rgb.data = 63
        self.node.rgb_mode_publisher.publish(rgb)

        tetas = self.node.search_for_person_data.angles
        # tetas = [-120, -60, 0, 60, 120]
        imshow_detected_people = self.node.search_for_person_data.show_image_people_detected
        # imshow_detected_people = True

        total_person_detected = []
        person_detected = []
        total_cropped_people = []
        cropped_people = []
        points = []
        croppeds = []

        # neck = NeckPosition()
        # neck.pan = float(180 - tetas[0])
        # neck.tilt = float(180)
        # self.node.neck_position_publisher.publish(neck)
        # time.sleep(1.0)

        people_ctr = 0
        delay_ctr = 0
        for t in tetas:
            print("Rotating Neck:", t)
            
            neck = NeckPosition()
            neck.pan = float(180 - t)
            neck.tilt = float(180)
            self.node.neck_position_publisher.publish(neck)
            if delay_ctr == 0: # since the initial angle of the tracking is never known, we do this to make sure there is time for the neck to reach the first position before analysing the yolo pose
                time.sleep(2.0)
            else:
                time.sleep(1.5)
            delay_ctr+=1

            # print(self.node.latest_person_pose.num_person)

            for people in self.node.latest_person_pose.persons:
                people_ctr+=1
                print(" - ", people.index_person, people.position_absolute.x,people.position_absolute.y, people.position_absolute.z)
                print(" - ", people.index_person, people.position_relative.x,people.position_relative.y, people.position_relative.z)
                aux = (people.position_absolute.x, people.position_absolute.y) 
                person_detected.append(aux)
                points.append(aux)

                if imshow_detected_people:

                    y1 = people.box_top_left_y
                    y2 = people.box_top_left_y + people.box_height

                    x1 = people.box_top_left_x
                    x2 = people.box_top_left_x + people.box_width

                    print(y1, y1, x1,x2)
                    br = CvBridge()
                    current_frame = br.imgmsg_to_cv2(self.node.latest_color_image, "bgr8")
                    cropped_image = current_frame[y1:y2, x1:x2]
                    cropped_people.append(cropped_image)
                    
                    croppeds.append(cropped_image)

            total_person_detected.append(person_detected.copy())
            total_cropped_people.append(cropped_people.copy())
            print("Total number of people detected:", len(person_detected), people_ctr)
            person_detected.clear()          
            cropped_people.clear()

        # print(len(cropped_image))
        # for cropped in cropped_people:
        #     cv2.imshow("Detected People", cropped)
        #     cv2.waitKey(1)
        #     time.sleep(5)

        print(total_person_detected)
        print(len(points))
       
        filtered_persons = []
        filtered_persons_cropped = []
        for frame in range(len(total_person_detected)):

            if not len(filtered_persons):
                for person in range(len(total_person_detected[frame])):
                    filtered_persons.append(total_person_detected[frame][person])
                    filtered_persons_cropped.append(total_cropped_people[frame][person])
            else:
                for person in range(len(total_person_detected[frame])):
                    same_person_ctr = 0
                    same_person_coords = (0,0)
                    for filtered in range(len(filtered_persons)): #_aux:

                        # print("??? ", total_person_detected[frame][person], filtered_persons[filtered])
                        dist = math.dist(total_person_detected[frame][person], filtered_persons[filtered])
                        # print("person:", person, "filtered:", filtered, "dist:", dist)
                        
                        if dist < 1.0:
                            same_person_ctr+=1
                            same_person_coords = filtered_persons[filtered]
                            same_person_cropped = filtered_persons_cropped[filtered] 
                        
                    if same_person_ctr > 0:
                        
                        # print(same_person_cropped)
                        # print(total_cropped_people[frame][person])
                        # print(len(same_person_cropped), len(total_cropped_people[frame][person]))
                        # print(same_person_cropped.shape[0], same_person_cropped.shape[1])
                        # print(total_cropped_people[frame][person].shape[0], total_cropped_people[frame][person].shape[1])
                        
                        # the same person is the person on the first frame, whereas total_cropped_people[frame][person] is the same person on the second frame
                        # if total_cropped_people[frame][person].shape[1] > same_person_cropped.shape[1]:
                            # filtered_persons_cropped.remove(same_person_cropped)
                            # filtered_persons_cropped.append(total_cropped_people[frame][person])
                            # total_cropped_people[frame][person] = 
                            # pass

                        # in some cases, I remove and then add again the same value, so it photos match the locations
                        filtered_persons_cropped.remove(same_person_cropped)
                        if total_cropped_people[frame][person].shape[1] > same_person_cropped.shape[1]:
                            filtered_persons_cropped.append(total_cropped_people[frame][person])
                        else:
                            filtered_persons_cropped.append(same_person_cropped)
                            
                        #print(same_person_ctr, same_person_coords, person)
                        filtered_persons.remove(same_person_coords)

                        avg_person = ((total_person_detected[frame][person][0]+same_person_coords[0])/2, (total_person_detected[frame][person][1]+same_person_coords[1])/2)
                        # print(avg_person)
                        filtered_persons.append(avg_person)
                        points.append(avg_person)

                    else:
                        filtered_persons.append(total_person_detected[frame][person])
                        filtered_persons_cropped.append(total_cropped_people[frame][person])

        # print("---", filtered_persons)
        show_detected_people = True
        
        ctr = 0
        for c in croppeds:
            ctr+=1
            cv2.imwrite("Person Detected_"+str(ctr)+".jpg", c)
        ctr = 0
        for c in filtered_persons_cropped:
            ctr+=1
            cv2.imwrite("Person Filtered_"+str(ctr)+".jpg", c)


        if show_detected_people:
            H = 720
            y_offset = 50
            x_offset = 50
            max_image_height = 0
            detected_person_final_image = np.zeros(( H+(y_offset*2), H*10, 3), np.uint8)
            
            i_ctr = 0
            for i in range(len(filtered_persons_cropped)):
                i_ctr += 1
                print("Image shape:", filtered_persons_cropped[i].shape)
                print("Image dtype:", filtered_persons_cropped[i].dtype)

                scale_factor  = H/filtered_persons_cropped[i].shape[0]
                width = int(filtered_persons_cropped[i].shape[1] * scale_factor)
                height = int(filtered_persons_cropped[i].shape[0] * scale_factor)

                if width > H//2:
                    scale_factor  = (H//2)/filtered_persons_cropped[i].shape[1]
                    width = int(filtered_persons_cropped[i].shape[1] * scale_factor)
                    height = int(filtered_persons_cropped[i].shape[0] * scale_factor)



                if height > max_image_height:
                    max_image_height = height

                dim = (width, height)
                print(scale_factor, dim)
                filtered_persons_cropped[i] = cv2.resize(filtered_persons_cropped[i], dim, interpolation = cv2.INTER_AREA)

                # cv2.imshow("Image"+str(i_ctr), i)

                detected_person_final_image[y_offset:y_offset+filtered_persons_cropped[i].shape[0], x_offset:x_offset+filtered_persons_cropped[i].shape[1]] = filtered_persons_cropped[i]

                detected_person_final_image = cv2.putText(
                    detected_person_final_image,
                    f"{'Customer '+str(i_ctr)}",
                    (x_offset, y_offset-10),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                ) 

                print(filtered_persons[i])
                
                detected_person_final_image = cv2.putText(
                    detected_person_final_image,
                    f"{'('+str(round(filtered_persons[i][0],2))+', '+str(round(filtered_persons[i][1],2))+')'}",
                    (x_offset, int(height+(1.5*y_offset))),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.75,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )

                x_offset += width+50

            print(max_image_height)

            detected_person_final_image = detected_person_final_image[0:max_image_height+(y_offset*2), 0:x_offset] # Slicing to crop the image
            cv2.imshow("Customers Detected", detected_person_final_image)
            cv2.waitKey(100)

        print("---", filtered_persons)
        points_to_send = ListOfPoints()
        # for debug, see all points and the average calculations
        # for p in points:
        for p in filtered_persons:
            aux = Point()
            aux.x = float(p[0])
            aux.y = float(p[1])
            aux.z = 0.0
            points_to_send.coords.append(aux)

        # print(points_to_send)
        self.node.search_for_person_publisher.publish(points_to_send)

        # for p in filtered_persons:
        #     pose = Pose2D()
        #     pose.x = p[0]
        #     pose.y = p[1]
        #     pose.theta = 180.0
        #     self.node.neck_to_coords_publisher.publish(pose)
        #     time.sleep(3)

        # neck = NeckPosition()
        # neck.pan = float(180)
        # neck.tilt = float(180)
        # self.node.neck_position_publisher.publish(neck)


    def show_restaurant_detected_customers_with_imread_images(self):


        filtered_persons_cropped = []
        filtered_persons_cropped.append(cv2.imread("Person Filtered_1.jpg"))
        filtered_persons_cropped.append(cv2.imread("Person Filtered_2.jpg"))

        # aux = cv2.imread("Person Filtered_1.jpg")
        # cv2.imshow("aaa", aux)
        # cv2.waitKey(0)

        if True:
            H = 720
            y_offset = 50
            x_offset = 50
            max_image_height = 0
            detected_person_final_image = np.zeros(( H+(y_offset*2), H*10, 3), np.uint8)
            
            i_ctr = 0
            for i in range(len(filtered_persons_cropped)):
                i_ctr += 1
                print("Image shape:", filtered_persons_cropped[i].shape)
                print("Image dtype:", filtered_persons_cropped[i].dtype)

                scale_factor  = H/filtered_persons_cropped[i].shape[0]
                width = int(filtered_persons_cropped[i].shape[1] * scale_factor)
                height = int(filtered_persons_cropped[i].shape[0] * scale_factor)

                if width > H//2 + 50:
                    scale_factor  = (H//2)/filtered_persons_cropped[i].shape[1]
                    width = int(filtered_persons_cropped[i].shape[1] * scale_factor)
                    height = int(filtered_persons_cropped[i].shape[0] * scale_factor)



                if height > max_image_height:
                    max_image_height = height

                dim = (width, height)
                print(scale_factor, dim)
                filtered_persons_cropped[i] = cv2.resize(filtered_persons_cropped[i], dim, interpolation = cv2.INTER_AREA)

                # cv2.imshow("Image"+str(i_ctr), i)

                detected_person_final_image[y_offset:y_offset+filtered_persons_cropped[i].shape[0], x_offset:x_offset+filtered_persons_cropped[i].shape[1]] = filtered_persons_cropped[i]

                detected_person_final_image = cv2.putText(
                    detected_person_final_image,
                    f"{'Customer '+str(i_ctr)}",
                    (x_offset, y_offset-10),
                    cv2.FONT_HERSHEY_DUPLEX,
                    1,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA
                ) 

                # print(filtered_persons[i])
                
                # detected_person_final_image = cv2.putText(
                #     detected_person_final_image,
                #     f"{'('+str(round(filtered_persons[i][0],2))+', '+str(round(filtered_persons[i][1],2))+')'}",
                #     (x_offset, int(height+(1.5*y_offset))),
                #     cv2.FONT_HERSHEY_DUPLEX,
                #     0.75,
                #     (255, 255, 255),
                #     1,
                #     cv2.LINE_AA
                # )

                x_offset += width+50

            print(max_image_height)

            detected_person_final_image = detected_person_final_image[0:max_image_height+(y_offset*2), 0:x_offset] # Slicing to crop the image
            ### add imwrite here to furthermore show in face
            ### test if imgwrite is a blocking function so we dont have the problem to send the file to face while it is not correctly created
            ### configure image size and layouts to fit face precisely
            ### add filename depending on date and hour, so when debugging we know when the image was generated
            ### if file with name already exists add a counter
            ### while to know the last counter
            cv2.imshow("Customers Detected", detected_person_final_image)
            cv2.waitKey(100)

        while True:
            pass