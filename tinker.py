"""
Goals
-----

1) Lift images out of movie - FFMPEG (borrow from resync)
2) Crop specific portions from specific frames
3) Synthesize sub-pieces from text
3a) Narration - square box
3b) Speech bubble incl pointer
3c) Variants eg "boom" sounds, dice rolls?
4) Combine sub-pieces to assemble a coherent page
5) Govern everything with a simple text file

"""
from PIL import Image
