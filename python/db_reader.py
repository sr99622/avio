import cv2
from storage import Detections

class DbReader:

    def __init__(self, arg):
        unpacked_args = arg[0].split(";")
        for line in unpacked_args:
            key_value = line.split("=")
            if key_value[0] == "db_name":
                db_name = key_value[1]

        self.db = Detections(("db_name=" + db_name,))

    def __call__(self, arg):
        img = arg[0][0]
        rts = arg[2][0]

        dets = self.db.get(rts)

        for row in dets:
            track_id = int(row[6])
            x = int(row[0] * img.shape[1])
            y = int(row[1] * img.shape[0])
            w = int(row[2] * img.shape[1])
            h = int(row[3] * img.shape[0])

            cv2.putText(img, str(rts), (40, 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255))

            
            if track_id == -1:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
            else:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), 1)
                cv2.putText(img, str(track_id), (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
            

        return img

