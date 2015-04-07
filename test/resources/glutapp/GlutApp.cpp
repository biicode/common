#include "glutapp.h" 
#include "%GLUT_USER%/glut/include/gl/glut.h"
#include "iostream" 

using namespace std;

GlutApp* theApp=0;

void OnDraw(void)
{
	//Borrado de la pantalla	
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

	//Para definir el punto de vista
	glMatrixMode(GL_MODELVIEW);	
	glLoadIdentity();
	
	if(theApp)
		theApp->Draw();

	//no borrar esta linea ni poner nada despues
	glutSwapBuffers();
}
void OnKeyboardDown(unsigned char key, int x_t, int y_t)
{
	if(theApp)
		theApp->Key(key);

	glutPostRedisplay();
}
void OnSpecialKeyboardDown(int key, int x, int y)
{
	if(theApp)
		theApp->SpecialKey(key);
}
void OnTimer(int value)
{
//poner aqui el código de animacion
	if(theApp)
		theApp->Timer(0.025);

	//no borrar estas lineas
	glutTimerFunc(25,OnTimer,0);
	glutPostRedisplay();
}

GlutApp::GlutApp(string name)
{
	if(theApp==0)
	{
		int argc=1;
		char* argv[1]={"Glut Application"};
		glutInit(&argc, argv);
		glutInitWindowSize(800,600);
		glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH);
		glutCreateWindow(name.c_str());

		//habilitar luces y definir perspectiva
		glEnable(GL_LIGHT0);
		glEnable(GL_LIGHTING);
		glEnable(GL_DEPTH_TEST);
		glEnable(GL_COLOR_MATERIAL);	
		glMatrixMode(GL_PROJECTION);
		gluPerspective( 40.0, 800/600.0f, 0.1, 150);

		theApp=this;
		//Registrar los callbacks
		glutDisplayFunc(OnDraw);
		glutTimerFunc(25,OnTimer,0);//le decimos que dentro de 25ms llame 1 vez a la funcion OnTimer()
		glutKeyboardFunc(OnKeyboardDown);
		glutSpecialFunc(OnSpecialKeyboardDown);
		
	}
}
void GlutApp::Run()
{
	glutMainLoop();	
}

