Jenkinsfile (Declarative Pipeline)

pipeline {
    agent { docker { image 'python:3.7.4' } }
    stages {
        stage('install requirements){
            pip install -r requirements.txt
        }
        stage('build') {
            steps {
                pyinstaller -D main.py
            }
        stage('copy') {
            steps {
                cp manual.txt dist/
                cp config.ini dist/
                cp graphics/ dist/
            }
        }
    }
}
