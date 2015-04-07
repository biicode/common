// Interaccion.cpp: implementation of the Interaccion class.
//
//////////////////////////////////////////////////////////////////////

#include "interaccion.h" 
#include <math.h> 
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

Interaccion::Interaccion()
{

}

Interaccion::~Interaccion()
{

}

void Interaccion::Rebote(Hombre &h, Caja c)
{
	float xmax=c.suelo.limite2.x-1;
	float xmin=c.suelo.limite1.x+1;
	if(h.posicion.x>xmax)
		h.posicion.x=xmax;
	if(h.posicion.x<xmin)
		h.posicion.x=xmin;
}
void Interaccion::Rebote(Esfera& e, Caja c)
{
	Rebote(e,c.suelo);
	Rebote(e,c.techo);
	Rebote(e,c.pared_dcha);
	Rebote(e,c.pared_izq);
}
bool Interaccion::Rebote(Esfera &e, Pared p)
{
	Vector2D dir;
	float dif=p.Distancia(e.posicion,&dir)-e.radio;
	if(dif<=0.0f)
		{
		Vector2D v_inicial=e.velocidad;
		e.velocidad=v_inicial-dir*2.0*(v_inicial*dir);
		e.posicion=e.posicion-dir*dif;
		return true;
		}
	return false;
}

bool Interaccion::Rebote(Esfera &esfera1, Esfera &esfera2)
{
	//Vector que une los centros
	Vector2D dif=esfera2.posicion-esfera1.posicion;
	float d=dif.modulo();
	float dentro=d-(esfera1.radio+esfera2.radio);

	if(dentro<0.0f)//si hay colision
	{
		//El modulo y argumento de la velocidad de la pelota1
		float v1=esfera1.velocidad.modulo();
		float ang1=esfera1.velocidad.argumento();

		//El modulo y argumento de la velocidad de la pelota2
		float v2=esfera2.velocidad.modulo();
		float ang2=esfera2.velocidad.argumento();
	
		//el argumento del vector que une los centros
		float angd=dif.argumento();	
		
		//Separamos las esferas, lo que se han incrustado
		//la mitad cada una
		Vector2D desp(dentro/2*(float)cos(angd),dentro/2*(float)sin(angd));	
		esfera1.posicion=esfera1.posicion+desp;
		esfera2.posicion=esfera2.posicion-desp;

		angd=angd-3.14159f/2;//la normal al choque
	
		//El angulo de las velocidades en el sistema relativo antes del choque
		float th1=ang1-angd;	
		float th2=ang2-angd;
		
		//Las componentes de las velocidades en el sistema relativo ANTES del choque
		float u1x=v1*(float)cos(th1);
		float u1y=v1*(float)sin(th1);
		float u2x=v2*(float)cos(th2);
		float u2y=v2*(float)sin(th2);	
	
		//Las componentes de las velocidades en el sistema relativo DESPUES del choque
		//la componente en X del sistema relativo no cambia
		float v1x=u1x;
		float v2x=u2x;

		//en el eje Y, rebote elastico
		float m1=esfera1.radio;
		float m2=esfera2.radio;
		float py=m1*u1y+m2*u2y;//Cantidad de movimiento inicial ejey
		float ey=m1*u1y*u1y+m2*u2y*u2y;//Energia cinetica inicial ejey
	
		//los coeficientes y discriminante de la ecuacion cuadrada
		float a=m2*m2+m1*m2;
		float b=-2*py*m2;
		float c=py*py-m1*ey;	
		float disc=b*b-4*a*c;
		if(disc<0)disc=0;

		//las nuevas velocidades segun el eje Y relativo
		float v2y=(-b+(float)sqrt(disc))/(2*a);
		float v1y=(py-m2*v2y)/m1;
		
		//Modulo y argumento de las velocidades en coordenadas absolutas
		float modv1,modv2,fi1,fi2;
		modv1=(float)sqrt(v1x*v1x+v1y*v1y);
		modv2=(float)sqrt(v2x*v2x+v2y*v2y);
		fi1=angd+(float)atan2(v1y,v1x);
		fi2=angd+(float)atan2(v2y,v2x);
		
		//Velocidades en absolutas despues del choque en componentes
		esfera1.velocidad.x=modv1*(float)cos(fi1);
		esfera1.velocidad.y=modv1*(float)sin(fi1);
		esfera2.velocidad.x=modv2*(float)cos(fi2);
		esfera2.velocidad.y=modv2*(float)sin(fi2);	

		return true;
	}
	return false;
}

bool Interaccion::Colision(Esfera e, Hombre h)
{
	Vector2D pos=h.GetPos(); //la posicion del hombre de la base
	pos.y+=h.GetAltura()/2.0f; //posicion del centro

	float distancia=(e.posicion-pos).modulo();
	if(distancia<e.radio)
		return true;	
	return false;
}
bool Interaccion::Colision(Gancho d, Pared p)
{
	Vector2D pos=d.GetPos();
	float dist=p.Distancia(pos);
	if(dist<d.GetRadio())
		return true;
	return false;
}
bool Interaccion::Colision(Gancho d, Caja c)
{
	//utilizo la funcion anterior
	return Colision(d,c.techo);
}
bool Interaccion::Colision(Gancho d, Esfera e)
{
	Pared aux; //Creamos una pared auxiliar
	Vector2D p1=d.posicion;
	Vector2D p2=d.origen;
	aux.SetPos(p1.x,p1.y,p2.x,p2.y); //Que coincida con el disparo.
	float dist=aux.Distancia(e.posicion); //para calcular su distancia al centro
	if(dist<e.radio)
		return true;
	return false;
}
bool Interaccion::Colision(Lanza d, Pared p)
{
	Vector2D pos=d.GetPos();
	float dist=p.Distancia(pos);
	if(dist<0.25)
		return true;
	return false;
}
bool Interaccion::Colision(Lanza d, Caja c)
{
	//utilizo la funcion anterior
	return Colision(d,c.techo);
}
bool Interaccion::Colision(Lanza d, Esfera e)
{
	Pared aux; //Creamos una pared auxiliar
	Vector2D p1=d.posicion;
	Vector2D p2=p1;
	p1.y-=d.largo;

	aux.SetPos(p1.x,p1.y,p2.x,p2.y); //Que coincida con el disparo.
	float dist=aux.Distancia(e.posicion); //para calcular su distancia al centro
	if(dist<e.radio)
		return true;
	return false;
}
bool Interaccion::Colision(Hombre h, Bonus b)
{
	Vector2D pos=h.GetPos(); //la posicion del hombre de la base
	pos.y+=h.GetAltura()/2.0f; //posicion del centro

	float distancia=(b.posicion-pos).modulo();
	if(distancia<h.GetAltura()/2.0f)
		return true;	
	return false;
}
