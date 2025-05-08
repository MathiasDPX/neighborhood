import os
import shutil
from glob import glob
from PIL import Image

def convert_png_to_webp():
    png_files = glob(os.path.join("png", "mipmap-*dpi", '**', '*.png'), recursive=True)
    
    output_base = "webp"
    if not os.path.exists(output_base):
        os.makedirs(output_base)
    
    for png_file in png_files:
        relative_path = os.path.dirname(png_file)
        output_dir = os.path.join(output_base, relative_path)
        
        os.makedirs(output_dir.replace("webp\\png\\", "webp\\", 1), exist_ok=True)
        
        filename = os.path.basename(png_file)
        webp_filename = os.path.splitext(filename)[0] + '.webp'
        webp_path = os.path.join(output_dir, webp_filename)
        webp_path = webp_path.replace("webp\\png\\", "webp\\", 1)
        
        with Image.open(png_file) as img:
            img.save(webp_path, 'WEBP')
            print(f'Converted {png_file} to {webp_path}')

if __name__ == '__main__':
    convert_png_to_webp()