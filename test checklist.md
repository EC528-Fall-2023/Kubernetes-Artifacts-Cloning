### Test Checklist
- [x] Check if -s and -d are input
- [x] ./main.sh -s test-demo -d  --> endless loop
- [x] Check if source and destination cluster exists
- [x] Has -n, check if namespaces exist in source/dest cluster
- [x] Check if objects exist in source namespace/cluster
- [x] Move single/multiple objects from source cluster to destination cluster
- [x] No -o given —> can move all the objects to target cluster
- [x] Clone all objects  from source cluster to dest cluster  -> ./main.sh -s test-demo -d test -a
- [x] Clone single/multiple namespaces to target cluster
- [x] Clone two objects to two namespaces
- [x] ./main.sh -s test-demo -d test -n source default -o deployment
- [x]  Check if labels exist in source namespace/cluster
- [x]  Clone single/multiples labels from all namespaces to target cluster
 ./main.sh -s test-demo -d test -l app=webapp app=mongo
- [x] Clone single/multiples labels from specific namespaces to target cluster
./main.sh -s test-demo -d test -l app=webapp app=mongo -n source
