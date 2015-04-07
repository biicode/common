#include "systemsolver.h"

#include <iostream>
#include <%EIGEN_USER_NAME%/eigen/Dense>
extern "C"
{
#include "%CSPARSE_USER_NAME%/csparse/cs.h"
}
using namespace Eigen;

vector<double>  SystemSolver::SolveSparse(vector<double> valuesB)
{
//THe matrix A
	vector<double> values;
	vector<int> rows;
	vector<int> nums;
	int num=0;

	for(sparseMatrix::const_iterator it=matrix.begin();it!=matrix.end();it++)
	{
		const sparseCol& col=it->second;
		for(sparseCol::const_iterator it2=col.begin();it2!=col.end();it2++)
		{
			values.push_back(it2->second);
			rows.push_back(it2->first);	
		}
		nums.push_back(num);
		num+=col.size();
	}
	nums.push_back(num);
	
	cs_sparse A;	
	int nnz=values.size();
	A.nzmax=nnz;
	A.m=num_row;
	A.n=num_col;
	A.x=new double[nnz];
	A.nz=-1;//column-compressed (not triplet)

	A.p =new ptrdiff_t[num_col+1]; /// column pointers (size n+1) or col indices (size nzmax)
	A.i=new ptrdiff_t[nnz] ;        /* row indices, size nzmax */

	unsigned int i;
	for(i=0;i<nnz;i++)
	{
		A.x[i]=values[i];
		A.i[i]=rows[i];
	}
	for(i=0;i<nums.size();i++)
	{
		A.p[i]=nums[i];
	}

	double* b=new double [valuesB.size()];
	memcpy(b,&valuesB[0],sizeof(double)*valuesB.size());
//	log<<"Problem defined: "<<timer.toc()<<endl;
//	log<<A.m<<", "<<A.n<<" nzmax: "<<A.nzmax<<" nz: "<<A.nz<<endl;
	cs_cholsol(1,&A,b);
	std::vector<double> ret(valuesB.size());

	memcpy(&ret[0],b,sizeof(double)*valuesB.size());
	
	//log<<"Time: "<<timer.toc()<<endl;
	//log.close();
	return ret;
}
vector<double>  SystemSolver::SolveDense(vector<double> valuesB)
{
	int size=max(num_col,num_row);
	MatrixXd A=MatrixXd::Zero(size,size);

	for(sparseMatrix::const_iterator it=matrix.begin();it!=matrix.end();it++)
	{
		const sparseCol& col=it->second;
		for(sparseCol::const_iterator it2=col.begin();it2!=col.end();it2++)
		{
			A(it->first,it2->first)=it2->second;	
		}
	}
	VectorXd b(valuesB.size());
	for(int i=0;i<valuesB.size();i++)
		b(i)=valuesB[i];

	VectorXd sol=A.colPivHouseholderQr().solve(b);
	vector<double> ret(valuesB.size());
	for(int i=0;i<ret.size();i++)
		ret[i]=sol(i);

	return ret;
}