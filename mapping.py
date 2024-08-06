import numpy as np
from opensfm import dataset
import open3d as o3d
from PIL import Image
import os
import csv
import subprocess
import time

def find_blue_pixels(image_path):
    # Open the image file
    image = Image.open(image_path)
    
    # Convert image to RGB mode if not already in that mode
    image = image.convert('RGB')
    
    # Get image dimensions
    width, height = image.size
    
    # Initialize list to store coordinates of blue pixels
    blue_pixels = []
    
    # Loop through all pixels in the image
    # for y in range(0, height, 10):
    #     for x in range(0, width, 10):
    for y in range(height):
        for x in range(width):
            # Get the RGB value of the pixel
            r, g, b = image.getpixel((x, y))
            # print(f"added {x} and {y}")
            
            # blue_pixels.append([x * 4, y * 4])
            # Check if the pixel is blue
            if r < 10 and g < 10 and b > 240:
                # Append the coordinate to the list
                blue_pixels.append([x * 4, y * 4])
    
    return blue_pixels

def find_point(nube, rec, shotname, pixel):
    shot = rec.shots[shotname]
    pose = shot.pose
    cam = shot.camera

    p1 = shot.pose.get_origin()
    p2 = cam.pixel_to_normalized_coordinates(pixel)
    bearing = cam.pixel_bearing(p2)
    scale = 1 / bearing[2]
    bearing = scale * bearing
    p2 = pose.inverse().transform(bearing)
    points = np.asarray(nube.points) #point cloud
    
    res = np.linalg.norm(np.cross(p2-p1, p1-points), axis=1)/np.linalg.norm(p2-p1)
    point = nube.points[np.argmin(res)] + np.array([572273, 4498560, 0])
    
    
    # point = closest_point_to_line_segment(p1, p2, points) + np.array([572273, 4498560, 0])

    return point

def closest_point_to_line_segment(p1, p2, points):
    # Convert points to a numpy array if it isn't already
    points = np.asarray(points)
    
    # Compute vectors
    p1_to_p2 = p2 - p1
    p1_to_points = points - p1
    
    # Compute cross product
    cross_product = np.cross(p1_to_p2, p1_to_points)
    
    # Compute the norm of the cross product and the vector p1 to p2
    norm_cross_product = np.linalg.norm(cross_product, axis=1)
    norm_p1_to_p2 = np.linalg.norm(p1_to_p2)
    
    # Calculate distances
    distances = norm_cross_product / norm_p1_to_p2
    
    # Find the index of the minimum distance
    closest_index = np.argmin(distances)
    
    # Return the closest point
    return points[closest_index]

def create_maps(map_path):
    nube = o3d.io.read_point_cloud('/code/NodeODM/data/9965ad3a-131d-4bdf-80c1-d3962086f787_copy/opensfm/undistorted/openmvs/scene_dense_dense_filtered.ply')
    data = dataset.DataSet('/code/NodeODM/data/9965ad3a-131d-4bdf-80c1-d3962086f787_copy/opensfm')
    rec = data.load_reconstruction()[0]

    csv_path_all = os.path.join(map_path, 'map_data_all.csv')
    csvoutput_all = open(csv_path_all, 'w', newline='')
    writer_all = csv.writer(csvoutput_all)
    writer_all.writerow(['X', 'Y', 'Z', 'Red', 'Green', 'Blue'])
    point_set_all = set()

    for shot in rec.shots:
        csv_path = os.path.join(map_path, f'map_data_{shot}.csv')
        with open(csv_path, 'w', newline='') as csvoutput:
            writer = csv.writer(csvoutput)
            writer.writerow(['X', 'Y', 'Z', 'Red', 'Green', 'Blue'])

            tif = f"/code/NodeODM/data/9965ad3a-131d-4bdf-80c1-d3962086f787_copy/opensfm/undistorted/images/{shot}.tif"
            blue = find_blue_pixels(tif)
            point_set = set()
            for index, pixel in enumerate(blue):
                point = find_point(nube, rec, shot, pixel)
                if (point[0], point[1], point[2]) not in point_set:
                    point_set.add((point[0], point[1], point[2]))
                    writer.writerow([point[0], point[1], point[2], 255.0, 0.0, 0.0])
                    print(f"added {index} of {len(blue)}")
                    
                if (point[0], point[1], point[2]) not in point_set_all:
                    point_set_all.add((point[0], point[1], point[2]))
                    writer_all.writerow([point[0], point[1], point[2], 255.0, 0.0, 0.0])
                    print("added to all")

        command = [
            "pdal",
            "translate",
            csv_path,
            f"/code/NodeODM/data/9965ad3a-131d-4bdf-80c1-d3962086f787_copy/mapping/ptc_{shot}.laz"
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

    csvoutput_all.close()
    command = [
        "pdal",
        "translate",
        "/code/NodeODM/data/9965ad3a-131d-4bdf-80c1-d3962086f787_copy/mapping/map_data_all.csv",
        "/code/NodeODM/data/9965ad3a-131d-4bdf-80c1-d3962086f787_copy/mapping/ptc_all.laz"
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
        

start_time = time.time()

map_path = '/code/NodeODM/data/9965ad3a-131d-4bdf-80c1-d3962086f787_copy/mapping'
if not os.path.exists(map_path):
    os.makedirs(map_path)
    

create_maps(map_path)
# blue = find_blue_pixels('/code/NodeODM/data/NodeODM/data/9965ad3a-131d-4bdf-80c1-d3962086f787_copy/images/S1074591.JPG')

end_time = time.time()


duration = end_time - start_time
print(f"Execution time: {duration} seconds")