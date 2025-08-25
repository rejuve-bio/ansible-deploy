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
# Setup Instructions for an existing machine

If you are working on an existing server or computer (i.e., not a fresh install), make sure to update the package lists first. This should complete without any issues:

```bash
sudo apt update
sudo apt upgrade -y
```
# Directory Stracture
```
ansible-deploy/

├── ansible.cfg # Ansible configuration file
├── inventory/
│ └── hosts.ini # Inventory file with target servers
├── playbooks/
│ ├── deploy_server.yml # Main deployment playbook
│ └── roles/
└── UI/
│ └── tasks/main.yml
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
└── Custom_Atomspace_builder/
│ └── tasks/main.yml
---
```
# Step by Step Guide

## Ansible Deployment for the  Custom Atomspace Builder ,the Generic Annotation service and UI

This guide walks through deploying the Rejuve Bio applications using Ansible.

## Prerequisites

- A remote server with SSH access
- Ansible installed on your local machine
- SSH keys configured for password-less login

## Deployment Steps

### 1. Prepare Your Remote Server

If you haven't set up your remote server (where you want to deploy the application), do this first:

1. Manually set up SSH access on your remote server
2. Configure the network so your machine can connect to the server
3. Create and copy SSH keys to the remote server:

```ssh-keygen -t rsa -b 4096```

```ssh-copy-id user@remote-server-ip```

### 2. Clone the Ansible Repository

On your local machine, run:

```git clone https://github.com/rejuve-bio/ansible-deploy.git```

```cd ansible-deploy```

### 3. Configure Inventory File (if you are using Local server ,skip this step)

Edit the inventory file at inventory/hosts.ini:

```[Custom_Atomspace_builder]```

```your_server_ip ansible_user=your_username ansible_port=22 ansible_ssh_private_key_file=~/.ssh/id_rsa ansible_become=true ansible_become_method=sudo```

Replace these placeholders:

- `your_server_ip` – Your server's IP address

- `your_username` – Your SSH username

- `22` – SSH port if different from default use the correct port

- `~/.ssh/id_rsa` – Path to your private key


### 4. Configure Environment Files

# For Custom Atomspace Builder:
# Edit only the following lines in:
# playbooks/roles/Custom_Atomspace_builder/templates/custom-atomspace-builder.env
```bash
LLM_PROVIDER="openai" or "gemini" 
LLM_API_KEY="your_api_key_here"
```
# For Annotation Service:
# Edit only the following lines in:
# playbooks/roles/Annotation/templates/.env
```bash
LLM_MODEL="openai" or gemini
OPENAI_API_KEY="your_LLM_API_KEY_here"
```
### 5. Run the Deployment (for Local Deployment)

Execute the playbook with:

#### to deploy only the UI

```cd /ansible-deploy``` run from the root directory

```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml   --tags UI_Local --ask-become-pass
```

#### to deploy only the Custom Atomspace Builder

```cd /ansible-deploy``` run from the root directory

```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml   --tags Custom_Atomspace_builder_Local --ask-become-pass
```

#### to deploy only the annotation

```cd /ansible-deploy``` run from the root directory

```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml   --tags annotation_Local --ask-become-pass
```

#### to deploy with MORK database

```cd /ansible-deploy``` run from the root directory

```bash 
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml   --tags MORK_Local --ask-become-pass
```

#### to deploy all with only Neo4j database

```cd /ansible-deploy``` run from the root directory 

```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml  --tags UI_Local,annotation_Local,Custom_Atomspace_builder_Local,local_network --ask-become-pass
```

#### to deploy all with MORK database

```cd /ansible-deploy``` run from the root directory 

```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml  --tags UI_Local,annotation_Local,Custom_Atomspace_builder_Local,MORK_Local,local_network --ask-become-pass
```
Enter your sudo password when prompted.

#### to deploy on Remote server

```update  hosts.ini```

```bash
ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml --tags UI_Remote,annotation_Remote,Custom_Atomspace_builder_Remote --ask-become-pass
```

## Summary
-Set up SSH access to your server

-Clone the Ansible repository

-Configure inventory file with your server details

-Update environment/config files for both services

-Run the Ansible playbook






