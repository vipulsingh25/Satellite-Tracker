import datetime
from sgp4.api import Satrec, jday
from pyproj import Transformer
from concurrent.futures import ThreadPoolExecutor

# Read the TLE data from the file
def read_tle_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return [(lines[i].strip(), lines[i+1].strip(), lines[i+2].strip()) for i in range(0, len(lines), 3)]

# Propagate satellite positions for a given time range
def propagate_satellite(satellite, start_date, end_date, interval_minutes=1):
    sat_name, line1, line2 = satellite
    satellite_obj = Satrec.twoline2rv(line1, line2)
    results = []
    current_date = start_date
    while current_date < end_date:
        jd, fr = jday(current_date.year, current_date.month, current_date.day,
                      current_date.hour, current_date.minute, current_date.second)
        e, r, v = satellite_obj.sgp4(jd, fr)
        if e == 0:
            results.append({
                'time': current_date.isoformat(),
                'satellite': sat_name,
                'Lx': r[0],
                'Ly': r[1],
                'Lz': r[2],
                'Vx': v[0],
                'Vy': v[1],
                'Vz': v[2],
            })
        elif e == 6:
            print(f"Error propagating satellite {sat_name} at {current_date.isoformat()}: Satellite has decayed.")
            break
        else:
            print(f"Error propagating satellite {sat_name} at {current_date.isoformat()}: error code {e}")
            break
        current_date += datetime.timedelta(minutes=interval_minutes)
    return results

# Convert ECEF coordinates to latitude, longitude, and altitude
def ecef2lla(pos_x, pos_y, pos_z):
    transformer = Transformer.from_crs("EPSG:4978", "EPSG:4326")
    lon, lat, alt = transformer.transform(pos_x, pos_y, pos_z)
    return lon, lat, alt

# Checking if a point is within the  user-defined locations

def is_within_bbox(lat, lon, bbox):
    min_lat = min(bbox, key=lambda x: x[0])[0]
    max_lat = max(bbox, key=lambda x: x[0])[0]
    min_lon = min(bbox, key=lambda x: x[1])[1]
    max_lon = max(bbox, key=lambda x: x[1])[1]
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon

# Main function to execute the above steps
def main():
    tle_file_path = '30sats.txt' # or 30000sats.txt
    satellites = read_tle_file(tle_file_path)
    start_date = datetime.datetime(2023, 6, 1, 0, 0, 0)  # Example start date
    end_date = start_date + datetime.timedelta(days=1)  # One day interval

    # Propagate satellite positions in parallel
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(propagate_satellite, sat, start_date, end_date) for sat in satellites]
        results = [future.result() for future in futures]

    # Flatten the list of results
    results = [item for sublist in results for item in sublist]

    # Convert ECEF to LLA for each satellite
    for result in results:
        lon, lat, alt = ecef2lla(result['Lx'], result['Ly'], result['Lz'])
        result['longitude'] = lon
        result['latitude'] = lat
        result['altitude'] = alt

    # Ask user for location coordinates
    bbox = [
        (16.66673, 103.58196),
        (69.74973, -120.64459),
        (-21.09096, -119.71009),
        (-31.32309, -147.79778)
    ]

    # Filter results to include only those within the location coordinates
    filtered_results = [result for result in results if is_within_bbox(result['latitude'], result['longitude'], bbox)]

    # Print filtered results in the required format
    for result in filtered_results:
        print(f"{result['time']}, {result['satellite']}, {result['longitude']}, {result['latitude']}, {result['altitude']}")

if __name__ == "__main__":
    main()

