package dummy.geom.primitives;
public class Main {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		Cubo c;
		Piramide p;
		c = new Cubo(12,300000);
		p = new Piramide(12,20000,20);
		double volCubo, volPiramide;
		volCubo = c.Volumen();
		volPiramide = p.Volumen();
		
		System.out.print("La superficie del cubo es " + c.Superficie());
		System.out.print("  El volumen del cubo es " + volCubo);
		System.out.print("  La densidad del cubo es " + c.Densidad());
		System.out.print("  La superficie de la piramide es " + p.Superficie());
		System.out.print("  El volumen de la piramide es " + volPiramide);
		System.out.println("  La densidad de la piramide es " + p.Densidad());
	}

}
