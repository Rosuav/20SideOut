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
import ast
from collections import defaultdict
import os
import subprocess
from PIL import Image
from panelparser import prescan, execute

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

def parse_panels(fn):
	with open(fn) as f:
		for pos, l in enumerate(f, 1):
			l = l.rstrip() # Always dispose of trailing whitespace
			line = l.lstrip()
			if not line or line.startswith("#"): continue
			indent = l[:-len(line)]
			while (yield (pos, indent, line)): yield None # Send True back in to have it re-send next time
	while (yield (-1, "", "")): yield None

def read_panels(fn):
	gen = parse_panels(fn)
	info = {"frame_usage": defaultdict(int), "panels": []}
	for pos, indent, line in gen:
		if not line: break
		if not indent:
			# It should be a panel header
			info["panels"].append([line])
			continue
		while True:
			_, peek, nextline = next(gen) # We don't care about continuation line numbers currently
			# TODO: Ensure that indentation isn't mismatched
			if len(peek) <= len(indent): break
			line += " " + nextline
		gen.send(1) # Put that thing back where it came from, or so help me, so help me...
		expr = compile(line, "%s:%d" % (fn, pos), "eval", ast.PyCF_ONLY_AST).body
		prescan(expr, info)
		info["panels"][-1].append(expr)
	return info

info = read_panels("Panels")
print("Need frames:", info["frame_usage"])
frames = get_frames(info["frame_usage"])

for panel in info["panels"]:
	# panel[0] is the metadata, everything else is a piece
	print(panel)
	# TODO: parse out the metadata here or above
	target = Image.new("RGB", (300, 400))
	#for segment in panel[1:]:
		#execute(segment, target)
