# Index within this frame only; not a persistent tracking ID.
uint32 detection_id
# Camera optical coordinates in meters: x right, y down, z forward.
geometry_msgs/Point center
# Pixel coordinates; z is always zero.
geometry_msgs/Point32 centroid_px
geometry_msgs/Polygon outline_px
float64 area_px2
