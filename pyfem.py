#!/usr/local/bin/python
#######################
# Finite element modeling program, correctly calculates the TM wavenumber
# of any geometry created by Gmsh.
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
# 
#######################
import scipy
import os.path
import re
import math

femVersion = '0.1'

def nodes(filename):
	file = open(filename, 'r')
	count_lines = len(file.readlines())
	file = open(filename, 'r')
	#print count_lines
	check = 0 
	loop = 0
	nodeList= []
	while count_lines != check:
		header = file.readline()
		header = header.strip()
		if header == "$NOD":
			numnodes = file.readline()
			numnodes = numnodes.strip()
			#print numnodes
			numnodes = int(numnodes)
			while loop < numnodes:
				loop = int(loop)
				test2 = file.readline()
				test2 = test2.strip()
				if test2 == '$ENDNOD':
					print "break"
					break
				else:
					newList = nodematrix(test2)
					nodeList.append(newList)
				loop = loop + 1
		check = check + 1
	return nodeList
		
def nodematrix(list):
	newList = []
	newList = list.split()
	lenth = len(newList)
	newList[0]=int(newList[0])
	loop = 1
	while loop < lenth:
		newList[loop] = float(newList[loop])
		loop = loop + 1
	#remove for z component
	newList.pop()
	###
	return newList
	
def Elms(filename, number):
	file = open(filename, 'r')
	count_lines = len(file.readlines())
	file = open(filename, 'r')
	#print count_lines
	check = 0 
	loop = 0
	elmList= []
	while count_lines != check:
		header = file.readline()
		header = header.strip()
		if header == "$ELM":
			numnodes = file.readline()
			numnodes = numnodes.strip()
			#print numnodes
			numnodes = int(numnodes)
			while loop < numnodes:
				loop = int(loop)
				test2 = file.readline()
				test2 = test2.strip()
				if test2 == '$ENDELM':
					print "Reached End for Some Reason."
					break
				else:
					newList = elmmatrix(test2)
					#print newList[0]
					if newList[0] == int(number):
						newList.pop(0)
						newList.pop(0)
						newList.pop(0)
						newList.pop(0)
						elmList.append(newList)
				loop = loop + 1
		check = check + 1
	#print elmList
	return elmList
	
def elmmatrix(list):
	newList = []
	newList = list.split()
	lenth = len(newList)
	newList[0]=int(newList[0])
	loop = 1
	while loop < lenth:
		newList[loop] = int(newList[loop])
		loop = loop + 1
	newList.pop(0)
	#print newList
	return newList
	
def elmRecurse(elementlist, nodelist):
	if elementlist == None:
		print "ERROR"
		return None
	#print elementlist
	check = 0
	elmLength = len(elementlist)
	#print elmLength
	numberofEls = len(elementlist[0])
	#print "Number of Elements: " + str(len(elementlist))
	while check < elmLength:
		check3 = 0
		while check3 < numberofEls:
			#Search for Node number
			#get working number
			nodeNumber = elementlist[check][check3]
			#how many times to cycle nodelist
			nodeLength = len(nodelist)
			check2 = 0
			while check2 < nodeLength:
				#print check2
				#print nodeNumber
				if nodeNumber == nodelist[check2][0]:
					#print 'matched ' + str(nodelist[check2][0])
					step = nodelist[check2]
					#step.pop(0)
					#print step
					elementlist[check][check3] = step	
					break		
				check2 = check2 + 1
			check3 = check3 + 1
		check = check + 1 
	#print len(elementlist)
	elementlist = trunk(elementlist)
	return elementlist
	
def trunk(matrix):
	# trunkate the element number out of the matrix, leaving
	# only the x and y coords.
	newList = []
	newList2 = []
	length = len(matrix) - 1
	length2 = len(matrix[0][0]) - 1
	# dive deep into the matrix until you get the single [num, x, y] vector
	# grab the length of that vector and make sure its 3, if its 2 ([x , y]) skip
	# that means you've already did it.
	# kind of a hack but it seems to work
	for xy in matrix:
		for y in xy:
			#print 'This is y:'
			#print y
			loop = 0
			#while loop < length2:
				#print xy[loop]
			leng = len(y)
			#print leng
				#print leng
			if leng == 3:
				y.pop(0)
				#print xy[loop]
				#loop = loop + 1
	return matrix
	
