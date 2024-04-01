# Fint
Find it, take action: Fint

Fint is a screen recorder designed to monitor and action. 

Fint is a desktop app moniotrs the user's active display (whatever screen the user has selected). Depending on the display we can do different things, character recognition, gesture recognition, measure idle time, pattern matching, etc., some things with AI and some things without, but to identify when a user is doing a certain activity (online shopping, gambling, playing games, slacking off). When Fint identifies a no no, it takes action.

Next projects:
- add mouse gesture recognition support, maybe a learn mode?
- add a GUI
- action support: text with twilio, voice to voice (hume.ai), notifications, open to ideas!
- OS: build Ubuntu, Linux support. Should be easy at this point, add_macOS() is only macOS specific piece to my knowledge
- mobile: would love to add mobile support, iOS permissions might be tough

## Installation and Setup

### Prerequisites

- Created this on python 3.11.8 + macOS

#### 1. Install Poetry
Poetry is a tool for dependency management and packaging in Python. To install Poetry, run the following command:
```sh
pipx install poetry
```


#### 2. Clone the Repository from GitHub:
```sh
git clone https://github.com/sahilpaayj/Fint.git
```

Enter the Repository
```sh
cd Fint
```


#### 3. Activate Virtual Environment (do this every time you are running code)
Poetry creates a virtual environment for your project. This is where dependencies and 'global' variables are stored. To activate this environment, run:
```sh
poetry shell
```


#### 4. Install Dependencies

Install the project dependencies with Poetry:
```sh
poetry install
```

You can later add dependencies with 
```sh
poetry add {some-library}
```