import numpy as np
import cv2
from mmseg.apis import inference_segmentor, init_segmentor, show_result_pyplot
from mmseg.core.evaluation import get_palette

class Segment:
    def __init__(self, arg):
        print("Segment.__init__")
        device = 'cuda:0'
        checkpoint = "mmlab/checkpoints/pspnet_r50-d8_512x1024_40k_cityscapes_20200605_003338-2966598c.pth"
        config = "mmlab/configs/pspnet/pspnet_r50-d8_512x1024_40k_cityscapes.py"
        self.palette = 'cityscapes'
        self.opacity = 0.5

        self.model = init_segmentor(config, checkpoint, device=device)

    def __call__(self, arg):
        img = arg[0][0]
        print("img shape:", img.shape)
        result = inference_segmentor(self.model, img)
        show_result_pyplot(
            self.model,
            img,
            result, 
            get_palette(self.palette),
            opacity=self.opacity
        )
        return img

if __name__ == "__main__":
    segment = Segment("ckpt_file=auto")
    img = cv2.imread("C:/Users/stephen/Pictures/test.jpg")
    img = segment(((np.asarray(img),),))
    cv2.imshow("image", img)
    cv2.waitKey(0)