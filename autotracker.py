import math
import numpy as np
from deepdiff import DeepDiff
from astral.sun import sun
from datetime import date, datetime, timedelta
from Rtree import *
from loader import load_data
from mbr import sector_bounding_box_geo
from visibility import is_visible
from confidence import calculate_area_ratios_with_threshold_split

class ChangingDetectionModel:
    def __init__(self, city, ordered_traj, radius=15, view_angle=78, worthy=(0.68, 0.95), tolerance=0.9, max_entries=3):
        self.city = city
        self.ordered_traj = ordered_traj
        self.radius = radius
        self.view_angle = view_angle
        self.worthy = worthy
        self.tolerance = tolerance
        self.rtree = RTree(max_entries=max_entries)
        self.first_rec = None
        self.first_rec_flag = 0

    # GPS noise generation function
    def generate_gps_noise(self):
        """
        Generate GPS noise for latitude and longitude.

        Returns:
            tuple: (lat_noise, lon_noise)
        """
        lat_noise = np.random.normal(0, 0.00000899 / 1.414)
        lon_noise = np.random.normal(0, 0.00001648 / 1.414)
        return lat_noise, lon_noise

    def generate_heading_noise(self):
        """
        Generate heading noise.

        Returns:
            float: heading_noise
        """
        heading_noise = np.random.normal(0, 5)
        return heading_noise

    def generate_timestamp_noise(self):
        """
        Generate timestamp noise.

        Returns:
            float: timestamp_noise
        """
        timestamp_noise = np.random.normal(0, 10000)
        return timestamp_noise

    def filtered_sin_value(self, sunrise: float, sunset: float, current_time: int) -> float:
        """
        Compute sin value based on sunrise and sunset times.
        Only values greater than 0.6 are retained, otherwise return 0.6.

        Parameters:
        - sunrise: float - sunrise time (hour)
        - sunset: float - sunset time (hour)
        - current_time: int - current time in hhmmss format

        Returns:
        - Filtered sin value (float)
        """
        hours = current_time // 10000
        minutes = (current_time // 100) % 100
        seconds = current_time % 100
        current_time_hours = hours + minutes / 60 + seconds / 3600

        if sunrise < current_time_hours < sunset:
            sin_value = np.sin((current_time_hours - sunrise) * np.pi / (sunset - sunrise))
            return sin_value if sin_value > 0.5 else 0.5
        else:
            return 0.5

    def process_trajectory(self, sampled_df, sample_id, test_mode, dynamic_radius=False):
        lng, lat, label, heading, img_width, pix_loc, date, time_stamp = load_data(sample_id, sampled_df)

        today = datetime.strptime(str(date[0]), "%Y%m%d").date()
        s = sun(self.city.observer, date=today)

        sunrise = s['sunrise'].astimezone().hour + s['sunrise'].astimezone().minute / 60
        sunset = s['sunset'].astimezone().hour + s['sunset'].astimezone().minute / 60

        i = 0
        while i < len(lng):
            data = {}
            coor = (lng[i], lat[i])

            if math.isnan(pix_loc[i]):
                vis_direc = float(heading[i])
            else:
                angle_bais = pix_loc[i] / (img_width[i] / 2) * (self.view_angle / 2)
                vis_direc = angle_bais + float(heading[i])

            if label[i] != 'None' and label[i] != 'none':
                data[label[i]] = data.get(label[i], 0) + 1

            while i < len(lng) - 1 and coor == (lng[i + 1], lat[i + 1]):
                i += 1
                if label[i] != 'None' and label[i] != 'none':
                    data[label[i]] = data.get(label[i], 0) + 1

            if test_mode == 'gps_noise':
                lat_noise, lon_noise = self.generate_gps_noise()
                coor = (coor[0] + lon_noise, coor[1] + lat_noise)

            if test_mode == 'heading_noise':
                heading_noise = self.generate_heading_noise()
                vis_direc = vis_direc + heading_noise

            if test_mode == 'timestamp_noise':
                time_stamp_noise = self.generate_timestamp_noise()
                time_stamp[i] = time_stamp[i] + time_stamp_noise

            if dynamic_radius:
                light_factor = self.filtered_sin_value(sunrise, sunset, time_stamp[i])
                now_radius = self.radius * light_factor
            else:
                now_radius = self.radius

            bottom_left, top_right = sector_bounding_box_geo(coor, now_radius, self.view_angle, vis_direc)
            rec = Rectangle(bottom_left[0], bottom_left[1], top_right[0], top_right[1], data, vis_direc, coor)

            results = self.rtree.search(rec)

            # No match found
            if not results:
                if len(data) > 0:
                    if self.first_rec is None:
                        self.first_rec = rec
                    self.rtree.insert(rec, data, vis_direc, coor)
                i += 1
                continue

            # Check visibility
            visible = []
            for rec_ite in range(len(results)):
                if is_visible(rec.heading, results[rec_ite].heading, self.view_angle, self.tolerance):
                    visible.append(rec_ite)

            if not visible:
                if len(data) > 0:
                    self.rtree.insert(rec, data, vis_direc, coor)
                i += 1
                continue

            results = [results[rec_ite] for rec_ite in visible]

            # Value judgment
            exceeding, updating = calculate_area_ratios_with_threshold_split(rec, results, self.worthy)

            # Below minimum threshold
            if not updating and not exceeding:
                if len(data) > 0:
                    self.rtree.insert(rec, data, vis_direc, coor)
                i += 1
                continue

            elif updating and not exceeding:
                for rec_id in updating:
                    target_dat = results[rec_id].data
                    diff = DeepDiff(target_dat, data)
                    if diff:
                        # Inconsistent — needs field inspection
                        continue
                    else:
                        # No update needed
                        continue

            else:
                # Above maximum threshold
                diff = ""
                for rec_id in exceeding:
                    target_data = results[rec_id].data
                    if DeepDiff(target_data, data):
                        diff = DeepDiff(target_data, data)
                        print("On", str(date[0]//10000)+'-'+str(date[0]%10000//100)+'-'+str(date[0]%100), "the changing log is:", diff)
                        # If differences exist, delete the current node
                        self.rtree.delete(results[rec_id])
                        if results[rec_id] == self.first_rec:
                            self.first_rec_flag = 1
                    else:
                        # Same data
                        continue

                # Insert new record if data is not empty
                if diff and len(data) != 0:
                    self.rtree.insert(rec, data, vis_direc, coor)

            i += 1
