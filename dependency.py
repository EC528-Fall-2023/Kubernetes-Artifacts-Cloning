#!/usr/bin/env python3
import sys
import yaml


# Does not yet handle DaemonSets outside of namespace
def findLabels(kubeObj, target_labels):
    matching_objects = []
    for obj in kubeObj:
        labels = {}
        if obj['kind'] == 'Service':
            labels = obj['spec'].get('selector', {})
        elif obj['kind'] == 'Deployment' or obj['kind'] == 'StatefulSet' or obj['kind'] == 'DaemonSet' or obj[
            'kind'] == "ReplicaSet":
            labels = obj['spec']['selector'].get('matchLabels', {})

        if any(target_labels.get(key) == labels.get(key) for key in target_labels):
            matching_objects.append([obj['kind'], obj['metadata']['name'], labels])

    # we can also return the obj yaml directly
    return matching_objects


def higherLevel(obj, kubeObj):  # Deployment, StatefulSet, DaemonSet
    dependencies = {"Secrets": [], "ConfigMaps": [], "AssociatedObjects": []}
    labels = obj['metadata'].get('labels', {})

    associated_objs = findLabels(kubeObj, labels)
    dependencies["AssociatedObjects"] = associated_objs

    if 'spec' in obj and 'template' in obj['spec'] and 'spec' in obj['spec']['template'] and 'containers' in \
            obj['spec']['template']['spec']:
        containers = obj['spec']['template']['spec']['containers']
        for container in containers:
            if 'env' in container:
                for env_var in container['env']:
                    if 'valueFrom' in env_var:
                        if 'secretKeyRef' in env_var['valueFrom']:
                            ref_name = env_var['valueFrom']['secretKeyRef'].get('name', 'Unknown')
                            dependencies["Secrets"].append(ref_name)
                        elif 'configMapKeyRef' in env_var['valueFrom']:
                            ref_name = env_var['valueFrom']['configMapKeyRef'].get('name', 'Unknown')
                            dependencies["ConfigMaps"].append(ref_name)
    return dependencies


def podDependencies(podObj, kubeObj):
    labels = podObj['metadata'].get('labels', {})
    associated_objs = findLabels(kubeObj, labels)
    dependencies = {
        "ConfigMaps": [],
        "Secrets": [],
        "PersistentVolumes": [],
        "PVC": [],
        "AssociatedObjects": associated_objs
    }

    if 'volumes' in podObj['spec']:
        for volume in podObj['spec']['volumes']:
            if 'configMap' in volume:
                dependencies["ConfigMaps"].append(volume['configMap']['name'])
            if 'secret' in volume:
                dependencies["Secrets"].append(volume['secret']['secretName'])
            if 'persistentVolumeClaim' in volume:
                dependencies["PVC"].append(volume['persistentVolumeClaim']['claimName'])

    if 'containers' in podObj['spec'] and 'volumeMounts' in podObj['spec']['containers'][0]:
        dependencies["PersistentVolumes"] = [volume_mount['name'] for volume_mount in
                                             podObj['spec']['containers'][0]['volumeMounts']]

    return dependencies


def pvDependencies(pvObj, kubeObj):
    labels = pvObj['metadata'].get('labels', {})
    associated_objs = findLabels(kubeObj, labels)

    return {
        "AssociatedObjects": associated_objs
    }


def pvcDependencies(pvcObj, kubeObj):
    labels = pvcObj['metadata'].get('labels', {})
    associated_objs = findLabels(kubeObj, labels)

    return {
        "AssociatedObjects": associated_objs
    }


def replicasetDependencies(rsObj, kubeObj):
    labels = rsObj['metadata'].get('labels', {})
    selector = rsObj['spec'].get('selector', {}).get('matchLabels', {})
    associated_objs = findLabels(kubeObj, selector)

    return {
        "Selector": selector,
        "AssociatedObjects": associated_objs
    }


def writeToYAML(dependencies, output_file):
    try:
        with open(output_file, 'w') as file:
            yaml.dump(dependencies, file)
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")


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


def findDependenciesByResourceName(kubeObj, resource_name, resource_type):
    resource_type_lower = resource_type.lower()
    for obj in kubeObj:
        if obj['kind'].lower() == resource_type_lower and obj['metadata'].get('name') == resource_name:
            if resource_type_lower == "pod":
                return podDependencies(obj, kubeObj)
            elif resource_type_lower == "replicaset":
                return replicasetDependencies(obj, kubeObj)
            elif resource_type_lower == "persistentvolume":
                return pvDependencies(obj, kubeObj)
            elif resource_type_lower == "persistentvolumeclaim":
                return pvcDependencies(obj, kubeObj)
            elif resource_type_lower in ["deployment", "statefulset", "daemonset"]:
                return higherLevel(obj, kubeObj)
    return {}


def dependencies_format(dependencies):
    result = {}
    for key, value in dependencies.items():
        if key == "AssociatedObjects":
            for item in value:
                type, resource_name = item[0:2]
                resource_type = type.lower()
                if resource_type not in result:
                    result[resource_type] = set()
                result[resource_type].add(resource_name)
        elif value:
            resource_key = key.lower()
            if resource_key not in result:
                result[resource_key] = set()
            result[resource_key].update(value)

    for key in result:
        result[key] = list(result[key])
    return result


def maintTest(fileName, resource_name, resource_type):
    kubeObj = extractObj(fileName)
    dependencies = findDependenciesByResourceName(kubeObj, resource_name, resource_type)
    print(dependencies)

    writeToYAML(dependencies_format(dependencies), "/tmp/clone/dependencies_output.yaml")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <file_name> <resource_name> <resource_type>")
        sys.exit(1)

    file_name = sys.argv[1]
    resource_type = sys.argv[2]
    resource_name = sys.argv[3]
    maintTest(file_name, resource_name, resource_type)


# if __name__ == "__main__":
#     file_name = input("Enter file name: ")
#     resource_name = input("Enter resource name: ")
#     resource_type = input("Enter resource type: ")
#     maintTest(file_name, resource_name, resource_type)

