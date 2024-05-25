import math
import os
import json
import uuid
import ntpath
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from pydantic import BaseModel
from itertools import combinations, islice
from tqdm import tqdm

OUTPUT_DIR = "output"
INPUT_DIR = "input"
UPSCALE = 2


class Template(BaseModel):
    size: int
    path: str
    dimensions: list
    box: list
    images: list

    def get_dimensions_tuple_list(self) -> list[tuple]:
        return [tuple(map(int, dimension.split(","))) for dimension in self.dimensions]

    def get_boxes_tuple_list(self) -> list[tuple]:
        return [tuple(map(int, box.split(","))) for box in self.box]

    def get_save_path(self) -> str:
        return (
            OUTPUT_DIR
            + "\\"
            + (split_path := self.path.rsplit("\\"))[1]
            + "\\"
            + get_file_name(split_path[2], False)
        )


def load_json_db(file_path: str):
    with open(file_path) as file:
        return json.load(file)


def get_file_name(path: str, extension: bool = True) -> str:
    if not extension:
        return str(ntpath.basename(path)).split(".")[0]
    return ntpath.basename(path)


def images_to_list(directory_path: str) -> list:
    images_list = os.listdir(directory_path)
    images_list = [
        image
        for image in images_list
        if image.endswith(".png") or image.endswith(".jpg") or image.endswith(".jpeg")
    ]
    return images_list


def chunker(image_list: list, chunk_size: int) -> list:
    chunks = []
    for i in range(0, len(image_list), chunk_size):
        chunk = tuple(image_list[i : i + chunk_size])
        if len(chunk) >= chunk_size:
            chunks.append(chunk)
    return list(chunks)


def get_random_combinations_of_images(
    images_list: list, combination: int, amount: int
) -> list:
    random.shuffle(images_list)
    combined_list = list(combinations(images_list, combination))

    if combination == 1:
        return combined_list

    if len(images_list) == combination:
        return combined_list

    if amount > len(combined_list):
        return []

    return list(random.sample(combined_list, amount))


def process_product_image(template: Template) -> None:
    try:
        if not os.path.exists(template.get_save_path()):
            os.makedirs(template.get_save_path())

        for image_tuple in template.images:
            template_image = Image.open(template.path)

            for idx, image in enumerate(image_tuple):
                process_image = Image.open(f"{INPUT_DIR}\\{image}")
                image_resized = process_image.resize(
                    template.get_dimensions_tuple_list()[idx]
                )
                template_image.paste(
                    image_resized, box=template.get_boxes_tuple_list()[idx]
                )

            upscale_multiplier = UPSCALE

            if template_image.height > 1800 or template_image.width > 1800:
                upscale_multiplier = 1  # math.floor(UPSCALE / 2)

            template_image = template_image.resize(
                (
                    template_image.width * upscale_multiplier,
                    template_image.height * upscale_multiplier,
                )
            )

            template_image.save(
                f"{template.get_save_path()}\\{str(uuid.uuid4())}_{get_file_name(template.path)}"
            )

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    db = load_json_db("db.json")
    images_list = images_to_list(INPUT_DIR)

    random = 0
    size = 1
    sample_amount = 3

    tasks = []

    if random == 1:
        for obj in db:
            if not size == 0 and obj["size"] == size:
                tmp = Template(
                    images=get_random_combinations_of_images(
                        images_list, size, sample_amount
                    ),
                    **obj,
                )
                tasks.append(tmp)

            elif size == 0:
                tmp = Template(
                    images=get_random_combinations_of_images(
                        images_list, obj["size"], sample_amount
                    ),
                    **obj,
                )
                tasks.append(tmp)

    elif random == 0:
        for obj in db:
            if not size == 0 and obj["size"] == size:
                chunked = chunker(images_list, size)
                tmp = Template(images=chunked, **obj)
                tasks.append(tmp)

            elif size == 0:
                chunked = chunker(images_list, obj["size"])
                tmp = Template(images=chunked, **obj)
                tasks.append(tmp)

    with tqdm(total=len(tasks), ncols=80) as pbar:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(process_product_image, tmp) for tmp in tasks]

            for future in as_completed(futures):
                future.result()
                pbar.update(1)
