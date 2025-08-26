pipeline{
    agent any
    stages{
        stage("Cloning from github"){
            steps{
                script{
                    echo "Cloning the repository"
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/Vbalimidi/Anime-Recomender-System.git']])
                }
            }
        }
    }
}