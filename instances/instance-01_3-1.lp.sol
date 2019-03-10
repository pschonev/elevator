holds(at(elevator(1),2),0).
holds(request(call(up),1),0).
holds(at(elevator(1),1),1).
do(elevator(1),move(-1),1).
holds(request(call(up),1),1).
holds(at(elevator(1),1),2).
do(elevator(1),serve,2).
