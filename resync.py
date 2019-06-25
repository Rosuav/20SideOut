# Regenerate all the sync files
# TODO: Allow an offset and scale to be applied to the frame numbers
import os
import subprocess

# Each frame is actually a pair - that one and the one following it.
# Ideally, this should span a hard cut in the movie, which makes frame
# counting easy. NOTE: This may take a couple of minutes of chugging,
# and may not show much output on the console while it does it.
frames = [
	2839, # When Joy finds the console for the first time
	158682, # The cat from the end credits - from console to yelp
]

frames.sort() # The renaming at the end depends on these being in order.

expr = "+".join("eq(n\\,%d)+eq(n\\,%d)" % (frm, frm+1) for frm in frames)
tmpfn = "sync/tmp%d.png"
subprocess.check_call([
	"ffmpeg", "-y", "-i", "InsideOut.mkv",
	"-vf", "select=%s,tile=2x1" % expr,
	"-vframes", str(len(expr)), "-s", "640x180",
	"-vsync", "0", tmpfn,
])
for idx, frm in enumerate(frames, 1):
	os.rename(tmpfn % idx, "sync/%d.png" % frm)

# TODO: Once ffmpeg builds that include the frame_pts parameter become more
# common, ditch the rename step at the end in favour of "-frame_pts","1".
# That may also remove the need to sort the frame list, although that's not
# expensive.
