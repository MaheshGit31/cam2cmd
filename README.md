# cam2cmd
a fun little phyton-based terminal "game" that turns your camera into ASCII so you see yourself in the terminal, but as random symbols and letters :o.


## Features
 
- **Three render modes**
  - Plain ASCII (brightness mapped to characters)
  - Color ASCII (each character painted with its pixel's color)
  - Half-block pixels (`▀` with separate foreground and background colors, so every cell shows two pixels)
  - **Camera switching**
- **Live FPS**
- Mirrored view

## Requirements
 
- Python 3.8+
- A webcam
- A terminal

## Install
 
```
pip install opencv-python numpy
```
 
## Run
 
Save the script as `ascii_cam.py`, then from its folder:
 
```
python ascii_cam.py
```


## Controls
 
| Key | Action |
| --- | --- |
| `c` | Cycle render mode (plain ASCII, color ASCII, half-block) |
| `m` | Switch to the next camera |
| `q` | Quit |
| `Ctrl + C` | Quit |
 
