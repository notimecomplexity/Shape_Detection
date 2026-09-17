"""A timer publishes one video frame at a time as sensor_msgs/Image."""
from pathlib import Path
import math
import cv2
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class VideoPublisher(Node):
    def __init__(self):
        super().__init__('video_publisher')
        self.declare_parameter('video_path', '')
        self.declare_parameter('fps', 0.0)
        self.declare_parameter('loop', False)
        self.declare_parameter('frame_id', 'camera_optical_frame')
        path = str(self.get_parameter('video_path').value)
        if not path or not Path(path).expanduser().is_file():
            raise ValueError('Provide video_path pointing to a video inside Ubuntu.')
        self.cap = cv2.VideoCapture(str(Path(path).expanduser()))
        if not self.cap.isOpened():
            self.cap.release()
            raise RuntimeError(f'Cannot open video: {path}')
        fps = float(self.get_parameter('fps').value)
        if fps == 0.0:
            fps = self.cap.get(cv2.CAP_PROP_FPS)
        if not math.isfinite(fps) or fps <= 0:
            fps = 30.0
        self.bridge = CvBridge()
        self.publisher = self.create_publisher(Image, '/camera/image_raw', qos_profile_sensor_data)
        self.timer = self.create_timer(1.0/fps, self.publish_frame)
        self.get_logger().info(f'Publishing {path} at {fps:.2f} frames/s')

    def publish_frame(self):
        # Do not consume the opening frames before the detector discovers us.
        if self.publisher.get_subscription_count() == 0:
            return
        ok, frame = self.cap.read()
        if not ok and self.get_parameter('loop').value:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = self.cap.read()
        if not ok:
            self.timer.cancel()
            self.cap.release()
            self.get_logger().info('End of video (or read failure). Press Ctrl+C to stop.')
            return
        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.get_parameter('frame_id').value
        self.publisher.publish(msg)

    def destroy_node(self):
        self.cap.release()
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = VideoPublisher()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
