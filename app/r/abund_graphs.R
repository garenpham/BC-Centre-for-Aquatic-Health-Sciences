#!/usr/bin/env Rscript

###R script for creating abundance graphs from relative abundance data.###

#Before starting, make sure that 'ALL_data_abund.csv' and 'metadata.csv' files are up to date and any new data added using the 'new_data.R' script.

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

# #Load files
# data_abund_sampleid <- read.table(file = "app/r/ALL_data_abund.csv",
#                                   sep = ",", header = TRUE)
# names(data_abund_sampleid)[1] <- "sample_ID"

# metadata <- read.table(file = "app/r/metadata.csv",
#                        sep = ",", header = TRUE,
#                        colClasses = c("NULL", "character", "character", "character", "character"))

# #Filter samples to include specific data
# data_abund_sampleid2 <- data_abund_sampleid %>% filter(str_detect(sample_ID, "SBio"))
# metadata2 <- metadata %>% filter(str_detect(sample_ID, "SBio"))

# #filter out columns with abundance < 0.01, add unclassified column 
# rel_abund_filter <- data_abund_sampleid2 %>% select_if(~any(. > 0.01))
# rel_abund_filter
# rel_abund_filter$Unclassified_Bacteria <- 1 - rowSums(rel_abund_filter[, -1])

# #Make long table for abundance graph and set order of variables on x axis
# rel_abund_long <- melt(rel_abund_filter, id.vars = "sample_ID", variable.name = "genus")
# rel_abund_long$value <- rel_abund_long$value
# rel_abund_long
# rel_abund_long["date"] = metadata2["date"]
# rel_abund_long$date <- factor(rel_abund_long$date, levels = c("03-Aug",
#                                                               "24-Aug",
#                                                               "13-Sep"
#                                                               ))

colors <- read.table(file = "app/r/colors.tsv",
                     sep = ",", header = TRUE, fill = TRUE,
                     colClasses = c("NULL", "character")) %>%
  as_tibble()
colors = collect(select(colors, mycolours))[[1]]

rel_abund_long <- read.table(file = "app/r/rel_abund_long.csv", 
                              sep = ",", header = TRUE)          
rel_abund_long$date <- factor(rel_abund_long$date, levels = c("Aug-3-21",
                                                              "Aug-24-21",
                                                              "Sep-13-21",
                                                              "Sep-27-21",
                                                              "Oct-13-21",
                                                              "Oct-27-21"
                                                              ))
pdf(NULL)
#Abundance plot with all samples separate (NOTE = colors won't work unless <46 samples)
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

#Abundance plot grouped (NOTE = colors won't work unless <46 samples)
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
        strip.text.x = element_text(angle = 45),
        strip.placement = "outside") +
  scale_fill_manual(values = colors)

ggsave(filename="data_abund_grouped.png", path="app/static/img/", device="png", width=6, height=4)
