Minecraft Pixel Art Generator

A Python script that converts any PNG/JPG image into a Minecraft .mcfunction file, allowing you to create pixel art in-game automatically. 
The script maps image pixels to Minecraft blocks (e.g., concrete or wool) and outputs commands ready for a datapack.

Features

Convert any image into Minecraft pixel art.
Supports Minecraft concrete and wool block palettes.
Automatically generates a .mcfunction file with /setblock commands.
Optional preview image to see how the pixel art will look in Minecraft.
Works directly with Minecraft datapacks for easy in-game use.



Requirements
Python 3.8 or higher
Libraries: Pillow, numpy
Install dependencies using pip:
pip install pillow numpy
A Minecraft world with cheats enabled to use commands.
Optional: familiarity with datapacks to run .mcfunction files.


Usage
1. Place your image
Put the image you want to convert in the same folder as the Python script, e.g.:
project/
    png_to_mc_pixelart.py
    myimage.png

2. Run the script

Open a terminal in the project folder and run:
python png_to_mc_pixelart.py myimage.png --width 128 --preview preview.png
myimage.png → input image file.
--width 128 → number of blocks wide in Minecraft (maintains aspect ratio).
--preview preview.png → generates a preview image showing the Minecraft block colors.
Output .mcfunction file will be saved to the path defined in the script (can be your Minecraft datapack folder).


3. Using the .mcfunction in Minecraft

Place the .mcfunction file in a datapack folder inside your world:
saves/<YourWorld>/datapacks/pixelartpack/data/pixelart/functions/pixelart.mcfunction

Open your world in Creative Mode with cheats enabled.

Open the chat and type:
/reload
/function pixelart:pixelart

Your pixel art should appear in-game automatically!

4. Optional Arguments

--flipy -> Flip the vertical orientation (top of image appears closer to you in Minecraft).
--blocktype -> Choose concrete or wool for block palette.
--out -> Specify a custom output path for the .mcfunction file.

5. Notes

Larger widths produce higher-fidelity pixel art but increase the number of blocks — may take longer to build in Minecraft.
For extremely large images, consider splitting into multiple .mcfunction files to reduce lag.

6. Example
python png_to_mc_pixelart.py myimage.png --width 128 --out "C:\Users\amiib\AppData\Roaming\.minecraft\saves\Pixel Art\datapacks\pixelartpack\data\pixelart\functions\pixelart.mcfunction" --preview preview.png --blocktype concrete
This generates a .mcfunction in your Minecraft world datapack and a preview image to check before building.