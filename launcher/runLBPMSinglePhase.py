import os
from math import ceil
import subprocess
import sys
import subprocess

def runLBPMSinglePhase(domain, targetdir, npx, npy, npz, voxelSize,
                      timesteps, gpuIDs, Fx, Fy, Fz, flux,
                      Pin, Pout, mu, restart, visInterval,
                      analysisInterval, permTolerance, terminal):
    bgkFlag = 'false';
    thermalFlag = 'false';
    visTolerance='true';
    fqFlag = 'false';
    DiffCoeff=1e-1;
    if(not os.path.exists(targetdir)):
        os.mkdir(targetdir)
    os.chdir(targetdir)
    tau=3*mu+0.5;
    Nx, Ny, Nz = domain.shape

    nx=ceil(Nx/npx);
    ny=ceil(Ny/npy);
    nz=ceil(Nz/npz);

    if (flux > 0):
        BC=4
    elif(Pin > 0):
        BC=3
    else:
        BC=0
        Pin=1/3
        Pout=1/3
        flux=0

    fileName='domain';

    if (restart):
        restartFq = 'true';
    else:
        restartFq='false';
        
    inputfile = ('Domain {', '\n' ,
                '    Filename = "', fileName, '.raw"', '\n',
                '    nproc = ', str(npx), ', ', str(npy), ', ', str(npz),'\n',
                '    n = ', str(nx), ', ', str(ny), ', ', str(nz),'\n',
                '    N = ', str(Nx), ', ', str(Ny), ', ', str(Nz),'\n',
                '    L = 1, 1, 1','\n',
                '    BC = ', str(BC),'\n',
                '    voxel_length = ', str(voxelSize*1e6),'\n',
                '    ReadType = "8bit"','\n',
                '    ReadValues = 0, 1','\n',
                '    WriteValues = 2, 0','\n',
                '}','\n',
                '','\n',
                'MRT {','\n',
                '    bgkFlag = ', bgkFlag,'\n',
                '    thermalFlag = ', thermalFlag,'\n',
                '    timestepMax = ', str(timesteps),'\n',
                '    tau = ', str(tau), '\n',
                '    F = ', str(Fx), ', ', str(Fy), ', ', str(Fz),'\n',
                '    Restart = false','\n',
                '    din = ', "{:e}".format(Pin*3),'\n',
                '    dout = ', "{:e}".format(Pout*3),'\n',
                '    flux = ', str(flux),'\n',
                '    visInterval = ', str(visInterval),  '\n',
                '    fqFlag = ', fqFlag,'\n',
                '    restartFq = ', restartFq,'\n',     
                '    analysis_interval = ', str(analysisInterval), '\n',          
                '    permTolerance = ', str(permTolerance),'\n',    
                '    visTolerance = ', visTolerance,'\n',    
                '}','\n',
                '','\n',
                'Thermal {','\n',
                '    DiffCoeff = ', str(DiffCoeff),'\n', 
                '}')
    fid = open('inputFile.db', 'wt')
    fid.write(''.join(inputfile))
    fid.close()
    
    if (not gpuIDs):
        runFile=('#!/bin/bash', '\n',
                 'export LBPM_DIR="/mnt/c/Users/THOMAS/Documents/Projects/Uni/LBPM-CPU"', '\n',
                 'export NUMPROCS=',str(npx*npy*npz), '\n',
                 'mpirun -np 1 $LBPM_DIR/bin/lbpm_serial_decomp inputFile.db', '\n',
                 'mpirun -np $NUMPROCS $LBPM_DIR/tests/lbpm_permeability_simulator inputFile.db'
                 )
    else:
        runFile=('#!/bin/bash', '\n',
                 'export LBPM_DIR="/mnt/c/Users/THOMAS/Documents/Projects/Uni/LBPM-GPU"', '\n',
                 'export NUMPROCS=',str(npx*npy*npz), '\n',
                 'mpirun -np 1 $LBPM_DIR/bin/lbpm_serial_decomp inputFile.db', '\n',
                 'CUDA_VISIBLE_DEVICES=', gpuIDs,' mpirun -np $NUMPROCS $LBPM_DIR/tests/lbpm_permeability_simulator inputFile.db'
                 )
        
    fid = open('runfile.db', 'wt')
    fid.write(''.join(runFile))
    fid.close()
    
    fid = open(fileName +'.raw','wb');
    domain.tofile(fid)
    fid.close()

    pathname = os.path.abspath('runfile.db')
    cmd = ["bash", pathname]

    print("Running solver...")
    
    subprocess.Popen(cmd, stdout=sys.stdout)