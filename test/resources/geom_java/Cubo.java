package dummy.geom.primitives;

public class Cubo {
	float lado;
	double peso;
	Cuadrado lados[]=new Cuadrado[6];
	
	public Cubo()
	{
		this.lado = 10;
		this.peso = 1000;
		for(int i=0;i<=5;i++)
		{
			this.lados[i] = new Cuadrado();
		}
		
	}
	
	public Cubo(float lado, double peso)
	{
		this.lado = lado;
		this.peso = peso;
		for(int i=0;i<=5;i++)
		{
			this.lados[i] = new Cuadrado(lado);
		}
	}
	
	public double Volumen()
	{
		double volumen = this.lado * this.lado * this.lado;
		return volumen;
	}
	
	public double Superficie()
	{
		double superficie = 0;
		for(int i=0;i<=5;i++)
		{
			superficie += this.lados[i].Superficie();
		}
		return superficie;
	}
	
	public double Densidad()
	{
		double volumen = Volumen();
		double densidad = this.peso/volumen;
		return densidad;
	}

}
