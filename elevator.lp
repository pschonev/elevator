% INSERT NAMES AND EMAIL ADDRESSES OF YOUR GROUP MEMBERS:
%
%
% note: maybe minimize the number of 'action()'s !?

#include <incmode>. % built-in incremental mode of clingo

#show. % output atoms will be declared below

#program base. % static rules go below
dir(up;down).
actions(move(1);move(-1);serve).
simple_requests(call(up);call(down)).
holds(at(X, Y),0):- agent(X), init(at(X, Y)).
holds(request(X,Y),0):-init(request(X,Y)).

#program step(t). % actions, effects, and minimization go below

{action(X,Y,t):agent(X), actions(Y)}agents. %maybe fix this to always do agents-many moves but only turn successfull ones into 'do()' commands to improve performance?

%basic positional information
current_pos(X,N+1,t):-action(X,move(up),t), holds(at(X,N),t-1).
current_pos(X,N-1,t):-action(X,move(down),t), holds(at(X,N),t-1).
current_pos(X,N,t):-action(X,serve,t), holds(at(X,N),t).
current_pos(X,N,t):-not action(X,Z,t),actions(Z), holds(at(X,N),t).

%stop elevators from leaving the building ...
:-action(X,move(up),t),holds(at(X,N),t-1),floor(N+1).
:-action(X,move(down),t),holds(at(X,N),t-1),floor(N-1).
%stop elevators from picking up nothing
:-action(X,serve,t),not holds(request(X,Y),t), current_pos(X,Y,t).

%making sure requests can be fulfilled
holds(request(Z,Y),t):-not action(X,serve,t), current_pos(X,Y,t), holds(request(Z,Y),t-1), simple_requests(Z).
holds(request(deliver(A),Y),t):-not action(elevator(A),serve,t), current_pos(elevator(A),Y,t), holds(request(deliver(A),Y),t).

%ensuring object permanence for elevators...
holds(at(X,Y),t):-current_pos(X,Y,t).

%'do'ing stuff
do(X,Y,t):-action(X,Y,t).


#show do(A,X,t) : do(A,X,t). % output atoms indicating actions

#show holds(X,t) : holds(X,t). % output atoms indicating states

#program check(t). % fulfillment of all requests can, e.g., be checked as follows


:- query(t), holds(request(R,F),t).
