#include "caja.h" 
#include "listaesferas.h" 
#include "listadisparos.h" 
#include "hombre.h" 
#include "esfera.h" 
#include "bonus.h" 
#include "disparo.h" 
#include "esferapulsante.h" 

class Mundo
{
public: 
	bool Impacto();
	int GetNumEsferas(); 
	bool CargarNivel();
	bool impacto;
	Mundo();
	virtual ~Mundo();

	ListaEsferas esferas;
	ListaDisparos disparos;
	Hombre hombre;
	Caja caja;
	Bonus* bonus;
	Pared plataforma;

	void TeclaEspecial(unsigned char key);
	void Tecla(unsigned char key);
	void Inicializa();
	void RotarOjo();
	void Mueve();
	void Dibuja();

	float x_ojo;
	float y_ojo;
	float z_ojo;
	int nivel;
};

