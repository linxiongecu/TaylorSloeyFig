# r script for lidar point cloud plot.
# package
library(lidR)
# data folder 
folder_path <- "C:/Users/lxiong/UMD/Review/Fig"
harney <- file.path(folder_path, 'FL_20170328_Harney_River_l0s3.las')

las <- readLAS(harney)
print(las)
# clip_circle(las, xcenter, ycenter, radius, ...)
library(sp)
x <- cbind(-81.1337, 25.4227) 
cord.dec = SpatialPoints(x, proj4string=CRS("+proj=longlat"))
center <- coordinates(spTransform(cord.dec, CRS("+init=epsg:32617")))
xcenter <- center[1]
ycenter <- center[2]
plot_field <- clip_circle(las, xcenter, ycenter, 12.5)
plot(plot_field, bg = "white", size = 5, axis= TRUE, legend = TRUE)

flamingo <- file.path(folder_path, 'FL_20171206_FIA8_l0s9.las')
las <- readLAS(flamingo)
print(las)
# clip_circle(las, xcenter, ycenter, radius, ...)
library(sp)
x <- cbind(-80.9105185, 25.1649753) 
cord.dec = SpatialPoints(x, proj4string=CRS("+proj=longlat"))
center <- coordinates(spTransform(cord.dec, CRS("+init=epsg:32617")))
xcenter <- center[1]
ycenter <- center[2]
plot_field_low <- clip_circle(las, xcenter, ycenter, 12.5)
plot(plot_field_low, bg = "white", size = 5, axis= TRUE, legend = TRUE)

### out to las. 
#writeLAS(las, file, index = FALSE)
writeLAS(plot_field_low, "C:/Users/lxiong/UMD/Review/Fig/low_plot.las")
writeLAS(plot_field, "C:/Users/lxiong/UMD/Review/Fig/high_plot.las")



install.packages("plotly")
library(plotly)

df <- data.frame(
  X = plot_field_low$X - 509000,
  Y = plot_field_low$Y - 2783000,
  Z = plot_field_low$Z
)
# Save DataFrame to CSV file
write.csv(df, "low.csv", row.names = FALSE)

df <- data.frame(
  X = plot_field$X - 486500,
  Y = plot_field$Y - 2811700,
  Z = plot_field$Z
)
write.csv(df, "high.csv", row.names = FALSE)

install.packages("scatterplot3d") # Install
library("scatterplot3d") # load
scatterplot3d(df, pch = 20, color=rainbow(length(df$Z)),angle = 35)
