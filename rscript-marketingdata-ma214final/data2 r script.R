trynsave = read.csv("Try-N-Save.csv")
library(ggplot2)


tvsales = trynsave[trynsave$Media == "TV", "Sales"]
avgtvsales = mean(tvsales)
radiosales = trynsave[trynsave$Media == "Radio", "Sales"]
avgradiosales = mean(radiosales)

boxplot(Sales~Media, data = trynsave)



qqnorm(residuals(fit))
qqline(residuals(fit))

plot(predict(fit), residuals(fit))

fit = aov(Sales~Media + Location, data = trynsave)
summary(fit)




#ChatGPT ggplot barchart
aggregate_data <- aggregate(Sales ~ Media + Location, trynsave, sum)


ggplot(aggregate_data, aes(x = Media, y = Sales, fill = Location)) +
  geom_bar(stat = "identity", position = "dodge") +
  labs(title = "Sales by Media Type and Location",
       x = "Media Type",
       y = "Total Sales (in thousands)",
       fill = "Location")
 
