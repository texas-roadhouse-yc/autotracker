from astral import LocationInfo
from autotracker import ChangingDetectionModel
from deepdiff import DeepDiff
import pandas as pd

print("Loading data...")
sampled_df = pd.read_csv('./data/sampled_dataset.csv')
updated_df = pd.read_csv('./data/updated_sampled_dataset.csv')
deleted_df = pd.read_csv('./data/deleted_sampled_dataset.csv')

print("Rtree building...")
from astral import LocationInfo

num_samples = 1000
positive_samples = num_samples // 2
ordered_traj = [x for x in range(positive_samples)]
negative_traj = [x for x in range(positive_samples, num_samples)]
# ordered_traj = [0]

# Get geographic information for Aalborg
city = LocationInfo("Aalborg", "Denmark", "Europe/Copenhagen", 57.05, 9.93)
radius = 30
view_angle = 78  # in degrees
worthy = (0.68, 0.9)
tolerance = 0.9
traj_times = 3
max_entries = 10

############################################################################################################
sum_trips = 0
num_succ = 0
num_fail = 0

for sample_id in ordered_traj:
    flag = 0
    model = ChangingDetectionModel(city, ordered_traj, radius, view_angle, worthy, tolerance, max_entries=3)
    model.process_trajectory(sampled_df, sample_id, 'normal', True)

    for i in range(traj_times):
        # Add GPS noise
        model.process_trajectory(updated_df, sample_id, 'gps_noise', True)
        sum_trips += 1
        if model.first_rec_flag == 1:
            num_succ += 1
            flag = 1
            break

    for i in range(traj_times, max_entries):
        if model.first_rec_flag == 1:
            break
        model.process_trajectory(updated_df, sample_id, 'gps_noise', True)
        sum_trips += 1


for sample_id in negative_traj:
    flag = 0
    model = ChangingDetectionModel(city, negative_traj, radius, view_angle, worthy, tolerance, max_entries=3)
    model.process_trajectory(sampled_df, sample_id, 'normal', True)
    saved_tree = str(model.rtree.root)

    for i in range(traj_times):
        # Add GPS noise
        model.process_trajectory(sampled_df, sample_id, 'gps_noise', True)

        if saved_tree != str(model.rtree.root):
            num_fail += 1
            break

avg_rank = sum_trips / positive_samples
succ_rate = num_succ / positive_samples * 1.00
fail_rate = num_succ / (num_succ + num_fail)

print("Reporting accuracy:")
print("3-SR:", succ_rate, "3-SP:", fail_rate, "ASU:", avg_rank)
