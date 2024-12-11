# VS Code
## this guide shall help creating a local dev environment with vscode

* install VScode
> $> yay -S code
* create ~/projects folder
> $> mkdir projects && cd projects
* clone git repos
> $> git clone git@github.com:rine77/homeassistantedupage.git
>
> $> git clone git@github.com:home-assistant/core.git
* open VScode
> $> cd homeassistantedupage
>
> $> code .
* press SHIFT+CTRL+P
* type "Python: Select Interpreter" and choose
* "Create Virtual Environment..."
* "Venv"
* "Create"
* choose at least Python 3.12.xxx
* check args in $projects/homeassistantedupage/.vscode/launch.json it should match your local directory
* open terminal in vscode and install python module homeassistant
> $> source ~projects/homeassistantedupage/.venv/bin/activate
> 
> $> pip install homeassistant
* now start your debug instance with pressing F5
