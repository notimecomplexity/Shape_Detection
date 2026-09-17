"""Subscribe to images; publish typed detections and an annotated image."""
import math
import cv2
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point, Point32
from cv_bridge import CvBridge, CvBridgeError
from pennair_interfaces.msg import ShapeDetection, ShapeDetectionArray
from .detection import analyze_frame


class ShapeDetector(Node):
    def __init__(self):
        super().__init__('shape_detector')
        for name, default in [('fx',2564.3186869), ('fy',2569.70273111),
                              ('cx',0.0), ('cy',0.0),
                              ('depth_in',239.25346088310212), ('show_debug',False)]:
            self.declare_parameter(name, default)
        self.calibration = [float(self.get_parameter(k).value)
                            for k in ('fx','fy','cx','cy','depth_in')]
        if not all(math.isfinite(x) for x in self.calibration) or any(
                self.calibration[i] <= 0 for i in (0,1,4)):
            raise ValueError('Calibration must be finite; fx, fy and depth_in must be positive.')
        self.show_debug = self.get_parameter('show_debug').value
        self.bridge = CvBridge()
        self.detections_pub = self.create_publisher(ShapeDetectionArray, '/shapes/detections', 10)
        self.image_pub = self.create_publisher(Image, '/shapes/annotated', qos_profile_sensor_data)
        self.subscription = self.create_subscription(
            Image, '/camera/image_raw', self.on_image, qos_profile_sensor_data)

    def on_image(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except CvBridgeError as exc:
            self.get_logger().error(f'Image conversion failed: {exc}')
            return
        detections, annotated = analyze_frame(frame, *self.calibration)
        result = ShapeDetectionArray()
        result.header = msg.header
        for i, data in enumerate(detections):
            detection = ShapeDetection()
            detection.detection_id = i
            x,y,z = data['center']
            detection.center = Point(x=float(x), y=float(y), z=float(z))
            u,v = data['centroid_px']
            detection.centroid_px = Point32(x=float(u),y=float(v),z=0.0)
            detection.outline_px.points = [Point32(x=float(u),y=float(v),z=0.0)
                                           for u,v in data['outline_px']]
            detection.area_px2 = float(data['area_px2'])
            result.detections.append(detection)
        # Publish even an empty array so consumers know there were no detections.
        self.detections_pub.publish(result)
        image = self.bridge.cv2_to_imgmsg(annotated, encoding='bgr8')
        image.header = msg.header
        self.image_pub.publish(image)
        if self.show_debug:
            cv2.imshow('PennAIR ROS 2', annotated)
            cv2.waitKey(1)

    def destroy_node(self):
        if self.show_debug:
            cv2.destroyAllWindows()
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = ShapeDetector()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
