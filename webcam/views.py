from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.http.response import StreamingHttpResponse

import cv2
import numpy as np
import datetime
import time

import core.utils as utils
import tensorflow as tf
from PIL import Image

# HOME PAGE -------------------------
def index(request):
	template = loader.get_template('index.html')
	return HttpResponse(template.render({}, request))
# -----------------------------------

# CAMERA 1 PAGE ---------------------
def camera_1(request):
	template = loader.get_template('camera1.html')
	return HttpResponse(template.render({}, request))
# -----------------------------------

# CAMERA 1 PAGE ---------------------
def camera_2(request):
	template = loader.get_template('camera2.html')
	return HttpResponse(template.render({}, request))
# -----------------------------------

# DISPLAY CAMERA 1 ------------------
def stream_1():

	cam_id = 0
	vid = cv2.VideoCapture(cam_id)

	while True:
		frame, class_count = detection(vid)

		frame = cv2.resize(frame, (1000, 700))

		print("\nObjects in frame:")
		row = 0
		for k in range(len(class_count)):
			if class_count[k] > 0: 
				row += 1
				infor = str(obj_classes[k]) + ": " + str(int(class_count[k]))
				print("  " + infor)
				frame = cv2.putText(frame,infor,(20,(row+1)*35), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)

		cv2.imwrite('demo.jpg', frame)
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + open('demo.jpg', 'rb').read() + b'\r\n')

def video_feed_1(request):
	return StreamingHttpResponse(stream_1(), content_type='multipart/x-mixed-replace; boundary=frame')
# -----------------------------------


# DISPLAY CAMERA 2 ------------------
def stream_2():
	
	cam_id = 2
	vid = cv2.VideoCapture(cam_id)

	while True:
		frame, class_count = detection(vid)

		frame = cv2.resize(frame, (1000, 700))

		print("\nObjects in frame:")
		row = 0
		for k in range(len(class_count)):
			if class_count[k] > 0: 
				row += 1
				infor = str(obj_classes[k]) + ": " + str(int(class_count[k]))
				print("  " + infor)
				frame = cv2.putText(frame,infor,(20,(row+1)*35), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)
		
		cv2.imwrite('demo.jpg', frame)
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + open('demo.jpg', 'rb').read() + b'\r\n')

def video_feed_2(request):
	return StreamingHttpResponse(stream_2(), content_type='multipart/x-mixed-replace; boundary=frame')
# -----------------------------------

# PARAMETERS FOR YOLO----------------
obj_classes = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed", "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]

return_elements = ["input/input_data:0", "pred_sbbox/concat_2:0", "pred_mbbox/concat_2:0", "pred_lbbox/concat_2:0"]
pb_file         = "./yolov3_coco.pb"
num_classes     = 80
input_size      = 416
graph           = tf.Graph()
return_tensors  = utils.read_pb_return_tensors(graph, pb_file, return_elements)
# -----------------------------------

# YOLO DETECTION --------------------
def detection(vid):
	with tf.Session(graph=graph) as sess:

		return_value, frame = vid.read()
		if return_value:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			image = Image.fromarray(frame)
		else:
			raise ValueError("No image!")


		frame_size = frame.shape[:2]
		image_data = utils.image_preporcess(np.copy(frame), [input_size, input_size])
		image_data = image_data[np.newaxis, ...]
		prev_time = time.time()

		pred_sbbox, pred_mbbox, pred_lbbox = sess.run(
			[return_tensors[1], return_tensors[2], return_tensors[3]],
					feed_dict={ return_tensors[0]: image_data})

		pred_bbox = np.concatenate([np.reshape(pred_sbbox, (-1, 5 + num_classes)),
									np.reshape(pred_mbbox, (-1, 5 + num_classes)),
									np.reshape(pred_lbbox, (-1, 5 + num_classes))], axis=0)

		bboxes = utils.postprocess_boxes(pred_bbox, frame_size, input_size, 0.3)
		bboxes = utils.nms(bboxes, 0.45, method='nms')
		image, detected = utils.draw_bbox(frame, bboxes)


		detected = np.asarray(detected)

		# print("------- frame i ---------")

		class_count = []

		for i in range(len(obj_classes)):   # 80
			obj_count = 0
			for j in range(len(detected)):
				if int(detected[j][5]) == i: obj_count += 1

			class_count = np.append(class_count, obj_count)

		curr_time = time.time()
		exec_time = curr_time - prev_time
		result = np.asarray(image)
		info = "time: %.2f ms" %(1000*exec_time)
		# cv2.namedWindow("result", cv2.WINDOW_AUTOSIZE)
		result = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
		
	return result, class_count
# -----------------------------------

