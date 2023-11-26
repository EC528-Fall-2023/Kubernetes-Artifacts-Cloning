#!/bin/bash

# This script acts as a kubectl plugin for cloning Kubernetes objects

#In the future, the resource type is defined by the dependency graph within the source cluster.
types=("serviceaccount" "persistentvolumes" "configmaps" "secret" "pods" "deployment" "service" "statefulsets" "daemonsets")

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

# Check if the namespace exists in target cluster, if not, create it.
function checkNamespace() {
    local namespace="$1"
    if ! kubectl get namespace "$namespace" --kubeconfig "$DEST_KUBECONFIG" 2>/dev/null; then
        echo "Namespace $namespace does not exist in the target cluster. Creating..."
        if kubectl create namespace "$namespace" --kubeconfig "$DEST_KUBECONFIG"; then
            echo "Namespace $namespace created."
        else
            echo "Failed to create namespace $namespace."
            exit 1
        fi
    fi
}


function switchCluster() {
    local CLUSTER_CONTEXT="$1"
    if kubectl config use-context "$CLUSTER_CONTEXT" 2>/dev/null; then
        echo "Switched to context: $CLUSTER_CONTEXT"
    else
        echo "Failed to switch to context: $CLUSTER_CONTEXT"
        exit 1
    fi
}


