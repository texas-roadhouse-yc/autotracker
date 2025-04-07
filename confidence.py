# Example input
# target_rectangle = Rectangle(0, 0, 4, 4)
# rectangle_list = [
#     Rectangle(1, 1, 3, 3),
#     Rectangle(0, 0, 2, 2),
#     Rectangle(3, 3, 5, 5),
#     Rectangle(0, 0, 5, 5)
# ]

# Test with a threshold of 0.3
# exceeding, non_exceeding = calculate_area_ratios_with_threshold_split(target_rectangle, rectangle_list, worthy=0.3)
# exceeding, non_exceeding


def calculate_area_ratios_with_threshold_split(target_rect, rect_list, worthy=(0.5, 0.8)):
    """
    Calculate the area ratios of a target rectangle with a list of Rectangle objects.
    Split the results into two lists: indices exceeding the threshold and those not exceeding it.

    Args:
    - target_rect: Rectangle object representing the target rectangle with latitude and longitude coordinates.
    - rect_list: list of Rectangle objects with latitude and longitude coordinates.
    - worthy: tuple, the threshold ratio; the first is the minimum ratio, the second is the maximum ratio.

    Returns:
    - Tuple of three lists:
      - First list contains indices where the area ratio exceeds the threshold.
      - Second list contains indices where the area ratio is between the thresholds.
      - Third list contains indices where the area ratio does not exceed the thresholds.
    """
    # Conversion factors
    lat_conversion = 8.98311174991017e-06  # Latitude change per meter
    lon_conversion = 1.6493697976793597e-05  # Longitude change per meter

    def area(rect):
        """
        Calculate the area of a rectangle in square meters.
        """
        width = max(0, (rect.x_max - rect.x_min) / lon_conversion)
        height = max(0, (rect.y_max - rect.y_min) / lat_conversion)
        return width * height

    target_area = area(target_rect)
    exceeding_indices = []
    updating_cand = []
    non_exceeding_indices = []

    for i, rect in enumerate(rect_list):
        # Calculate intersection coordinates
        intersect_x_min = max(target_rect.x_min, rect.x_min)
        intersect_y_min = max(target_rect.y_min, rect.y_min)
        intersect_x_max = min(target_rect.x_max, rect.x_max)
        intersect_y_max = min(target_rect.y_max, rect.y_max)

        # Calculate intersection area in square meters
        intersect_width = max(0, (intersect_x_max - intersect_x_min) / lon_conversion)
        intersect_height = max(0, (intersect_y_max - intersect_y_min) / lat_conversion)
        intersect_area = intersect_width * intersect_height

        # Calculate area ratio
        ratio = intersect_area / target_area if target_area > 0 else 0

        # Categorize based on the ratio
        if ratio > worthy[1]:
            exceeding_indices.append(i)
        elif worthy[0] < ratio <= worthy[1]:
            updating_cand.append(i)
        else:
            non_exceeding_indices.append(i)

    return exceeding_indices, updating_cand  # , non_exceeding_indices
