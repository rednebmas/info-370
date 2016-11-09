# Nick Nordale

#install.packages("tidyr")
#install.packages("dplyr")
#library(tidyr)
#library(dplyr)

reviews <- read.table("~/reviews.csv", header = TRUE, sep = ',', quote="\"", comment.char = "", as.is = TRUE)
businesses <- read.table("~/info-370/data/businesses.csv", header = TRUE, sep = ',', quote="\"", comment.char = "", as.is = TRUE)

merged <- merge(businesses, reviews, by.x = "id", by.y = "business", all = FALSE)
#write.table(merged, file = "~/merged_table.csv", sep = ",")

#merged %>%
#  mutate(categories = strsplit(categories, ",")) %>% 
#  unnest(categories)

split_categories <- strsplit(merged$categories, ",")
id_with_category <- data.frame("id" = rep(merged$id, sapply(split_categories, length)), categories = unlist(split_categories))
#breakout_by_category <- merge(id_with_category, merged, by.x = "id", by.y = "id", all.x = TRUE)

#write.table(breakout_by_category, file = "~/breakout_by_category.csv", sep = ",")
