import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# At Aalborg
# lat 0.00004491 = 5m
# lng 0.00007936 = 5m

def load_data(sample_id, dataset):
    # Generate coordinate sequence
    dataset = dataset[(dataset['sample_id'] == sample_id)].reset_index(drop=True)
    coordinate_sequence = [(row['raw_lng'], row['raw_lat'], row['etl_cls'], row['heading'], row['img_width'], row['x'], row['date_no'], row['time_no']) for _, row in dataset.iterrows()][:]

    # Extract longitude and latitude
    lng, lat, label, heading, img_width, x, date, time = zip(*coordinate_sequence)

    # Use pandas to handle NaNs and replace them with 'None'
    label_series = pd.Series(label)
    label_series = label_series.fillna('None')
    # Convert the processed result back to a tuple
    label = tuple(label_series)

    # Calculate the picture location (x - image_width / 2)
    pic_loc = tuple(np.subtract(np.array(x), np.array(img_width)/2))

    return lng, lat, label, heading, img_width, pic_loc, date, list(time)