function get_all_namespaces() {
  local namespaces=($(kubectl get namespaces --kubeconfig $SRC_KUBECONFIG -o custom-columns=NAME:.metadata.name --no-headers=true))
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
    local resource_name="$4"
    local output_file_list=()

    # Check if the resource exists in the source namespace
    if ! kubectl get "$resource_type" -n "$namespace" --kubeconfig "$SRC_KUBECONFI" 2>/dev/null; then
        echo "Resource: $resource_type not exist in $SRC_KUBECONFIG"
        return
    fi

    # Check if the resource name is specified
    if [ -z "$resource_name" ]; then
        local names=($(kubectl get "$resource_type" --kubeconfig $SRC_KUBECONFIG -n "$namespace" --no-headers=true -o custom-columns=NAME:.metadata.name | grep -v 'kube-root-ca.crt' | grep -v 'kubernetes' | grep -v 'default'))
    else
        local names=("$resource_name")
    fi
    
    # if configmap and secret (and so on) has existed in the target cluster, k8s will combine them instead of overwriting
    # therefore, the script will first check if the resouce has exisited in target cluster --> exist, delete it, then apply

    for n in "${names[@]}"; do
        local resource_exists=false
        if kubectl get "$resource_type" "$n" -n "$namespace" --kubeconfig "$DEST_KUBECONFIG" &>/dev/null; then
            # exist -> delete
            kubectl delete "$resource_type" "$n" -n "$namespace" --kubeconfig "$DEST_KUBECONFIG"
            resource_exists=true
        fi

        > "/tmp/clone/${namespace}_${n}.yaml" # clear
        kubectl get "$resource_type" "$n" --kubeconfig $SRC_KUBECONFIG -n "$namespace" -o yaml > "/tmp/clone/${namespace}_${n}.yaml"

        if [ "$resource_type" == "service" ]; then
            > "/tmp/clone/${namespace}_${n}_modified.yaml"
            # Modify service YAML
            yq eval 'del(.spec.ports[0].nodePort) | del(.spec.clusterIPs) | del(.spec.clusterIP)' "/tmp/clone/${namespace}_${n}.yaml" > "/tmp/clone/${namespace}_${n}_modified.yaml"
            kubectl apply -f "/tmp/clone/${namespace}_${n}_modified.yaml" --kubeconfig="$DEST_KUBECONFIG" -n "$namespace" 
        else
            # Apply other YAMLs directly
            kubectl apply -f "/tmp/clone/${namespace}_${n}.yaml" --kubeconfig="$DEST_KUBECONFIG" -n "$namespace" 
        fi

        if [ "$resource_exists" = true ]; then
            echo "$n already existed in the target cluster and has been replaced."
        else
            echo "$n migrated to the target cluster."
        fi

        output_file_list+=("/tmp/clone/${namespace}_${n}.yaml")

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

function check_filter(){
    # check if the command contains -n
    if [[ "$has_NAMESPACE" == false ]]; then

        NAMESPACES=($(get_all_namespaces))
    
    fi

    if [[ "$has_LABELS" == false ]]; then

        LABELS=("")
    fi

    # check if the command contains -o
    if [[ "$has_OBJECTS" == false ]]; then
    
        OBJECTS=("")

    fi
}

function require_arg() {
    local type="$1"
    local value="$2"
    if [[ -z $value || $value == -* ]]; then
	echo "Error: Argument for $type is missing" >&2
	usage
	exit 1
    fi
}

function combination(){
    #switchCluster "$SRC_KUBECONFIG"
    for namespace in "${NAMESPACES[@]}"; do
        
        if [ -z "$LABELS" ] && [ -n "$OBJECTS" ]; then
	    # If labels are empty but objects are not, filtering yaml based on the given object types
            for object in "${OBJECTS[@]}"; do
                local name_list=()
                echo "Namespace: $namespace, Object Type: $object"
                name_list+=($(kubectl get $object --kubeconfig $SRC_KUBECONFIG -n $namespace --no-headers=true -o custom-columns=NAME:.metadata.name | grep -v 'kube-root-ca.crt'| grep -v 'kubernetes'| grep -v 'default'))
                for name in "${name_list[@]}"; do
                    cloneAndModifyYaml "$object" "$namespace" "$DEST_KUBECONFIG" "$name"
                done
            done


        elif [ -n "$LABELS" ] && [ -z "$OBJECTS" ]; then
	    # If labels are not empty but objects are, filtering yaml based on labels
            for label in "${LABELS[@]}"; do
                for type in "${types[@]}"; do
                    local name_list=()
                    echo "Namespace: $namespace, Label: $label, Type: $type"
                    name_list+=($(kubectl get $type --kubeconfig $SRC_KUBECONFIG --selector="$label" -n $namespace --no-headers=true -o custom-columns=NAME:.metadata.name | grep -v 'kube-root-ca.crt'| grep -v 'kubernetes'| grep -v 'default'))
                    for name in "${name_list[@]}"; do
                        cloneAndModifyYaml "$type" "$namespace" "$DEST_KUBECONFIG" "$name"
                    done
                done
            done
        elif [ -n "$LABELS" ] && [ -n "$OBJECTS" ]; then
	    # Mix and match labels and objects if both of them are not empty
            for object in "${OBJECTS[@]}"; do
                local name_list=()
                for label in "${LABELS[@]}"; do
                    echo "Namespace: $namespace, Label: $label, Object Type: $object"
                    name_list+=($(kubectl get $object --kubeconfig $SRC_KUBECONFIG -n $namespace --selector="$label" --no-headers=true -o custom-columns=NAME:.metadata.name | grep -v 'kube-root-ca.crt'| grep -v 'kubernetes'| grep -v 'default'))
                done
                for name in "${name_list[@]}"; do
                    cloneAndModifyYaml "$object" "$namespace" "$DEST_KUBECONFIG" "$name"
                done
            done
        else
            # Clone all if objects and labels are not provided
            for type in "${types[@]}"; do
                local name_list=()
                name_list+=($(kubectl get $type --kubeconfig $SRC_KUBECONFIG -n $namespace --no-headers=true -o custom-columns=NAME:.metadata.name | grep -v 'kube-root-ca.crt'| grep -v 'kubernetes'| grep -v 'default'))
                for name in "${name_list[@]}"; do
                    cloneAndModifyYaml "$type" "$namespace" "$DEST_KUBECONFIG" "$name"
                done
            done
            echo "Getting and migrating all resources in namespace: $namespace"
        fi
    done

}

# ---------- Program Starts Here ----------

# parse command
has_NAMESPACE=false;
has_LABELS=false;
has_OBJECTS=false;

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -s|--source) 
	    require_arg "$1" "$2"
            SRC_KUBECONFIG="$2"; 
            shift 2
            ;;
        -d|--destination) 
	    require_arg "$1" "$2"
            DEST_KUBECONFIG="$2"; 
            shift 2
            ;;
        -n|--namespace)   
	    require_arg "$1" "$2"
    	    has_NAMESPACE=true
            NAMESPACES+=("$2")
            shift 2
            while [[ "$1" != -* && "$#" -gt 0 ]]; do
                NAMESPACES+=("$1")
                shift
            done
            ;;
        -l|--labels)  
	    require_arg "$1" "$2"	
            has_LABELS=true
            LABELS+=("$2")
            shift 2
            while [[ "$1" != -* && "$#" -gt 0 ]]; do
                LABELS+=("$1")
                shift
            done
	    echo $LABELS
            ;;
        -o|--objects) 
	    require_arg "$1" "$2"
            has_OBJECTS=true
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

check_filter
#testing
#echo $has_NAMESPACE, $has_LABELS, $has_OBJECTS

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

#Check environment before migration

# 0.1. Check if the machine has installed yq

if ! command -v yq &>/dev/null; then
    if [[ $(uname) == "Darwin" ]]; then
        echo "yq is not installed. Installing with Homebrew..."
        brew install yq
    else
        echo "yq is not installed, and automatic installation is not supported on this platform. Please install yq manually."
        exit 1
    fi
fi

# 0.2. Check if /tmp/clone folder exists, if not, create it

if [ ! -d "/tmp/clone" ]; then
    mkdir -p "/tmp/clone"
fi

