// OpenGL.h: interface for the OpenGL class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_opengl_h__2b1af605_baa9_4751_9d16_b7310454f0b6__included_)
#define afx_opengl_h__2b1af605_baa9_4751_9d16_b7310454f0b6__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#pragma warning (disable: 4786)

#include <string> 
#include <vector> 

class OpenGL  
{
public:
	OpenGL();
	virtual ~OpenGL();
	static void PrintText(char *mensaje, int x, int y, unsigned char r=255, unsigned char g=255, unsigned char b=255);

	static unsigned int LoadTexture(char* texture_file);
	static void DeleteTextures();

protected:
	static std::vector<std::string> nombre_texturas;
	static std::vector<unsigned int> id_texturas;
};

#endif // !defined(afx_opengl_h__2b1af605_baa9_4751_9d16_b7310454f0b6__included_)

