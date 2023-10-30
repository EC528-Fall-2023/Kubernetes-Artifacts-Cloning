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
![alt text](https://github.com/EC528-Fall-2023/Kubernetes-Artifacts-Cloning/blob/main/solution%20structure.jpg "Structure for the solution")

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

   Migrating all basic objects within a namespace from source cluster to destination cluster
   - Pods
   - Services
   - Persistent Volumes
   - Namespaces
   - Deployments
   - ReplicaSets
   - DaemonSets
   - StatefulSets
   - ConfigMaps
   - Secrets

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
## Acceptance criteria:
Finding out whether cloning a Kubernetes Artifact from a source cluster to a destination cluster with command line syntax is feasible.

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
   1. Get objects from ETCD snapshot
   2. Compare querying object between etcd & kubernetes api
   3. Test kubectl clone with different cases
   4. Get dependencies of specific cluster
- ### Fifth Sprint:
   1. Performance analysis of kubectl clone
   2. Finalize kubectl clone plugin
 
---
## Terminology:
- **Object(Artifact):** These are entities, typically described in YAML format, within Kubernetes that represent the state of the cluster. They define the running application, resource allocation, and policies for restarts, upgrades, and fault tolerance.

- **Pod:** A Kubernetes Pod is a collection of one or more containers that share storage and network resources.

- **Node:** A Kubernetes Node is a worker machine responsible for running and managing containerized applications.

- **Cluster:** A Kubernetes Cluster is a grouping of nodes that run containerized applications in an automated and distributed manner.

- **ConfigMaps:** ConfigMaps are API objects that allow you to store configurations for other objects to use in the form of key-value pairs.
