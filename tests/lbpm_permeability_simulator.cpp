#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <iostream>
#include <exception>
#include <stdexcept>
#include <fstream>

#include "models/MRTModel.h"
//#define WRITE_SURFACES

/*
 * Simulator for single-phase flow in porous media
 * James E. McClure 2013-2014
 */

using namespace std;


int main(int argc, char **argv)
{
	//*****************************************
	// ***** MPI STUFF ****************
	//*****************************************
	// Initialize MPI
	int rank,nprocs;
	MPI_Init(&argc,&argv);
	MPI_Comm comm = MPI_COMM_WORLD;
	MPI_Comm_rank(comm,&rank);
	MPI_Comm_size(comm,&nprocs);
	{
		// parallel domain size (# of sub-domains)
		int nprocx,nprocy,nprocz;
		int iproc,jproc,kproc;

		if (rank == 0){
			printf("********************************************************\n");
			printf("Running Single Phase Permeability Calculation \n");
			printf("********************************************************\n");
		}
			// Initialize compute device
	    int device=ScaLBL_SetDevice(rank);
	    ScaLBL_DeviceBarrier();
	    MPI_Barrier(comm);
		ScaLBL_MRTModel MRT(rank,nprocs,comm);
		auto filename = argv[1];
		MRT.ReadParams(filename);
		MRT.SetDomain();    // this reads in the domain 
		MRT.ReadInput();
		MRT.Create();       // creating the model will create data structure to match the pore structure and allocate variables
		MRT.Initialize();   // initializing the model will set initial conditions for variables
		MRT.Run();	 
		//MRT.VelocityField();
	}
	// ****************************************************
	MPI_Barrier(comm);
	MPI_Finalize();
	// ****************************************************
}
