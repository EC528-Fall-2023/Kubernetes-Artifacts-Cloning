import yaml

def extract_resources(yaml_file):
    with open(yaml_file, 'r') as file:
        try:
            objs = yaml.safe_load_all(file)
            for obj in objs:
                if obj is None:
                    continue
                kind = obj.get('kind')
                metadata = obj.get('metadata', {})
                name = metadata.get('name', 'Unknown')

                if kind in ['Deployment', 'ReplicaSet', 'DaemonSet', 'StatefulSet']:
                    spec = obj.get('spec', {})
                    replicas = spec.get('replicas', 'N/A' if kind in ['DaemonSet', 'StatefulSet'] else 1)
                    template = spec.get('template', {})
                    pod_spec = template.get('spec', {})
                    containers = pod_spec.get('containers', [])
                    resources_list = [container.get('resources', {}) for container in containers]

                    if kind == 'StatefulSet':
                        volume_templates = spec.get('volumeClaimTemplates', [])
                        for template in volume_templates:
                            storage = template.get('spec', {}).get('resources', {}).get('requests', {}).get('storage', 'Unknown')
                            resources_list.append({'storage': storage})

                    print("Object Name:", name, ", Type:", kind, ", Replicas:", str(replicas), ", Resources:", resources_list)

                elif kind == 'PersistentVolumeClaim':
                    spec = obj.get('spec', {})
                    storage = spec.get('resources', {}).get('requests', {}).get('storage', 'Unknown')
                    resources = {'storage': storage}
                    print("Object Name:", name, ", Type:", kind, ", Replicas: N/A, Resources:", resources)

        except yaml.YAMLError as exc:
            print("Error parsing YAML file:", exc)

if __name__ == "__main__":
    yaml_file = "info_of_minikube.yaml"
    extract_resources(yaml_file)
