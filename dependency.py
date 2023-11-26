import yaml

#Does not yet handle DaemonSets outside of namespace
def findLabels(kubeObj, target_labels):
    matching_objects = []
    for obj in kubeObj:
        labels = {}
        if obj['kind'] == 'Service':
            labels = obj['spec'].get('selector', {})
        elif obj['kind'] == 'Deployment' or obj['kind'] == 'StatefulSet' or obj['kind'] == 'DaemonSet' or obj['kind'] == "ReplicaSet":
            labels = obj['spec']['selector'].get('matchLabels', {})
            
        if any(target_labels.get(key) == labels.get(key) for key in target_labels):
            matching_objects.append([obj['kind'], obj['metadata']['name'], labels])

    #we can also return the obj yaml directly
    return matching_objects


def podDependencies(podObj, kubeObj):
    podName = podObj['metadata'].get('name', "")
    ns = podObj['metadata'].get('namespace', "default")
    config_maps, secrets, pvcs = [], [], []
    labels = podObj['metadata'].get('labels', {})

    if 'volumes' in podObj['spec']:
        for volume in podObj['spec']['volumes']:
            if 'configMap' in volume:
                config_maps.append(volume['configMap']['name'])
            if 'secret' in volume:
                secrets.append(volume['secret']['secretName'])
            if 'persistentVolumeClaim' in volume:
                pvcs.append(volume['persistentVolumeClaim']['claimName'])

    persistent_volumes = []
    if 'containers' in podObj['spec'] and 'volumeMounts' in podObj['spec']['containers'][0]:
        persistent_volumes = [volume_mount['name'] for volume_mount in podObj['spec']['containers'][0]['volumeMounts']]

    print("Pod name:", podName)
    print("Namespace:", ns)
    print("Dependencies for Pod:\n")
    print("Config maps: ", config_maps)
    print("Secrets: ", secrets)
    print("Persistent volumes: ", persistent_volumes)
    print("PVCs: ", pvcs)
    print("Labels: ", labels)
    print("\nAssociated Obj:")
    print(findLabels(kubeObj, labels))
    print("----------------------------------")
    
def extractObj(file_path):
    try:
        with open(file_path, 'r') as file:
            documents = yaml.safe_load_all(file.read())
        top_level_objects = [doc for doc in documents if doc is not None]

        return top_level_objects
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return []
    except FileNotFoundError:
        print("The file was not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
def maintTest():
    kubeObj = extractObj("test.yml")
    for obj in kubeObj:
        kind = obj['kind']
        if kind == "Pod":
            podDependencies(obj, kubeObj)
    
if __name__ == "__main__":
    maintTest()


    # need to find statefulset
    # need to check for replicasts
