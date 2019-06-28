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
   https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.paste
5) Govern everything with a simple text file

Need a tool to measure an image and find the appropriate coords
Also a tool to pick frames by scanning the movie.
"""
import os
import subprocess
from PIL import Image

def cache_frames(frames):
	try:
		got = set(os.listdir("frames"))
	except FileNotFoundError:
		os.mkdir("frames")
		got = set()
	frames = sorted(f for f in frames if "%d.png"%f not in got)
	if not frames: return # Got 'em all!
	expr = "+".join("eq(n\\,%d)" % frm for frm in frames)
	tmpfn = "frames/tmp%d.png"
	subprocess.check_call([
		"ffmpeg", "-y", "-i", "InsideOut.mkv",
		"-vf", "select=%s" % expr,
		"-vframes", str(len(frames)),
		"-vsync", "0", tmpfn,
	])
	for idx, frm in enumerate(frames, 1):
		os.rename(tmpfn % idx, "frames/%d.png" % frm)

def get_frames(frames):
	cache_frames(frames)
	return {f: Image.open("frames/%d.png" % f) for f in frames}

frames = get_frames([2839, 2840])
print(frames)
