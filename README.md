---
# Seamless Kubernetes Artifacts Cloning
---
Project Members:
- Yang Zeng Lu (ylu149@bu.edu)
- Huanjia Liang (hjliang@bu.edu)
- Chen Qin (cqin@bu.edu)
- Zeyu Su (suz@bu.edu)


Project Mentors:
- Mudit Verma
- Pankaj Thorat
---

## Demo
1. Sprint 1 Demo
  - Video: https://drive.google.com/file/d/1Z4qHl7f_VoqTE5u_RJZHtbc5YJk-_zHp/view?usp=sharing
  - Slide: https://docs.google.com/presentation/d/1FwfGiANWx7YXiKDqEk44b3bk1b8Ca_JUZ4UpKAlLGbk/edit?usp=share_link
2. Sprint 2 Demo
  - Video: https://drive.google.com/file/d/1N1lxMwgkdPSXE-OrpjoDQ2XdskJj7fPM/view?usp=sharing
  - Slide: https://docs.google.com/presentation/d/18NDsu-o_hRxpfE_t5pgW4kGkH9WqZ_N9FCPA-ZMZKhE/edit?usp=sharing
3. Sprint 3 Demo
  - Video: https://drive.google.com/file/d/1XQgMggvMHjYAgVdGXt7POdgEj9JA3ngk/view?usp=sharing
  - Slide: https://docs.google.com/presentation/d/1oBbQ8YCLvOvei6NFMF049_H8_1s0dvXjS06JYqgdUcA/edit?usp=sharing
4. Sprint 4 Demo
  - Video: https://drive.google.com/file/d/14vOJKMWeUFISYpvTXTyU6z9B0jKTG4GD/view?usp=sharing
  - Slide: https://docs.google.com/presentation/d/1-Ov7xDmd_bAE6YLBiOw2xXWs8F-GsdqVh7idgD6a9QA/edit?usp=sharing

---

## Vision and Goals of The Project: 
As modern computing trends increasingly shift towards offloading computational tasks to the cloud, the deployment of Kubernetes, an open-source platform designed for managing containerized workloads and services, has become indispensable for cloud data centers. 

One significant challenge in deploying Kubernetes within cloud data centers is the replication of Kubernetes object deployments from one cluster to another. Currently, there is no efficient method for transferring existing Kubernetes objects to a new cluster, often requiring developers to manually rewrite code and files to redeploy previously instantiated artifacts on a new cluster. This complexity arises from the fact that Kubernetes objects frequently have dependencies in the form of cluster-specific configurations, configuration maps, node-specific resource requirements, and more.

The objective of this project is to develop a tool that simplifies the migration of Kubernetes artifacts between clusters, reducing the need for manual intervention in existing environments. The concept revolves around examining the Kubernetes etcd (a key-value store used by Kubernetes that contains cluster data) to extract Kubernetes objects and any related dependency information associated with the artifact. If this information can be successfully acquired, the tool will then proceed to analyze the resources available in the new cluster and perform a comparison to identify any discrepancies between the clusters. Once this is complete, the tool should attempt to resolve the dependency issues and deploy the Kubernetes object into the new cluster. This process enables the automatic adjustment of the new cluster to replicate the dependencies of the previous one.

Overall, this seamless method of copying and pasting a Kubernetes object will prove essential for deploying new clusters and even establishing new data centers. It has the potential to reduce documentation requirements during the initial deployment of objects, minimize the time needed to recreate objects on new clusters, and facilitate seamless automation.

---
## Users/Personas Of The Project:
 - **Cloud Developers:** Cloud developers are empowered by this tool to seamlessly migrate deployed Kubernetes objects, or artifacts, between clusters with varying environment setups. It simplifies the process of replicating applications across different stages of development, testing, and production, ensuring consistency and reducing manual configuration overhead.

 - **Site Reliability Engineers (SREs):** SREs can rely on this tool to efficiently duplicate and migrate entire application ecosystems across clusters with diverse configurations. This capability greatly assists in their responsibilities of maintaining application reliability, diagnosing issues, and conducting extensive testing in different environments, ultimately enhancing the overall resilience of the system.

---
## Solution Architecture:
<img width="479" alt="Solution Architecture Image" src="https://github.com/EC528-Fall-2023/Kubernetes-Artifacts-Cloning/assets/36748450/66210d49-6490-479d-83b0-6f7e70f7ffbb">