# 1. Check if clusters exist 

# 1.1 Check if -s and -d are input
if [[ -z "${SRC_KUBECONFIG}" || -z "${DEST_KUBECONFIG}" ]]; then
    echo "Error: --source and --destination options are mandatory!"
    usage
    exit 1
else

# 1.2 Check if source and destination cluster exists
    src=$(kubectl config get all --kubeconfig $SRC_KUBECONFIG 2>&1)
    dest=$(kubectl config get all --kubeconfig $DEST_KUBECONFIG 2>&1)
    if [[ $src == *"Error in configuration"*  ]] || [[ $dest == *"Error in configuration"*  ]]; then 
        echo "Cluster name not exists, check below"
        kubectl config get-contexts
        exit 1
    fi
    #get dest cluster config file: used to connect destination host

    # TODO:USE config yaml file to connect another machine
    #kubectl config use-context $SRC_KUBECONFIG
    #kubectl config view --raw > "/tmp/clone/$SRC_KUBECONFIG-config.yaml"
    #kubectl config use-context $DEST_KUBECONFIG
    #kubectl config view --raw > "/tmp/clone/$DEST_KUBECONFIG-config.yaml"
fi

# 2. Has -n, check if namespaces exist in source/dest cluster

for ns in "${NAMESPACES[@]}"; do
    # source
    if $has_NAMESPACE ; then
        if ! kubectl get namespace "$ns" --kubeconfig "$SRC_KUBECONFIG" 2>/dev/null; then
        echo "Namespace $namespace does not exist in the source cluster. Check below"
        kubectl get namespace --kubeconfig "$SRC_KUBECONFIG"
        exit 1
        fi
        # destination
    fi
    checkNamespace "$ns"
done


# 3. Check if objects exist in source namespace/cluster
if [[ "$has_OBJECTS" == true ]]; then
    for obj in "${OBJECTS[@]}"; do
        object_found=false  # Flag to track if the object is found in any namespace
        for ns in "${NAMESPACES[@]}"; do
            object_list=($(kubectl get "$obj" -n "$ns" --kubeconfig "$SRC_KUBECONFIG" --no-headers=true -o custom-columns=NAME:.metadata.name | grep -v 'kubernetes'| grep -v 'kube-root-ca.crt'| grep -v 'default'))
            if [ ${#object_list[@]} -gt 0 ]; then
                echo "Object $obj exists in namespace: $ns"
                object_found=true
                break
            fi
        done
        if [ "$object_found" == false ]; then
            echo "Object $obj does not exist in any of the specified namespaces."
            exit 1
        fi
    done
fi

# 4. Check if labels exist in source namespace/cluster
if [[ "$has_LABELS" == true ]]; then
    echo "check Labels"
    for label in "${LABELS[@]}"; do
        label_found=false  # Flag to track if the label is found in any namespace
        for ns in "${NAMESPACES[@]}"; do
	    echo $ns
            for type in "${types[@]}"; do
		echo $type    
                label_list=($(kubectl get "$type" -n "$ns" -l "$label" --kubeconfig "$SRC_KUBECONFIG" --no-headers=true -o custom-columns=NAME:.metadata.name | grep -v 'kubernetes'| grep -v 'kube-root-ca.crt'| grep -v 'default'))
		echo $label_list
                if [ ${#label_list[@]} -gt 0 ]; then
                    echo "Label $label exists in namespace: $ns"
                    label_found=true
                    break
                fi
            done
            if [ "$label_found" == true ]; then
                break
            fi
        done
        if [ "$label_found" == false ]; then
            echo "Object $label does not exist in any of the specified namespaces."
            exit 1
        fi
    done
fi


#---------------- Environment Check Done ----------------

#In the future, the resource type is defined by the dependency graph within the source cluster.
#types=("serviceaccount" "persistentvolumes" "configmaps" "secret" "pods" "deployment" "service" "statefulsets" "daemonsets")

# apply order must be: "persistentvolumes" "configmaps" "secret" "pods" "deployment" "service" "replicasets" "statefulsets" "daemonsets"
if [[ $ALL ]] ; then
    echo "Cloning all objects from source cluster with KUBECONFIG: ${SRC_KUBECONFIG} to destination cluster with KUBECONFIG: ${DEST_KUBECONFIG}..."
    #switchCluster "$SRC_KUBECONFIG"

    namespace_list=($(get_all_namespaces))
    for namespace in "${namespace_list[@]}"; do
        checkNamespace "$namespace"
        for type in "${types[@]}"; do
            cloneAndModifyYaml "$type" "$namespace" "$DEST_KUBECONFIG"
        done
    done
    exit 0
fi

combination

# ask user to delete the tmp file
echo "Do you want to delete the yaml file? (y/n)"
read answer

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    rm /tmp/clone/*.yaml
fi
