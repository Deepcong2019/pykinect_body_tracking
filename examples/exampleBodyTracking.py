import math

import cv2

import pykinect_azure as pykinect

if __name__ == "__main__":

	# Initialize the library, if the library is not found, add the library path as argument
	pykinect.initialize_libraries(track_body=True)

	# Modify camera configuration
	device_config = pykinect.default_configuration
	device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_OFF
	device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED
	#print(device_config)

	# Start device
	device = pykinect.start_device(config=device_config)

	# Start body tracker
	tracker_config = pykinect.default_tracker_configuration
	tracker_config.sensor_orientation = pykinect.K4ABT_SENSOR_ORIENTATION_DEFAULT
	tracker_config.tracker_processing_mode = pykinect.K4ABT_TRACKER_PROCESSING_MODE_GPU
	tracker_config.gpu_device_id = 0
	bodyTracker = pykinect.start_body_tracker(tracker_configuration=tracker_config)

	cv2.namedWindow('Depth image with skeleton',cv2.WINDOW_NORMAL)
	while True:

		# Get capture
		capture = device.update()

		# Get body tracker frame
		body_frame = bodyTracker.update()

		# Get the color depth image from the capture
		ret_depth, depth_color_image = capture.get_colored_depth_image()

		# Get the colored body segmentation
		ret_color, body_image_color = body_frame.get_segmentation_image()

		if not ret_depth or not ret_color:
			continue
			
		# Combine both images
		combined_image = cv2.addWeighted(depth_color_image, 0.6, body_image_color, 0.4, 0)

		# Draw the skeletons
		combined_image = body_frame.draw_bodies(combined_image)
		num_bodies = body_frame.get_num_bodies()
		print("画面中的人数:", num_bodies)
		# 打印关节点信息
		for i in range(num_bodies):
			sk = body_frame.get_body_skeleton(i)
			for i in range(32):
				origin_point = (0, 0, 0)
				position = sk.joints[i].position
				point_i = (position.v[0], position.v[1], position.v[2])
				# 计算欧几里得距离
				distance = math.sqrt((point_i[0] - origin_point[0]) ** 2 + (point_i[1] - origin_point[1]) ** 2 + (point_i[2] - origin_point[2]) ** 2)

				print("Distance between points:", distance)
				orientation = sk.joints[i].orientation
				confidence_level = sk.joints[i].confidence_level
				print(
					"Joint[{}]: Position[mm] ( {}, {}, {} ); Orientation ( {}, {}, {}, {}); Confidence Level ({})".format(
						i, position.v[0], position.v[1], position.v[2], orientation.v[0], orientation.v[1],
						orientation.v[2], orientation.v[3], confidence_level
					))
			print("\n")



		# print_body_information(body)

		# Overlay body segmentation on depth image
		cv2.imshow('Depth image with skeleton', combined_image)

		# Press q key to stop
		if cv2.waitKey(1) == ord('q'):  
			break