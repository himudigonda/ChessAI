# chess_app/model.py

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        residual = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        out = F.relu(out)
        return out


class ChessNet(nn.Module):
    def __init__(self, board_size=8, num_channels=17, num_residual_blocks=256):
        super(ChessNet, self).__init__()
        self.board_size = board_size
        self.num_channels = num_channels

        self.conv1 = nn.Conv2d(num_channels, 512, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(512)
        self.relu = nn.ReLU(inplace=True)

        self.residual_blocks = nn.Sequential(
            *[ResidualBlock(512) for _ in range(num_residual_blocks)]
        )

        self.attention = nn.MultiheadAttention(embed_dim=512, num_heads=8)

        # Policy head
        self.policy_conv = nn.Conv2d(512, 256, 1)
        self.policy_bn = nn.BatchNorm2d(256)
        self.policy_relu = nn.ReLU(inplace=True)
        self.policy_fc = nn.Linear(
            256 * board_size * board_size, board_size * board_size * 73
        )

        # Value head
        self.value_conv = nn.Conv2d(512, 256, 1)
        self.value_bn = nn.BatchNorm2d(256)
        self.value_relu = nn.ReLU(inplace=True)
        self.value_fc1 = nn.Linear(256 * board_size * board_size, 1024)
        self.value_fc2 = nn.Linear(1024, 1)

        # Quality head
        self.quality_conv = nn.Conv2d(512, 256, 1)
        self.quality_bn = nn.BatchNorm2d(256)
        self.quality_relu = nn.ReLU(inplace=True)
        self.quality_fc1 = nn.Linear(256 * board_size * board_size, 256)
        self.quality_fc2 = nn.Linear(256, 5)  # 5 classes

        self.dropout = nn.Dropout(p=0.3)

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.residual_blocks(x)

        batch_size, channels, height, width = x.size()
        x_reshaped = x.view(batch_size, channels, height * width)
        x_reshaped = x_reshaped.permute(2, 0, 1)
        attn_output, _ = self.attention(x_reshaped, x_reshaped, x_reshaped)
        attn_output = (
            attn_output.permute(1, 2, 0)
            .contiguous()
            .view(batch_size, channels, height, width)
        )

        # Policy
        p = self.policy_relu(self.policy_bn(self.policy_conv(attn_output)))
        p = p.view(p.size(0), -1)
        p = self.policy_fc(p)
        p = F.log_softmax(p, dim=1)

        # Value
        v = self.value_relu(self.value_bn(self.value_conv(attn_output)))
        v = v.view(v.size(0), -1)
        v = self.value_fc1(v)
        v = self.dropout(F.relu(v))
        v = torch.tanh(self.value_fc2(v))

        # Quality
        q = self.quality_relu(self.quality_bn(self.quality_conv(attn_output)))
        q = q.view(q.size(0), -1)
        q = self.quality_fc1(q)
        q = self.dropout(F.relu(q))
        q = self.quality_fc2(q)

        return p, v, q

    def predict_move_quality(self, x):
        self.eval()
        with torch.no_grad():
            _, _, q = self.forward(x)
            quality_probs = F.softmax(q, dim=1).detach().cpu().numpy()
            quality_index = np.argmax(quality_probs, axis=1)[0]
            move_quality_mapping = {
                0: "Blunder",
                1: "Bad Step",
                2: "Average Step",
                3: "Good Step",
                4: "Great Step",
            }
            return move_quality_mapping.get(quality_index, "Average Step")


def load_model(model, path, device):
    state_dict = torch.load(path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    print(f"Model loaded from {path}")


def save_model(model, path):
    model.cpu()
    torch.save(model.state_dict(), path)
    print(f"Model saved to {path}")
