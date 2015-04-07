package %USER%.%BLOCKSIMPLENAME%;

public class Pretty {
	public static void pretty()	{
		System.out.print("* ");
		Hello.hello();
		System.out.println(" *");
		
		%CALL_EXTERNAL_PRETTY%
	}
}