def elementCoeff(elementlist):
	ElementCoeffMatrix=[]
	for element in elementlist:
		# in ELEMENT ->
		# ELEMENT[0] is first element
		# ELEMENT[0][0] is first element X
		# ELEMENT[0][1] is first element Y
		one = 0
		two = 1
		three = 2
		x = 0
		y = 1
		P1 = (element[two][y] - element[three][y])
		P2 = (element[three][y] - element[one][y])
		P3 = (element[one][y] - element[two][y])
		Q1 = (element[three][x] - element[two][x])
		Q2 = (element[one][x] - element[three][x])
		Q3 = (element[two][x] - element[one][x])
		Area = 0.5*(P2*Q3 - P3*Q2)
		#print 'area is: ' + str(Area)
		Coef = 1/(4*Area)
		# Ce(ij)=(1/4A)(PiPJ+QiQj)
		C11 = Coef*(P1*P1 + Q1*Q1)
		C22 = Coef*(P2*P2 + Q2*Q2)
		C33 = Coef*(P3*P3 + Q3*Q3)
		C12 = Coef*(P1*P2 + Q1*Q2)
		C21 = C12
		C13 = Coef*(P1*P3 + Q1*Q3)
		C31 = C13
		C23 = Coef*(P2*P3 + Q2*Q3)
		C32 = C23
		CoeffMatrix = [[C11, C12, C13],[C21, C22, C23],[C31,C32,C33]]		
		
		ElementCoeffMatrix.append(CoeffMatrix)
	return ElementCoeffMatrix
	
def GlobalMatrix(elementCoeffMatrix, filename):
	# Nodes x Nodes sized matrix
	# Sum i 1-N Cij = 0 = Sum j 1-N Cij
	Elements = Elms(filename,2)
	node = nodes(filename)
	nodelen = len(node)
	GlobalMatrix = []
	# Find Golbal Cij elements 
	i = 1
	while i <= nodelen:
		GlobalElementList = []
		j = 1
		
		while j <= nodelen:
			GlobalElement = 0
			elementnumber = 1

			#print 'C' + str(i) + str(j) 
			# find all Cii's
			if i == j:
				for elem in Elements:
					nodenumber = 0
					for node in elem:
						if node == j:
							#print 'In element number ' + str(elementnumber) + ' use node number ' + str(nodenumber + 1)
							#print elementCoeffMatrix[elementnumber - 1][nodenumber][nodenumber]
							GlobalElement = GlobalElement + elementCoeffMatrix[elementnumber - 1][nodenumber][nodenumber]
						nodenumber = nodenumber + 1 
					elementnumber = elementnumber + 1 
				#GlobalMatrix.append('C('+ str(elementnumber) + ')'  + str(nodenumber + 1)  + str(nodenumber + 1))
			# find the rest
			else:
				for elem in Elements:
					nodenumber2 = 0
					for nodej in elem:
						nodenumber = 0
						for nodei in elem:
							if nodei == i:
								#GlobalElement = 0
								if nodej == j:
									#print 'In element number ' + str(elementnumber) + ' use node number ' + str(nodenumber + 1) + ' and ' + str(nodenumber2 + 1)		
									#print elementCoeffMatrix[elementnumber - 1][nodenumber][nodenumber2]
									GlobalElement = GlobalElement + elementCoeffMatrix[elementnumber - 1][nodenumber][nodenumber2]
								nodenumber2 = nodenumber2 + 1
							nodenumber = nodenumber + 1 
					elementnumber = elementnumber + 1 
			GlobalElementList.append(GlobalElement)
			j = j + 1
		GlobalMatrix.append(GlobalElementList)
		i = i + 1
	return GlobalMatrix

def TMatrix(elementlist, filename):
	AreaMat = []
	TEffMatrix = []
	TMatrix = []
	for element in elementlist:
		#print element
		one = 0
		two = 1
		three = 2
		x = 0
		y = 1
		P1 = (element[two][y] - element[three][y])
		P2 = (element[three][y] - element[one][y])
		P3 = (element[one][y] - element[two][y])
		Q1 = (element[three][x] - element[two][x])
		Q2 = (element[one][x] - element[three][x])
		Q3 = (element[two][x] - element[one][x])
		Area = 0.5*(P2*Q3 - P3*Q2)
		T11 = Area/6
		T22 = Area/6
		T33 = Area/6
		T12 = Area/12
		T21 = T12
		T13 = Area/12
		T31 = T13
		T23 = Area/12
		T32 = T23
		TMatrix = [[T11, T12, T13],[T21, T22, T23],[T31,T32,T33]]		
		
		TEffMatrix.append(TMatrix)
	GlobalTEffMatrix = GlobalMatrix(TEffMatrix, filename)
	#print GlobalTEffMatrix
	return GlobalTEffMatrix
	
