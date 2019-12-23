Jenkinsfile (Declarative Pipeline)

pipeline {
    agent { docker { image 'python:3.7.4' } }
    stages {
        stage('build') {
            steps {
                pip install -r requirements.txt
                pyinstaller -D main.py
            }
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
