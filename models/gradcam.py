from decimal import HAVE_THREADS
from re import T
import copy
import time
import torch
import torch.nn.functional as F

def find_yolo_layer(model, layer_name):
    """Find yolov5 layer to calculate GradCAM and GradCAM++
    Args:
        model: yolov5 model.
        layer_name (str): the name of layer with its hierarchical information.

    Return:
        target_layer: found layer
    """
    hierarchy = layer_name.split('_')
    target_layer = model.model._modules[hierarchy[0]]
    # print(target_layer)
    for h in hierarchy[1:]:
        target_layer = target_layer._modules[h]
    return target_layer


class YOLOV5GradCAM:
    def __init__(self, model, layer_name, img_size=(640, 640)):
        self.model = model
        # self.gradients = []
        # self.activations = []
        target_layer = find_yolo_layer(self.model, layer_name)
        print('Target_layer', target_layer)

        # Because of https://github.com/pytorch/pytorch/issues/61519,
        # we don't use backward hook to record gradients.
        target_layer.register_forward_hook(self.save_activation) #self.save_activation
        target_layer.register_forward_hook(self.save_gradient)

        device = 'cuda' if next(self.model.model.parameters()).is_cuda else 'cpu'
        self.model(torch.zeros(1, 3, *img_size, device=device))
        print('[INFO] saliency_map_size :', self.activations[0].shape[2:])
    
    def save_activation(self, module, input, output):
        activation = output.clone()
        self.activations = activation.cpu().detach()
        # self.activations['value'] = activation.cpu().detach()
        print('forward:', type(output))
        return None

    def save_gradient(self, module, input, output):
        if not hasattr(output, "requires_grad") or not output.requires_grad:
            # You can only register hooks on tensor requires grad.
            return

        # Gradients are computed in reverse order
        def _store_grad(grad):
            self.gradients = grad.cpu().detach()

        output.register_hook(_store_grad)
    
    def forward(self, input_img, class_idx=True):
        """
        Args:
            input_img: input image with shape of (1, 3, H, W)
        Return:
            mask: saliency map of the same spatial dimension with input
            logit: model output
            preds: The object predictions
        """
        saliency_maps = []
        b, c, h, w = input_img.size()
        tic = time.time()
        preds, logits = self.model(input_img)
        print("[INFO] model-forward took: ", round(time.time() - tic, 4), 'seconds')
        for logit, cls, cls_name in zip(logits[0], preds[1][0], preds[2][0]):
            if class_idx:
                score = logit[cls]
            else:
                score = logit.max()
            self.model.zero_grad()
            tic = time.time()
            score.backward(retain_graph=True)
            print(f"[INFO] {cls_name}, model-backward took: ", round(time.time() - tic, 4), 'seconds')
            gradients = self.gradients
            activations = self.activations
            b, k, u, v = gradients.size()
            alpha = gradients.view(b, k, -1).mean(2)
            weights = alpha.view(b, k, 1, 1)
            saliency_map = (weights * activations).sum(1, keepdim=True)
            
            saliency_map = F.relu(saliency_map)
            saliency_map = F.interpolate(saliency_map, size=(h, w), mode='bilinear', align_corners=False)
            saliency_map_min, saliency_map_max = saliency_map.min(), saliency_map.max()
            saliency_map = (saliency_map - saliency_map_min).div(saliency_map_max - saliency_map_min).data
            saliency_maps.append(saliency_map)
        return saliency_maps, logits, preds

    def __call__(self, input_img):
        return self.forward(input_img)