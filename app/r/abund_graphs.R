#!/usr/bin/env Rscript

###R script for creating abundance graphs from relative abundance data.###

#Load necessary packages:
library("stringr")
library("plyr")
library("dplyr")
library("readr")
library("vegan")
library("devtools")
library("ggvegan")
library("reshape2")
library("ggtext")
library("RColorBrewer")

colors <- read.table(file = "app/r/colors.tsv",
                     sep = ",", header = TRUE, fill = TRUE,
                     colClasses = c("NULL", "character")) %>%
  as_tibble()
colors = collect(select(colors, mycolours))[[1]]

rel_abund_long <- read.table(file = "app/r/rel_abund_long.csv", 
                              sep = ",", header = TRUE)          

#Stops the script from outputting all plots to a .pdf
pdf(NULL)

#Abundance graph with all samples separate (NOTE = colors won't work unless < 46 samples)
ggplot(rel_abund_long, aes(x = sample_ID, y = value, fill = genus)) + 
  geom_bar(stat = "identity") +
  labs(x=NULL, 
       y="Relative Abundance (%)") +
  theme_classic() +
  theme(legend.text = element_text(face="italic"),
        legend.title = element_blank(),
        legend.key.size = unit(10, "pt"),
        axis.text.x = element_text(angle = 45, vjust = 1, hjust = 1)) +
  scale_fill_manual(values = colors)

ggsave(filename="data_abund_separate.png", path="app/static/img/", device="png", width=9, height=4)

#Abundance graph grouped (NOTE = colors won't work unless < 46 samples)
ggplot(rel_abund_long, aes(x = sample_ID, y = value, fill = genus)) + 
  geom_bar(stat = "identity") +
  geom_col(width=1) +
  expand_limits(y=0) +
  labs(x=NULL, 
       y="Relative Abundance (%)") +
  facet_grid(~date, scale = "free_x", space = "free", switch = "x") +
  theme_classic() +
  theme(legend.text = element_text(face="italic"),
        legend.title = element_blank(),
        legend.key.size = unit(10, "pt"),
        axis.text.x = element_blank(),
        axis.ticks.x = element_blank(),
        strip.background = element_blank(),
        strip.text.x = element_text(angle = 80),
        strip.placement = "outside") +
  scale_fill_manual(values = colors)

ggsave(filename="data_abund_grouped.png", path="app/static/img/", device="png", width=6, height=4)
