import cv2
import storage
import numpy as np

class Darknet:
	def __init__(self, arg):
		print("Darknet.__init__")

		cfg = "yolov4.cfg"
		weights = "yolov4.weights"
		db_name = ""
		self.has_db = False

		unpacked_args = arg[0].split(";")
		for line in unpacked_args:
			key_value = line.split("=")
			if key_value[0] == "cfg":
				cfg = key_value[1]
			if key_value[0] == "weights":
				weights = key_value[1]
			if key_value[0] == "db_name":
				db_name = key_value[1]
		print("cfg:", cfg, "\nweights:", weights, "\ndb_name:", db_name)

		net = cv2.dnn.readNet(weights, cfg)
		net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
		net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
		self.model = cv2.dnn_DetectionModel(net)
		self.model.setInputParams(size=(1280, 1280), scale=1/255)

		if len(db_name) > 0:
			self.db = storage.Detections(("db_name=" + db_name,))
			self.has_db = True

		print("initialized")

	def __call__(self, arg):

		img = arg[0][0]
		dpn = arg[2][0]

		classIds, scores, boxes = self.model.detect(img, confThreshold=0.2, nmsThreshold=0.4)

		frame_ids = np.full((classIds.shape[0],), dpn)
		track_ids = np.full((classIds.shape[0],), -1)

		# dimensions are normalized to accomodate rescaling the original image in later stages
		fboxes = boxes.astype(float)
		fboxes[:,(0, 2)] /= img.shape[1]
		fboxes[:,(1, 3)] /= img.shape[0]

		if scores.ndim > 1:
			scores = np.squeeze(scores)
		if classIds.ndim > 1:
			classIds = np.squeeze(classIds)

		arr = np.vstack((scores, classIds, track_ids, frame_ids))
		detections = np.hstack((fboxes, np.transpose(arr)))

		# detections are filtered for people with proper aspect ratio to reduce false positives
		for i in range(detections.shape[0]-1, 0, -1):
			det = detections[i]
			if det[5] != 0:
				detections = np.delete(detections, (i), axis=0)
			else:
				aspect = (det[3] * img.shape[0]) / (det[2] * img.shape[1])
				if aspect < 1 or aspect > 4:
					detections = np.delete(detections, (i), axis=0)

		for det in detections:
			p1 = (int(det[0] * img.shape[1]), int(det[1] * img.shape[0]))
			p2 = (int((det[0] + det[2]) * img.shape[1]), int((det[1] + det[3]) * img.shape[0]))
			cv2.rectangle(img, p1, p2, (255, 255, 255), 1)

		if self.has_db:
			self.db.put(detections)

		return img

