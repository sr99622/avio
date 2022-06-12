import sqlite3
import argparse
import cv2

class Detections:
    def table_exists(self):
        self.c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' \
                        AND name='detections'")
        if self.c.fetchone()[0]==1:
            result = True
        else:
            result = False
        return result

    def create_table(self):
        self.c.execute("CREATE TABLE detections (frame_id int, track_id int, obj_id int, \
                        x real, y real, w real, h real, prob real)")
        print("table created")
        self.c.execute("CREATE INDEX idx_frame_id ON detections(frame_id)")
        print("table indexed")

    def drop_table(self):
        self.c.execute("DROP TABLE detections")
        print("table dropped")

    def get(self, frame_id):
        self.c.execute("SELECT x, y, w, h, prob, obj_id, track_id, frame_id FROM detections WHERE frame_id=?", (frame_id,))
        return self.c.fetchall()

    def count(self, frames):
        if not frames:
            self.c.execute("SELECT COUNT(frame_id) FROM detections")
        else:
            self.c.execute("SELECT COUNT(DISTINCT frame_id) FROM detections")
        row = self.c.fetchone()
        return row[0]

    def index(self):
        self.c.execute("CREATE INDEX idx_frame_id ON detections(frame_id)")

    def put(self, arg):
        for row in arg:
            x = float(row[0])
            y = float(row[1])
            w = float(row[2])
            h = float(row[3])
            p = float(row[4])
            o = int(row[5])
            t = int(row[6])
            f = int(row[7])

            self.c.execute("INSERT INTO detections(frame_id, track_id, obj_id, x, y, w, h, prob) \
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (f, t, o, x, y, w, h, p))
        self.conn.commit()

    def connect(self, db_name):
        print("connecting to database:", db_name)
        self.conn = sqlite3.connect(db_name)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        if self.table_exists():
            print("detections table exists")
        else:
            print("detections table does not exist")
            self.create_table()
            print("detections table created")
        print("Database initialized")

    def __init__(self, arg):
        db_name = ""
        self.show_detections = False
        unpacked_args = arg[0].split(";")
        for line in unpacked_args:
            key_value = line.split("=")
            if key_value[0] == "db_name":
                db_name = key_value[1]

        self.connect(db_name)

