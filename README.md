# TFG---CoraHealth-Platform
Here is my Bachelor Thesis for Biomedical Engineering, a intuituve platform for Cardiovascular prediction and data analysis. Aquí se encuentra mi Trabajo de FIn de Grado, una plataforma intuitiva para la predicción de riesgo cardiovascular y visualización de datos clínicos.

READ_ME (EN):

This document details how to run the application developed with Streamlit to access the platform from any computer.
Important: For the platform to display correctly, it is recommended to use your browser in dark mode.

0. Prerequisites
Before starting, make sure you have Python 3.8 or higher installed. You can download it from python.org. During the installation on Windows, make sure to check the "Add Python to PATH" option.

1. Download and unzip the project
Download the .zip file containing this document and unzip it in your preferred location (for example, in your Downloads folder or on your Desktop).

2. Open the system terminal
- Windows: Press Win + R, type cmd, and press Enter. You can also search for PowerShell in the Windows search bar.
- macOS: Press Cmd + Space, type Terminal, and press Enter.

3. Install Streamlit (if not already installed)
Type the following command in the terminal and press Enter:
pip install streamlit
Note for macOS or Linux users: If the previous command doesn't work, use pip3 instead (throughout all installations, see step 5):
pip3 install streamlit

 
4. (Optional) Create a virtual environment
It is highly recommended to create a virtual environment to keep the project's dependencies isolated.
Run the following command inside the project folder (after navigating to the unzipped .zip folder using the cd command):
python -m venv venv

Activate the virtual environment:
- On Windows:
venv\Scripts\activate
- On macOS / Linux:
source venv/bin/activate
 

5. Install the required libraries
The platform requires a series of additional dependencies. First, navigate to the project folder (see step 5) and run:
pip install -r requirements.txt
This will automatically install all the necessary libraries for the application to work correctly.

6. Run the platform
Change the terminal directory to the project folder using the cd command, replacing the path with the actual location where you unzipped the .zip file:
cd C:\Users\YourUser\Downloads\my_platform
Next, run the application with:
streamlit run app.py
Alternative: If you prefer not to change directories, you can run the full path directly:
streamlit run C:\Users\YourUser\Downloads\my_platform\app.py
The platform will open automatically in a new tab in your browser. If it doesn't open on its own, copy and paste the address that appears in the terminal into your browser, typically: http://localhost:8501

Common problems and how to solve them
- "pip is not recognized as an internal or external command": Ensure that Python is properly installed and that the option to add it to the system's PATH was checked during installation.
- "Module not found": Run pip install -r requirements.txt again and double-check that you are in the correct project folder in your terminal.
- The browser does not open automatically: Manually copy the address http://localhost:8501 and paste it into your web browser's search bar.


READ_ME (ES):
En este documento se detalla cómo ejecutar la aplicación desarrollada con Streamlit para acceder a la plataforma desde cualquier ordenador.

Importante: para la correcta visualización de la plataforma, se recomienda tener el navegador en modo oscuro.

0.- Requisitos previos
Antes de comenzar, asegúrate de tener instalado Python 3.8 o superior. Puedes descargarlo desde python.org. Durante la instalación en Windows, marca la opción "Add Python to PATH".

1. Descargar y descomprimir el proyecto
Descarga el archivo .zip que contiene este documento y descomprímelo en la ubicación que desees (por ejemplo, en la carpeta Descargas o en el Escritorio).

2. Abrir la terminal del sistema
•	Windows: Pulsa Win + R, escribe cmd y pulsa Enter. También puedes buscar PowerShell en el buscador de Windows.
•	macOS: Pulsa Cmd + Espacio, escribe Terminal y pulsa Enter.

3. Instalar Streamlit (si no está instalado)
Escribe el siguiente comando en la terminal y pulsa Enter:
pip install streamlit

Nota para usuarios de macOS o Linux:
Si el comando anterior no funciona, usa pip3 en su lugar (a lo largo de todas las instalaciones, ver punto 5):
pip3 install streamlit

4. (Opcional) Crear un entorno virtual
Se recomienda crear un entorno virtual para mantener separadas las dependencias del proyecto.
Ejecuta los siguientes comandos dentro de la carpeta del proyecto (habiendo cambiado la ruta mediante el comando cd y la ubicación del archivo .zip descomprimido):
python -m venv venv

Activa el entorno virtual:
- En Windows:
venv\Scripts\activate
- En macOS / Linux:
source venv/bin/activate
 

5. Instalar las librerías necesarias
La plataforma requiere una serie de dependencias adicionales. Navega primero hasta la carpeta del proyecto (ver paso 5) y ejecuta:
pip install -r requirements.txt
Esto instalará automáticamente todas las librerías necesarias para que la aplicación funcione correctamente.


6. Ejecutar la plataforma
Cambia el directorio de la terminal a la carpeta del proyecto con el comando cd, sustituyendo la ruta por la ubicación real donde descomprimiste el .zip:
cd C:\Users\TuUsuario\Downloads\mi_plataforma
A continuación, ejecuta la aplicación con:
streamlit run app.py

Alternativa: si prefieres no cambiar de directorio, puedes ejecutar la ruta completa directamente:
streamlit run C:\Users\TuUsuario\Downloads\mi_plataforma\app.py

La plataforma se abrirá automáticamente en una pestaña de tu navegador. Si no se abre sola, copia y pega en el navegador la dirección que aparece en la terminal, normalmente:
http://localhost:8501

Problemas comunes y cómo solucionarlos

- "pip no se reconoce como comando": asegura de que Python está bien instalado y añadido al PATH del sistema.
- "Module not found": ejecuta de nuevo pip install -r requirements.txt y comprueba que estás en la carpeta correcta.
- El navegador no se abre automáticamente: copia manualmente la dirección http://localhost:8501 en tu navegador.
