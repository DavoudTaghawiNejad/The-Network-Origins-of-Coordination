ffmpeg -f image2 -r 1/0.5 -i movie_%05d.png -c:v libx264 -pix_fmt yuv420p out.mp4