#def nodeIdenity(filename, listof):
#	node = nodes(filename)
#	nodelen = len(node)
#	i = 1
#	TCompleteList= []
#	while i <= nodelen:
#		TList = []
#		j = 1
#		while j <= nodelen:
#			if i == x and j == x:
#				T = 1
#				#print i
				#print x
				#print j
				
#			else:
#				T = 0
				#print T
				
#			TList.append(T)
#			j = j + 1
#		i = i + 1
#		TCompleteList.append(TList)
#	return TCompleteList
	
def FreeNode(elementCoeffMatrix, elementlist, filename):
	C = GlobalMatrix(elementCoeffMatrix, filename)
	T = TMatrix(elementlist, filename)
	BoarderElms = Elms(filename, 1)

	NewMatrix = []
	NumberT = []
	NumberT2 = []
	NumberC = []
	NumberC2 = []
	loop = 0
	nodelist = nodes(filename)
	length = len(nodelist)
	for q in nodelist:
		NumberT.append(q[0])
	lf = []
	PrescribedNodeFlag = 0;
	length3 = length - len(BoarderElms)
	for i in range(length):
		Cff = []
		Tff = []
		for k in range(len(BoarderElms)):
			if len(NumberT) == length3:
				break
			if i == (BoarderElms[k][0]):
				PrescribedNodeFlag = 1
				break		
			if PrescribedNodeFlag == 0:
				p = BoarderElms[k][0]
				if NumberT.count( p ) != 0:
					NumberT.remove(p)
				else:
					break
				
			else:
				PrescribeNodeFlag = 0
	return NumberT

def TMSolve(C, T, Number):
	NewCMatrix = []
	NewTMatrix = []
	#print len(T)
	#Cff = scipy.mat(C)
	#print Cff
	#Tff= scipy.mat(T)
	#print Tff
	nodelen = len(Number)
	i = 1
	Num = 0
	while i < nodelen:
		TList = []
		CList = []
		j = 1
		while j < nodelen:
			#print j - 1
			#Ftt = 'T' + str(Num+i-1) + '_' + str(Num+j-1)
			Ftt = T[Number[i]-1][Number[j]-1]
			TList.append(Ftt)
			#Fcc = 'C' + str(Num+i-1) + '_' + str(Num+j-1)
			Fcc = C[Number[i]-1][Number[j]-1]
			CList.append(Fcc)	
			j = j + 1
		i = i + 1
		NewTMatrix.append(TList)
		NewCMatrix.append(CList)
	Tff = scipy.mat(NewTMatrix)
	Cff = scipy.mat(NewCMatrix)
	TffI = Tff.I
	AMat = TffI*Cff
	lam = scipy.linalg.eigvals(AMat)
	return lam

def TESolve(C, T, Number, PNodes):
	NewCMatrix = []
	NewTMatrix = []
	for x in PNodes:
		Number.append(x)
	Number.sort()
	Cff = scipy.mat(C)
	#print Cff
	Tff= scipy.mat(T)
	#print Tff
	nodelen = len(Number)
	i = 0
	Num = 0
	while i < nodelen:
		TList = []
		CList = []
		j = 0
		while j < nodelen:
			#Ftt = 'T' + str(Num+i-1) + '_' + str(Num+j-1)
			Ftt = T[Number[i]-1][Number[j]-1]
			TList.append(Ftt)
			#Fcc = 'C' + str(Num+i-1) + '_' + str(Num+j-1)
			Fcc = C[Number[i]-1][Number[j]-1]
			CList.append(Fcc)	
			j = j + 1
		i = i + 1
		NewTMatrix.append(TList)
		NewCMatrix.append(CList)
	Tff = scipy.mat(NewTMatrix)
	Cff = scipy.mat(NewCMatrix)
	#print Cff
	TffI = Tff.I
	AMat = TffI*Cff
	lam = scipy.linalg.eigvals(AMat)
	return lam
