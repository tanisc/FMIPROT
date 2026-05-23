import sys, os, csv, json, cv2, re
# Detectron2 imports
# Add local detectron2 to path
sys.path.insert(0, os.path.abspath('/FMIprot/srcrun/master_report/src/plugins/ml_panoptic_resnet_detectron2_1/detectron2'))
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

import warnings
warnings.filterwarnings("ignore", message=".*meshgrid.*")

# realdir for script
bindir = os.path.realpath(os.path.split(sys.argv[0])[0])
# visualized  output directory - Make None to disable visualization
vis_dir = os.path.join(bindir, 'visualized_output')
vis_dir = None
# model directory
model_dir = os.path.join(bindir, 'model')
# categories JSON file
categories_json = os.path.join(model_dir, 'categories.json')
# model name
model_name = "COCO-PanopticSegmentation/panoptic_fpn_R_101_3x"

# Define categories for fsc_ground
ground_snow_cats = ['ground_snow_litter', 'ground_snow_litter_wet', 'ground_snow_rough', 'ground_snow_rough_1o4', 'ground_snow_rough_2o4', 'ground_snow_rough_3o4', 'ground_snow_smooth', 'ground_snow_tracks']
ground_partsnow_cats = []
ground_nosnow_cats = ['ground_grass_dead', 'ground_grass_soil', 'ground_lichen', 'ground_lichen_grass', 'vegetation_grass', 'vegetation_grass_brown', 'vegetation_short', 'vegetation_short_brown']

# Define categories for fsc_mountain
mountain_snow_cats = ['mountain_forested_snow', 'mountain_rocky_snow', 'mountain_snow']
mountain_partsnow_cats = ['mountain_snow_1o4', 'mountain_snow_2o4', 'mountain_snow_3o4','mountain_forested_snow_1o4', 'mountain_forested_snow_2o4', 'mountain_forested_snow_3o4', 'mountain_rocky_snow_1o4', 'mountain_rocky_snow_2o4', 'mountain_rocky_snow_3o4']
mountain_nosnow_cats = ['mountain_dark', 'mountain_forested', 'mountain']

# Define categories for fsc_canopy
canopy_snow_cats = ['tree_canopy_snow','tree_bare_snow']
canopy_partsnow_cats = ['tree_canopy_snow_1o4', 'tree_canopy_snow_2o4', 'tree_canopy_snow_3o4']
canopy_nosnow_cats = ['tree_canopy', 'tree_canopy_dark', 'tree_bare', 'tree_canopy_overexposed']


def get_class_info(categories_json):
    """
    Reads source JSON files to determine the number and names of thing and stuff classes.
    """
    with open(categories_json, 'r') as f:
        data = json.load(f)
        
    categories = data['categories']
    types = data["category_types"]
    all_classes = [cat['name'] for cat in categories]
    thing_classes = [cat['name'] for cat in categories if types.get(cat['name']) != 'stuff']
    stuff_classes = [cat['name'] for cat in categories if types.get(cat['name']) == 'stuff']

    return thing_classes, stuff_classes, all_classes


# Set up the configuration and create the predictor
cfg = get_cfg()
# set device
cfg.MODEL.DEVICE = "cpu"  
# Load the base model config
cfg.merge_from_file(model_zoo.get_config_file(model_name + ".yaml"))

# Get the number of classes from the dataset definition files
thing_classes, stuff_classes, all_classes = get_class_info(categories_json)

# Set the number of classes for the model heads
cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(thing_classes)
cfg.MODEL.SEM_SEG_HEAD.NUM_CLASSES = len(stuff_classes) + 1 # +1 for the thing class

# Set the model weight file path
cfg.MODEL.WEIGHTS = os.path.join(model_dir, "model_final.pth")

# Set the score threshold for detections
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5

cfg.freeze()
predictor = DefaultPredictor(cfg)

# Create a temporary metadata object
metadata = MetadataCatalog.get(f"abc123_inference_meta")
metadata.thing_classes = thing_classes
metadata.stuff_classes = ["thing"] + stuff_classes 

# Create the output directory if it doesn't exist
if vis_dir is not None:
    os.makedirs(vis_dir, exist_ok=True)

def get_fractional_weight(col_name):
    """
    Parses a column name to find a fractional suffix like '_1o4' and returns the weight.
    e.g., 'ground_snow_rough_1o4' -> 0.25
    Returns 1.0 if no fractional suffix is found.
    """
    match = re.search(r'_(\d+)o(\d+)$', col_name)
    if match:
        numerator, denominator = map(int, match.groups())
        if denominator != 0:
            return numerator / denominator
    return 1.0

