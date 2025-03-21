import os
import argparse
from PIL import Image
from tqdm import tqdm


def resize_image(image_path, output_path, max_size=None, min_size=None, keep_format=False):
    with Image.open(image_path) as img:
        # Capture original format BEFORE converting
        original_format = img.format.upper() if img.format else None

        # Convert image to RGB
        img = img.convert('RGB')

        # Determine new size maintaining aspect ratio
        if max_size is not None:
            ratio = min(max_size / img.width, max_size / img.height)
        elif min_size is not None:
            ratio = max(min_size / img.width, min_size / img.height)
        else:
            raise ValueError("Either max_size or min_size must be specified.")

        new_size = (int(img.width * ratio), int(img.height * ratio))
        resized_img = img.resize(new_size, Image.Resampling.BILINEAR)

        # Clear metadata
        resized_img.info = {}

        # Determine valid formats
        valid_formats = {'JPEG': 'jpg', 'PNG': 'png', 'BMP': 'bmp', 'GIF': 'gif'}

        # Set the extension correctly
        if keep_format and original_format in valid_formats:
            extension = valid_formats[original_format]
            save_format = original_format
        else:
            extension = 'png'
            save_format = 'PNG'

        output_path = os.path.splitext(output_path)[0] + f'.{extension}'

        save_params = {'format': save_format}
        if extension == 'png':
            save_params.update({'optimize': True, 'compress_level': 9})
        elif extension == 'jpg':
            save_params.update({'quality': 95})

        resized_img.save(output_path, **save_params)


def resize_dataset(input_dir, output_dir, max_size=None, min_size=None, keep_format=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Collect all image paths
    all_image_paths = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
                input_path = os.path.join(root, file)
                all_image_paths.append(input_path)

    # Resize images with a progress bar
    for input_path in tqdm(all_image_paths, desc="Resizing images"):
        output_path = os.path.join(output_dir, os.path.relpath(input_path, input_dir))
        output_subdir = os.path.dirname(output_path)

        if not os.path.exists(output_subdir):
            os.makedirs(output_subdir)

        resize_image(input_path, output_path, max_size=max_size, min_size=min_size, keep_format=keep_format)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Resize images in a dataset using max_size or min_size.")
    parser.add_argument('input_directory', type=str, help="Path to the input dataset directory.")
    parser.add_argument('output_directory', type=str, help="Path to the output resized dataset directory.")
    parser.add_argument('--max_size', type=int, default=None,
                        help="Maximum size of the longest edge of the resized images.")
    parser.add_argument('--min_size', type=int, default=None,
                        help="Minimum size of the shortest edge of the resized images.")
    parser.add_argument('--keep_format', action='store_true',
                        help="Keep the original file format instead of converting to PNG.")

    args = parser.parse_args()

    if args.max_size and args.min_size:
        parser.error("Specify either --max_size or --min_size, not both.")

    if not args.max_size and not args.min_size:
        parser.error("Either --max_size or --min_size must be specified.")

    resize_dataset(args.input_directory, args.output_directory, max_size=args.max_size, min_size=args.min_size,
                   keep_format=args.keep_format)
