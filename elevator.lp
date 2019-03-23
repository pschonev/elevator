% INSERT NAMES AND EMAIL ADDRESSES OF YOUR GROUP MEMBERS:
%
%
% note: maybe minimize the number of 'action()'s !?

#include <incmode>. % built-in incremental mode of clingo

#show. % output atoms will be declared below
%#show holds/2.
%#show do/3.
%#show current_pos/3.

#program base. % static rules go below
dir(up;down).
actions(move(1);move(-1);serve). %J: find out if order is relevant for evaluation P: Yes it does
simple_requests(call(up);call(down)).
holds(at(X, Y),0):- agent(X), init(at(X, Y)).
holds(request(X,Y),0):-init(request(X,Y)).

hireq(U):- init(request(_,U)), not 1{init(request(_,V)):floor(V),U!=V,U<V}.
lowreq(U):- init(request(_,U)), not 1{init(request(_,V)):floor(V),U!=V,U>V}.
#show hireq(U):hireq(U).
#show lowreq(U):lowreq(U).



#program step(t). % actions, effects, and minimization go below
%{do(X,Y,t): actions(Y)}1:-agent(X).

% case of one elevator: iteratively look up highest/lowest request and decide which one elevator is closer to and go in that direction
do(X,move(1),t) :- holds(at(X,Y),t-1), not holds(request(_,Y),t-1), hireq(H), loreq(L), Y-L > H-Y, holds(request(_,H),t-1). 
do(X,move(-1),t) :- holds(at(X,Y),t-1), not holds(request(_,Y),t-1), hireq(H), loreq(L), Y-L < H-Y, holds(request(_,L),t-1).
do(X,move(1),t) :- holds(at(X,Y),t-1), not holds(request(_,Y),t-1), loreq(L), not holds(request(_,L),t-1).
do(X,move(-1),t) :- holds(at(X,Y),t-1), not holds(request(_,Y),t-1), hireq(H), not holds(request(_,H),t-1). 

do(X,serve,t) :- holds(at(X,Y),t-1), holds(request(_,Y),t-1).

%basic positional information
holds(at(X,Y+1),t):-do(X,move(1),t), holds(at(X,Y),t-1).
holds(at(X,Y-1),t):-do(X,move(-1),t), holds(at(X,Y),t-1).
holds(at(X,Y),t):-do(X,serve,t), holds(at(X,Y),t-1).
holds(at(X,Y),t):-not do(X,_,t),holds(at(X,Y),t-1).


%stop elevators from leaving the building ...
:-holds(at(X,Y),t),not floor(Y).

%stop elevators from picking up nothing
:-do(X,serve,t),not holds(request(_,Y),t-1), holds(at(X,Y),t).


% stop elevevators from not picking up when they are on a floor with a request
% this needs to be changed for multi-elevator instances to work efficiently!!!
%:- not do(X,serve,t), holds(request(_,Y),t-1), holds(at(X,Y),t-1).

% stop elevator from going into a direction where there is no request
% doesn't actually do anything; even if changing greater/lesser than signs it doesn't break the program
% change this to 'not 1{notreq(Z,t):Z>Y}'
notreq(Z,t) :- floor(Z), not holds(request(_,Z),t).

:- do(X,move(1),t+1), holds(at(X,Y),t), notreq(Z,t),Z<Y.
:- do(X,move(-1),t+1), holds(at(X,Y),t), notreq(Z,t),Z>Y.

%after elevator moved it has to do an action (move or serve) in the next timestep
:- do(X,move(1),t-1), not do(X,serve,t),not do(X,move(1),t).
:- do(X,move(-1),t-1), not do(X,serve,t),not do(X,move(-1),t).


%stop all elevators from doing nothing at a time step
:- holds(_,t), not do(_,_,t). 

%dirty way to save some headache...
temp(X,serve,t,Y):- do(X,serve,t), holds(at(X,Y),t).

%ensuring object permanence for elevators...
holds(at(X,Y),t):-holds(at(X,Y),t).


holds(request(R,Y),t):-holds(request(R,Y),t-1),not temp(_,serve, t, Y), simple_requests(R).

holds(request(deliver(X),Y),t):-holds(request(deliver(X),Y),t-1),not temp(elevator(X),serve, t, Y), agent(elevator(X)).

%minimize 
#minimize{1,t:holds(_,t)}.
#minimize{1,X,Y,t:do(X,Y,t)}.

#show do(A,X,t) : do(A,X,t). % output atoms indicating actions


%#show current_pos(X,F,t): current_pos(X,F,t).

%#show flag(t):flag(t).

#program check(t). % fulfillment of all requests can, e.g., be checked as follows
#show holds(X,t) : holds(X,t). % output atoms indicating states
:- query(t), holds(request(R,F),t).