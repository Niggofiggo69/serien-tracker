name: Build Android APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Code auschecken
        uses: actions/checkout@v4

      - name: Python einrichten
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Android SDK Lizenzen akzeptieren
        run: yes | sdkmanager --licenses || true

      - name: Flet CLI & Abhängigkeiten installieren
        run: |
          pip install flet==0.85.1

      # FIX: Wir "füttern" Flet mit automatischen Ja-Antworten, damit es ohne Fragen durchläuft
      - name: APK builden
        run: |
          yes "" | flet build apk

      - name: APK als Download bereitstellen
        uses: actions/upload-artifact@v4
        with:
          name: serien-tracker-apk
          path: build/apk/*.apk
