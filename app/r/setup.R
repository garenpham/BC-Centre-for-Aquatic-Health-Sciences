#!/usr/bin/env Rscript

install.packages("pacman")
pacman::p_load(stringr, plyr, dplyr, readr, vegan, devtools, remotes, reshape2, ggtext, RColorBrewer)
remotes::install_github("gavinsimpson/ggvegan")
