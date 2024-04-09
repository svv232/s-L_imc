V=sorted
D=range
C=len
A=print
from datamodel import OrderDepth,UserId,TradingState,Order as H
from typing import List
from collections import defaultdict as F
from collections import deque
import numpy as B,jsonpickle as E
def G(x,y):
	try:A=B.vstack([B.ones(C(x)),x]).T;D,E=B.linalg.lstsq(A,B.array(y),rcond=None)[0];return D,E
	except:raise B.linalg.LinAlgError(f"{x.shape}, {y.shape} something went wrong with the shape")
def I(x):return B.std(x)
class J:
	def __init__(A,size=10):A.size=size;A.buff=[];A.idx=0
	def add(A,item):
		if C(A.buff)<A.size:A.buff.append(item)
		else:A.buff[A.idx%A.size]=item
		A.idx+=1
	def __iter__(A):
		if C(A.buff)<A.size:
			for F in A.buff:yield F
		else:
			E=A.idx%A.size
			for B in D(E,C(A.buff)):yield A.buff[B]
			for B in D(E):yield A.buff[B]
	def __len__(A):return C(A.buff)
class L:
	def __init__(A,data=''):
		B=data
		if B=='':A.regression_model=F(J);A.tick_delta=100;A.std_dev=0
		else:B=E.decode(B);A.regression_model=B.regression_model;A.tick_delta=B.tick_delta;A.std_dev=B.std_dev
	def __str__(A):return E.encode(A)
	def add_point(A,product,y):B=product;A.regression_model[B].add(y);A.std_dev=I(A.regression_model[B].buff)
	def slope(A,product):E=product;F=B.array([B*A.tick_delta for B in D(C(A.regression_model[E]))]);H=B.array([A for A in A.regression_model[E]]);J,I=G(F,H);return I
class K:
	def run(Q,state):
		C=state;D={}
		for B in C.order_depths:
			A('######### Product: '+B+' #########');H=C.order_depths[B];E=[];F=M(H);G=L(C.traderData);G.add_point(B,F);I=G.slope(B);I=0;J=C.position.get(B,0);A('Acceptable price : '+str(F));E=N(B,F,H,I,J);K=J
			for O in E:K-=O.quantity
			A('Expected position: ',K);D[B]=E;C.traderData=str(G)
		P=0;A(D);return D,P,C.traderData
def M(o):
	C=0;B=0
	for(D,A)in o.buy_orders.items():C+=D*A;B+=A
	for(D,E)in o.sell_orders.items():A=E*-1;C+=D*A;B+=A
	return C/B if B!=0 else 0
T=20
U=-20
def N(product,acceptable_price,order_depth,slope,position):
	W=acceptable_price;P=position;O=slope;J=order_depth;I=product;E=[];X=W+.5*O;Y=W-.5*O;Q=V([(A,-1*B)for(A,B)in J.sell_orders.items()if A<X],key=lambda x:x[0]);R=V([(A,B)for(A,B)in J.buy_orders.items()if A>Y],key=lambda x:x[0],reverse=True);A('Slope: ',O);A('Buy acceptable price: ',X);A('Asks: ',J.sell_orders);A('Acceptable asks: ',Q);A('Sell acceptable price: ',Y);A('Bids: ',J.buy_orders);A('Acceptable bids: ',R);K=sum([A for(B,A)in Q]);L=sum([A for(B,A)in R]);F=P-K+L
	if F>T:S=F-T;M=K;N=L-S
	elif F<U:S=U-F;M=K-S;N=L
	else:M=K;N=L
	Z=P-M+N;A('Potential position delta: ',F);A('New potential position: ',Z);C=M;D=N;A('Position: ',P);A('Number of ask orders to place: ',C);A('Number of bid orders to place: ',D)
	for(G,B)in Q:
		if C==0:break
		if B>C:E.append(H(I,G,-1*C));C=0
		else:E.append(H(I,G,B));C-=B
	for(G,B)in R:
		if D==0:break
		if B>D:E.append(H(I,G,D));D=0
		else:E.append(H(I,G,-B));D-=B
	return E