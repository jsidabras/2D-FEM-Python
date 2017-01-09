#!/usr/local/bin/python
#######################
# Finite element modeling program using the pyfem library
# correctly calculates the TM wavenumber of any geometry created by Gmsh.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Origional work: Jason Sidabras
# Useage: $./femtest.py <msh file>
# 
#######################
import pyfem
import scipy
import math
filename = None
# 25 free nodes
#filename = './SquareWG_25Nodes.msh'
if filename == None:
	import sys
	filename = sys.argv[1]
node = pyfem.nodes(filename)
trielm = pyfem.Elms(filename, 2)
trielmRec = pyfem.elmRecurse(trielm, node)
elmCoeff = pyfem.elementCoeff(trielmRec)
C = pyfem.GlobalMatrix(elmCoeff, filename)
T = pyfem.TMatrix(trielmRec, filename)

FreeNodes = pyfem.FreeNode(elmCoeff,trielmRec, filename)
PNodes = []
for x in pyfem.Elms(filename, 1):
	PNodes.append(x[0])
#lam = pyfem.TMSolve(C, T, FreeNodes)
#One = [0,1,2,3]
#lam.sort()
#print 'TM Modes:'
#for x in lam:
#	print math.sqrt(x)
lam = pyfem.TESolve(C, T, FreeNodes, PNodes)
lam.sort()
#Print out TE Modes... if working.
print 'TE Modes:'
for x in lam:
	#if x.imag == 0 and x.real > 0:
	print math.sqrt(x)

