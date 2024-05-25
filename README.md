> **Laziness:** AI GENERATED CONTENT

# Wall Art Mockup Generator (For Etsy, Shopify, etc..)

This project is a Python script that generates wall art mockups for images and image sets. It takes images from an input directory and places them into a template image, simulating a wall frame.

### How it works

Place your images into the input directory.
The script uses templates from the templates directory. Each template represents a different layout of frames on a wall.
The script then copies the images from the input directory and pastes them into the frames in the template image.
The resulting mockup images are saved in the output directory.

### Running the script

To run the script, execute the main.py file

### Requirements

This project requires Python 3 and the following Python libraries

- PIL (Pillow)
- pydantic
- tqdm
- concurrent.futures

### Customizing the script

You can customize the script by modifying the main.py file. For example, you can change the size variable to specify the number of images to be used in each mockup, or the sample_amount variable to specify the number of mockups to generate.

### Note

This script uses multithreading to speed up the generation of mockups. The number of threads used can be adjusted by changing the max_workers parameter in the ThreadPoolExecutor call.
