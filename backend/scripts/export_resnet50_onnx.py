from pathlib import Path

import torch
import torchvision.models as models


class ResNet50Embedding(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        try:
            weights = models.ResNet50_Weights.IMAGENET1K_V2
            resnet = models.resnet50(weights=weights)
        except AttributeError:
            resnet = models.resnet50(pretrained=True)

        self.features = torch.nn.Sequential(*list(resnet.children())[:-1])

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        embeddings = self.features(images)
        return torch.flatten(embeddings, 1)


def main() -> None:
    output_path = Path(__file__).resolve().parents[1] / "models" / "resnet50_embedding.onnx"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    model = ResNet50Embedding().eval()
    dummy_input = torch.randn(1, 3, 224, 224)

    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        input_names=["image"],
        output_names=["embedding"],
        dynamic_axes={
            "image": {0: "batch"},
            "embedding": {0: "batch"},
        },
        opset_version=17,
    )

    print(f"Exported {output_path}")


if __name__ == "__main__":
    main()
