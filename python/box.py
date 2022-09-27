class Box:
    def __init__(self, dims, flag):

        flags = ("xyxy", "tlwh", "shape")
        if flag not in flags:
            raise Exception("invalid flag, allowable values are", flags)

        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.w = 0
        self.h = 0

        if flag == "xyxy":
            self.x1, self.y1, self.x2, self.y2 = tuple(map(int, dims))
            self.w = self.x2 - self.x1
            self.h = self.y2 - self.y1

        if flag == "tlwh":
            self.x1, self.y1, self.w, self.h = map(int, dims)
            self.x2 = int(self.x1 + self.w)
            self.y2 = int(self.y1 + self.h)

        if flag == "shape":
            self.y2, self.x2 = map(int, dims)
            self.w, self.h = map(int, dims)

    def __str__(self):
        return "x1: %d, y1: %d, x2: %d, y2: %d, w: %d, h: %d" % (self.x1, self.y1, self.x2, self.y2, self.w, self.h)

    def within(self, box):
        result = False
        if self.x1 >= box.x1 and self.x2 <= box.x2 and self.y1 >= box.y1 and self.y2 <= box.y2:
            result = True
        return result

    def trim(self, box):
        self.x1 = int(max(self.x1, box.x1))
        self.y1 = int(max(self.y1, box.y1))
        self.x2 = int(min(self.x2, box.x2))
        self.y2 = int(min(self.y2, box.y2))

    def toInt(self):
        self.x1 = int(self.x1)
        self.y1 = int(self.y1)
        self.x2 = int(self.x2)
        self.y2 = int(self.y2)
        self.w = int(self.w)
        self.h = int(self.h)

    def growTo(self, new_width, new_height):
        delta_x = new_width - self.w
        self.x1 = int(self.x1 - delta_x / 2)
        self.x2 = int(self.x2 + delta_x / 2)
        delta_y = new_height - self.h
        self.y1 = int(self.y1 - delta_y / 2)
        self.y2 = int(self.y2 + delta_y / 2)

    def scale(self, factor):
        new_width = self.w * factor
        new_height = self.h * factor
        self.growTo(new_width, new_height)

    def center(self):
        x = int(self.x1 + (self.x2 - self.x1) / 2)
        y = int(self.y1 + (self.y2 - self.y1) / 2)
        return (x, y)

    def tl(self):
        return (self.x1, self.y1)

    def br(self):
        return (self.x2, self.y2)

    def shift(self, delta):
        self.x1 += delta[0]
        self.x2 += delta[0]
        self.y1 += delta[1]
        self.y2 += delta[1]                 

