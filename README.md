# FEMA Image Attachment Generator

## Overview

This Python application allows you to create a PDF with up to 4 images, along with a header containing essential property details. The PDF serves as an attachment page to a FEMA Elevation Certificate.

## Features

- Generate a PDF with up to 4 images
- Add a header with property details like:
  - File Number
  - Property Address
  - City
  - State
  - Zip Code
- Include user-defined descriptions for each image
- Add an asterisk note indicating that the PDF is an attachment to a FEMA Elevation Certificate

## Installation

1. Clone this repository
```git clone <https://github.com/yourusername/FEMA-Image-Attachment-Generator.git>```
2. Navigate to the repository folder
```cd FEMA-Image-Attachment-Generator```
3. Install the required packages
```pip install -r requirements.txt```

## Usage

Run `main.py` to start the application.
```python -m FEMA_Attachment_Generator.main```

### GUI Interface

- Follow the on-screen instructions to attach images, add descriptions, and input property details.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT License
