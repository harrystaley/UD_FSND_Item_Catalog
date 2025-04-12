# UD_FSND_Item_Catalog

## Project Overview

This repository hosts a project from the Udacity Full Stack Nanodegree program, showcasing an Item Catalog web application. The application is built using Flask, SQLAlchemy, and OAuth 2.0. The project demonstrates proficiency in frontend styling and backend development with Python. It also includes setup instructions for a Vagrant virtual environment. The web application serves as a microservice, providing a catalog of items for users to browse and interact with.

## Setup and Installation

To get started with this project, follow these steps:

1. Install [Vagrant](https://www.vagrantup.com/downloads.html) and [VirtualBox](https://www.virtualbox.org/wiki/Downloads).
2. Clone this repository.
3. Navigate to the directory of the cloned repository and launch the Vagrant VM by running:
    ```
    $ vagrant up
    ```
4. Once done, log into the VM using:
    ```
    $ vagrant ssh
    ```
5. Navigate to the project's directory within the VM:
    ```
    $ cd /vagrant/UD_FSND_Item_Catalog
    ```
6. Install the project dependencies:
    ```
    $ pip install -r requirements.txt
    ```
7. Run the application:
    ```
    $ python application.py
    ```
8. Open your web browser and visit `http://localhost:8000`

## Usage

Once you've started the application, you can:

- View the list of categories and their items.
- Log in using OAuth 2.0 (Google or Facebook).
- Add, edit, or delete an item (only if you are logged in).
- View the JSON endpoints by visiting `http://localhost:8000/catalog.json`

## Contribution Guidelines

Contributions to this repository are welcome. To contribute:

1. Fork the repository.
2. Create a new branch for your changes.
3. Commit your changes in your branch.
4. Submit a pull request.

Before submitting your pull request, ensure your changes do not break the application. All changes should be well-documented within the code.

## License

This project is licensed under the terms of the MIT license. For more details, see the [LICENSE](LICENSE) file.