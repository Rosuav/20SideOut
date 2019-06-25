# Regenerate all the sync files
# TODO: Allow an offset and scale to be applied to the frame numbers
import os
import subprocess

# Each frame is actually a pair - that one and the one following it.
# Ideally, this should span a hard cut in the movie, which makes frame
# counting easy. NOTE: This may take a couple of minutes of chugging,
# and may not show much output on the console while it does it.
frames = { # Keep these in order of frame number
	2839: "find_console", # When Joy finds the console for the first time
	158682: "cat_yelp", # The cat from the end credits - from console to yelp
}

expr = "+".join("eq(n\\,%d)+eq(n\\,%d)" % (frm, frm+1) for frm in frames)
tmpfn = "sync/tmp%d.png"
subprocess.check_call([
	"ffmpeg", "-y", "-i", "InsideOut.mkv",
	"-vf", "select=%s,tile=2x1" % expr,
	"-vframes", str(len(expr)), "-s", "640x180",
	"-vsync", "0", tmpfn,
])
for idx, name in enumerate(frames.values(), 1):
	os.rename(tmpfn % idx, "sync/%s.png" % name)
