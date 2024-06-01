

import os
import torch
import torchvision
import torchvision.transforms as transforms
from torchvision import models
from torch.utils.data import Dataset, DataLoader, ConcatDataset
import timm
import torchvision.io as io
from PIL import Image
import pandas as pd
import cv2
import os
import glob

#path_contecst = "/content/"
#path_models = "/content/drive/MyDrive/RZD_CP_HACK_2024_dalniy_vostok/"
#name_video = '/content/drive/MyDrive/RZD_CP_HACK_2024_dalniy_vostok/VID-20240301-WA0023.mp4'

def extract_frames(video_path, output_folder, fps=1):
    video_name = os.path.basename(video_path).split('.')[0]
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)

    frame_interval = int(video_fps / fps)

    frame_count = 0
    time_list = []

    os.makedirs(os.path.join(output_folder, "images"), exist_ok=True)
    os.makedirs(os.path.join(output_folder, "labels"), exist_ok=True)

    while cap.isOpened():
        frame_id = cap.get(cv2.CAP_PROP_POS_FRAMES)
        ret, frame = cap.read()
        if not ret:
            break
        if frame_id % frame_interval == 0:
            timestamp = frame_id / video_fps
            time_list.append(timestamp)

            frame_path = os.path.join(output_folder, "images/" + f"{video_name}_frame_{frame_count:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            label_path = os.path.join(output_folder, "labels/" + f"{video_name}_frame_{frame_count:04d}.txt")
            with open(label_path, "w+") as my_file:
                my_file.write("0")
            frame_count += 1

    cap.release()
    return time_list

class CustomDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.images = sorted(
            [os.path.join(root_dir, 'images', f) for f in os.listdir(
                os.path.join(root_dir, 'images')
            ) if f.endswith(('.png', '.jpg', '.jpeg'))]  
        )
        self.labels = [int(open(os.path.join(root_dir, 'labels', f.rsplit('.', 1)[0] + '.txt'), 'r').read().strip()) for f in os.listdir(os.path.join(root_dir, 'images'))]

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image_path = self.images[idx]
        label = self.labels[idx]
        image = io.read_image(image_path)
        if self.transform:
            image = transforms.functional.to_pil_image(image)
            image = self.transform(image)
        return image, label

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main_danila(path_contecst, path_models, name_video):
  # first model
  model2 = timm.create_model('tf_efficientnetv2_s', num_classes=4)
  model2.load_state_dict(torch.load(path_models+'model_4_classes.pth',
                                  map_location=torch.device(device)))
  time_list = extract_frames(name_video, path_contecst+'my_test_11/', fps=1)
  transform = transforms.Compose([transforms.Resize(256),
                                transforms.ToTensor(),
                                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])

  dataset11 = CustomDataset(path_contecst+'my_test_11', transform)
  test_loader = DataLoader(dataset11, batch_size=16, shuffle=False)
  model2.eval()
  all_time = []
  i = 0
  with torch.no_grad():
      for data in test_loader:
          inputs, labels = data
          inputs = inputs.to(device)
          labels = labels.to(device)
          outputs = model2(inputs)
          preds = torch.softmax(outputs, dim=1)
          for value in preds[:, 1:3]:
            for val in value:
              if val >= 0.5:
                  all_time.append(time_list[i])
              i += 1
  all_time_new = []
  i = 0
  while i <= (len(all_time)-2):
    if all_time[i+1] - all_time[i] <= 4:
      all_time_new.append(all_time[i])
      i += 2
    i += 1

  all_time_new = [str(round(i)) for i in all_time_new]
  df = pd.DataFrame({'name': [name_video.split('/')[-1]], 'all_time': [';'.join(all_time_new)]})
  # ----
  model3 = timm.create_model('tf_efficientnetv2_s', num_classes=2)
  model3.load_state_dict(torch.load(path_models+'danilovskaya_model_2_classes.pth',
                                  map_location=torch.device(device)))
  model3.eval()
  all_time = []
  i = 0
  with torch.no_grad():
      for data in test_loader:
          inputs, labels = data
          inputs = inputs.to(device)
          labels = labels.to(device)
          outputs = model3(inputs)
          preds = torch.softmax(outputs, dim=1)
          for value in preds[:, 1]:
            if value >= 0.3:
              all_time.append(time_list[i])
            i += 1
  all_time_new2 = []
  i = 0
  while i <= (len(all_time)-3):
    if all_time[i+2] - all_time[i] <= 4:
      all_time_new2.append(all_time[i])
      i += 3
    i += 1

  all_time_new2 = [str(round(i)) for i in all_time_new2]
  df2 = pd.DataFrame({'name': [name_video.split('/')[-1]], 'all_time': [';'.join(all_time_new2)]})
  # combining our results
  df3 = pd.merge(df, df2, on='name')
  df3['value'] = df3.apply(lambda x: ';'.join([i for i in [x['all_time_x'], x['all_time_y']] if i != '']), axis=1)
  df3.drop(['all_time_x', 'all_time_y'], axis=1, inplace=True)
  df3['value'] = df3.apply(lambda x: ','.join(['{:02d}:{:02d}'.format(int(int(i) // 60), int(int(i) % 60)) for i in sorted(set(x['value'].split(';')))]), axis=1)
  return df3
