# Satellite Tracker

Satellite Tracker is a Python script that propagates satellite positions using Two-Line Element Sets (TLEs) and computes their locations in terms of latitude, longitude, and altitude. It filters the results to include only satellites within a specified user-defined loaction and outputs the data in a specified format.

## Dependencies Used:

1. sgp4
2. pyproj
3. dask

## Usage

1. Place TLE Data File: Place your TLE data file in the same directory as the script. By default, the script expects a file named '30sats.txt' or '30000sats.txt'.

2. Run the Script:

    python satellite_tracker.py

3. Input User-defined Coordinates: Follow the prompts to input the User-defined coordinates when prompted.

4. View Results: Once the script completes execution, you will see the filtered results printed in the specified format.

## Configuration

1. Modify the tle_file_path variable in the script to specify the path to your TLE data file if it's different from the default (30sats.txt or 30000sats.txt).
2. Adjust the bbox variable to define the bounding box coordinates as per your requirements.
