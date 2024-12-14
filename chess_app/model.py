# chess_app/model.py

import torch
import torch.nn as nn
import torch.nn.functional as F

class ChessNet(nn.Module):
    def __init__(self, board_size=8, num_channels=17):  # Updated to 17 channels
        super(ChessNet, self).__init__()
        self.board_size = board_size
        self.num_channels = num_channels

        # Convolutional layers
        self.conv1 = nn.Conv2d(in_channels=self.num_channels, out_channels=256, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(256, 256, 3, padding=1)
        self.conv3 = nn.Conv2d(256, 256, 3, padding=1)
        self.conv4 = nn.Conv2d(256, 256, 3, padding=1)

        # Policy head
        self.policy_conv = nn.Conv2d(256, 2, 1)  # Produces 2 channels
        self.policy_fc = nn.Linear(128, board_size * board_size * 73)  # Adjusted input size to match flattened output

        # Value head
        self.value_conv = nn.Conv2d(256, 1, 1)
        self.value_fc1 = nn.Linear(board_size * board_size, 256)
        self.value_fc2 = nn.Linear(256, 1)

    def forward(self, x):
        # Shared layers
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))

        # Policy head
        p = F.relu(self.policy_conv(x))
        # Debug statements (optional, can be removed in production)
        # print(f"Shape of p after policy_conv: {p.shape}")  
        p = p.view(p.size(0), -1)  # Flatten
        # print(f"Shape of p after flattening: {p.shape}")  
        p = self.policy_fc(p)
        p = F.log_softmax(p, dim=1)

        # Value head
        v = F.relu(self.value_conv(x))
        v = v.view(v.size(0), -1)  # Flatten
        v = F.relu(self.value_fc1(v))
        v = torch.tanh(self.value_fc2(v))

        return p, v


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