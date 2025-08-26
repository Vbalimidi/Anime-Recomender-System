pipeline{
    agent any
    environment{
        VENV_DIR = "venv"
        GCP_PROJECT = "animerecomender"
        GCLOUD_PATH = "/var/jenkins_home/google-cloud-sdk/bin"
        KUBECTL_AUTH_PLUGIN = "/usr/lib/google-cloud-sdk/bin"
    }
    stages{
        stage("Cloning from github"){
            steps{
                script{
                    echo "Cloning the repository"
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Vbalimidi/Anime-Recomender-System.git']])
                }
            }
        }

        stage("Making a virtual environment"){
            steps{
                script{
                    echo "Making a virtual environment"
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    pip install dvc
                    '''
                }
            }
        }

        stage("Pulling data from dvc remote storage"){
            steps{
                withCredentials([file(credentialsId:'gcp-anime', variable:'GOOGLE_APPLICATION_CREDENTIALS')]){
                    echo "Pulling data from dvc remote storage"
                    sh'''
                    . ${VENV_DIR}/bin/activate
                    dvc pull
                    '''
                }
            }
        }

        stage("Building docker image"){
            steps{
                withCredentials([file(credentialsId:'gcp-anime', variable:'GOOGLE_APPLICATION_CREDENTIALS')]){
                    echo "Building docker image"
                    sh'''
                    export PATH=$PATH:${GCLOUD_PATH}
                    gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
                    gcloud config set project ${GCP_PROJECT}
                    gcloud auth configure-docker --quiet
                    docker build -t gcr.io/${GCP_PROJECT}/anime-recomender:latest .
                    docker push gcr.io/${GCP_PROJECT}/anime-recomender:latest
                    '''
                }
            }
        }

        stage("Deploying to Kubernetes"){
            steps{
                withCredentials([file(credentialsId:'gcp-anime', variable:'GOOGLE_APPLICATION_CREDENTIALS')]){
                    echo "Deploying to Kubernetes"
                    sh'''
                    export PATH=$PATH:${GCLOUD_PATH}:${KUBECTL_AUTH_PLUGIN}
                    gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
                    gcloud config set project ${GCP_PROJECT}
                    gcloud container clusters get-credentials anime-app-cluster --region us-central1
                    kubectl apply -f deployment.yaml
                    '''
                }
            }
        }
    }
}