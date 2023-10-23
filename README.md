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
- Sprint 1 Demo https://drive.google.com/file/d/1Z4qHl7f_VoqTE5u_RJZHtbc5YJk-_zHp/view?usp=sharing
- Sprint 2 Demo https://drive.google.com/file/d/1N1lxMwgkdPSXE-OrpjoDQ2XdskJj7fPM/view?usp=sharing

---
## Terminology:
- **Object(Artifact):** These are entities, typically described in YAML format, within Kubernetes that represent the state of the cluster. They define the running application, resource allocation, and policies for restarts, upgrades, and fault tolerance.

- **Pod:** A Kubernetes Pod is a collection of one or more containers that share storage and network resources.

- **Node:** A Kubernetes Node is a worker machine responsible for running and managing containerized applications.

- **Cluster:** A Kubernetes Cluster is a grouping of nodes that run containerized applications in an automated and distributed manner.

- **ConfigMaps:** ConfigMaps are API objects that allow you to store configurations for other objects to use in the form of key-value pairs.


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
## Scope and Features Of The Project:
 - **Easy to use:** Given the command line code specifying source and destination cluster an automatic cloning of artifacts should occur. 
 - **Selective migration:** If given parameters such as namespaces, labels, etc. the program should clone only the given parameters.
 - **Prevent Changes on Artifacts:** Everything within the artifact should stay unchanged after cloning (Pods, API services, Ingresses, ConfigMaps, Secrets, Volumes, Deployments, and StatefulSets) to the destination cluster. 
 - **Automation:** The migration should have minimized manual intervention, and the transfer should be automated.

---
## Solution Concept:
The project aims to address the challenges associated with replicating Kubernetes clusters in an efficient and automated manner. The proposed solution concept involves a multi-step approach, with a strong emphasis on feasibility analysis, which includes dependency analysis, selective migration, and the utilization of Kubernetes' etcd for the migration process.

### 1. Dependency Analysis:

   A dependency analysis will be carried out to determine the relationships and dependencies between Kubernetes objects within a cluster.  
   The goal is to identify any dependencies that may hinder successful migration and to develop strategies for resolving them.

### 2. Selective Migration:

   The migration utility will support selective migration based on parameters such as namespaces, labels, and object types.
   Users will be able to specify which objects and configurations they want to migrate from the source cluster to the destination cluster.

### 3. Leveraging Kubernetes etcd:
   
   The project capitalizes on local key-value store of Kubernetes' cluster, known as etcd, which stores critical information about the cluster, such as Kubernetes clusters’ configurations.
   By interfacing with etcd, the utility gains access to a comprehensive source of information regarding the cluster's objects and their relationships.

By examining the three key aspects during tool development, we can determine the viability of our proposed concept. If it's not feasible, we'll provide a clear explanation detailing why and the challenges faced.

---
## Acceptance criteria:
Finding out whether cloning a Kubernetes Artifact from a source cluster to a destination cluster with command line syntax is feasible.

---
## Release Planning:
- ### First Sprint:
   1. Learn about Kubernetes
   2. Create a small-scale Kubernetes deployment with ~2 or more machines
   3. Look into the etcd to see what information is available
- ### Second Sprint:
- ### Third Sprint:
- ### Fourth Sprint:
- ### Fifth Sprint:
