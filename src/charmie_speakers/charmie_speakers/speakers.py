#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from charmie_interfaces.msg import RobotSpeech

import pygame
from gtts import gTTS
from pathlib import Path


class RobotSpeak():
    def __init__(self):
        self.filename = '1.mp3'
        pygame.init()
        self.home = str(Path.home())
        # print(self.home)

    def speak(self, speech: RobotSpeech):

        if speech.language == 'pt':
            lang = speech.language
            print("Language: Portuguese")
        elif speech.language == 'en':
            lang = speech.language
            print("Language: English")
        else:
            lang = 'en'
            print("Language: Other (Default: English)")


        tts = gTTS(text=str(speech.command), lang=lang)
        tts.save(self.home+'/'+self.filename)
        pygame.mixer.music.load(self.home+'/'+self.filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pass
        

class SpeakerNode(Node):

    def __init__(self):
        super().__init__("Speaker")
        self.get_logger().info("Initialised CHARMIE Speaker Node")
        self.charmie_speech = RobotSpeak()

        self.speaker_command_subscriber = self.create_subscription(RobotSpeech, "speech_command", self.speaker_command_callback, 10)
        self.flag_speech_done_publisher = self.create_publisher(Bool, "flag_speech_done", 10)
        
    def speaker_command_callback(self, speech: RobotSpeech):

        print("\nReceived String:", speech.command)
        self.charmie_speech.speak(speech)
        flag = Bool()
        flag.data = True
        self.flag_speech_done_publisher.publish(flag)
        print("Finished Speaking.")

        


def main(args=None):
    rclpy.init(args=args)
    node = SpeakerNode()
    rclpy.spin(node)
    rclpy.shutdown()
