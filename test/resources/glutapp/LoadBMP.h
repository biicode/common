/*
 * LoadBMP.cpp: Load a 24-bit BMP image into imageData array.
 */
#include <iostream> 
#include <stdio.h> 
#include <stdlib.h> 

using namespace std;
   
#pragma pack(2)  // 2 byte packing
typedef struct {
   unsigned char magic1;   // 'B'
   unsigned char magic2;   // 'M'
   unsigned int size;      // File size
   unsigned short int reserved1, reserved2;
   unsigned int pixelOffset; // offset to image data
} Header;
   
#pragma pack() // default packing
typedef struct {
   unsigned int size;    // Size of this info header
   int cols, rows;       // cols and rows of image
   unsigned short int planes;
   unsigned short int bitsPerPixel; // number of bits per pixel
   unsigned int compression;
   unsigned int cmpSize;
   int xScale, yScale;
   unsigned int numColors;
   unsigned int importantColors;
} InfoHeader;
   

//returns 
unsigned char* loadBMP(char *filename,int& imageRows,int& imageCols) 
{
   Header header;
   InfoHeader infoHeader;
   FILE *fin;
   fin = fopen(filename, "rb+");
   if (fin == NULL) {
	   cout<<"Cannot open: "<<filename<<endl;
	   return 0;
   }
   
   // Process header
   fread(&header, sizeof(header), 1, fin);
   // Test if this is really a BMP file
   if (!((header.magic1 == 'B') && (header.magic2 == 'M'))) {
      cout<<"Not a valid BMP: "<< filename<<endl;
      return 0;
   }
   
   // Process Info Header
   fread(&infoHeader, sizeof(infoHeader), 1, fin);
   // Test if this is a 24-bit uncompressed BMP file
   if (infoHeader.bitsPerPixel != 24 || infoHeader.compression) {
	   cout<<"Cannot handle this type of BMP file "<<filename<<" bits: "<<infoHeader.bitsPerPixel<<endl;
      return 0;
   }
   
   imageRows = infoHeader.rows;
   imageCols = infoHeader.cols;
  unsigned char* imageData = (unsigned char*)malloc(3 * sizeof(unsigned char) * infoHeader.cols * infoHeader.rows);
   int count = 0;
   for (int row = 0; row < infoHeader.rows; row++) {
      for (int col = 0; col < infoHeader.cols; col++) {
			 fread(imageData + count + 2, sizeof(unsigned char), 1, fin); // blue 
			 fread(imageData + count + 1, sizeof(unsigned char), 1, fin); // green
			 fread(imageData + count, sizeof(unsigned char), 1, fin);     // red
			 count = count + 3;
      }
   }
   return imageData;
}
