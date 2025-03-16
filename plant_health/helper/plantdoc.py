import os

'''
PlantDoc - Dataset preparation for plant health classification
'''

# parsing PlantDoc dataset
def parse_plantdoc(path):
    dataset = []
    for split in ['train', 'test']:
        dir_path = os.path.join(path, split)
        for folder in os.listdir(dir_path):
            folder_path = os.path.join(dir_path, folder)
            if os.path.isdir(folder_path):
                # clean labels
                labels = [label.lower().replace('_', ' ') for label in folder.split(' ') if label.lower() != 'leaf']

                # split labels into species, healthy/unhealthy, and specific health conditions
                species = labels[0]
                if (len(labels) == 1):
                    health_labels = None
                    health_class = 'healthy'
                else:
                    health_labels = ' '.join(labels[1:])
                    health_class = 'unhealthy'

                # find image paths
                for image_file in os.listdir(folder_path):
                    if image_file.endswith(('.jpg', '.png', '.jpeg')):
                        image_path = os.path.join(folder_path, image_file)

                        # add to dataset
                        dataset.append({
                            'dataset': 'PlantDoc',
                            'split': split,
                            'image_path': image_path,
                            'species': species,
                            'health_labels': health_labels,
                            'health_class': health_class,
                            'bbox': None,
                        })
    return dataset
