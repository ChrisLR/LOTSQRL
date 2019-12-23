Jenkinsfile (Declarative Pipeline)

pipeline {
    agent { docker { image 'python:3.7.4' } }
    stages {
        stage('build') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pyinstaller -D main.py'
            }
        }
        stage('copy') {
            steps {
                sh 'cp manual.txt dist/'
                sh 'cp config.ini dist/'
                sh 'cp graphics/ dist/'
            }
        }
    }
}
