#include "systemsolver.h"

int main(int arg, char** argv)
{
/*  MatrixXd m(2,2);
  m(0,0) = 3;
  m(1,0) = 2.5;
  m(0,1) = -1;
  m(1,1) = m(1,0) + m(0,1);
  std::cout << m << std::endl;
  
  MatrixXf m2 = MatrixXf::Random(3,3);
  m2 = (m2 + MatrixXf::Constant(3,3,1.2)) * 50;
  cout << "m2 =" << endl << m2 << endl;
  VectorXf v(3);
  v << 1, 2, 3;
  cout << "m * v =" << endl << m2 * v << endl;*/

  SystemSolver solver;
  vector<double> b;
  int size=10;  
  for(int i=0;i<size;i++)
  {
	  solver(i,i)=i+1;
	  b.push_back(1);
  }
  vector<double> sol=solver.SolveSparse(b);
  cout<<"*************** SPARSE *************** "<<endl;
  for(int i=0;i<size;i++)
	  cout<<i<<": "<<sol[i]<<endl;
 vector<double> sol2=solver.SolveDense(b);
   cout<<"*************** DENSE *************** "<<endl;
  for(int i=0;i<size;i++)
	  cout<<i<<": "<<sol2[i]<<endl;
}
