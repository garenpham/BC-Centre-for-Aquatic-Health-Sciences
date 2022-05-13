#!/usr/bin/env Rscript

# If this pre-install setup script works as intended, pacman wont be needed
install.packages("pacman")
pacman::p_load(stringr, plyr, dplyr, readr, vegan, devtools, remotes, reshape2, ggtext, RColorBrewer)
remotes::install_github("gavinsimpson/ggvegan")
