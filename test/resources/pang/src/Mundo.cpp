#include "mundo.h" 

#include "interaccion.h" 
#include "ganchoespecial.h" 
#include "lanza.h" 
#include "factoria.h" 

#include <math.h> 
#include "%GLUTAPP_USER%/glutapp/opengl.h"
#include "%GLUT_USER%/glut/include/gl/glut.h" 

#include <stdlib.h> 

Mundo::Mundo()
{
	bonus=0;
}
Mundo::~Mundo()
{
	esferas.DestruirContenido();
	disparos.DestruirContenido();
}
void Mundo::RotarOjo()
{
	float dist=sqrt(x_ojo*x_ojo+z_ojo*z_ojo);
	float ang=atan2(z_ojo,x_ojo);
	ang+=0.05f;
	x_ojo=dist*cos(ang);
	z_ojo=dist*sin(ang);
}
void Mundo::Dibuja()
{
	gluLookAt(x_ojo, y_ojo, z_ojo,  // posicion del ojo
			0.0, y_ojo, 0.0,      // hacia que punto mira  (0,0,0) 
			0.0, 1.0, 0.0);      // definimos hacia arriba (eje Y)    

	//aqui es donde hay que poner el codigo de dibujo
	caja.Dibuja();
	hombre.Dibuja();
	disparos.Dibuja();
	plataforma.Dibuja();
	if(bonus)
		bonus->Dibuja();
	esferas.Dibuja();
}

void Mundo::Mueve()
{
	for(int i=esferas.GetNumero()-1;i>=0;i--)
	{
		for(int j=0;j<disparos.GetNumero();j++)
		{
			int tipo=disparos[j]->GetTipo();
			if(tipo==GANCHO || tipo==GANCHO_ESPECIAL)
			{
				Gancho* g=(Gancho*)disparos[j];
				if(Interaccion::Colision(*g,*esferas[i]))
				{
					Esfera* e=esferas[i]->Dividir();
					if(e==0) //no division
						esferas.Eliminar(esferas[i]);
					else
					{
						if(!bonus)
						{
							bonus=new Bonus;
							bonus->SetPos(e->GetPos());
						}
						esferas.Agregar(e);
					}
					disparos.Eliminar(j);
					break;
				}
			}
			if(tipo==LANZA)
			{
				Lanza* g=(Lanza*)disparos[j];
				if(Interaccion::Colision(*g,*esferas[i]))
				{
					esferas.Eliminar(i);
					disparos.Eliminar(j);
					break;
				}
			}
		}
	}

	hombre.Mueve(0.025f);
	if(bonus)
		bonus->Mueve(0.025f);

	disparos.Mueve(0.025f);
	disparos.Colision(caja);
	disparos.Colision(plataforma);

	esferas.Mueve(0.025f);
	esferas.Rebote();
	esferas.Rebote(plataforma);
	esferas.Rebote(caja);
	Esfera *aux=esferas.Colision(hombre);
	if(aux!=0)
	{
		if(hombre.GetNumBonus()==0)
			impacto=true;
		hombre.SetNumBonus(0);
		esferas.Eliminar(aux);
	}
	Interaccion::Rebote(hombre,caja);

	if(bonus)
	{
		if(Interaccion::Colision(hombre,*bonus))
		{
			hombre.IncrementaNumBonus();
			delete bonus;
			bonus=0;
		}
		else if(bonus->GetPos().y<0)
		{
			delete bonus;
			bonus=0;
		}
	}
}



void Mundo::TeclaEspecial(unsigned char key)
{
	switch(key)
	{
	case GLUT_KEY_LEFT:
		hombre.SetVel (-5.0f, 0.0f);
		break;
	case GLUT_KEY_RIGHT:
		hombre.SetVel (5.0f, 0.0f);
		break;
	}
}

