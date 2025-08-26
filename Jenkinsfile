pipeline{
    agent any
    environment{
        VENV_DIR = "venv"
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
    }
}