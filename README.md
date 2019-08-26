erd-repl is a basic REPL web app for [erd](https://github.com/BurntSushi/erd), it's based on erd, Flask, Backbone, and Bootstrap.
It lets you easily preview the result of your erd source code on the web so that you can try erd in no time and "draw" ERD diagrams quickly.

You can try it online on https://serene-forest-18642.herokuapp.com/erd-repl/.
Or, if you like to try it locally, here are the steps by using a virtualenv:

1. Create a new virtualenv: `python -m venv ~/venv/erd-repl && source ~/venv/erd-repl/bin/activate`
2. Install Python packages: `pip install -r requirements.txt`
3. git clone this repo and modify `config.py` to meet your needs, especially the `erd` binary path.
4. Run the app by `python erd.py`

Note: the `erd` binary must reside somewhere on your system, of course.

