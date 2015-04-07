package dummy.geom.primitives;

public class Cuadrado {
	float lado;
	
	public Cuadrado()
	{
		this.lado = 10;	
	}
	public Cuadrado(float lado)
	{
		this.lado = lado;	
	}
	public float Superficie()
	{
		float superficie = this.lado * this.lado;
		return superficie;	
	}
}
