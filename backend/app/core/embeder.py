import torch
import torch.nn.functional as F
import torchvision.models as models
import torchvision.transforms as T


resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
resnet.eval()
feature_extractor = torch.nn.Sequential(*list(resnet.children())[:-1])