void Mundo::Tecla(unsigned char key)
{
	switch(key)
	{
		case ' ': if(disparos.GetNumero()<MAX_DISPAROS)
				{
					Disparo* d=Factoria::CrearDisparo(hombre);
					disparos.Agregar(d);
				}
				break;	
	}
}
void Mundo::Inicializa()
{
	impacto=false;
	
	x_ojo=0;
	y_ojo=7.5;
	z_ojo=30;
		
	nivel=0;
	CargarNivel();
}

bool Mundo::CargarNivel()
{
	
	nivel++;
	//inicializar
	hombre.SetPos(0,0);
	esferas.DestruirContenido();
	disparos.DestruirContenido();
	if(bonus)
	{
		delete bonus;
		bonus=0;
	}

	if(nivel==1)
	{
		//bii://alpes.bmp
		//bii://arena.bmp
		//bii://tierra.bmp
		//bii://ladrillos.bmp
		//bii://agua.bmp
		//bii://muro.bmp
		caja.SetFondo("%USER%/pang/bin/alpes.bmp");
		caja.SetFondoParedes("%USER%/pang/bin/arena.bmp");
		plataforma.SetFondo("%USER%/pang/bin/tierra.bmp");
		plataforma.SetPos(-5.0f,9.0f,5.0f,9.0f);
		Esfera *e1=new Esfera(1.5f,2,4,5,15);
		e1->SetColor(0,0,255);
		esferas.Agregar(e1); //esfera
	}
	if(nivel==2)
	{
		caja.SetFondo("%USER%/pang/bin/tierra.bmp");
		caja.SetFondoParedes("%USER%/pang/bin/muro.bmp");
		plataforma.SetFondo("%USER%/pang/bin/ladrillos.bmp");
		plataforma.SetPos(-3.0f,6.0f,3.0f,6.0f);
		plataforma.SetColor(255,0,0);
		EsferaPulsante* e3=new EsferaPulsante;
		e3->SetPos(0,12);
		e3->SetVel(5,3);
		esferas.Agregar(e3);
	}
	if(nivel==3)
	{
		caja.SetFondo("%USER%/pang/bin/agua.bmp");
		caja.SetFondoParedes("%USER%/pang/bin/arena.bmp");
		plataforma.SetPos(-10.0f,12.0f,4.0f,10.0f);
		plataforma.SetColor(255,0,255);
		for(int i=0;i<5;i++)
		{
			Esfera* aux=new Esfera(1.5,-5+i,12,i,5);
			aux->SetColor(i*40,0,255-i*40);
			esferas.Agregar(aux);
		}
	}
	if(nivel>3 && nivel<=7)
	{
		if(rand()%2)
			caja.SetFondo("%USER%/pang/bin/muro.bmp");
		else
			caja.SetFondo("%USER%/pang/bin/ladrillos.bmp");
	
		if(rand()%2)
			caja.SetFondoParedes("%USER%/pang/bin/agua.bmp");
		else
			caja.SetFondoParedes("%USER%/pang/bin/tierra.bmp");
	
		plataforma.SetPos(-5.0f,9.0f,5.0f,8.5f);
		for(int i=0;i<nivel;i++)
		{
			Esfera* e=Factoria::CrearEsfera(caja);
			esferas.Agregar(e);
		}
	}
	if(nivel==8)
	{
		caja.SetFondo("%USER%/pang/bin/agua.bmp");
		caja.SetFondoParedes("%USER%/pang/bin/agua.bmp");
		plataforma.SetPos(-10.0f,25.0f,4.0f,25.0f);
		plataforma.SetColor(255,0,255);
		for(int i=0;i<15;i++)
		{
			Esfera* aux=new Esfera(1.0,0,10,i,5);
			aux->SetColor(i*40,0,255-i*40);
			esferas.Agregar(aux);
		}
	}
	if(nivel<=8)
		return true;
	return false;
}

bool Mundo::Impacto()
{
	return impacto;
}
int Mundo::GetNumEsferas()
{
	return esferas.GetNumero();
}
