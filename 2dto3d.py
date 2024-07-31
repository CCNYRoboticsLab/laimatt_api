


shot = rec.shots[image]
pt2D = shot.project(pt3D)
pt2D_px = cam.normalized_to_pixel_coordinates(pt2D)
nube = o3d.io.read_point_cloud('./opensfm/undistorted/openmvs/scene_dense_dense_filtered.ply')
data = dataset.DataSet('./opensfm')
rec = data.load_reconstruction()[0]
shot = rec.shots[image]
pose = shot.pose
cam = shot.camera
pt2D = cam.pixel_to_normalized_coordinates(pt2D_px)
bearing = cam.pixel_bearing(pt2D)
t3D_world = pose.inverse().transform(bearing)
p1 = shot.pose.get_origin()
p2 = cam.pixel_to_normalized_coordinates([x, y])
bearing = cam.pixel_bearing(p2)
scale = 1 / bearing[2]
bearing = scale * bearing
p2 = pose.inverse().transform(bearing)
points = np.asarray(nube.points) #point cloud
res = np.linalg.norm(np.cross(p2-p1, p1-points), axis=1)/np.linalg.norm(p2-p1)

