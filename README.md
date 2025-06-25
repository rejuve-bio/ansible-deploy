# 🧠 Rejuve Bio Service Deployment (Ansible)

An infrastructure automation project for deploying Rejuve Bio’s core services to dedicated servers using Ansible. This setup includes centralized inventory, reusable roles, and a unified playbook to streamline deployment and scaling across environments.

---

## 📦 Features

- 🚀 One-command deployment for all services  
- 🧬 Support for Biocypher KG, Annotation, AI Assistant, Hypothesis, and Galaxy  
- 🔐 Secure configuration via `ansible-vault`  
- 🔁 Modular Ansible roles for reusability and scaling  
- 📂 Organized directory structure for inventory, roles, and playbooks  
- 🧰 Compatible with SSH-based provisioning and cloud/VPS instances  

---

## ⚙️ Installation

### Prerequisites

- Python 3.8+  
- Ansible 2.10+  
- SSH access to your target servers  
- Passwordless `sudo` access for deployment user  

---
# Directory Stracture
```
ansible-deploy/
├── ansible.cfg # Ansible configuration file
├── inventory/
│ └── hosts.ini # Inventory file with target servers
├── playbooks/
│ ├── deploy_server.yml # Main deployment playbook
│ └── roles/
│ ├── biocypher/
│ │ └── tasks/main.yml
│ ├── annotation/
│ │ └── tasks/main.yml
│ ├── AI_Assistant/
│ │ └── tasks/main.yml
│ ├── Hypothesis/
│ │ └── tasks/main.yml
│ └── Galaxy/
│ └── tasks/main.yml

---

## Clone the repository

```bash
git clone https://github.com/rejuve-bio/ansible-deploy.git
cd ansible-deploy

#🛠 Customize Services Before Deployment
##Navigate to the playbooks/roles/ directory:

```bash
cd playbooks/roles
```
##2.Select the service(s) you want to deploy
##Open and edit the tasks/main.yml file inside the selected role folder(s) to match your deployment logic:
```bash
- name: Pull and run AI Assistant container
  docker_container:
    name: ai_assistant
    image: rejuvebio/ai-assistant:latest
    ports:
      - "8080:8080"
    restart_policy: always
```
---
#▶️ Running the Deployment
##Deploy All Services
###To deploy all services as defined in the deploy_server.yml playbook:
```bash
ansible-playbook playbooks/deploy_server.yml
```
##Deploy a Specific Service
###To deploy a specific service only (e.g. biocypher):
```bash
ansible-playbook playbooks/deploy_server.yml --limit biocypher
```

---

