package dummy.geom.primitives;

public class Piramide {
	float lado;
	float altura;
	double peso;
	Triangulo lados[]=new Triangulo[4];
	Cuadrado base;
	
	public Piramide()
	{
		this.lado = 10;
		this.peso = 1000;
		this.altura = 15;
		for(int i=0;i<=3;i++)
		{
			this.lados[i] = new Triangulo();
		}
		this.base = new Cuadrado();	
	}
	
	public Piramide(float lado, double peso, float altura)
	{
		this.lado = lado;
		this.peso = peso;
		this.altura = altura;
		for(int i=0;i<=3;i++)
		{
			lados[i] = new Triangulo(lado,altura);
		}
		this.base = new Cuadrado(lado);
	}
	
	public double Volumen()
	{
		double h = Math.sqrt((this.altura*this.altura)-(((this.lado)/2)*((this.lado)/2)));
		double volumen = (this.lado*this.lado*h)/3;
		return volumen;
	}

	public double Superficie()
	{
		double superficie = 0;
		for(int i=0;i<=3;i++)
		{
			superficie += this.lados[i].Superficie();
		}
		superficie += this.base.Superficie();
		return superficie;
	}
	
	public double Densidad()
	{
		double volumen = Volumen();
		double densidad = this.peso/volumen;
		return densidad;
	}

}
