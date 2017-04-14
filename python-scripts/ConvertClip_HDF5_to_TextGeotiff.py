#Code produced through UMBC's Joint Center for Earth Systems Technology
#If you have any questions or concerns regarding the following script, please contact Amanda Rumsey at arumsey@umbc.edu
#The purpose of this code is to convert datasets within imerg hdf files to txt files and to clip the files by a bounding box specified by the user

#start of the program
print("starting the conversion from hdf to txt file:")
print("")

#import all necessary packages
print("importing packages")
import os
import glob
import numpy as np
import h5py
import gdal
import math
import osr
print("packages imported")
print("")

#list of methods
#this method will print all of the names of hdf internal files
print("defining methods")
def printname(name):
 print(name)
print("method definitions complete")
print("")

#assign current working directory
dir=os.getcwd()
print("the current directory is: "+dir)
print("")

#make directory folder (if it does not already exist) and directory variable for output text files
print("creating a directories for output text and raster files")
txtdir= os.path.join(dir+os.sep, 'text_files')
if not os.path.exists(txtdir):
 os.makedirs(txtdir)
print("text file directory created")
print("")

rasdir= os.path.join(dir+os.sep, 'raster_files')
if not os.path.exists(rasdir):
 os.makedirs(rasdir)
print("raster file directory created")
print("")

#list of hdf files to be converted
print("list of hdf files")
hdflist=glob.glob(os.path.join('*.hdf5'))
hdflist2=glob.glob(os.path.join('*-h5'))
hdflist3=glob.glob(os.path.join('*.h5'))

hdflist4=glob.glob(os.path.join('*-H5'))
hdflist5=glob.glob(os.path.join('*.H5'))
hdflist6=glob.glob(os.path.join('*.HDF5'))

hdflist=hdflist+hdflist2+hdflist3+hdflist4+hdflist5+hdflist6
print(hdflist)
print("")

'''
#available datasets in hdf files
print("available datasets in HDF5 files: ")
singlehdflist=hdflist[0]
insidehdffile=h5py.File(singlehdflist,"r+")
insidehdffile.visit(printname)
insidehdffile.close()
print("")
'''

#user input for clipping capability
print("enter the bounding box in decimal degrees")
print("enter northern latitude: ")
bottom=input()
print("enter southern latitude: ")
top=input()
print("enter eastern longitude: ")
right=input()
print("enter western longitude: ")
left=input()
print("")

#datatype conversion
#this loop clips the data by the user input bounding box outputs
#this loop outputs the indvidual lat long and precip datasets available within the hdf file as indivdual text files
#this loop also orgainzed the lat long and precip data and combines it into a sigle textfile
for hdffile in hdflist:
	#clipping and datatype conversion
	#read and write hdf file
	print("reading the hdf file: "+hdffile)
	currenthdffile=h5py.File(hdffile,"r+")
	print("reading hdf file complete")
	print("")

	#data retrieval
	#This is where you extract the datasets you want
	#you can add more variables if you would like
	#this is done in the format varible=hdffilename['dataset']
	print("creating arrays for latitude, longitude and surface precipitation")
	lat=currenthdffile['Grid/lat']
	long=currenthdffile['Grid/lon']
	precip=currenthdffile['Grid/precipitationCal']
	latitude=np.array(lat)
	longitude=np.array(long)
	precipitation=np.array(precip)
	print("creation of arrays complete")
	print("")

	#identifying clipping boundaries
	print("identifying clipping boundaries")
	topindex = (np.abs(latitude-float(top))).argmin()
	bottomindex = (np.abs(latitude-float(bottom))).argmin()
	leftindex = (np.abs(longitude-float(left))).argmin()
	rightindex = (np.abs(longitude-float(right))).argmin()
	print("")

	#listing coordinates
	print("bounding top coordinate: "+str(top))
	print("bounding bottom coordinate: "+str(bottom))
	print("bounding left coordinate: "+str(left))
	print("bounding right coordinate: "+str(right))
	print("")
	print("closest top coordinate: "+str(latitude[topindex]))
	print("closest bottom coordinate: "+str(latitude[bottomindex]))
	print("closest left coordinate: "+str(longitude[leftindex]))
	print("closest right coordinate: "+str(longitude[rightindex]))
	print("")
	print("top index: "+ str(topindex))
	print("bottom index: "+ str(bottomindex))
	print("left index: "+ str(leftindex))
	print("right index: "+ str(rightindex))

	#clipping
	print("clipping")
	finallat=latitude[topindex:bottomindex+1]
	precip1=precipitation[leftindex:rightindex+1]
	finallong=longitude[leftindex:rightindex+1]
	finalprecip=precip1[:,topindex:bottomindex+1]
	print("")

	#align lat long and precip information for combined text file
	print("combining lat long and precip date")
	preciprows=len(finalprecip[:1,])
	precipcolumns=len(finalprecip[1,:])
	listsize=(preciprows*precipcolumns)+1
	preciplist=[0]*listsize
	latlist=[0]*listsize
	longlist=[0]*listsize
	preciplist[0]="Precipitation"
	latlist[0]="Latitude"
	longlist[0]="Longitude"
	index=0
	for i in range(preciprows):
		for j in range(precipcolumns):
			index=index+1
			latlist[index]=finallat[j]
			longlist[index]=finallong[i]
			preciplist[index]=finalprecip[i,j]
	print("combination of data complete")
	print("")
##############
	print("writing raster")
	print("")
	def array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):

		cols = array.shape[1]
		rows = array.shape[0]
		originX = rasterOrigin[0]
		originY = rasterOrigin[1]

		driver = gdal.GetDriverByName('GTiff')
		outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
		outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
		outband = outRaster.GetRasterBand(1)
		outband.WriteArray(array)
		outRasterSRS = osr.SpatialReference()
		outRasterSRS.ImportFromEPSG(4326)
		outRaster.SetProjection(outRasterSRS.ExportToWkt())
		outband.FlushCache()


	def main(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):
		reversed_arr =np.flipud(np.rot90(array))  ####array[::-1] # reverse array so the tif looks like the array
		array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,reversed_arr) # convert array to raster
		#array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array) # convert array to raster


	if __name__ == "__main__":
		rasterOrigin = (finallong[0],finallat[0])
		pixelWidth = round(long[1]-long[0],5)
		pixelHeight = round(lat[1]-lat[0],5)
		newRasterfn = os.path.join(rasdir, hdffile[:-5]+"_subset.tif")
		array = finalprecip


		main(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array)

	print("raster writing complete")
	print("")
###############
	#converting to text file
	print("converting arrays to text files")
	outputlat=os.path.join(txtdir, hdffile[:-5]+"_lat_clipped.txt")
	outputlong=os.path.join(txtdir, hdffile[:-5]+"_lon_clipped.txt")
	outputprecip=os.path.join(txtdir, hdffile[:-5]+"_precip_clipped.txt")
	outputcombined=os.path.join(txtdir, hdffile[:-5]+"_precip_combined.txt")
	np.savetxt(outputlat,finallat,fmt='%f')
	np.savetxt(outputlong,finallong,fmt='%f')
	np.savetxt(outputprecip,finalprecip,fmt='%f')
	with open(outputcombined,"w") as file:
		for i in range(finallat.shape[0]):
			for m in range(finallong.shape[0]):
				out_string=""
				out_string=str(finallat[i])
				file.write(out_string)
				out_string=","+str(finallong[m])
				file.write(out_string)
				out_string=","+str(finalprecip[m,i])
				file.write(out_string)
				out_string="\n"
				file.write(out_string)

	print("")

print("script complete!")


