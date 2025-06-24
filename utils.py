import os, argparse
from PIL import Image, ImageTk


def get_pet_paths (src_folder="src"):
    return {
        name: os.path.join(src_folder, name)
        for name in os.listdir(src_folder)
        if os.path.isdir(os.path.join(src_folder, name))    
    }

def load_img_from(folder_path):
    images = []
    for fname in sorted(os.listdir(folder_path)):
        if fname.endswith((".png", ".jpg")):
            try:
                img = Image.open(os.path.join(folder_path, fname)).resize((64,64), Image.Resampling.LANCZOS)
                images.append(ImageTk.PhotoImage(img))
            except Exception as e:
                print(f"Error cargando {fname}: {e}")
    return images

def parse_args(pet_choices):
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--mode", "-m", 
        choices=["random", "square"],
        default="random",
        help="\nDefault movement mode: 'random'.\n"   
    )
    parser.add_argument(
        "--quantity", "-q",
        type=int,
        default=1,
        help="Number of pets to create, be carefull."
    )
    parser.add_argument(
        "--pet", "-p",
        choices=pet_choices,
        default="white_cat",
        help="Choose a pet or white_cat will be created by default."
    )
    return parser.parse_args()