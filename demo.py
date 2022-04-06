import numpy as np
import torch
from torchvision import models

def get_layers_with_logits(x, model):
    operations = []
    '''
    def hook(module, input, output):
        def h(grad):
            operations.append(grad)
        output.register_hook(h)
    handle = model.features[15].register_forward_hook(hook)
    '''
    def hook(module, input, output):
        print(output)
        operations.append(output)
    handle = model.features[15].register_full_backward_hook(hook)
    
    logits = model(x)
    handle.remove()
    return logits, operations

def main():
    test = torch.rand((1, 3, 224, 224))
    test.requires_grad = True
    with torch.enable_grad():
        model = models.vgg16(pretrained=False, num_classes=1000)
        model.load_state_dict(torch.load('./models_torch/vgg16-397923af.pth'))
        model.eval()
        
        logits, operations = get_layers_with_logits(test, model)
        feature = operations[0]

main()