def calculate_weighted_fsc(cat_areas, snow_cats, partsnow_cats, nosnow_cats, image_area, min_area_percent=0.5):
    weighted_snow_area = 0
    weighted_nosnow_area = 0
    min_area = image_area * min_area_percent / 100.

    for col in snow_cats:
        if col in cat_areas:
            weighted_snow_area += cat_areas[col] * (cat_areas[col] >= min_area)

    for col in partsnow_cats:
        if col in cat_areas:
            weight = get_fractional_weight(col)
            weighted_snow_area += cat_areas[col] * (cat_areas[col] >= min_area) * weight
            weighted_nosnow_area += cat_areas[col] * (cat_areas[col] >= min_area) * (1 - weight)

    for col in nosnow_cats:
        if col in cat_areas:
            weighted_nosnow_area += cat_areas[col] * (cat_areas[col] >= min_area)

    total_area = weighted_snow_area + weighted_nosnow_area
    fsc = int(100 * weighted_snow_area / total_area) if total_area > 0 else 'nan'
    return fsc


def segment_image(imagefile,maskfile, imagetime=None, visfile=None):
    # todo: mask use (if possible)
    img = cv2.imread(imagefile)
    height, width = img.shape[:2]
    image_area = height * width

    # Perform inference
    panoptic_seg, segments_info = predictor(img)["panoptic_seg"]
    if visfile is not None:
        # Create a visualizer with our manually created metadata
        v = Visualizer(img[:, :, ::-1], metadata, scale=1)
        # Draw the panoptic segmentation predictions
        out = v.draw_panoptic_seg(panoptic_seg.to("cpu"), segments_info, alpha=0.25)
        # Save the image
        cv2.imwrite(visfile, out.get_image()[:, :, ::-1])

    category_areas = {cat : 0 for cat in thing_classes + stuff_classes}
    for s, segment in enumerate(segments_info):
        segment.update({"category" : thing_classes[segment["category_id"]-1] if segment["isthing"] else stuff_classes[segment["category_id"]-1] })
        segments_info[s] = segment
        category_areas[segment['category']] += segment['area']

    return category_areas, image_area

def process_image(imagefile,maskfile,imagetime=None,visfile=None):
    category_areas, image_area = segment_image(imagefile,maskfile,imagetime=imagetime,visfile=visfile)
    fsc_ground = calculate_weighted_fsc(category_areas, ground_snow_cats, ground_partsnow_cats, ground_nosnow_cats, image_area)
    fsc_mountain = calculate_weighted_fsc(category_areas, mountain_snow_cats, mountain_partsnow_cats, mountain_nosnow_cats, image_area)
    fsc_canopy = calculate_weighted_fsc(category_areas, canopy_snow_cats, canopy_partsnow_cats, canopy_nosnow_cats, image_area)

    result = []
    result += ["Snow Cover Fraction on Ground", fsc_ground]
    result += ["Snow Cover Fraction on Mountain", fsc_mountain]
    result += ["Snow Cover Fraction on Canopy", fsc_canopy]
    for cat in thing_classes + stuff_classes:
        result += [cat, category_areas[cat]]
    result = list(map(str, result))

    return result

if os.path.splitext(sys.argv[1])[1] == '.csv':
    # batch processing
    batch_list_file = sys.argv[1]
    batch_results_file = sys.argv[2]

    print('Reading batch list file')
    batch_list = []
    with open(batch_list_file) as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            batch_list.append(row)
    print('%s images to process' % len(batch_list))

    print('Limiting number of images to 5000 since the plugin crashes. More images will be processed in the next run.')
    batch_list = batch_list[:5000]

    print('Processing images and saving results')
    batch_results = []
    open(batch_results_file, 'w').close()
    for imagetime, imagefile, maskfile in batch_list:
        visfile = os.path.join(vis_dir, os.path.basename(imagefile)) if vis_dir is not None else None
        try:
            result = process_image(imagefile,maskfile,imagetime=imagetime, visfile = visfile)
            result = [
                "Snow Cover Status",
                "Time",
                imagetime
            ] + result
            batch_results.append(result)
            with open(batch_results_file, 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(result)

        except Exception as e:
            print('Processing %s failed. Image skipped.' % os.path.split(imagefile)[1])
            print(e)

    print('Results saved at %s' % batch_results_file)

else:
    # single image processing
    imagefile = sys.argv[1]
    maskfile = sys.argv[2]
    visfile = os.path.join(vis_dir, os.path.basename(imagefile)) if vis_dir is not None else None
    result = process_image(imagefile,maskfile,visfile = visfile) 
    print(",".join(["Snow Cover Status"] + result))


