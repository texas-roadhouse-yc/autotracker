def is_visible(direction1, direction2, wide_angle, tolerance):
    # Calculate the angle between the two directions
    angle_difference = abs(direction1 - direction2)
    angle_difference = min(angle_difference, 360 - angle_difference)

    # Check whether it is smaller than half of the wide angle
    return angle_difference < (wide_angle / 2) * tolerance
