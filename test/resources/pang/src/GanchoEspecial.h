// GanchoEspecial.h: interface for the GanchoEspecial class.
//
//////////////////////////////////////////////////////////////////////

#if !defined(afx_ganchoespecial_h__7c467ee3_be4d_4ae3_8466_b1f35ae33f97__included_)
#define afx_ganchoespecial_h__7c467ee3_be4d_4ae3_8466_b1f35ae33f97__included_

#if _msc_ver > 1000
#pragma once
#endif // _msc_ver > 1000

#include "gancho.h" 

class GanchoEspecial : public Gancho  
{
public:
	void Dibuja();
	GanchoEspecial();
	virtual ~GanchoEspecial();

};

#endif // !defined(afx_ganchoespecial_h__7c467ee3_be4d_4ae3_8466_b1f35ae33f97__included_)

