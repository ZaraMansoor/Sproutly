import os

'''
HousePlant2 - Dataset preparation for plant health classification (YOLO format)
'''

# class labels
ds_labels = ['Dehydration', 'Healthy']

# read YOLO format labels
def read_labels(label_path):
    with open(label_path, 'r') as f:
        labels = []
        bbox = []
        for line in f.readlines():
            parts = line.strip().split()
            label = int(parts[0])
            label = ds_labels[label]
            labels.append(label)
            if (len(parts) == 5):
                x_center, y_center, width, height = map(float, parts[1:])
                bbox.append((label, x_center, y_center, width, height))
    labels = list(set(labels))
    return labels, bbox

def parse_houseplant2(path):
    dataset = []
    for split in ['train', 'valid', 'test']:
        image_dir = os.path.join(path, split, 'images')
        label_dir = os.path.join(path, split, 'labels')
        
        if not os.path.exists(image_dir) or not os.path.exists(label_dir):
            print(f'Skipping {split} - Missing folders')
            continue
        
        for image_file in os.listdir(image_dir):
            if image_file.endswith(('.jpg', '.png', '.jpeg')):
                # find image and label paths
                image_path = os.path.join(image_dir, image_file)

                label_file = os.path.splitext(image_file)[0] + '.txt'
                label_path = os.path.join(label_dir, label_file)

                if os.path.exists(label_path):
                    # read labels
                    labels, bbox = read_labels(label_path)
                    if 'Dehydration' in labels:
                        health_labels = 'dehydration'
                        health_class = 'unhealthy'
                    else:
                        health_labels = None
                        health_class = 'healthy'
                    
                    # species aren't specified in this dataset
                    species = None
                    
                    # add to dataset
                    dataset.append({
                        'dataset': 'HousePlant2',
                        'split': split,
                        'image_path': image_path,
                        'species': species,
                        'health_labels': health_labels,
                        'health_class': health_class,
                        'bbox': bbox,
                    })
    return dataset
