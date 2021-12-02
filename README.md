#Gui for Braininterface Project
Hierbei handelt es sich um eine Gui, welche mit Hilfe von PySide2 und Matpllotlib generiert wurde.
Zunächst wird ein Canvas erzeugt, auf dem die Grafik abgebildet werden soll.
Da Matplotlib schon viele Nützliche Funktionen beinhaltet, werden auch die Navigation-Tools direkt mit eingebunden, um die Grafik besser anpassen zu können.

Über den Start-Stop Knopf wird ein Timer ausgelöst, der die Grafik automatisch updated.

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

