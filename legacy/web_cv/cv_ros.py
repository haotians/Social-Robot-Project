#!/usr/bin/env python
import roslib
roslib.load_manifest('cv_detect_ros')
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class image_converter:

  def __init__(self):
    self.image_pub = rospy.Publisher("image_topic_2",Image,queue_size=10)
    self.video_capture = cv2.VideoCapture(0)
    cv2.namedWindow("Image window", 1)
    self.bridge = CvBridge()
    # self.image_sub = rospy.Subscriber("image_topic",Image,self.callback)


def talker():
    ic = image_converter()
    rospy.init_node('image_converter', anonymous=True)
    rate = rospy.Rate(10) # 10hz

    # face_casc_path ="/usr/local/share/OpenCV/haarcascades/haarcascadesscade_frontalface_default.xml"
    face_casc_path = "/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml"

    face_cascade = cv2.CascadeClassifier(face_casc_path)

    while not rospy.is_shutdown():
        try:
            ret, cv_image = ic.video_capture.read()
        except CvBridgeError, e:
            print e

        gray=cv2.cvtColor(cv_image,cv2.COLOR_BGR2GRAY)

        faces=face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(30,30),
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                )

        for (x, y, w, h) in faces:
            cv2.rectangle(cv_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.imshow("Image window", cv_image)
        cv2.waitKey(3)

        ic.image_pub.publish(ic.bridge.cv2_to_imgmsg(cv_image, "bgr8"))

        rate.sleep()


if __name__ == '__main__':
    # main(sys.argv)
    talker()
