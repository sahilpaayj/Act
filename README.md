# Act

AI needs context to be used in a meaningful way. AI wearables let you context IRL, but so much of the user's time is on the phone or computer.

There is learn mode, where you can teach an AI a repetetive action.
There is recall, where the AI can tell you anything that happened.
There is not a way for an AI to understand when to take action without defined triggers. Computer context will enable AI to do this.

On a computer or phone, Act monitors the user's active display (whatever screen the user has selected). Depending on the display monitor in different ways, character, gesture, or object recognition, pattern matching, measure idle time, etc. or any combination. The aim of Act is to identify certain things, events, patterns, etc. to provide AI agents with the ability to act.

Next projects:
- browser extension to parse HTML for key words or phrases
- gesture + object recognition
- GUI is in tkinter... sole purpose is to launch background process, not supposed to interact with it much. Open to ideas for better desktop apps!
- Add hume to understand user sentiment when taking action
- OS: Ubuntu, Linux support. Should be easy at this point, display and multiprocessing fork in app_run() are macOS
- mobile: would love to add mobile support, iOS permissions might be tough to get around, Shortcuts are an option but its not perfect by any means. Please help.

## Installation and Setup

### Prerequisites

- python 3.11.8
- macOS (for now)

#### 1. Install Poetry
Poetry is a tool for dependency management and packaging in Python. 
To install Poetry, run the following command:
```sh
pipx install poetry
```


#### 2. Clone the Repository from GitHub:
```sh
git clone [copy link]
```

Enter the Repository
```sh
cd [repo]
```


#### 3. Activate Virtual Environment (do this every time you are running code)
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