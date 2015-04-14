// ListaDisparos.cpp: implementation of the ListaDisparos class.
//
//////////////////////////////////////////////////////////////////////

#include "listadisparos.h" 
#include "interaccion.h" 
//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

ListaDisparos::ListaDisparos()
{
	numero=0;
}

ListaDisparos::~ListaDisparos()
{

}

void ListaDisparos::Dibuja()
{
	for(int i=0;i<numero;i++)
		lista[i]->Dibuja();
}

void ListaDisparos::Mueve(float t)
{
	for(int i=0;i<numero;i++)
		lista[i]->Mueve(t);
}

void ListaDisparos::DestruirContenido()
{
	for(int i=0;i<numero;i++)
		delete lista[i];

	numero=0;
}

bool ListaDisparos::Agregar(Disparo *d)
{
	for(int i=0;i<numero;i++)//para evitar que se añada una esfera ya existente
		if(lista[i]==d)
			return false;

	if(numero<MAX_DISPAROS)
	   lista[numero++]=d;
	else 
		return false;
	return true;
}
void ListaDisparos::Colision(Pared p)
{
	for(int i=numero-1;i>=0;i--)
	{
		int tipo=lista[i]->GetTipo();
		if(tipo==GANCHO || tipo==GANCHO_ESPECIAL)
		{
			Gancho* g=(Gancho*)lista[i];
			if(Interaccion::Colision(*g,p))
			{
				lista[i]->SetVel(0,0);
			}
		}
		if(tipo==LANZA)
		{
			Lanza* g=(Lanza*)lista[i];
			if(Interaccion::Colision(*g,p))
			{
				Eliminar(i);
			}
		}
	}
}
void ListaDisparos::Colision(Caja c)
{
	for(int i=numero-1;i>=0;i--)
	{
		int tipo=lista[i]->GetTipo();
		if(tipo==GANCHO || tipo==GANCHO_ESPECIAL)
		{
			Gancho* g=(Gancho*)lista[i];
			if(Interaccion::Colision(*g,c))
			{
				lista[i]->SetVel(0,0);
			}
		}
		if(tipo==LANZA)
		{
			Lanza* g=(Lanza*)lista[i];
			if(Interaccion::Colision(*g,c))
			{
				Eliminar(i);
			}
		}
	}
}
Disparo *ListaDisparos::operator [](int i)
{
	if(i>=numero)
		i=numero-1;
	if(i<0)
		i=0;
	
	return lista[i];
}
void ListaDisparos::Eliminar(int index)
{
	if((index<0)||(index>=numero))
		return;
	
	delete lista[index];

	numero--;
	for(int i=index;i<numero;i++)
		lista[i]=lista[i+1];

}

void ListaDisparos::Eliminar(Disparo *e)
{
	for(int i=0;i<numero;i++)
  		if(lista[i]==e)
		{
	  		Eliminar(i);
	  		return;
		}

}
