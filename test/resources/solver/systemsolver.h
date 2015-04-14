#pragma once

#include <map>
#include <iostream>
#include <fstream>
#include <vector>

#pragma warning (disable: 4786)
using namespace std;

class SystemSolver 
{
protected:
public:
	typedef map<int, double> sparseCol;
	typedef map<int, sparseCol> sparseMatrix;

	friend  ostream& operator<<(ostream& os, const SystemSolver& mat)
	{
		for(sparseMatrix::const_iterator it=mat.matrix.begin();it!=mat.matrix.end();it++)
		{
			const sparseCol& col=it->second;
			for(sparseCol::const_iterator it2=col.begin();it2!=col.end();it2++)
				os<<it2->first<<"-"<<it->first<<": "<<it2->second<<endl;
		}
		return os;
	}
public:
	SystemSolver (){num_col=num_row=0;}
	virtual ~SystemSolver (){;}
	int NumCol(){return num_col;}
	int NumRow(){return num_row;}
	double& operator()(int index_i,int index_j)
	{
		if(index_i+1>num_row)num_row=index_i+1;
		if(index_j+1>num_col)num_col=index_j+1;
		return matrix[index_j][index_i];
	}
	vector<double> SolveDense(vector<double> values);
	vector<double> SolveSparse(vector<double> values);

public:
	sparseMatrix matrix; //maps indices to value
	int num_col;
	int num_row;
};

