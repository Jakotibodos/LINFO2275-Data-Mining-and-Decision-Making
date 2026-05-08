import torch.nn as nn
import torch.nn.functional as F

class CnnQNetwork(nn.Module):
    def __init__(self, width=10, height=20):
        super(CnnQNetwork, self).__init__()
        
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1)
        
        #Flatten the output for the fully connected layers
        self.fc1 = nn.Linear(64 * width * height, 512)
        self.fc2 = nn.Linear(512, 1)

        self._create_weights()

    def _create_weights(self):
        for m in self.modules():
            if isinstance(m, (nn.Linear, nn.Conv2d)):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        # x shape: (batch, height, width) -> add channel dim
        if len(x.shape) == 3:
            x = x.unsqueeze(1) 
            
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        
        x = x.view(x.size(0), -1) # Flatten
        x = F.relu(self.fc1(x))
        return self.fc2(x)