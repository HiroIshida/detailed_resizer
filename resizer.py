#!/usr/bin/env python3
import dataclasses
import rospy
from sensor_msgs.msg import Image

from cv_bridge import CvBridge
import cv2

@dataclasses.dataclass
class Resizer:
    x_min: int
    x_max: int
    y_min: int
    y_max: int
    x_res: int
    y_res: int

    def __call__(self, img):
        img_resized = img[self.x_min:self.x_max, self.y_min:self.y_max]
        img_rescaled = cv2.resize(img_resized, (self.x_res, self.y_res), interpolation=cv2.INTER_CUBIC)
        # https://pythonexamples.org/python-opencv-cv2-resize-image/
        return img_rescaled

    @classmethod
    def from_rosparam(cls):
        return cls(
                rospy.get_param('~x_min', 150),
                rospy.get_param('~x_max', 400),
                rospy.get_param('~y_min', 100),
                rospy.get_param('~y_max', 600),
                rospy.get_param('~x_res', 224),
                rospy.get_param('~y_res', 224))

class ResizerNode:
    def __init__(self, resizer: Resizer):
        self.resizer = resizer
        self.publisher = rospy.Publisher('~out', Image, queue_size=1)
        self.subscriber = rospy.Subscriber('~inp', Image, queue_size=100, callback=self.callback)

    def callback(self, img_msg: Image):
        bridge = CvBridge()
        img = bridge.imgmsg_to_cv2(img_msg, desired_encoding='passthrough')
        img_resized = self.resizer(img)
        img_resized_msg = bridge.cv2_to_imgmsg(img_resized, encoding='bgr8')
        img_resized_msg.header = img_msg.header
        self.publisher.publish(img_resized_msg)

if __name__=='__main__':
    rospy.init_node('resizer_node')
    resizer = Resizer.from_rosparam()
    node = ResizerNode(resizer)
    rospy.spin()
