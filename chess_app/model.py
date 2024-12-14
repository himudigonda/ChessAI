# chess_app/model.py

import torch
import torch.nn as nn
import torch.nn.functional as F

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

        self.conv1 = nn.Conv2d(in_channels=self.num_channels, out_channels=512, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(512)
        self.relu = nn.ReLU(inplace=True)

        # Residual blocks
        self.residual_blocks = nn.Sequential(
            *[ResidualBlock(512) for _ in range(num_residual_blocks)]
        )

        # Attention mechanism (Self-Attention Layer)
        self.attention = nn.MultiheadAttention(embed_dim=512, num_heads=8)

        # Policy head
        self.policy_conv = nn.Conv2d(512, 256, 1)
        self.policy_bn = nn.BatchNorm2d(256)
        self.policy_relu = nn.ReLU(inplace=True)
        self.policy_fc = nn.Linear(256 * board_size * board_size, board_size * board_size * 73)

        # Value head
        self.value_conv = nn.Conv2d(512, 256, 1)
        self.value_bn = nn.BatchNorm2d(256)
        self.value_relu = nn.ReLU(inplace=True)
        self.value_fc1 = nn.Linear(256 * board_size * board_size, 1024)
        self.value_fc2 = nn.Linear(1024, 1)

        self.dropout = nn.Dropout(p=0.3)

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.residual_blocks(x)

        # Reshape for attention: (sequence_length, batch, embedding_dim)
        batch_size, channels, height, width = x.size()
        x_reshaped = x.view(batch_size, channels, height * width)
        x_reshaped = x_reshaped.permute(2, 0, 1)  # (sequence_length, batch, embedding_dim)

        # Apply self-attention
        attn_output, _ = self.attention(x_reshaped, x_reshaped, x_reshaped)
        attn_output = attn_output.permute(1, 2, 0).contiguous().view(batch_size, channels, height, width)

        # Policy head
        p = self.policy_relu(self.policy_bn(self.policy_conv(attn_output)))
        p = p.view(p.size(0), -1)
        p = self.policy_fc(p)
        p = F.log_softmax(p, dim=1)

        # Value head
        v = self.value_relu(self.value_bn(self.value_conv(attn_output)))
        v = v.view(v.size(0), -1)
        v = self.value_fc1(v)
        v = self.dropout(F.relu(v))
        v = torch.tanh(self.value_fc2(v))

        return p, v

    def predict_move_quality(self, x):
        """
        Predicts the quality of the move: Great, Good, Average, Bad, Blunder
        """
        # Placeholder implementation
        # In practice, this should be trained with labeled data
        # Here we use the value head to classify move quality
        _, value = self.forward(x)
        value = value.squeeze().detach().cpu().numpy()
        if value > 0.75:
            return "Great Step"
        elif value > 0.5:
            return "Good Step"
        elif value > 0.25:
            return "Average Step"
        elif value > 0.0:
            return "Bad Step"
        else:
            return "Blunder"

def load_model(model, path, device):
    """Load model with proper device handling"""
    state_dict = torch.load(path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    print(f"Model loaded from {path}")

def save_model(model, path):
    """Save model to CPU for better compatibility"""
    model.cpu()
    torch.save(model.state_dict(), path)
    print(f"Model saved to {path}")