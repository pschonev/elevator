%select target to walk to for each idle elevator!

% INSERT NAMES AND EMAIL ADDRESSES OF YOUR GROUP MEMBERS:
% Philipp Schoneville, schoneville@uni-potsdam.de
% Jonas Mikkelsen, mikkelsen@uni-potsdam.de
% note: maybe minimize the number of 'action()'s !?

#include <incmode>. % built-in incremental mode of clingo

#show. % output atoms will be declared below
%#show holds/2.
%#show do/3.

#program base. % static rules go below
holds(at(X, Y),0):- agent(X), init(at(X, Y)).
holds(request(X,Y),0):-init(request(X,Y)).
idle(X,0):-agent(X).
current_pos(X,Y,0):-holds(at(X,Y),0).

#program step(t). % actions, effects, and minimization go below

{select(X,Y,t): holds(request(_,Y),t)}1:-agent(X), idle(X,t-1).
% :- select(X1,Y,t), select(X2,Y,t),X1!=X2.
% :- select(X1,Y1,t), select(X2,Y2,t), current_pos(X1,Z1,t), current_pos(X2,Z2,t), X1!=X2, Z1>Z2, Y1<Y2.


%idle flag
idle(X,t):- do(X,serve,t), agent(X).

%handling select over time
select(X,Y,t):-select(X,Y,t-1), not do(X,serve,t-1).

%movement
current_pos(X,Y+1,t):-current_pos(X,Y,t-1),select(X,Y2,t),Y2>Y.
flag(t):-current_pos(X,Y,t-1),select(X,Y2,t),Y2>Y.
current_pos(X,Y-1,t):-current_pos(X,Y,t-1), select(X,Y2,t),Y2<Y.
flag(t):-current_pos(X,Y,t-1), select(X,Y2,t),Y2<Y.
current_pos(X,Y,t):-current_pos(X,Y,t-1), not select(X,_,t).
current_pos(X,Y,t):-current_pos(X,Y,t-1), not flag(t).

do(X,serve,t):-select(X,Y,t-1), current_pos(X,Y,t-1).


%outputs
do(X,move(1),t):-current_pos(X,Y,t), current_pos(X,Y2,t-1),Y>Y2.
do(X,move(-1),t):-current_pos(X,Y,t), current_pos(X,Y2,t-1),Y<Y2.

holds(at(X,Y),t):- current_pos(X,Y,t).

%dirty way to save some headache...
temp(X,serve,t,Y):- do(X,serve,t), current_pos(X,Y,t).


%handling requests over time
holds(request(R,Y),t):-holds(request(R,Y),t-1), not temp(_,serve, t, Y)  .



%minimize
#minimize{1,t: select(_,_,t)}.
#minimize{1,t:holds(_,t)}.
#minimize{1,X,Y,t:do(X,Y,t)}.

#show do(A,X,t) : do(A,X,t). % output atoms indicating actions


#show current_pos(X,F,t): current_pos(X,F,t).
#show select(X,Y,t): select(X,Y,t).
#show idle(X,t):idle(X,t).

#program check(t). % fulfillment of all requests can, e.g., be checked as follows
#show holds(X,t) : holds(X,t). % output atoms indicating states
:- query(t), holds(request(R,F),t).
