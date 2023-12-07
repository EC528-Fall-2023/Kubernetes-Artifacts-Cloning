import yaml

def extract_resources(yaml_file):
    with open(yaml_file, 'r') as file:
        try:
            objs = yaml.safe_load_all(file)
            for obj in objs:
                if obj is None:
                    continue
                kind = obj.get('kind')
                if kind in ['Deployment', 'ReplicaSet', 'StatefulSet', 'DaemonSet']:
                    metadata = obj.get('metadata', {})
                    name = metadata.get('name', 'Unknown')
                    spec = obj.get('spec', {})
                    replicas = spec.get('replicas', 'N/A' if kind == 'DaemonSet' else 1)
                    template = spec.get('template', {})
                    pod_spec = template.get('spec', {})
                    containers = pod_spec.get('containers', [])
                    for container in containers:
                        resources = container.get('resources', {})
                        print("Object Name:", name, ", Type:", kind, ", Replicas:", str(replicas), ", Resources:", resources)
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML file: {exc}")

if __name__ == "__main__":
    yaml_file = "info_of_minikube.yaml"
    extract_resources(yaml_file)
