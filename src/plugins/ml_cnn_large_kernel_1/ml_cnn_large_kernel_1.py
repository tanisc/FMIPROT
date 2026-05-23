import sys, os, csv
# supress messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
import numpy as np
from tensorflow import keras

# realdir for script
bindir = os.path.realpath(os.path.split(sys.argv[0])[0])

# Labels for predicted classes
class_names=[0,50,100]

# Keras model used to make predictions
# requires wrapt < 1.15 in python3
print('Loading the model')
model=keras.models.load_model(os.path.join(bindir,'models/large_kernels_Monimet'))

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
        try:
            # Predict
            # Load image and resize to 256x256
            img = tf.keras.utils.load_img(
            imagefile, target_size=(256, 256)
            )
            img_array = tf.keras.utils.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0) # Create a batch
            # Call model.predict to make a prediction
            predictions = model.predict(img_array,verbose = 0)
            score = tf.nn.softmax(predictions[0])
            # Pick the label with the highest probability. 
            predicted_class=class_names[np.argmax(score)]
            result = [
                "Snow Cover Status",
                "Time",
                imagetime,
                "Snow Cover Fraction",
                predicted_class,
                "Confidence",
                "{:.2f}".format( 100 * np.max(score))
            ]
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
    # image to predict
    image = sys.argv[1]
    # mask to use
    mask = sys.argv[2]

    # Predict
    # Load image and resize to 256x256
    img = tf.keras.utils.load_img(
    image, target_size=(256, 256)
    )
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) # Create a batch
    # Call model.predict to make a prediction
    predictions = model.predict(img_array,verbose = 0)
    score = tf.nn.softmax(predictions[0])
    # Pick the label with the highest probability. 
    predicted_class=class_names[np.argmax(score)]
    print(
        "Snow Cover Status,Snow Cover Fraction,{},Confidence,{:.2f}"
        .format(predicted_class, 100 * np.max(score))
    )