---
## Solution Concept:
### Build a kubectl plugin called **clone** that can migrate specified objects from source cluster to destination cluster
- **Label Selector**
  Allow selection of user-defined labels to get objects.
  Can be done by
  ```bash
  kubectl get <object> --selector=<label>
  ```
- **Object Selector**
  Allow selection of Kubernetes artifacts.
  Can be done by
  ```bash
  kubectl get <object>
  ```
- **Config Files**
  Allow cluster switching through config files as well as direct access to the cluster.
  Can be done by
  ```bash
  kubectl config view --raw > <filename>.yaml #Get the config file of current cluster
  kubectl --kubeconfig=<filename>.yaml <kubectl command> #Direct kubectl access to given cluster through config file
  ```
- **Dependency Analysis**
  - Method 1: Reverse engineering kubeview to get dependency.
  - Method 2: Filter through YAML files to get dependency. (Need to validate feasibility)
- **Copy Entire Cluster**
  - Method 1: Get needed object information through the Kubernetes API server into a YAML file.
  - Method 2: Get needed object information through ETCD snapshot into a YAML file.
---
## Scope and Features Of The Project:
 - **Easy to use:** Given the command line code specifying source and destination cluster an automatic cloning of artifacts should occur. 
 - **Selective migration:** If given parameters such as namespaces, labels, etc. the program should clone only the given parameters.
 - **Prevent Changes on Artifacts:** Everything within the artifact should stay unchanged after cloning (Pods, API services, Ingresses, ConfigMaps, Secrets, Volumes, Deployments, and StatefulSets) to the destination cluster. 
 - **Automation:** The migration should have minimized manual intervention, and the transfer should be automated.

---
## Minimal Viable Product:
  1. Implement a Kubectl plugin
  2. Migrating all basic objects within a namespace from source cluster to destination cluster
     - Pods
     - Services
     - Persistent Volumes
     - Persistent Volume Chains
     - Namespaces
     - Deployments
     - ReplicaSets
     - DaemonSets
     - StatefulSets
     - ConfigMaps
     - Secrets
   3. Ability to migrate the whole namespace that can consist of multiple objects
   4. Ability to migrate over objects by label
   5. Ability to migrate the whole cluster (including all its objects)

     Example: kubectl -s source_cluster -d destination_cluster --all -n namespace
---
## Reach Goal
**A Kubectl plugin that can clone user-specified object/namespace/label/single object from given source cluster to the destination cluster**
```bash
kubectl clone
  -s/--source <KUBECONFIG_SRC_CLUSTER>
  -d/--destination  <KUBECONFIG_DEST_CLUSTER>
  -o/--objects pods, services, ……….., all
  -l/--labels  e.g. app=robot-shop  
  -n/--namepsace <name>
  -a/--all Everything that exists in this cluster should be migrated
  -i/--item Specified single object with related dependencies
  -h/--help Get usage of plugin

```
Example: 
 - kubectl clone -o all -n robot-shop -s source_config -d dest_config
 - kubectl clone -o pods, services -n robot-shop -s source_config -d dest_config 
 - kubectl clone -a -s source_config -d dest_config 

---
## Release Planning:
- ### First Sprint:
   1. Learn about Kubernetes architecture
   2. Create a small-scale Kubernetes deployment with ~2 or more machines
   3. Migrate namespaces within the same cluster
- ### Second Sprint:
   1. Deploy a more complex Kubernetes application to a Kubernetes cluster
   2. Migrating objects between clusters
   3. Snapshot the ETCD
   4. Use Kubeview to visualize dependency
- ### Third Sprint:
   1. Implement kubectl clone functionality
  
       - Implement object selector flag of kubectl clone
       - Implement namespace selector flag of kubectl clone
       - Implement label selector flag of kubectl clone
- ### Fourth Sprint:
   1. Debug and finalize Clone Utility MVP
   2. Test kubectl clone with different edge cases and input validation
   3. Get all dependencies of a specific object inside a cluster
- ### Fifth Sprint:
   1. Performance analysis of kubectl clone
   2. 2. Use Velereo to migrate PVC Data
   3. Finalize kubectl clone plugin reach goals
 
---
## Terminology:
- **Object(Artifact):** These are entities, typically described in YAML format, within Kubernetes that represent the state of the cluster. They define the running application, resource allocation, and policies for restarts, upgrades, and fault tolerance.

