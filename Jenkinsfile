pipeline {
    agent any

    environment {
        PLAYWRIGHT_BROWSERS_PATH = 'C:/Users/aswin/AppData/Local/ms-playwright'
        OPENSEARCH_URL = 'https://localhost:9200'
        OPENSEARCH_USER = 'admin'
        JUNIT_REPORT = 'C:/ProgramData/Jenkins/.jenkins/workspace/Amazon-Playwright-Automation/reports/junit.xml'
    }

    stages {
        stage('Check Environment') {
            steps {
                bat 'python --version'
                bat 'java --version'
            }
        }

        stage('Check Playwright Browser') {
            steps {
                bat '''
                    dir "C:/Users/aswin/AppData/Local/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-win64"
                '''
            }
        }

        stage('Run Playwright Tests') {
            steps {
                bat '''
                    if not exist "%WORKSPACE%\\reports" mkdir "%WORKSPACE%\\reports"
                '''

                dir('C:/Users/aswin/Desktop/project/amazon-automation') {
                    bat '''
                        "C:/Users/aswin/Desktop/project/amazon-automation/venv/Scripts/python.exe" -m pytest tests -v --html="%WORKSPACE%\\reports\\report.html" --self-contained-html --junitxml="%WORKSPACE%\\reports\\junit.xml"
                    '''
                }
            }
        }

        stage('Publish Results to OpenSearch') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'opensearch-password',
                        variable: 'OPENSEARCH_PASSWORD'
                    )
                ]) {
                    withEnv([
                        'JUNIT_REPORT=C:/ProgramData/Jenkins/.jenkins/workspace/Amazon-Playwright-Automation/reports/junit.xml'
                    ]) {
                        dir('C:/Users/aswin/Desktop/project/amazon-automation') {
                            bat '''
                                "C:/Users/aswin/Desktop/project/amazon-automation/venv/Scripts/python.exe" publish_results.py
                            '''
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true,
                  testResults: 'reports/junit.xml'

            archiveArtifacts artifacts: 'reports/**',
                             allowEmptyArchive: true
        }
    }
}