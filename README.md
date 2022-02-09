Um Das Projekt zum Laufen zu bringen, sollte man zunächst ein Virtual Environment anlegen.

Dies geht über:
python -m venv venv

Um das venv zu aktivieren nutzt man folgenden Befehl:
venv\Script\activate

wenn ein Fehler auftritt kann das bei windows an sicherheitseinstellungen liegen dann nutzt man diesen Befehl:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
und anschließend 
venv\Scripts\activate  (je nach python installation \Script\... oder \Scripts\...)

(Alles aus dem Root-Verzeichnis heraus)

als nächstes installiert man über 
pip install -r requirements.txt

die benötigten Module.

Ich verwende übrigens Python3.7.9

Wenn eines der python-scripts ausgeführt werden soll, sollte das Workingdirectory = dem Ordner des Scripts sein, da andere Dateien über sys.path.append('../../Brain_Interface') eingebunden werden
