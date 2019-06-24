# Regenerate all the sync files
# TODO: Allow an offset and scale to be applied to the frame numbers
import subprocess

# Each frame is actually a pair - that one and the one following it.
# Ideally, this should span a hard cut in the movie, which makes frame
# counting easy.
frames = {
	2839: "find_console", # When Joy finds the console for the first time
}

for frm, desc in frames.items():
	subprocess.check_call([
		"ffmpeg", "-y", "-i", "InsideOut.mkv",
		"-vf", "select=gte(n\\,%d),tile=2x1" % frm,
		"-vframes", "1", "-s", "640x180",
		"sync/%s.png" % desc,
	])
