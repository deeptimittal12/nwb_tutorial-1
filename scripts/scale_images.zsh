#!/usr/bin/env zsh

convert $1/flow_chart.png -resize 25% $2/flow_chart.png
convert $1/hdfsnap_processing.png -resize 25% $2/hdfsnap_processing.png
convert $1/hdfsnap_final.png -resize 25% $2/hdfsnap_final.png
convert $1/hdfsnap_closed.png -resize 25% $2/hdfsnap_closed.png
