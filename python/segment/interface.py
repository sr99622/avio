#
# code derivd from https://debuggercafe.com/semantic-segmentation-using-pytorch-fcn-resnet/
#

import torchvision
import torch
import segmentation_utils

class Segment:
    def __init__(self):
        print("Segment.__init__")

        self.model = torchvision.models.segmentation.fcn_resnet50(pretrained=True)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.eval().to(self.device)
        

    def __call__(self, arg):
        img = arg[0][0]

        outputs = segmentation_utils.get_segment_labels(img, self.model, self.device)
        outputs = outputs['out']
        segmented_image = segmentation_utils.draw_segmentation_map(outputs)

        img = segmentation_utils.image_overlay(img, segmented_image)


        return img