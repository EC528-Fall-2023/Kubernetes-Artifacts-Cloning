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
## 1. Vision and Goals of The Project: 
Our project aims to develop a tool that will help our users migrate Kubernetes artifacts between clusters with zero downtime.

### Goal:
 - **Easy to use**
 - **Seamless clone**
 - **Selective migration** 
 - **Automation**
---
## 2. Users/Personas Of The Project:
This tool should be used by **Cloud Developers** and/or **SREs(Site Reliability Engineers)** who need to migrate deployed artifacts to a cluster that might have a different environment setup.

---
## 3. Scope and Features Of The Project:
 - **Easy to use** With a given source and destination cluster, the command line will trigger the tool for artifact cloning.
 - **Seamless clone** Everything within the artifact should stay unchanged after cloning (like Pod, Service, Ingress, Config Map, Secrets, Volumes, Deployment, and StatefulSet)
 - **Selective migration** With given parameters such as namespaces, labels, and so on, the user can migrate part of the artifact
 - **Automation** The migration should have minimized manual intervention, and the transfer should be automated. With just one command, the transfer is done and safe.

---
## 4. Solution Concept:

---
## 5. Acceptance criteria:

---
## 6. Release Planning:
