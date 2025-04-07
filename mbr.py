import math
import matplotlib.pyplot as plt

def sector_bounding_box_geo(center, radius, view_angle, direction_angle):
    """
    Calculate the bounding box of a sector with geographic scaling.

    Parameters:
    - center: tuple (lon, lat), the center of the circle.
    - radius: float, the radius in meters.
    - view_angle: float, the angular range of the sector in degrees.
    - direction_angle: float, the direction of the sector centerline in degrees.

    Returns:
    - A tuple of two points: (bottom_left, top_right), each as (lon, lat).
    """
    cx, cy = center

    # Conversion factors for geographic coordinates (specific to Aalborg)
    lat_conversion = 8.98311174991017e-06  # Latitude change per meter
    lon_conversion = 1.6493697976793597e-05  # Longitude change per meter

    # Convert radius to geographic distance
    radius_lat = radius * lat_conversion
    radius_lon = radius * lon_conversion

    half_angle = view_angle / 2

    # Calculate angles of the sector edges in radians
    start_angle = math.radians(90 - direction_angle - half_angle)
    end_angle = math.radians(90 - direction_angle + half_angle)

    # Include the center and two boundary points on the arc
    points = [
        (cx, cy),  # center
        (cx + radius_lon * math.cos(start_angle), cy + radius_lat * math.sin(start_angle)),  # start edge
        (cx + radius_lon * math.cos(end_angle), cy + radius_lat * math.sin(end_angle)),  # end edge
    ]

    # Compute the bounding box of these points
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    bottom_left = (min(xs), min(ys))
    top_right = (max(xs), max(ys))

    return bottom_left, top_right
