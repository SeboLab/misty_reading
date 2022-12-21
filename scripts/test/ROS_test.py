#!/usr/bin/env python
import rospy
import random
from std_msgs.msg import Int32MultiArray, Int32, Empty, Float32, String
from misty.srv import *
import speech_recognition as sr

# Copied from https://github.com/Wisc-HCI/Reading-With-Misty/blob/master/src/misty/src/examples/demo_misty.py

def wave(pub, rate):
    pos1 = Int32MultiArray()
    pos1.data = [0, 90]
    pub.publish(pos1)
    rate.sleep()
    pos1.data = [0, 180, 100]
    pub.publish(pos1)
    rate.sleep()
    rate.sleep()
    pos1.data = [0, 90, 100]
    pub.publish(pos1)
    rate.sleep()

def resetMisty(arm, hd, rate):
    pos1 = Int32MultiArray()
    pos1.data = [2, 90, 100]
    arm.publish(pos1)
    pos2 = Int32MultiArray()
    pos2.data = [0, 0, 0, 100]
    hd.publish(pos2)
    rate.sleep()

def speak(pub, text):
    pub.publish(text)

def sleep(milliseconds):
    rate = rospy.Rate(1000)
    for i in range(0, milliseconds):
        rate.sleep()

def dance(mvArm, mvHd, drvTrk, stopDrv, spk):
    newRate = rospy.Rate(1)
    pos1 = Int32MultiArray()
    pos1.data = [100, 50, 500]
    drvTrk.publish(pos1)
    pos1.data = [1, 180, 100]
    mvArm.publish(pos1)
    pos1.data = [-5, -3, 0, 100]
    mvHd.publish(pos1)
    newRate.sleep()
    pos1.data = [-100, -50, 500]
    drvTrk.publish(pos1)
    pos1.data = [1, 90, 100]
    mvArm.publish(pos1)
    pos1.data = [0, 0, 0, 100]
    mvHd.publish(pos1)
    newRate.sleep()
    pos1.data = [50, -100, 500]
    drvTrk.publish(pos1)
    pos1.data = [0, 180, 100]
    mvArm.publish(pos1)
    pos1.data = [5, -3, 0, 100]
    mvHd.publish(pos1)
    newRate.sleep()
    pos1.data = [-50, 100, 500]
    drvTrk.publish(pos1)
    pos1.data = [0, 90, 100]
    mvArm.publish(pos1)
    pos1.data = [0, 0, 0, 100]
    mvHd.publish(pos1)
    newRate.sleep()
    stopDrv.publish()

def end(spk, rate):
    speak(spk, "Thank you. Goodbye.")

def send_commands():
    rospy.init_node('demo_misty')
    spk = rospy.Publisher('misty/command/speak', String, queue_size=10)
    drvTrk = rospy.Publisher('misty/command/driveForTime', Int32MultiArray, queue_size=10)
    mvArm = rospy.Publisher('misty/command/moveArm', Int32MultiArray, queue_size=10)
    mvHd = rospy.Publisher('misty/command/moveHead', Int32MultiArray, queue_size=10)
    stopDrv = rospy.Publisher('misty/command/stopDriving', Empty, queue_size=10)
    

    rate = rospy.Rate(1) # 10hz
    rate.sleep()
    resetMisty(mvArm, mvHd, rate)

    wave(mvArm, rate)
    speak(spk, "Hello, what should I do today?")
    sleep(3000)

    r = sr.Recognizer()
    end_flag = False
    while not end_flag:
        print("Say something!")

        # obtain audio from the microphone
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)

        # recognize speech using Sphinx Speech Recognition
        try:
            spoken_string = r.recognize_sphinx(audio).lower()
            print("I heard: " + spoken_string)
            if "wave" in spoken_string:
                wave(mvArm, rate)
            elif "dance" in spoken_string:
                dance(mvArm, mvHd, drvTrk, stopDrv, spk)
                speak(spk, "How was that?")
                sleep(1500)
            elif "thank you" in spoken_string:
                end(spk, rate)
                end_flag = True
                resetMisty(mvArm, mvHd, rate)
            elif "what can you do" in spoken_string:
                speak(spk, "Currently, I am able to wave, and dance. Would you like to see my dance?")
                sleep(6000)
            else:
                speak(spk, "I don't think I understood that. For a list of things I can do, say What can you do?")
                sleep(8000)
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")

if __name__ == '__main__':
    send_commands()