- **Pod:** Pods are the smallest unit of deployment in Kubernetes. They reside on cluster nodes and have their IP addresses, enabling them to communicate with the rest of the cluster. A single pod can host one or more containers, providing storage and networking resources. One of the key characteristics of Kubernetes pods is that they are ephemeral. In practice, a pod can fail without impacting the system's functioning. Kubernetes automatically replaces each failed pod with a new pod replica and keeps the cluster running. Aside from being container wrappers, pods also store configuration information that instructs Kubernetes on how to run the containers.

- **Services:** Services provide a way to expose applications running in pods. Their purpose is to represent a set of pods that perform the same function and set the policy for accessing those pods. Although pod failure is an expected event in a cluster, Kubernetes replaces the failed pod with a replica with a different IP address. This creates problems in communication between pods that depend on each other.

- **Volume:** Volumes are objects whose purpose is to provide storage to pods. There are two basic types of volumes in Kubernetes:
  - **Ephemeral volumes:** Ephemeral volumes persist only during the lifetime of the pod they are tied to.
  - **Persistent volumes:** Persistent volumes are not destroyed when the pod crashes. Persistent volumes are created by issuing a request called PersistentVolumeClaim (PVC). Kubernetes uses PVCs to provision volumes, which then act as links between pods and physical storage.

- **Namespaces:** The purpose of the Namespace object is to act as a separator of resources in the cluster. A single cluster can contain multiple namespaces, allowing administrators to organize the cluster better and simplify resource allocation. A new cluster comes with multiple namespaces created for system purposes and the default namespace for users. Administrators can create any number of additional namespaces - for example, one for development and one for testing.

- **Deployments:** 
  Deployments are controller objects that provide instructions on how Kubernetes should manage the pods hosting a containerized application. Using deployments, administrators can:

    - Scale the number of pod replicas.
    - Rollout updated code.
    - Perform rollbacks to older code versions.

  Once created, the deployment controller monitors the health of the pods and nodes. In case of a failure, it destroys the failed pods and creates new ones. It can also bypass the malfunctioning nodes, enabling the application to remain functional even when a hardware error occurs.


- **ReplicationControllers:** ReplicationControllers ensure that the correct number of pod replicas are running on the cluster at all times. When creating a ReplicationController, the administrator specifies the desired number of pods. The controller then maintains their number, creating additional pods and terminating the extra ones when necessary.

- **ReplicaSets:** ReplicaSets serve the same purpose as ReplicationControllers, i.e. maintaining the same number of pod replicas on the cluster. However, the difference between these two objects is the type of selectors they support. While ReplicationControllers accept only equality-based selectors, ReplicaSets additionally support set-based selectors.

- **DaemonSets:** DaemonSets are controller objects whose purpose is to ensure that specific pods run on specific (or all) nodes in the cluster. Kubernetes scheduler ignores the pods created by a DaemonSet, so those pods last for as long as the node exists. This object is particularly useful for setting up daemons that need to run on each node, like those used for cluster storage, log collection, and node monitoring. By default, a DaemonSet creates a pod on every node in the cluster. If the object needs to target specific nodes, their selection is performed via the nodeSelector field in the configuration file.

- **StatefulSets:** While Deployments and Replication Controllers can handle stateless apps, stateful apps require a workload object called StatefulSet. A StatefulSet gives each pod a unique identity, which persists across pod restarts.

- **ConfigMaps:** ConfigMaps are Kubernetes objects used to store container configuration data in key-value pairs. By separating configuration data from the rest of the container image, ConfigMaps enable the creation of lighter and more portable images. They also allow developers to use the same code with different configurations depending on whether the app is in the development, testing, or production phase.
  
- **Secrets:** Secretes is a type of Kubernetes object that are used to store sensitive information, such as passwords, API keys, and tokens. They provide a way to manage sensitive data and ensure it is securely stored and transmitted to the pods in the cluster.

- **Node:** A Kubernetes Node is a worker machine responsible for running and managing containerized applications. Nodes are the underlying hardware or virtual machines on which Kubernetes runs. Each node has the necessary components to run pods and is managed by the control plane. These components include the kubelet, which is responsible for communication between the control plane and the node, and the kube-proxy, which maintains network rules on the node.

- **Cluster:** A cluster refers to the set of nodes that run containerized applications. These nodes can be physical machines or virtual machines. The cluster is the foundation of Kubernetes and is responsible for running the applications and managing the workloads. It provides a platform for orchestrating and managing containerized applications, ensuring that they run smoothly and reliably.
