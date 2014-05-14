"""
Simple water flow example using ANUGA:
Transcritical flow without shock over a bump.
"""

#------------------------------------------------------------------------------
# Import necessary modules
#------------------------------------------------------------------------------
import sys
import anuga
from anuga import Domain as Domain
from math import cos
from numpy import zeros, ones, float
from time import localtime, strftime, gmtime
from anuga.operators.set_w_uh_vh_operators import Polygonal_set_w_uh_vh_operator


#-------------------------------------------------------------------------------
# Copy scripts to time stamped output directory and capture screen
# output to file
#-------------------------------------------------------------------------------
time = strftime('%Y%m%d_%H%M%S',localtime())

#output_dir = 'transcritical_'+time
output_dir = '.'
output_file = 'transcritical'

#anuga.copy_code_files(output_dir,__file__)
#start_screen_catcher(output_dir+'_')


#------------------------------------------------------------------------------
# Setup domain
#------------------------------------------------------------------------------
dx = 0.1
dy = dx
L = 25.
W = 3*dx

BC_polygonL = [[0,0],[dx,0.0], [dx,W], [0,W]]
BC_polygonR = [[L,0.],[L,W], [L-dx,W], [L-dx,0.]]

# structured mesh
points, vertices, boundary = anuga.rectangular_cross(int(L/dx), int(W/dy), L, W, (0.0, 0.0))

#domain = anuga.Domain(points, vertices, boundary) 
domain = Domain(points, vertices, boundary) 

domain.set_name(output_file)                
domain.set_datadir(output_dir) 

#------------------------------------------------------------------------------
# Setup Algorithm, either using command line arguments
# or override manually yourself
#------------------------------------------------------------------------------
from anuga.utilities.argparsing import parse_standard_args
alg, cfl = parse_standard_args()
domain.set_flow_algorithm(alg)
domain.set_CFL(cfl)

#------------------------------------------------------------------------------
# Setup initial conditions
#------------------------------------------------------------------------------
def elevation(x,y):
    z_b = zeros(len(x))
    for i in range(len(x)):
        if (8.0 <= x[i] <= 12.0):
            z_b[i] = 0.2 - 0.05*(x[i]-10.0)**2
        else:
            z_b[i] = 0.0
    return z_b
domain.set_quantity('elevation',elevation)
domain.set_quantity('friction', 0.0)
domain.set_quantity('xmomentum', 0.0)


def stage(x,y):
    return 0.66*ones(len(x))
domain.set_quantity('stage', stage)

#-----------------------------------------------------------------------------
# Setup boundary conditions
#------------------------------------------------------------------------------
from math import sin, pi, exp
Br = anuga.Reflective_boundary(domain)      # Solid reflective wall
Bt = anuga.Transmissive_boundary(domain)    # Continue all values on boundary 
BdL = anuga.Dirichlet_boundary([1.0144468506259066, 1.53, 0.]) # Constant boundary values
BdR = anuga.Dirichlet_boundary([0.4057809296474606, 1.53, 0.]) # Constant boundary values


# Associate boundary tags with boundary objects
domain.set_boundary({'left': BdL, 'right': BdR, 'top': Br, 'bottom': Br})

w_uh_vhL= [1.0144468506259066, 1.53, 0.]
w_uh_vhR= [0.4057809296474606, 1.53, 0.]
Polygonal_set_w_uh_vh_operator(domain,w_uh_vhL,BC_polygonL)
Polygonal_set_w_uh_vh_operator(domain,w_uh_vhR,BC_polygonR)

#===============================================================================
##from anuga.visualiser import RealtimeVisualiser
##vis = RealtimeVisualiser(domain)
##vis.render_quantity_height("stage", zScale =h0*500, dynamic=True)
##vis.colour_height_quantity('stage', (0.0, 0.5, 1.0))
##vis.start()
#===============================================================================


#------------------------------------------------------------------------------
# Produce a documentation of parameters
#------------------------------------------------------------------------------
parameter_file=open('parameters.tex', 'w')
parameter_file.write('\\begin{verbatim}\n')
from pprint import pprint
pprint(domain.get_algorithm_parameters(),parameter_file,indent=4)
parameter_file.write('\\end{verbatim}\n')
parameter_file.close()

#------------------------------------------------------------------------------
# Evolve system through time
#------------------------------------------------------------------------------
for t in domain.evolve(yieldstep = 1.0, finaltime = 300.):
    #print domain.timestepping_statistics(track_speeds=True)
    print domain.timestepping_statistics()
    #vis.update()


#test against know data    
#vis.evolveFinished()

