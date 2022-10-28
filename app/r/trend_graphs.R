library(ggplot2)
library(dplyr)
library(stringr)

# Load data

# This will have to be change later 2022-10-26
data <- read.csv(file = 'app/r/trend_long.csv')
data$date_collected <- as.Date(data$date_collected)


specify_decimal <- function(x, k) trimws(format(round(x, k), nsmall=k))
#Plot
png(filename = "app/static/img/trend_data.png")
data %>%
  tail(10) %>%
  ggplot( aes(x=date_collected, y=fraction_total_reads, color=name)) +
  xlab(str_glue("Daterange \n {data$date_collected[1]} to {data$date_collected[nrow(data)]}")) + ylab("Relative Abundance") +
    geom_line() +
    geom_point() +
    geom_text(
    data = . %>% filter(fraction_total_reads == data$fraction_total_reads),
    aes(label = specify_decimal(fraction_total_reads, 4)),
    vjust = "inward", hjust = "inward",
    show.legend = FALSE) +
    ggtitle("Relative Abundance Graph (Species/Date range)")
dev.off()
