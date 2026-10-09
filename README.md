# Python AWS Automation Project

A Python Flask application deployed on AWS EC2 using Ansible and Docker, with Nginx as a reverse proxy and Amazon RDS PostgreSQL as the database.

## Project Overview

This project demonstrates how to automate the deployment and operation of a Python web application on AWS.

The application runs inside a Docker container on EC2. Ansible automates Docker installation, application deployment, runtime configuration, and Nginx setup. Database credentials are managed using Ansible Vault.

## Architecture

```text
                     User / Browser
                           |
                        HTTP :80
                           |
                     Nginx Reverse Proxy
                           |
                         AWS EC2
                           |
                      Docker Engine
                           |
                    Flask Application
                           |
                     RDS PostgreSQL
                        Port 5432
```

**Automation flow:**

```text
Local Machine (Ansible Control Node)
                  |
                 SSH
                  |
                 EC2
                  |
        Ansible Playbooks
          |             |
       Install        Deploy
       Docker          App
                         |
                  Docker Container
                         |
                   Nginx :80
                         |
                    RDS Database
```

## Technologies Used

| Technology     | Purpose                                                |
| -------------- | ------------------------------------------------------ |
| Python         | Application development                                |
| Flask          | Web application and HTTP endpoints                     |
| PostgreSQL     | Relational database                                    |
| Amazon EC2     | Application hosting                                    |
| Amazon RDS     | Managed PostgreSQL database                            |
| Docker         | Application packaging and container execution          |
| Ansible        | Infrastructure configuration and deployment automation |
| Nginx          | Reverse proxy for incoming HTTP traffic                |
| Ansible Vault  | Protection of database secrets                         |
| Git and GitHub | Version control and source code hosting                |
| Linux and SSH  | Server administration and remote access                |

## Application Endpoints

| Endpoint  | Purpose                             |
| --------- | ----------------------------------- |
| `/`       | Displays the project home page      |
| `/health` | Checks application health           |
| `/users`  | Retrieves user data from PostgreSQL |

## Repository Structure

python-ansible-aws-project/
├── app/
│   ├── app.py
│   └── requirements.txt
│
├── inventory/
│   ├── hosts
│   └── group_vars/
│       └── webservers/
│           ├── vars.yml
│           └── vault.yml
│
├── playbooks/
│   ├── configure-nginx.yml
│   ├── configure-service.yml
│   ├── deploy-app.yml
│   ├── deploy-docker-app.yml
│   ├── disable-old-app.yml
│   ├── install-docker.yml
│   └── setup-server.yml
│
├── templates/
│   ├── docker.env.j2
│   ├── myapp.service.j2
│   └── nginx.conf.j2
│
├── .dockerignore
├── .gitignore
├── Dockerfile
└── README.md


## Prerequisites

* An AWS account with an Ubuntu EC2 instance.
* An RDS PostgreSQL database reachable from EC2.
* Security groups configured for SSH access, HTTP traffic, and EC2-to-RDS PostgreSQL connectivity.
* Ansible installed on the control machine.
* SSH access to the EC2 instance.
* Database settings configured in Ansible group variables.
* Database password stored in encrypted Ansible Vault variables.

## Configuration

### 1. Configure the inventory

Update `inventory/hosts` with the current EC2 public IP and the correct SSH key path.

Example:

```ini
[webservers]
server1 ansible_host=<EC2_PUBLIC_IP> ansible_user=ubuntu ansible_ssh_private_key_file=~/ansible-key.pem
```

Use your actual EC2 address locally. Avoid publishing unnecessary infrastructure details.

### 2. Configure database variables

Set non-secret connection settings in:

```text
inventory/group_vars/webservers/vars.yml
```

The application uses these environment variables:

```text
DB_HOST
DB_NAME
DB_USER
DB_PASSWORD
DB_PORT
```

Store the database password in the encrypted Vault file. The `templates/docker.env.j2` template passes the values into the container at runtime.

## Deployment

Run commands from the project root on the Ansible control machine.

### Step 1: Test Ansible connectivity

```bash
ansible webservers -i inventory -m ping --ask-vault-pass
```

### Step 2: Install Docker on EC2

```bash
ansible-playbook -i inventory playbooks/install-docker.yml --ask-vault-pass
```

### Step 3: Handle the existing systemd application

If the legacy `myapp.service` is still running on port 5000, stop and disable it before deploying Docker on the same host port:

```bash
ansible-playbook -i inventory playbooks/disable-old-app.yml --ask-vault-pass
```

This step is for the migration from the old systemd deployment.

### Step 4: Deploy the Docker application

```bash
ansible-playbook -i inventory playbooks/deploy-docker-app.yml --ask-vault-pass
```

This playbook copies the application files to EC2, prepares the runtime environment, builds the Docker image, starts the container, and tests the health and database endpoints.

### Step 5: Configure Nginx

```bash
ansible-playbook -i inventory playbooks/configure-nginx.yml --ask-vault-pass
```

Nginx forwards incoming HTTP requests to the Flask application exposed on EC2 port 5000.

## Verification

Check the running container:

```bash
ansible webservers -i inventory -m command -a "docker ps" -b --ask-vault-pass
```

Check the application locally on EC2:

```bash
ansible webservers -i inventory -m uri -a "url=http://127.0.0.1:5000/health status_code=200" -b --ask-vault-pass
```

Test the public application from your local machine, replacing the placeholder with the current EC2 public IP:

```bash
curl -I http://<EC2_PUBLIC_IP>
curl http://<EC2_PUBLIC_IP>/health
curl http://<EC2_PUBLIC_IP>/users
```

## Security Practices

* Keep `vault.yml` encrypted and never commit database passwords in plaintext.
* Never commit private SSH keys, `.pem` files, or runtime `.env` files.
* Use `.dockerignore` to keep credentials and unnecessary files out of the Docker build context.
* Keep database credentials out of the Dockerfile and Docker image.
* Restrict the RDS security group to the required application resources.
* Allow public HTTP access through Nginx instead of exposing the Flask backend port directly to the internet.
* Limit SSH access to trusted source IP addresses.

## Learning Outcomes

This project provides practical experience with:

* Linux and SSH administration.
* AWS EC2 and RDS connectivity.
* Python Flask application deployment.
* Docker images, containers, port mapping, and runtime environment variables.
* Ansible inventories, group variables, playbooks, templates, and service management.
* Ansible Vault for secret management.
* Nginx reverse proxy configuration.
* Git commits and GitHub-based source control.

## Future Improvements

* Improve deployment idempotency and rollback handling.
* Add structured application logging and monitoring.
* Use AWS IAM roles and managed secret storage where appropriate.
* Add automated tests and more deployment health checks.
