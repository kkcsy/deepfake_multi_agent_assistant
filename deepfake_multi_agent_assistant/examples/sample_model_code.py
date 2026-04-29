import torch
import torch.nn as nn


class ReconstructionDiscrepancyHead(nn.Module):
    """A minimal classification head for original and discrepancy features."""

    def __init__(self, feature_dim: int = 1024, num_classes: int = 2):
        super().__init__()
        self.classifier = nn.Sequential(
            nn.Linear(feature_dim * 2, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(1024, num_classes),
        )

    def forward(self, original_feature: torch.Tensor, recon_feature: torch.Tensor) -> torch.Tensor:
        discrepancy = original_feature - recon_feature
        fused = torch.cat([original_feature, discrepancy], dim=1)
        return self.classifier(fused)
