import os

'''
HousePlant - Dataset preparation for plant health classification (YOLO format)
'''

# class labels
ds_labels = ['Alocasia-Green-Velvet-Micholitziana-Frydek-', 
             'Aloe-Vera-Aloe-barbadensis-', 
             'Inch-Plant-Tradescantia-zebrina-', 
             'Philippine-Evergreen-Aglaonema-Commutatum-', 
             'Pothos-Epipremnum-aureum-', 
             'Rubber-Fig-Ficus-Elastica-', 
             'Snake-Plant-Dracaena-trifasciata-', 
             'Spear-Plant-Dracaena-angolensis-', 
             'Spider-Plant-Chloropythum-Comosum-', 
             'Swiss Cheese Plant -Monstera Deliciosa-', 
             'Unhealthy-Dehydration', 
             'Unhealthy-Leaf-Curl', 
             'Unhealthy-Mineral-Deficiency', 
             'Unhealthy-Overwatering', 
             'Unhealthy-Powdery-Mildew', 
             'Unhealthy-Rust', 
             'Unhealthy-Sunburn']

# additional mappings (some datapoints are missing labels)
extra_mappings = {
    'Late-Blight': 'Unhealthy-Late-Blight',
    'late-blight': 'Unhealthy-Late-Blight',
    'bacterial-leaf-spot': 'Unhealthy-Bacterial-Spot',
    'BacterialSpot': 'Unhealthy-Bacterial-Spot',
    'Bac': 'Unhealthy-Bacterial-Spot',
    'Dehydration': 'Unhealthy-Dehydration',
    'leaf-curl': 'Unhealthy-Leaf-Curl',
}

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
            x_center, y_center, width, height = map(float, parts[1:])
            bbox.append((label, x_center, y_center, width, height))

    for key, mapped_label in extra_mappings.items():
        if key in label_path:
            labels.append(mapped_label)

    labels = list(set(labels))
    return labels, bbox

def parse_houseplant(path):
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

                    # clean health labels
                    health_labels = [i.lower().replace('unhealthy-', '').replace('-', ' ') for i in labels if i.startswith('Unhealthy')]
                    health_labels = ', '.join(health_labels)

                    species_labels = [i for i in labels if not i.startswith('Unhealthy')]

                    # exclude images with more than one species label
                    if len(labels) > 0 and len(species_labels) <= 1: 
                        # find species and health class
                        species = None if (len(species_labels)==0) else species_labels[0]
                        health_class = 'healthy' if not health_labels else 'unhealthy'

                        # add to dataset
                        dataset.append({
                            'dataset': 'HousePlant',
                            'split': split,
                            'image_path': image_path,
                            'species': species,
                            'health_labels': health_labels,
                            'health_class': health_class,
                            'bbox': bbox,
                        })
    return dataset
