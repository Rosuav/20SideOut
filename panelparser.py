"""Parse the panel definition, derived from Python syntax

Entry points:

prescan(expr, info) - prescan an expression, doing minimal work
execute(expr, img) - execute the expression over the given image
"""

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

def execute(expr, img):
	raise NotImplementedError
