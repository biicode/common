package dummy.geom.primitives;

public class Triangulo {
	float lado;
	float altura;
	
	public Triangulo()
	{
		this.lado = 10;
		this.altura = 15;
	}
	public Triangulo(float lado, float altura)
	{
		this.lado = lado;
		this.altura = altura;
	}
	public float Superficie()
	{
		float superficie = (this.lado * this.altura)/2;
		return superficie;	
	}

}
