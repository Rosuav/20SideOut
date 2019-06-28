"""Parse the panel definition, derived from Python syntax

Entry points:

prescan(expr, info) - prescan an expression, doing minimal work
execute(expr, info) - execute the expression over the given image
"""
from PIL import Image, ImageDraw

def prescan_Call(expr, info):
	"""Call places the called object at the target location"""
	if len(expr.args) != 2: raise SyntaxError("Must call an object with (x, y)")
	# TODO: Ensure that args is a pair of constant integers
	if expr.keywords: raise NotImplementedError("Gravity isn't done yet, sorry")
	prescan(expr.func, info)

def prescan_Constant(expr, info):
	"""A constant string is created as a text node; a constant int is a frame."""
	if isinstance(expr.value, str): return
	if isinstance(expr.value, int):
		# Save the frame number because we'll need it
		info["frame_usage"][expr.value] += 1
		return
	raise SyntaxError("Bad constant type")

def prescan_Subscript(expr, info):
	"""Subscripting an object crops it."""
	# yes, you can crop text if you want to - won't be common though
	prescan(expr.value, info)
	# assume we have an Index tuple in the slice
	coords = expr.slice.value.elts
	if len(coords) == 4: return # Crop without scaling
	if len(coords) == 6: return # Crop and scale
	raise SyntaxError("Bad crop")

def prescan(expr, info):
	"""Pre-scan an expression without executing it

	Fetches up any sort of useful metadata but does minimal work
	"""
	f = globals()["prescan_" + type(expr).__name__]
	if f: f(expr, info)
	else: raise SyntaxError("Unexpected expression in panel definition", expr)

# ----------------------

# Tiny image just for font metrics
measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))

def execute_Call(expr, info):
	piece = execute(expr.func, info)
	pos = tuple(c.value for c in expr.args) # assumes all are constant ints
	print("Pasting", piece)
	info["target"].paste(piece, pos)

def execute_Constant(expr, info):
	"""A constant string is created as a text node; a constant int is a frame."""
	if isinstance(expr.value, str):
		size = measure.textsize(expr.value)
		ret = Image.new("RGB", size)
		ImageDraw.Draw(ret).text((0,0), expr.value)
		return ret
	if isinstance(expr.value, int):
		return info["frames"][expr.value]
	raise SyntaxError("Bad constant type")

def execute_Subscript(expr, info):
	base = execute(expr.value, info)
	coords = [c.value for c in expr.slice.value.elts]
	# piece = f.resize(box=(450, 0, 880, 480), size=(150, 150*(480-0)//(880-450)))
	if len(coords) == 4:
		# Crop without scaling
		print(coords)
		return base.resize(box=coords)
	if len(coords) == 6:
		# Crop and scale
		# Use Ellipsis for width/height to maintain aspect ratio
		# Note that coordinates are inclusive-exclusive, so (x2-x1)
		# will be the original width.
		x1, y1, x2, y2, w, h = coords
		if w is ...:
			w = h * (x2 - x1) // (y2 - y1)
		elif h is ...:
			h = w * (y2 - y1) // (x2 - x1)
		return base.resize(box=(x1,y1,x2,y2), size=(w,h))
	raise SyntaxError("Bad crop")

def execute(expr, info):
	"""Actually execute the given expression"""
	f = globals()["execute_" + type(expr).__name__]
	if f: return f(expr, info)
	else: raise SyntaxError("Unexpected expression in panel definition", expr)
