#!/bin/bash

# This script acts as a kubectl plugin for cloning Kubernetes objects

function usage() {
    echo "Usage: kubectl clone [OPTIONS]"
    echo
    echo "Options:"
        echo "-s, --source          KUBECONFIG of the source cluster."
    echo "-d, --destination     KUBECONFIG of the destination cluster."
    echo "-o, --objects         List of Kubernetes objects to clone (comma separated e.g. pods,services). Use 'all' to clone all objects."
    echo "-l, --labels          Label selector to filter the objects to be cloned (e.g. app=robot-shop)."
    echo "-n, --namespace       Namespace of the objects to be cloned."
    echo "-a, --all             Migrate everything that exists in the source cluster."
    echo "-h, --help            Display this help and exit."
    echo
    echo "Example:"
    echo "kubectl clone -s /path/to/source/kubeconfig -d /path/to/destination/kubeconfig -o pods,services -l app=robot-shop -n my-namespace"
}

function checkNamespace(){
    local namespace="$1"
    if ! kubectl get namespace "$namespace" --context="$DEST_KUBECONFIG" 2>/dev/null; then
    echo "Namespace $namespace does not exist in the target cluster. Creating..."
    kubectl create namespace "$namespace" --context="$DEST_KUBECONFIG"
    echo "Namespace $namespace created."
    fi
}

function switchCluster(){
    CLUSTER_CONTEXT="$1"
    kubectl config use-context $CLUSTER_CONTEXT
}

function get_namespaces() {
  local namespaces=($(kubectl get namespaces -o custom-columns=NAME:.metadata.name --no-headers=true))
  local valid_namespaces=()

  for ns in "${namespaces[@]}"; do
    if [[ $ns == "kube-node-lease" ]] || [[ $ns == "kube-public" ]] || [[ $ns == "kube-system" ]]; then
      continue
    fi
    valid_namespaces+=("$ns")
  done
  echo "${valid_namespaces[@]}"
}

function cloneAndModifyYaml() {
    local resource_type="$1"
    local namespace="$2"
    local dest_cluster="$3"
    local label="$4"  
    local output_file_list=()

    # Check if the resource exists in the source namespace
    if ! kubectl get "$resource_type" -n "$namespace" --context="$SRC_KUBECONFIG" 2>/dev/null; then
        return
    fi

    local names=($(kubectl get "$resource_type" -n "$namespace" --no-headers=true -o custom-columns=NAME:.metadata.name | grep -v 'kube-root-ca.crt'))

    for n in "${names[@]}"; do
        > "/tmp/${namespace}_${n}.yaml" # clear
        kubectl get "$resource_type" "$n" -n "$namespace" -o yaml > "/tmp/${namespace}_${n}.yaml"

        if [ "$resource_type" == "service" ]; then
            > "/tmp/${namespace}_${n}_modified.yaml"
            # Modify service YAML
            yq eval 'del(.spec.ports[0].nodePort) | del(.spec.clusterIPs) | del(.spec.clusterIP)' "/tmp/${namespace}_${n}.yaml" > "/tmp/${namespace}_${n}_modified.yaml"
            kubectl apply -f "/tmp/${namespace}_${n}_modified.yaml" --context="$dest_cluster" -n "$namespace"
        else
            # Apply other YAMLs directly
            kubectl apply -f "/tmp/${namespace}_${n}.yaml" --context="$dest_cluster" -n "$namespace"
        fi

        echo "$n migrated!"
        output_file_list+=("/tmp/${namespace}_${n}.yaml")
    done

    echo "${output_file_list[@]}"
}

# function cloneConfigMapYaml() {
#     cloneAndModifyYaml "configmap" "$1" "$2"
# }

# function cloneServiceYaml() {
#     cloneAndModifyYaml "service" "$1" "$2"
# }

# function cloneOtherYaml() {
#     cloneAndModifyYaml "$1" "$2" "$3"
# }


# ---------- Program Starts Here ----------

# parse command
# only support single namespace now
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -s|--source) 
            SRC_KUBECONFIG="$2"; 
            shift 2
            ;;
        -d|--destination) 
            DEST_KUBECONFIG="$2"; 
            shift 2
            ;;
        -n|--namespace)   #如果没有-n的话就clone all
            NAMESPACES+=("$2")
            shift 2
            while [[ "$1" != -* && "$#" -gt 0 ]]; do
                NAMESPACES+=("$1")
                shift
            done
            ;;
        -l|--labels)  
            LABELS+=("$2")
            shift 2
            while [[ "$1" != -* && "$#" -gt 0 ]]; do
                LABELS+=("$1")
                shift
            done
            ;;
        -o|--objects) 
            OBJECTS+=("$2")
            shift 2
            while [[ "$1" != -* && "$#" -gt 0 ]]; do
                OBJECTS+=("$1")
                shift
            done
            ;;
        -a|--all) 
            ALL=true 
            shift
            ;;
        -h|--help) 
            usage; 
            exit 0 
            ;;
        *) echo "Unknown parameter passed: $1"; usage; exit 1 ;;
    esac
done


echo "source: $SRC_KUBECONFIG"
echo "destination: $DEST_KUBECONFIG"

for ns in "${LABELS[@]}"; do
  echo "label: $ns"
done

for name in "${NAMESPACES[@]}"; do
    echo "namespace: $name"
done

for obj in "${OBJECTS[@]}"; do
    echo "object: $obj"
done
types=("persistentvolumes" "configmaps" "secret" "pods" "deployment" "service" "replicasets" "statefulsets" "daemonsets")

#Check environment before migration

# 1. Check if clusters exist 

if [[ -z "${SRC_KUBECONFIG}" || -z "${DEST_KUBECONFIG}" ]]; then
    echo "Error: --source and --destination options are mandatory!"
    usage
    exit 1
else
    #check if source and destination cluster exists
    src=$(kubectl config use-context $SRC_KUBECONFIG 2>&1)
    dest=$(kubectl config use-context $DEST_KUBECONFIG 2>&1)
    if [[ $src == *"no context exists"*  ]] || [[ $dest == *"no context exists"*  ]]; then 
        echo "Cluster name not exists, check below"
        kubectl config get-contexts
        exit 1
    fi
    #get dest cluster config file: used to connect destination host
    kubectl config use-context $DEST_KUBECONFIG
    kubectl config view --raw > "$DEST_KUBECONFIG-config.yaml"
fi



# apply order must be: "persistentvolumes" "configmaps" "secret" "pods" "deployment" "service" "replicasets" "statefulsets" "daemonsets"
if $ALL; then
    echo "Cloning all objects from source cluster with KUBECONFIG: ${SRC_KUBECONFIG} to destination cluster with KUBECONFIG: ${DEST_KUBECONFIG}..."
    switchCluster "$SRC_KUBECONFIG"

    namespace_list=($(get_namespaces))
    for namespace in "${namespace_list[@]}"; do
        checkNamespace "$namespace"
        for type in "${types[@]}"; do
            cloneAndModifyYaml "$type" "$namespace" "$DEST_KUBECONFIG"
        done
    done
fi

# 2.1. Check if namespaces exist in  source cluster

# 2.2. Check if namespaces exist in  dest cluster
if [ -n "${NAMESPACES[*]}" ]; then
    for name in "${NAMESPACES[@]}"; do
        checkNamespace "$name"
    done
else
    echo "NAMESPACES is empty. No need checking"
fi

# 3. Check if objects exist in source namespace



