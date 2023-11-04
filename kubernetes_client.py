import json
from datetime import datetime

from kubernetes import client, config
from kubernetes.client.rest import ApiException


config.load_kube_config()
api_instance = client.CoreV1Api()  # use for getting core resources

# get all namespaces names
try:
    namespaces = api_instance.list_namespace()
    namespace_names = [item.metadata.name for item in namespaces.items]
    print("Namespaces:", namespace_names)
except ApiException as e:
    print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)


namespace_name = "source"


class ScrapeData:
    def __init__(self):
        self.pods = []
        self.services = []
        self.endpoints = []
        self.persistent_volumes = []
        self.persistent_volume_claims = []
        self.deployments = []
        self.daemon_sets = []
        self.replica_sets = []
        self.stateful_sets = []
        self.ingresses = []
        self.config_maps = []
        self.secrets = []

def custom_json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

try:
    pods = api_instance.list_namespaced_pod(namespace_name)
    services = api_instance.list_namespaced_service(namespace_name)
    endpoints = api_instance.list_namespaced_endpoints(namespace_name)
    persistent_volumes = api_instance.list_persistent_volume()
    persistent_volume_claims = api_instance.list_namespaced_persistent_volume_claim(namespace_name)
    deployments = client.AppsV1Api().list_namespaced_deployment(namespace_name)
    daemonsets = client.AppsV1Api().list_namespaced_daemon_set(namespace_name)
    replicatesets = client.AppsV1Api().list_namespaced_replica_set(namespace_name)
    statefulsets = client.AppsV1Api().list_namespaced_stateful_set(namespace_name)
    configmap = api_instance.list_namespaced_config_map(namespace_name)

    ingresses = client.NetworkingV1Api().list_namespaced_ingress(namespace_name)
    secrets = api_instance.list_namespaced_secret(namespace_name)

    pods_info = [item.to_dict() for item in pods.items]
    services_info = [item.to_dict() for item in services.items]
    endpoints_info = [item.to_dict() for item in endpoints.items]
    secrets_info = [item.to_dict() for item in secrets.items]
    ingresses_info = [item.to_dict() for item in ingresses.items]
    persistent_volumes_info=[item.to_dict() for item in persistent_volumes.items]
    persistent_volume_claims_info=[item.to_dict() for item in persistent_volume_claims.items]
    deployments_info=[item.to_dict() for item in deployments.items]
    daemonsets_info=[item.to_dict() for item in daemonsets.items]
    replicatesets_info=[item.to_dict() for item in replicatesets.items]
    statefulsets_info=[item.to_dict() for item in statefulsets.items]
    configmap_info=[item.to_dict() for item in configmap.items]


    data = ScrapeData()
    data.pods = pods_info
    data.services=services_info
    data.endpoints=endpoints_info
    data.persistent_volumes=persistent_volumes_info
    data.persistent_volume_claims=persistent_volume_claims_info
    data.deployments=deployments_info
    data.daemon_sets=daemonsets_info
    data.replica_sets=replicatesets_info
    data.stateful_sets=statefulsets_info
    data.ingresses=ingresses_info
    data.config_maps=configmap_info
    data.secrets=secrets_info

    data_dict = {
        "pods": data.pods,
        "services": data.services,
        "endpoints": data.endpoints,
        "persistent_volumes": data.persistent_volumes,
        "persistent_volume_claims": data.persistent_volume_claims,
        "deployments": data.deployments,
        "daemon_sets": data.daemon_sets,
        "replica_sets": data.replica_sets,
        "stateful_sets": data.stateful_sets,
        "ingresses": data.ingresses,
        "config_maps": data.config_maps,
        "secrets": data.secrets
    }

    output_file = "data.json"


    with open(output_file, "w") as json_file:
        json.dump(data_dict, json_file, indent=4, default=custom_json_serializer)



    print("--------- Pods ---------")
    for pod in pods_info:
        if "metadata" in pod and "name" in pod["metadata"] and pod["metadata"]["name"] is not None:
            print(pod["metadata"]["name"])

        if "spec" in pod and "containers" in pod["spec"]:
            for container in pod["spec"]["containers"]:
                # find secrets
                if "env" in container and container["env"] is not None:
                    for env in container["env"]:
                        if "value_from" in env and env["value_from"] is not None:
                            # find secrets
                            if "secret_key_ref" in env["value_from"] \
                                    and env["value_from"]["secret_key_ref"] is not None \
                                    and "name" in env["value_from"]["secret_key_ref"] \
                                    and env["value_from"]["secret_key_ref"]["name"] is not None:
                                print(env["value_from"]["secret_key_ref"]["name"])
                            # find configMaps
                            if "config_map_key_ref" in env["value_from"] \
                                    and env["value_from"]["config_map_key_ref"] is not None \
                                    and "name" in env["value_from"]["config_map_key_ref"] \
                                    and env["value_from"]["config_map_key_ref"]["name"] is not None:
                                print(env["value_from"]["config_map_key_ref"]["name"])
        # temporarily not consider dependencies in  volumes
        if "volumes" in pod["spec"]:
            for volume in pod["spec"]["volumes"]:
                # Show PVCs
                if volume["persistent_volume_claim"] is not None:
                    print(volume["persistent_volume_claim"])
                # Show ConfigMap mounted as a volume
                if volume["config_map"] is not None:
                    print(volume["config_map"])
                # Show Secret mounted as a volume
                if volume["secret"] is not None:
                    print(volume["secret"])

    # Services
    print("--------- Services ---------")
    for service in services_info:
        if service["metadata"]["name"] is not None:
            print(service["metadata"]["name"])
            service_id = service["metadata"]["name"]
            if service_id == "kubernetes":
                continue
            for endpoint in endpoints_info:
                if endpoint["metadata"]["name"] is not None and service_id == endpoint["metadata"]["name"]:
                    service["subsets"] = endpoint["subsets"]
            for subset in service["subsets"]:
                addresses = (subset.get("addresses", []) + subset.get("notReadyAddresses", []))
                for address in addresses:
                    if address is not None:
                        if address["target_ref"]["kind"] == "Pod":
                            print(address["target_ref"]["name"])
        # Find all external IPs of service, and add them
        if service["status"]["load_balancer"]["ingress"] is not None:
            for lb in service["status"]["load_balancer"]["ingress"]:
                ip = lb["ip"]
                print(ip)
    # Add Ingresses and link to Services
    print("--------- Ingresses Untested ---------")
    for ingress in ingresses_info:
        print(ingress["metadata"]["name"])
        if ingress["status"]["load_balancer"]["ingress"] is not None:
            for lb in ingress["status"]["load_balancer"]["ingress"]:
                ip = lb["ip"]
                print("Ingress external ips:" + ip)
        # Ingresses joined to Services by the rules
        if ingress["spec"]["rules"] is not None:
            for rule in ingress["spec"]["rules"]:
                # if (!rule.http.paths) {
                # continue
                # }
                if rule["http"]["paths"] is None:
                    continue
                for path in rule["http"]["paths"]:
                    print(path["backend"]["service_name"])
        # Find linked secrets for TLS certs
        if ingress["spec"]["tls"] is not None:
            for tls in ingress["spec"]["tls"]:
                for secret in secrets_info:
                    if secret["metadata"]["name"] == tls["secret_name"]:
                        print(secret["metadata"]["name"])
    # continue parsing other resource
    # print("Pods in namespace:", json.dumps(pods_info, indent=2))
    # print("Services in namespace:", json.dumps(services_info, indent=2))
    # print("Endpoints in namespace:", json.dumps(endpoints_info, indent

except ApiException as e:
    print("Exception when calling CoreV1Api: %s\n" % e)



