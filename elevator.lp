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
actions(serve;move(1);move(-1)). %find out if order is relevant for evaluation
simple_requests(call(up);call(down)).
holds(at(X, Y),0):- agent(X), init(at(X, Y)).
holds(request(X,Y),0):-init(request(X,Y)).

#program step(t). % actions, effects, and minimization go below
{do(X,Y,t): actions(Y)}1:-agent(X).

%basic positional information
current_pos(X,N+1,t):-do(X,move(1),t), holds(at(X,N),t-1).
current_pos(X,N-1,t):-do(X,move(-1),t), holds(at(X,N),t-1).
current_pos(X,N,t):-do(X,serve,t), holds(at(X,N),t-1).
current_pos(X,N,t):-not do(X,_,t),holds(at(X,N),t-1).

%stop elevators from leaving the building ...
:-current_pos(X,N,t),not floor(N).

%stop elevators from picking up nothing
:-do(X,serve,t),not holds(request(_,Y),t-1), current_pos(X,Y,t).

%stop elevevators from not picking up when they are on a floor with a request
:- holds(request(_,Y),t+1),holds(at(_,Y),t).
:- do(X,serve,t),holds(at(X,Y),t), do(X',serve,t),holds(at(X',Y),t),X!=X'. 

%stop elevator from going into a direction where there is no request
%doesn't actually do anything; even if changing greater/lesser than signs it doesn't break the program
%:- do(X,move(1),t+1), holds(at(X,Y),t), not 1{holds(request(_,Z),t): Z > Y,floor(Z)}.
%:- do(X,move(-1),t+1), holds(at(X,Y),t), not 1{holds(request(_,Z),t): Z > Y,floor(Z)}.

%after elevator moved it has to do an action (move or serve) in the next timestep
:- do(X,move(1),t-1), not do(X,serve,t),not do(X,move(1),t).
:- do(X,move(-1),t-1), not do(X,serve,t),not do(X,move(-1),t).


%stop all elevators from doing nothing at a time step
:- holds(_,t), not do(_,_,t). 

%dirty way to save some headache...
temp(X,serve,t,Y):- do(X,serve,t), current_pos(X,Y,t).

%ensuring object permanence for elevators...
holds(at(X,Y),t):-current_pos(X,Y,t).


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