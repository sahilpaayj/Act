Certainly! I'll format the setup instructions for your project Fint in a README.md style, incorporating best practices for installing Poetry and setting up the project.

# Fint

Fint is a screen recorder designed to monitor online shopping activity. It captures images of the user's active window, processes them with OCR (Optical Character Recognition) and/or a Language Model. If the AI detects online shopping activity, it alerts hume.ai, an emotionally aware voice-to-voice AI, to engage with the user and help reconsider their purchasing decisions.

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