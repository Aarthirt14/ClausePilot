from typing import Tuple

import torch
from torch import nn


class TemperatureScaler(nn.Module):
	"""Learn a single temperature for logit scaling."""
	def __init__(self) -> None:
		super().__init__()
		self.temperature = nn.Parameter(torch.ones(1))

	def forward(self, logits: torch.Tensor) -> torch.Tensor:
		return logits / self.temperature


def fit_temperature(logits: torch.Tensor, labels: torch.Tensor, max_iter: int = 50) -> Tuple[TemperatureScaler, float]:
	"""Optimize temperature on validation logits using NLL."""
	scaler = TemperatureScaler()
	optimizer = torch.optim.LBFGS([scaler.temperature], lr=0.1, max_iter=max_iter)
	criterion = nn.CrossEntropyLoss()

	def closure():
		optimizer.zero_grad()
		loss = criterion(scaler(logits), labels)
		loss.backward()
		return loss

	optimizer.step(closure)
	final_loss = float(criterion(scaler(logits), labels).item())
	return scaler, final_loss


def apply_temperature(logits: torch.Tensor, scaler: TemperatureScaler) -> torch.Tensor:
	return torch.softmax(scaler(logits), dim=-1)
