import cv2
import numpy as np

def overlap(box, online_targets):
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    sum_overlap = 0.0

    for t in online_targets:

        x1, y1, w, h = t.tlwh.astype(int)
        x2 = x1 + w
        y2 = y1 + h

        overlap_area = 0.0

        if x1 > box[0] and y1 > box[1] and x1 < box[2] and y1 < box[3]:
            overlap_area = (box[2] - x1) * (box[3] - y1)
        
        if box[0] > x1 and box[1] > y1 and box[0] < x2 and box[1] < y2:
            overlap_area = (x2 - box[0]) * (y2 - box[1])

        sum_overlap += overlap_area

    return sum_overlap / box_area

class Worker():
    def __init__(self, arg):
        print("Worker.init", arg) 
        self.frame_id = 0
        self.last_ids = []
        self.desired_width = 256
        self.desired_height = 512

    def __call__(self, arg):
        print("Worker.call", len(arg[0]))
        img = arg[0][0][0]
        online_targets = arg[1]

        return self.draw_boxes(img, online_targets)

    def draw_boxes(self, orig_img, online_targets):
        img = np.ascontiguousarray(np.copy(orig_img))
        self.frame_id += 1
        frame_id_text = '{}'.format(int(self.frame_id)).zfill(5)
        linesize = 2

        for t in online_targets:
            tlwh = t.tlwh
            track_id = int(t.track_id)
            id_text = '{}'.format(int(track_id)).zfill(5)
            color = ((37 * track_id) % 255, (17 * track_id) % 255, (29 * track_id) % 255)

            x, y, w, h = tlwh
            box = tuple(map(int, (x, y, x + w, y + h)))
            x1, y1, x2, y2 = box
            y1 = max(y1, 0)
            x1 = max(x1, 0)
            y2 = min(y2, img.shape[0])
            x2 = min(x2, img.shape[1])
            w = x2 - x1
            h = y2 - y1


            if self.frame_id % 10 == 0:

                if h > 512 and h / w > 2.0:
                    filename = "C:/Users/stephen/Pictures/flatiron/" + frame_id_text + "_" + id_text + ".jpg"

                    if overlap((x1, y1, x2, y2), online_targets) < 0.6:
                        
                        #adjust box boundaries to fill the resolution normalized rectangle
                        projected_height = int(h * 1.1)
                        delta_y = projected_height - h
                        y1 = y1 - int(delta_y / 2)
                        y2 = y2 + int(delta_y / 2)

                        projected_width = projected_height / 2
                        delta_x = projected_width - w
                        x1 = x1 - int(delta_x / 2)
                        x2 = x2 + int(delta_x / 2)

                        if x1 > 0 and x2 < img.shape[1] and y1 > 0 and y2 < img.shape[0]:

                            dh = self.desired_height
                            dw = self.desired_width

                            scale = dh / h
                            w = int(w * scale)

                            blank = np.zeros((dh, dw, 3), dtype=np.uint8)
                            crop = orig_img[y1:y2, x1:x2]

                            resized = cv2.resize(crop, (dw, dh), interpolation=cv2.INTER_AREA)
                            #blank[:dh, w_diff:w+w_diff, :] = resized
                            blank[:dh, :dw, :] = resized
        
                            linesize = 4

                            if not track_id in self.last_ids:
                                self.last_ids.append(track_id)
                                print("wrote to file", filename)
                                color = (255, 255, 255)
                                cv2.imwrite(filename, blank)
                            else:
                                print("rejected for duplicate", filename)
                                color = (0, 0, 255)
                                self.last_ids.remove(track_id)


                        else:
                            color = (0, 255, 0)
                            print("rejected for overlap", filename)


            cv2.rectangle(img, box[0:2], box[2:4], color, linesize)
            cv2.putText(img, id_text, (box[0], box[1]), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        return cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_AREA)