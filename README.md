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

```git clone https://github.com/Abdu1964/ansible-deploy_v2.0.git```
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
For Custom Atomspace Builder:

Edit these files in playbooks/roles/Custom_Atomspace_builder/templates/:

```custom-atomspace-builder.env```
```config.yaml.j2```

## For Annotation Service:
create your  .env in playbooks/roles/annotation/templates/

```cd playbooks/roles/annotation/templates/```

create .env and configure it

## For UI :
create your  .env in playbooks/roles/UI/templates/

```cd playbooks/roles/annotation/templates/```

create .env and configure it

### 5. Run the Deployment (for Local Deployment)
Execute the playbook with:
#### to deplay only the UI

```cd /ansible-deploy``` run from the root directory

```ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml   --tags UI_Local --ask-become-pass```

#### to deplay only the Custom Atomspace Builder

```cd /ansible-deploy``` run from the root directory

```ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml   --tags Custom_Atomspace_builder_Local --ask-become-pass```

#### to deplay only the annotation

```cd /ansible-deploy``` run from the root directory

```ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml   --tags annotation_Local --ask-become-pass```

#### to deplay all
```cd /ansible-deploy``` run from the root directory

```ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml   --tags UI_Local,annotation_Local,Custom_Atomspace_builder_Local --ask-become-pass```

Enter your sudo password when prompted.

#### to deplay on Remote server
```update  hosts.ini```
```ansible-playbook -i inventory/hosts.ini playbooks/deploy_server.yml   --tags UI_Remote,annotation_Remote,Custom_Atomspace_builder_Remote --ask-become-pass```

## Summary
-Set up SSH access to your server

-Clone the Ansible repository

-Configure inventory file with your server details

-Update environment/config files for both services

-Run the Ansible playbook

